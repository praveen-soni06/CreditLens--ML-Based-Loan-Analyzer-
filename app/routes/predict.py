from datetime import datetime, timedelta
from email.utils import parseaddr
from functools import lru_cache
from pathlib import Path

from flask import Blueprint, current_app, flash, jsonify, render_template, request, session, redirect, url_for
import joblib
import pandas as pd

from app.database.db import db, Application, Prediction, EmailVerification
from app.utils.email_utils import (
    generate_verification_code,
    get_email_delivery_notice,
    is_smtp_configured,
    send_application_status_email,
    send_verification_code_email,
    send_decision_notification_email,
)
from app.utils.lifecycle import add_timeline_event, generate_application_ref, set_application_status
from app.utils.nlp_explainer import (
    explanation_record_to_payload,
    generate_loan_decision_explanation,
    get_latest_decision_explanation,
    save_decision_explanation,
)

predict_bp = Blueprint('predict', __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / 'ML' / 'model.pkl'
SCALER_PATH = PROJECT_ROOT / 'ML' / 'scaler.pkl'

FEATURE_COLUMNS = [
    'person_age',
    'person_gender',
    'person_education',
    'person_income',
    'person_emp_exp',
    'loan_amnt',
    'loan_int_rate',
    'loan_percent_income',
    'credit_history_length',
    'credit_score',
    'previous_loan_defaults_on_file',
    'age_group',
    'income_group',
    'credit_category',
    'person_home_ownership_OTHER',
    'person_home_ownership_OWN',
    'person_home_ownership_RENT',
    'loan_intent_EDUCATION',
    'loan_intent_HOMEIMPROVEMENT',
    'loan_intent_MEDICAL',
    'loan_intent_PERSONAL',
    'loan_intent_VENTURE',
]

EDUCATION_ORDER = {
    'High School': 0,
    'Associate': 1,
    'Bachelor': 2,
    'Master': 3,
    'Doctorate': 4,
}

LOW_RISK_CONFIDENCE_THRESHOLD = 0.75
MAX_VERIFICATION_ATTEMPTS = 5
VALID_HOME_OWNERSHIP = {'RENT', 'OWN', 'MORTGAGE', 'OTHER'}
VALID_LOAN_INTENTS = {
    'PERSONAL',
    'EDUCATION',
    'MEDICAL',
    'HOMEIMPROVEMENT',
    'VENTURE',
    'DEBTCONSOLIDATION',
}


def require_loan_assistant():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if session.get('role') != 'loan_assistant':
        return redirect(url_for('dashboard.dashboard'))

    return None


def is_valid_email(value):
    parsed_name, parsed_email = parseaddr(value)
    return bool(
        parsed_email
        and parsed_email == value
        and '@' in parsed_email
        and '.' in parsed_email.rsplit('@', 1)[-1]
    )


def get_prediction_result_and_risk(ml_decision, confidence_score):
    risk_score, risk_level = get_risk_score_and_category(ml_decision, confidence_score)
    hybrid_decision = get_hybrid_decision_by_risk(risk_level)

    if hybrid_decision == "approved":
        return "Approved", risk_level
    if hybrid_decision == "rejected":
        return "Rejected", risk_level

    # For medium risk, keep model tendency for explanation while final decision stays pending.
    return get_result_from_ml_decision(ml_decision), risk_level


def get_approval_class_label():
    return int(current_app.config.get("MODEL_APPROVAL_CLASS_LABEL", 0))


def get_result_from_ml_decision(ml_decision):
    return "Approved" if int(ml_decision) == get_approval_class_label() else "Rejected"


def get_risk_score_and_category(ml_decision, confidence_score):
    confidence = float(confidence_score or 0.0)
    confidence = max(0.0, min(1.0, confidence))
    decision_result = get_result_from_ml_decision(ml_decision)

    # Risk score is interpreted as probability of repayment stress.
    risk_score = (1.0 - confidence) if decision_result == "Approved" else confidence

    if decision_result == "Approved" and confidence >= LOW_RISK_CONFIDENCE_THRESHOLD:
        return risk_score, "Low"
    if decision_result == "Rejected" and confidence >= LOW_RISK_CONFIDENCE_THRESHOLD:
        return risk_score, "High"
    return risk_score, "Medium"


def get_hybrid_decision_by_risk(risk_level):
    normalized = str(risk_level or "").strip().lower()
    if normalized == "low":
        return "approved"
    if normalized == "high":
        return "rejected"
    return "pending"


def get_latest_prediction(application_id):
    return (
        Prediction.query
        .filter_by(application_id=application_id)
        .order_by(Prediction.predicted_at.desc(), Prediction.id.desc())
        .first()
    )


def render_prediction_result(result_data):
    prediction = result_data.get('prediction')
    return render_template(
        'result.html',
        result=result_data['result'],
        reasons=result_data['reasons'],
        suggestions=result_data['suggestions'],
        risk_level=result_data['risk_level'],
        risk_score=result_data.get('risk_score'),
        applicant_name=result_data['applicant_name'],
        application_id=result_data['application_id'],
        nlp_explanation=result_data.get('nlp_explanation'),
        confidence_score=prediction.confidence_score if prediction else None
    )


def get_dev_verification_code(verification):
    if current_app.config.get('EMAIL_DEV_OUTBOX', True) and not is_smtp_configured():
        return verification.verification_code
    return None


def get_result_redirect_url(application_id):
    return url_for('predict.prediction_result', application_id=application_id)


def get_submission_redirect_url(application_id):
    return url_for('predict.submission_status', application_id=application_id)


def render_email_verification_screen(application, verification, error=None, delivery_notice=None):
    return render_template(
        'verify_email.html',
        application_id=application.id,
        customer_email=application.customer_email,
        customer_name=application.customer_name,
        error=error,
        delivery_notice=delivery_notice,
        dev_verification_code=get_dev_verification_code(verification)
    )


def generate_and_store_nlp_explanation(application, prediction, result, risk_level, confidence_score, language_code="en", force=False):
    if not force:
        existing = get_latest_decision_explanation(
            application_id=application.id,
            decision_result=result,
            language_code=language_code
        )
        if existing:
            return explanation_record_to_payload(existing)

    explanation_data = generate_loan_decision_explanation(
        application=application,
        prediction=prediction,
        result=result,
        risk_level=risk_level,
        confidence_score=confidence_score,
        language_code=language_code
    )

    record = save_decision_explanation(
        application=application,
        prediction=prediction,
        decision_result=result,
        language_code=language_code,
        explanation_data=explanation_data
    )
    return explanation_record_to_payload(record)


def validate_application_values(
    customer_name,
    customer_email,
    person_age,
    person_gender,
    person_education,
    person_income,
    person_emp_exp,
    person_home_ownership,
    credit_score,
    credit_history_length,
    previous_loan_defaults_on_file,
    loan_amnt,
    loan_int_rate,
    loan_intent,
):
    errors = []

    if not customer_name:
        errors.append("Customer name is required.")
    if not is_valid_email(customer_email):
        errors.append("A valid customer email is required for application-time OTP verification.")
    if not 18 <= person_age <= 80:
        errors.append("Age must be between 18 and 80.")
    if person_gender not in (0, 1):
        errors.append("Gender selection is invalid.")
    if person_education not in EDUCATION_ORDER:
        errors.append("Education selection is invalid.")
    if person_income <= 0:
        errors.append("Annual income must be greater than zero.")
    if person_emp_exp < 0:
        errors.append("Employment experience cannot be negative.")
    if person_home_ownership not in VALID_HOME_OWNERSHIP:
        errors.append("Home ownership selection is invalid.")
    if not 300 <= credit_score <= 900:
        errors.append("Credit score must be between 300 and 900.")
    if credit_history_length < 0:
        errors.append("Credit history length cannot be negative.")
    if previous_loan_defaults_on_file not in (0, 1):
        errors.append("Previous loan defaults selection is invalid.")
    if loan_amnt <= 0:
        errors.append("Loan amount must be greater than zero.")
    if loan_int_rate <= 0:
        errors.append("Interest rate must be greater than zero.")
    if loan_intent not in VALID_LOAN_INTENTS:
        errors.append("Loan intent selection is invalid.")

    return errors


def build_result_data(application, prediction):
    risk_score, _ = get_risk_score_and_category(
        prediction.ml_decision,
        prediction.confidence_score
    )
    result, risk_level = get_prediction_result_and_risk(
        prediction.ml_decision,
        prediction.confidence_score
    )
    risk_score, _ = get_risk_score_and_category(
        prediction.ml_decision,
        prediction.confidence_score
    )
    reasons, suggestions = get_prediction_notes(
        result=result,
        risk_level=risk_level,
        confidence_score=prediction.confidence_score,
        credit_score=application.credit_score,
        previous_loan_defaults_on_file=application.previous_loan_defaults_on_file,
        loan_percent_income=application.loan_percent_income,
        person_emp_exp=application.person_emp_exp,
        person_income=application.person_income,
    )
    explanation_record = get_latest_decision_explanation(
        application_id=application.id,
        decision_result=result,
        language_code="en"
    )
    return {
        'result': result,
        'reasons': reasons,
        'suggestions': suggestions,
        'risk_level': risk_level,
        'risk_score': risk_score,
        'application_id': application.id,
        'applicant_name': application.customer_name,
        'prediction': prediction,
        'nlp_explanation': explanation_record_to_payload(explanation_record)
    }


def get_prediction_notes(result, risk_level, confidence_score, credit_score,
                         previous_loan_defaults_on_file, loan_percent_income,
                         person_emp_exp, person_income):
    reasons = [
        f"ML model predicted {result.lower()} with {confidence_score:.0%} confidence."
    ]
    suggestions = []

    if credit_score < 600:
        reasons.append("Credit score is below the preferred lending threshold.")
        suggestions.append("Improve credit score by maintaining timely repayments.")

    if previous_loan_defaults_on_file == 1:
        reasons.append("Previous loan default history increases repayment risk.")
        suggestions.append("Provide stronger financial documents and repayment evidence.")

    if loan_percent_income > 0.5:
        reasons.append("Loan amount is relatively high compared to annual income.")
        suggestions.append("Consider reducing the loan amount for better eligibility.")

    if person_emp_exp < 1 and person_income < 300000:
        reasons.append("Limited work experience may reduce repayment stability.")
        suggestions.append("Provide employment proof or add a stronger income profile.")

    if result == "Approved" and not suggestions:
        suggestions = [
            "Ensure all submitted documents match the declared values.",
            "Maintain repayment discipline for future credit strength."
        ]

    if result == "Rejected" and not suggestions:
        suggestions = [
            "Review your financial profile and apply again after improving key risk factors."
        ]

    if risk_level == "Medium":
        suggestions.append("Send this application for manager review before final approval.")

    return reasons, suggestions


def get_age_group_value(age):
    if age <= 25:
        return 0
    if age <= 35:
        return 1
    if age <= 45:
        return 2
    if age <= 60:
        return 3
    return 4


def get_income_group_value(income):
    if income <= 30000:
        return 0
    if income <= 60000:
        return 1
    if income <= 100000:
        return 2
    return 3


def get_credit_category_value(score):
    if score <= 588:
        return 0
    if score <= 670:
        return 1
    if score <= 740:
        return 2
    if score <= 800:
        return 3
    return 4


def build_model_input(
    person_age,
    person_gender,
    person_education,
    person_income,
    person_emp_exp,
    person_home_ownership,
    loan_amnt,
    loan_intent,
    loan_int_rate,
    loan_percent_income,
    credit_history_length,
    credit_score,
    previous_loan_defaults_on_file,
):
    feature_values = {
        'person_age': person_age,
        'person_gender': person_gender,
        'person_education': EDUCATION_ORDER[person_education],
        'person_income': person_income,
        'person_emp_exp': person_emp_exp,
        'loan_amnt': loan_amnt,
        'loan_int_rate': loan_int_rate,
        'loan_percent_income': loan_percent_income,
        'credit_history_length': credit_history_length,
        'credit_score': credit_score,
        'previous_loan_defaults_on_file': previous_loan_defaults_on_file,
        'age_group': get_age_group_value(person_age),
        'income_group': get_income_group_value(person_income),
        'credit_category': get_credit_category_value(credit_score),
        'person_home_ownership_OTHER': int(person_home_ownership == 'OTHER'),
        'person_home_ownership_OWN': int(person_home_ownership == 'OWN'),
        'person_home_ownership_RENT': int(person_home_ownership == 'RENT'),
        'loan_intent_EDUCATION': int(loan_intent == 'EDUCATION'),
        'loan_intent_HOMEIMPROVEMENT': int(loan_intent == 'HOMEIMPROVEMENT'),
        'loan_intent_MEDICAL': int(loan_intent == 'MEDICAL'),
        'loan_intent_PERSONAL': int(loan_intent == 'PERSONAL'),
        'loan_intent_VENTURE': int(loan_intent == 'VENTURE'),
    }

    return pd.DataFrame([[feature_values[column] for column in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)


@predict_bp.route('/application')
def application():
    guard = require_loan_assistant()
    if guard:
        return guard

    current_date = datetime.now().strftime("%d %b %Y")
    application_ref = f"LN-{datetime.now().strftime('%d%m%H%M')}"

    return render_template(
        'index.html',
        current_date=current_date,
        application_ref=application_ref
    )


@lru_cache(maxsize=1)
def load_ml_artifacts():
    return joblib.load(MODEL_PATH), joblib.load(SCALER_PATH)


def finalize_prediction(application):
    model, scaler = load_ml_artifacts()
    model_input = build_model_input(
        person_age=application.person_age,
        person_gender=application.person_gender,
        person_education=application.person_education,
        person_income=application.person_income,
        person_emp_exp=application.person_emp_exp,
        person_home_ownership=application.person_home_ownership,
        loan_amnt=application.loan_amnt,
        loan_intent=application.loan_intent,
        loan_int_rate=application.loan_int_rate,
        loan_percent_income=application.loan_percent_income,
        credit_history_length=application.credit_history_length,
        credit_score=application.credit_score,
        previous_loan_defaults_on_file=application.previous_loan_defaults_on_file,
    )
    scaled_input = scaler.transform(model_input)
    ml_decision = int(model.predict(scaled_input)[0])

    if hasattr(model, 'predict_proba'):
        probabilities = model.predict_proba(scaled_input)[0]
        classes = list(model.classes_)
        confidence_score = float(probabilities[classes.index(ml_decision)])
    else:
        confidence_score = 0.75

    result, risk_level = get_prediction_result_and_risk(ml_decision, confidence_score)
    risk_score, _ = get_risk_score_and_category(ml_decision, confidence_score)
    hybrid_decision = get_hybrid_decision_by_risk(risk_level)

    reasons, suggestions = get_prediction_notes(
        result=result,
        risk_level=risk_level,
        confidence_score=confidence_score,
        credit_score=application.credit_score,
        previous_loan_defaults_on_file=application.previous_loan_defaults_on_file,
        loan_percent_income=application.loan_percent_income,
        person_emp_exp=application.person_emp_exp,
        person_income=application.person_income,
    )

    email_needed = False
    final_decision = hybrid_decision
    decision_at_value = None
    flag = "clear" if final_decision in ("approved", "rejected") else "review"

    if final_decision in ("approved", "rejected"):
        decision_at_value = datetime.utcnow()
        email_needed = True

    new_prediction = get_latest_prediction(application.id)
    if new_prediction:
        new_prediction.ml_decision = ml_decision
        new_prediction.confidence_score = confidence_score
        new_prediction.risk_score = risk_score
        new_prediction.risk_category = risk_level
        new_prediction.flag = flag
        new_prediction.final_decision = final_decision
        new_prediction.decided_by = None
        new_prediction.decision_at = decision_at_value
        new_prediction.predicted_at = datetime.utcnow()
    else:
        new_prediction = Prediction(
            application_id=application.id,
            ml_decision=ml_decision,
            confidence_score=confidence_score,
            risk_score=risk_score,
            risk_category=risk_level,
            flag=flag,
            final_decision=final_decision,
            decided_by=None,
            decision_at=decision_at_value,
            email_sent=0,
            predicted_at=datetime.utcnow()
        )
        db.session.add(new_prediction)

    db.session.commit()

    if final_decision == "pending":
        set_application_status(
            application,
            "manual_review",
            queue="manual_review",
            actor_role="system",
            description="ML analysis completed. Medium-risk application routed to manual review queue."
        )
    elif final_decision == "approved":
        set_application_status(
            application,
            "approved",
            queue="fast_approval",
            actor_role="system",
            description="Low-risk application recommended and finalized for approval."
        )
    else:
        set_application_status(
            application,
            "rejected",
            queue="high_risk",
            actor_role="system",
            description="High-risk application recommended and finalized for rejection."
        )
    add_timeline_event(
        application.id,
        "ml_completed",
        "ML Analysis Completed",
        f"Risk category: {risk_level}.",
        actor_role="system"
    )
    db.session.commit()

    explanation_payload = generate_and_store_nlp_explanation(
        application=application,
        prediction=new_prediction,
        result=result,
        risk_level=risk_level,
        confidence_score=confidence_score,
        language_code="en",
        force=False
    )

    if email_needed and new_prediction.email_sent == 0:
        try:
            delivery = send_decision_notification_email(
                application=application,
                prediction=new_prediction,
                result=result,
                reasons=reasons,
                suggestions=suggestions,
                explanation_data=explanation_payload,
                force=False
            )
            if delivery.get("mode") in ("smtp", "outbox"):
                new_prediction.email_sent = 1
                db.session.commit()
        except Exception as exc:
            db.session.rollback()
            current_app.logger.exception("Failed to send automatic decision email: %s", exc)

    return {
        'result': result,
        'reasons': reasons,
        'suggestions': suggestions,
        'risk_level': risk_level,
        'risk_score': risk_score,
        'application_id': application.id,
        'applicant_name': application.customer_name,
        'prediction': new_prediction,
        'nlp_explanation': explanation_payload
    }


@predict_bp.route('/verify-email/<int:application_id>', methods=['GET', 'POST'])
def verify_email(application_id):
    guard = require_loan_assistant()
    if guard:
        return guard

    verification = EmailVerification.query.filter_by(application_id=application_id).first_or_404()
    application = verification.application
    error = None

    if request.method == 'POST':
        code = request.form.get('verification_code', '').strip()

        if verification.verified:
            return render_template(
                'submitted.html',
                application_ref=application.application_ref,
                application_id=application.id,
                customer_email=application.customer_email,
                message="Email is already verified. Application tracking is active."
            )

        if datetime.utcnow() > verification.expires_at:
            error = 'The verification code has expired. Please resubmit the application to receive a new code.'
        elif verification.attempts >= MAX_VERIFICATION_ATTEMPTS:
            error = 'Too many incorrect attempts. Please start a new application to receive a fresh code.'
        elif code != verification.verification_code:
            verification.attempts += 1
            db.session.commit()
            error = 'The code is incorrect. Please check your email and try again.'
        else:
            verification.verified = True
            set_application_status(
                application,
                "under_review",
                queue="underwriting",
                actor_role="customer",
                description="Customer email verified. Application moved to underwriting queue."
            )
            db.session.commit()
            return render_template(
                'submitted.html',
                application_ref=application.application_ref,
                application_id=application.id,
                customer_email=application.customer_email,
                message="Email verified successfully. Application tracking is now active."
            )

    return render_email_verification_screen(application, verification, error=error)


@predict_bp.route('/result/<int:application_id>')
def prediction_result(application_id):
    guard = require_loan_assistant()
    if guard:
        return guard

    application = Application.query.get_or_404(application_id)
    verification = EmailVerification.query.filter_by(application_id=application_id).first()

    if verification and not verification.verified:
        return redirect(url_for('predict.verify_email', application_id=application_id))

    prediction = get_latest_prediction(application_id)
    if prediction:
        return render_prediction_result(build_result_data(application, prediction))

    result_data = finalize_prediction(application)
    return render_prediction_result(result_data)


@predict_bp.route('/api/explanation/<int:application_id>', methods=['GET'])
def explanation_api(application_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    application = Application.query.get_or_404(application_id)
    prediction = get_latest_prediction(application_id)
    if not prediction:
        return jsonify({"success": False, "message": "Prediction not ready yet."}), 404

    result, risk_level = get_prediction_result_and_risk(
        prediction.ml_decision,
        prediction.confidence_score
    )
    force_refresh = str(request.args.get("refresh", "0")).lower() in ("1", "true", "yes")
    language_code = (request.args.get("lang", "en") or "en").strip().lower()

    try:
        payload = generate_and_store_nlp_explanation(
            application=application,
            prediction=prediction,
            result=result,
            risk_level=risk_level,
            confidence_score=prediction.confidence_score,
            language_code=language_code,
            force=force_refresh
        )
    except Exception as exc:
        current_app.logger.exception("Failed to generate NLP explanation: %s", exc)
        return jsonify({"success": False, "message": f"Explanation generation failed: {exc}"}), 500

    return jsonify({
        "success": True,
        "application_id": application_id,
        "result": result,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "confidence_score": prediction.confidence_score,
        "explanation": payload
    })


@predict_bp.route('/api/verify-email/<int:application_id>', methods=['POST'])
def verify_email_api(application_id):
    if 'user_id' not in session or session.get('role') != 'loan_assistant':
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    verification = EmailVerification.query.filter_by(application_id=application_id).first_or_404()
    application = verification.application
    payload = request.get_json(silent=True) or {}
    code = str(payload.get('verification_code', '')).strip()

    if verification.verified:
        prediction = get_latest_prediction(application.id)
        return jsonify({
            "success": True,
            "message": "Email already verified.",
            "redirect_url": get_submission_redirect_url(application.id)
        })

    if datetime.utcnow() > verification.expires_at:
        return jsonify({
            "success": False,
            "message": "The verification code has expired. Please resend OTP."
        }), 400

    if verification.attempts >= MAX_VERIFICATION_ATTEMPTS:
        return jsonify({
            "success": False,
            "message": "Too many incorrect attempts. Please start a new application."
        }), 429

    if code != verification.verification_code:
        verification.attempts += 1
        db.session.commit()
        remaining_attempts = max(MAX_VERIFICATION_ATTEMPTS - verification.attempts, 0)
        return jsonify({
            "success": False,
            "message": "Invalid OTP. Please check the code and try again.",
            "remaining_attempts": remaining_attempts
        }), 400

    verification.verified = True
    set_application_status(
        application,
        "under_review",
        queue="underwriting",
        actor_role="customer",
        description="Customer email verified. Application moved to underwriting queue."
    )
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "OTP verified successfully. Application tracking is active.",
        "redirect_url": get_submission_redirect_url(application.id)
    })


@predict_bp.route('/submitted/<int:application_id>')
def submission_status(application_id):
    guard = require_loan_assistant()
    if guard:
        return guard

    application = Application.query.get_or_404(application_id)
    verification = EmailVerification.query.filter_by(application_id=application_id).first()

    if verification and not verification.verified:
        return render_email_verification_screen(
            application,
            verification,
            delivery_notice="We have sent a 6-digit verification code to the customer's email address."
        )

    return render_template(
        'submitted.html',
        application_ref=application.application_ref,
        application_id=application.id,
        customer_email=application.customer_email,
        message="Email verified successfully. Application tracking is now active."
    )


@predict_bp.route('/submitted/<int:application_id>/track')
def track_submitted_application(application_id):
    guard = require_loan_assistant()
    if guard:
        return guard

    application = Application.query.get_or_404(application_id)
    verification = EmailVerification.query.filter_by(application_id=application_id).first()

    if verification and not verification.verified:
        return redirect(url_for('predict.verify_email', application_id=application.id))

    session['tracking_verified_application_id'] = application.id
    session.pop('tracking_application_id', None)
    session.pop('tracking_otp', None)
    session.pop('tracking_otp_expires_at', None)
    return redirect(url_for('tracking.tracking_status'))


@predict_bp.route('/api/verify-email/<int:application_id>/resend', methods=['POST'])
def resend_verification_email_api(application_id):
    if 'user_id' not in session or session.get('role') != 'loan_assistant':
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    verification = EmailVerification.query.filter_by(application_id=application_id).first_or_404()
    application = verification.application

    if verification.verified:
        return jsonify({
            "success": False,
            "message": "Email already verified for this application."
        }), 400

    verification.verification_code = generate_verification_code()
    verification.expires_at = datetime.utcnow() + timedelta(minutes=15)
    verification.attempts = 0

    try:
        delivery = send_verification_code_email(
            application.customer_name,
            application.customer_email,
            verification.verification_code
        )
        db.session.commit()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Failed to resend verification email via API: %s", exc)
        return jsonify({"success": False, "message": f"Could not resend OTP: {exc}"}), 500

    return jsonify({
        "success": True,
        "message": get_email_delivery_notice(delivery) or "A new OTP has been sent to your email.",
        "cooldown_seconds": 45,
        "dev_verification_code": get_dev_verification_code(verification)
    })


@predict_bp.route('/verify-email/<int:application_id>/resend', methods=['POST'])
def resend_verification_email(application_id):
    guard = require_loan_assistant()
    if guard:
        return guard

    verification = EmailVerification.query.filter_by(application_id=application_id).first_or_404()
    application = verification.application

    if verification.verified:
        flash("Email is already verified for this application.", "info")
        return redirect(url_for('predict.verify_email', application_id=application_id))

    verification.verification_code = generate_verification_code()
    verification.expires_at = datetime.utcnow() + timedelta(minutes=15)
    verification.attempts = 0

    try:
        delivery = send_verification_code_email(
            application.customer_name,
            application.customer_email,
            verification.verification_code
        )
        db.session.commit()
        flash(get_email_delivery_notice(delivery) or "Verification email sent again.", "success")
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Failed to resend verification email: %s", exc)
        flash(f"Could not resend verification email: {exc}", "error")

    return redirect(url_for('predict.verify_email', application_id=application_id))


@predict_bp.route('/predict', methods=['POST'])
def predict():
    guard = require_loan_assistant()
    if guard:
        return guard

    try:
        customer_name = request.form.get('customer_name', '').strip()
        customer_email = request.form.get('customer_email', '').strip().lower()

        person_age = int(request.form.get('person_age', 0) or 0)
        person_gender = int(request.form.get('person_gender', 0) or 0)
        person_education = request.form.get('person_education', '').strip()

        person_income = float(request.form.get('person_income', 0) or 0)
        person_emp_exp = int(request.form.get('person_emp_exp', 0) or 0)
        person_home_ownership = request.form.get('person_home_ownership', '').strip()

        credit_score = int(request.form.get('credit_score', 0) or 0)
        credit_history_length = float(request.form.get('credit_history_length', 0) or 0)
        previous_loan_defaults_on_file = int(request.form.get('previous_loan_defaults_on_file', 0) or 0)

        loan_amnt = float(request.form.get('loan_amnt', 0) or 0)
        loan_int_rate = float(request.form.get('loan_int_rate', 0) or 0)
        loan_intent = request.form.get('loan_intent', '').strip()

        loan_percent_income = round((loan_amnt / person_income), 4) if person_income > 0 else 0

    except ValueError:
        return render_template(
            'result.html',
            result="Rejected",
            reasons=["Invalid input values. Please enter valid numeric data."],
            suggestions=["Check all numeric fields and submit again."],
            risk_level="High",
            applicant_name="Applicant",
            application_id=None
        )

    validation_errors = validate_application_values(
        customer_name=customer_name,
        customer_email=customer_email,
        person_age=person_age,
        person_gender=person_gender,
        person_education=person_education,
        person_income=person_income,
        person_emp_exp=person_emp_exp,
        person_home_ownership=person_home_ownership,
        credit_score=credit_score,
        credit_history_length=credit_history_length,
        previous_loan_defaults_on_file=previous_loan_defaults_on_file,
        loan_amnt=loan_amnt,
        loan_int_rate=loan_int_rate,
        loan_intent=loan_intent,
    )
    if validation_errors:
        return render_template(
            'result.html',
            result="Rejected",
            reasons=validation_errors,
            suggestions=["Return to the application form, correct the invalid details, and submit again."],
            risk_level="High",
            applicant_name=customer_name if customer_name else "Applicant",
            application_id=None
        )

    try:
        new_application = Application(
            application_ref=generate_application_ref(),
            loan_assistant_id=session.get('user_id'),
            customer_name=customer_name,
            customer_email=customer_email,
            person_age=person_age,
            person_gender=person_gender,
            person_education=person_education,
            person_income=person_income,
            person_emp_exp=person_emp_exp,
            person_home_ownership=person_home_ownership,
            loan_amnt=loan_amnt,
            loan_intent=loan_intent,
            loan_int_rate=loan_int_rate,
            loan_percent_income=loan_percent_income,
            credit_history_length=credit_history_length,
            credit_score=credit_score,
            previous_loan_defaults_on_file=previous_loan_defaults_on_file,
            submitted_at=datetime.utcnow(),
            tracking_status="submitted",
            review_queue="email_verification",
            status_updated_at=datetime.utcnow()
        )
        db.session.add(new_application)
        db.session.flush()
        add_timeline_event(
            new_application.id,
            "submitted",
            "Application Submitted",
            "Loan application captured by loan assistant.",
            actor_role="loan_assistant"
        )

        code = generate_verification_code()
        verification = EmailVerification(
            application_id=new_application.id,
            verification_code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            verified=False,
            attempts=0
        )
        db.session.add(verification)

        try:
            delivery = send_verification_code_email(customer_name, customer_email, code)
            send_application_status_email(
                customer_name=customer_name,
                customer_email=customer_email,
                application_ref=new_application.application_ref,
                status_label="Submitted",
                message="Your loan application has been submitted for credit underwriting review. Please complete email OTP verification to activate tracking."
            )
        except Exception as e:
            db.session.rollback()
            return render_template(
                'result.html',
                result="Rejected",
                reasons=["Failed to send verification email.", str(e)],
                suggestions=["Verify SMTP settings and email credentials.", "Try again later."],
                risk_level="High",
                applicant_name=customer_name if customer_name else "Applicant",
                application_id=None
            )

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return render_template(
            'result.html',
            result="Rejected",
            reasons=[f"Database error while saving application: {str(e)}"],
            suggestions=["Check DB schema and field compatibility."],
            risk_level="High",
            applicant_name=customer_name if customer_name else "Applicant",
            application_id=None
        )

    return render_email_verification_screen(
        new_application,
        verification,
        delivery_notice=get_email_delivery_notice(delivery)
    )
