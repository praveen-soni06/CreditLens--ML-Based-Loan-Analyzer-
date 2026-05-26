from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path

from flask import Blueprint, render_template, request, session, redirect, url_for
import joblib
import pandas as pd

from app.database.db import db, Application, Prediction, EmailVerification
from app.utils.email_utils import (
    generate_verification_code,
    send_verification_code_email,
    send_decision_notification_email,
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


def require_loan_assistant():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if session.get('role') != 'loan_assistant':
        return redirect(url_for('dashboard.dashboard'))

    return None


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

    result = "Approved" if ml_decision == 1 else "Rejected"
    if result == "Rejected":
        risk_level = "High"
    elif confidence_score >= 0.75:
        risk_level = "Low"
    else:
        risk_level = "Medium"

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
    final_decision = "pending"
    decision_at_value = None
    flag = "review"

    if risk_level != "Medium":
        flag = "clear"
        final_decision = result.lower()
        decision_at_value = datetime.utcnow()
        email_needed = True

    new_prediction = Prediction(
        application_id=application.id,
        ml_decision=ml_decision,
        confidence_score=confidence_score,
        flag=flag,
        final_decision=final_decision,
        decided_by=None,
        decision_at=decision_at_value,
        email_sent=0,
        predicted_at=datetime.utcnow()
    )

    db.session.add(new_prediction)
    db.session.commit()

    if email_needed:
        send_decision_notification_email(
            customer_name=application.customer_name,
            customer_email=application.customer_email,
            result=result,
            reasons=reasons,
            suggestions=suggestions
        )
        new_prediction.email_sent = 1
        db.session.commit()

    return {
        'result': result,
        'reasons': reasons,
        'suggestions': suggestions,
        'risk_level': risk_level,
        'application_id': application.id,
        'applicant_name': application.customer_name,
        'prediction': new_prediction
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
            return redirect(url_for('predict.application'))

        if datetime.utcnow() > verification.expires_at:
            error = 'The verification code has expired. Please resubmit the application to receive a new code.'
        elif code != verification.verification_code:
            verification.attempts += 1
            db.session.commit()
            error = 'The code is incorrect. Please check your email and try again.'
        else:
            verification.verified = True
            db.session.commit()
            result_data = finalize_prediction(application)
            return render_template(
                'result.html',
                result=result_data['result'],
                reasons=result_data['reasons'],
                suggestions=result_data['suggestions'],
                risk_level=result_data['risk_level'],
                applicant_name=result_data['applicant_name'],
                application_id=result_data['application_id']
            )

    return render_template(
        'verify_email.html',
        application_id=application_id,
        customer_email=application.customer_email,
        customer_name=application.customer_name,
        error=error
    )


@predict_bp.route('/predict', methods=['POST'])
def predict():
    guard = require_loan_assistant()
    if guard:
        return guard

    try:
        customer_name = request.form.get('customer_name', '').strip()
        customer_email = request.form.get('customer_email', '').strip()

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

    try:
        new_application = Application(
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
            submitted_at=datetime.utcnow()
        )
        db.session.add(new_application)
        db.session.commit()

        code = generate_verification_code()
        verification = EmailVerification(
            application_id=new_application.id,
            verification_code=code,
            expires_at=datetime.utcnow() + timedelta(minutes=15),
            verified=False,
            attempts=0
        )
        db.session.add(verification)
        db.session.commit()

        try:
            send_verification_code_email(customer_name, customer_email, code)
        except Exception as e:
            return render_template(
                'result.html',
                result="Rejected",
                reasons=["Failed to send verification email.", str(e)],
                suggestions=["Verify SMTP settings and email credentials.", "Try again later."],
                risk_level="High",
                applicant_name=customer_name if customer_name else "Applicant",
                application_id=new_application.id
            )

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

    return render_template(
        'verify_email.html',
        application_id=new_application.id,
        customer_email=customer_email,
        customer_name=customer_name,
        error=None
    )
