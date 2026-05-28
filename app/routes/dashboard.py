from datetime import datetime

from flask import Blueprint, current_app, flash, render_template, redirect, request, session, url_for

from app.database.db import Application, db
from app.routes.predict import (
    finalize_prediction,
    generate_and_store_nlp_explanation,
    get_hybrid_decision_by_risk,
    get_latest_prediction,
    get_prediction_notes,
    get_prediction_result_and_risk,
)
from app.utils.lifecycle import set_application_status
from app.utils.email_utils import (
    get_email_delivery_mode,
    get_email_delivery_notice,
    send_decision_notification_email,
)

dashboard_bp = Blueprint('dashboard', __name__)


def require_credit_manager():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if session.get('role') != 'credit_manager':
        return redirect(url_for('predict.application'))

    return None


def get_risk_level(prediction):
    if not prediction:
        return "Medium"

    return get_prediction_result_and_risk(
        prediction.ml_decision,
        prediction.confidence_score
    )[1]


def get_final_status(prediction):
    if not prediction:
        return "Pending Review"

    if prediction.final_decision == "approved":
        return "Approved"

    if prediction.final_decision == "rejected":
        return "Rejected"

    if prediction.final_decision == "hold":
        return "On Hold"

    return "Pending Review"


def clamp_percentage(value):
    return max(0, min(100, round(value, 1)))


def average(values):
    clean_values = [float(value) for value in values if value is not None]
    if not clean_values:
        return 0
    return sum(clean_values) / len(clean_values)


def percentile_rank(values, current_value):
    clean_values = sorted(float(value) for value in values if value is not None)
    if not clean_values or current_value is None:
        return 0
    below_or_equal = sum(1 for value in clean_values if value <= float(current_value))
    return clamp_percentage((below_or_equal / len(clean_values)) * 100)


@dashboard_bp.route('/dashboard')
def dashboard():
    guard = require_credit_manager()
    if guard:
        return guard

    applications = Application.query.order_by(Application.id.desc()).all()
    per_page = 10
    try:
        page = max(1, int(request.args.get("page", 1)))
    except ValueError:
        page = 1

    approved_count = 0
    rejected_count = 0
    pending_count = 0
    high_risk_count = 0
    low_risk_count = 0
    medium_risk_count = 0
    manual_queue_count = 0
    email_sent_count = 0
    email_waiting_count = 0
    email_not_sent_count = 0
    queue_counts = {}

    for application in applications:
        prediction = get_latest_prediction(application.id)

        status = get_final_status(prediction)
        risk = get_risk_level(prediction)
        if prediction:
            hybrid_recommendation = get_hybrid_decision_by_risk(risk)
            if hybrid_recommendation == "pending":
                ml_recommendation = "Pending Review"
            else:
                ml_recommendation = hybrid_recommendation.capitalize()
        else:
            ml_recommendation = "Pending"

        if not prediction:
            email_status = "OTP Pending"
        elif prediction.email_sent:
            email_status = "Sent"
        elif prediction.final_decision == "pending":
            email_status = "Waiting Decision"
        else:
            email_status = "Not Sent"

        if email_status == "Sent":
            email_sent_count += 1
        elif email_status == "Waiting Decision":
            email_waiting_count += 1
        else:
            email_not_sent_count += 1

        queue_label = (application.review_queue or "underwriting").replace("_", " ").title()
        queue_counts[queue_label] = queue_counts.get(queue_label, 0) + 1

        if status == "Approved":
            approved_count += 1
        elif status == "Rejected":
            rejected_count += 1
        else:
            pending_count += 1

        if risk == "High":
            high_risk_count += 1
        elif risk == "Low":
            low_risk_count += 1
        else:
            medium_risk_count += 1

        if application.review_queue == "manual_review" or status == "Pending Review":
            manual_queue_count += 1

    total_applications = len(applications)
    total_pages = max(1, (total_applications + per_page - 1) // per_page)
    page = min(page, total_pages)
    start_index = (page - 1) * per_page
    page_applications = applications[start_index:start_index + per_page]
    page_window_start = max(1, page - 2)
    page_window_end = min(total_pages, page + 2)

    recent_applications = []
    for application in page_applications:
        prediction = get_latest_prediction(application.id)
        status = get_final_status(prediction)
        risk = get_risk_level(prediction)
        if prediction:
            hybrid_recommendation = get_hybrid_decision_by_risk(risk)
            if hybrid_recommendation == "pending":
                ml_recommendation = "Pending Review"
            else:
                ml_recommendation = hybrid_recommendation.capitalize()
        else:
            ml_recommendation = "Pending"

        if not prediction:
            email_status = "OTP Pending"
        elif prediction.email_sent:
            email_status = "Sent"
        elif prediction.final_decision == "pending":
            email_status = "Waiting Decision"
        else:
            email_status = "Not Sent"

        recent_applications.append({
            "id": application.id,
            "ref": application.application_ref,
            "name": application.customer_name,
            "status": status,
            "risk": risk,
            "ml_recommendation": ml_recommendation,
            "email_status": email_status,
            "tracking_status": application.tracking_status,
            "queue": application.review_queue
        })

    stats = {
        "total": total_applications,
        "approved": approved_count,
        "rejected": rejected_count,
        "pending": pending_count,
        "high_risk": high_risk_count,
        "low_risk": low_risk_count,
        "medium_risk": medium_risk_count,
        "manual_queue": manual_queue_count
    }

    def rate(value):
        return round((value / total_applications) * 100) if total_applications else 0

    total_analytics = {
        "rate_cards": [
            {
                "label": "Approval Rate",
                "value": f"{rate(approved_count)}%",
                "note": f"{approved_count} approved",
                "percent": rate(approved_count),
                "tone": "success",
            },
            {
                "label": "Pending Workload",
                "value": f"{rate(pending_count)}%",
                "note": f"{pending_count} in progress",
                "percent": rate(pending_count),
                "tone": "warning",
            },
            {
                "label": "High Risk Exposure",
                "value": f"{rate(high_risk_count)}%",
                "note": f"{high_risk_count} high risk",
                "percent": rate(high_risk_count),
                "tone": "danger",
            },
            {
                "label": "Manual Queue",
                "value": f"{rate(manual_queue_count)}%",
                "note": f"{manual_queue_count} need review",
                "percent": rate(manual_queue_count),
                "tone": "warning",
            },
        ],
        "status_chart": {
            "labels": ["Approved", "Rejected", "Pending"],
            "values": [approved_count, rejected_count, pending_count],
        },
        "risk_chart": {
            "labels": ["Low", "Medium", "High"],
            "values": [low_risk_count, medium_risk_count, high_risk_count],
        },
        "queue_chart": {
            "labels": list(queue_counts.keys()),
            "values": list(queue_counts.values()),
        },
        "email_chart": {
            "labels": ["Sent", "Waiting", "Not Sent"],
            "values": [email_sent_count, email_waiting_count, email_not_sent_count],
        },
    }

    rejection_reasons = [
        "Low income compared to requested loan amount",
        "Weak or limited credit history",
        "Low credit score below preferred threshold",
        "Previous loan default indicators"
    ]

    return render_template(
        'dashboard.html',
        stats=stats,
        rejection_reasons=rejection_reasons,
        recent_applications=recent_applications,
        total_analytics=total_analytics,
        pagination={
            "page": page,
            "per_page": per_page,
            "total": total_applications,
            "total_pages": total_pages,
            "start": start_index + 1 if total_applications else 0,
            "end": min(start_index + per_page, total_applications),
            "has_prev": page > 1,
            "has_next": page < total_pages,
            "prev_page": page - 1,
            "next_page": page + 1,
            "pages": list(range(page_window_start, page_window_end + 1)),
        }
    )


@dashboard_bp.route('/review')
def review_default():
    guard = require_credit_manager()
    if guard:
        return guard

    latest_application = Application.query.order_by(Application.id.desc()).first()

    if latest_application:
        return redirect(url_for('dashboard.review', application_id=latest_application.id))

    return redirect(url_for('predict.application'))


@dashboard_bp.route('/review/<int:application_id>')
def review(application_id):
    guard = require_credit_manager()
    if guard:
        return guard

    application = Application.query.get_or_404(application_id)
    prediction = get_latest_prediction(application_id)

    ai_recommendation = "Pending"
    risk_level = "Medium"
    confidence = None

    if prediction:
        hybrid_recommendation = get_hybrid_decision_by_risk(get_risk_level(prediction))
        if hybrid_recommendation == "pending":
            ai_recommendation = "Pending Review"
        else:
            ai_recommendation = hybrid_recommendation.capitalize()

        if prediction.confidence_score is not None:
            confidence = round(prediction.confidence_score * 100)

        risk_level = get_risk_level(prediction)

    decision_factors = []

    if application.person_income > 0 and application.loan_amnt <= (application.person_income * 0.5):
        decision_factors.append("Income level supports the requested loan amount.")
    else:
        decision_factors.append("Loan amount is relatively high compared to declared income.")

    if application.credit_score >= 700:
        decision_factors.append("Credit score is strong and within a preferred approval range.")
    elif application.credit_score >= 600:
        decision_factors.append("Credit score is acceptable but may require manual review.")
    else:
        decision_factors.append("Credit score is below the preferred approval threshold.")

    if application.previous_loan_defaults_on_file == 0:
        decision_factors.append("No previous loan defaults were found on file.")
    else:
        decision_factors.append("Previous loan default history increases lending risk.")

    portfolio_applications = Application.query.all()
    income_values = [item.person_income for item in portfolio_applications]
    credit_values = [item.credit_score for item in portfolio_applications]
    burden_values = [(item.loan_percent_income or 0) * 100 for item in portfolio_applications]
    interest_values = [item.loan_int_rate for item in portfolio_applications]
    employment_values = [item.person_emp_exp for item in portfolio_applications]

    income = float(application.person_income or 0)
    loan = float(application.loan_amnt or 0)
    loan_to_income_percent = (loan / income * 100) if income > 0 else 0
    debt_burden_percent = float(application.loan_percent_income or 0) * 100
    if debt_burden_percent <= 0:
        debt_burden_percent = loan_to_income_percent
    interest_rate = float(application.loan_int_rate or 0)
    credit_score_percent = clamp_percentage((application.credit_score - 300) / 600 * 100)
    employment_percent = clamp_percentage((application.person_emp_exp or 0) / 10 * 100)
    default_risk_percent = 12 if application.previous_loan_defaults_on_file == 0 else 88

    if prediction and prediction.risk_score is not None:
        raw_model_risk = float(prediction.risk_score)
        model_risk_percent = raw_model_risk * 100 if raw_model_risk <= 1 else raw_model_risk
    else:
        model_risk_percent = {"Low": 24, "Medium": 58, "High": 86}.get(risk_level, 58)
    model_risk_percent = clamp_percentage(model_risk_percent)

    if application.credit_score >= 750:
        credit_band = "Excellent"
        credit_tone = "success"
    elif application.credit_score >= 650:
        credit_band = "Stable"
        credit_tone = "warning"
    else:
        credit_band = "Weak"
        credit_tone = "danger"

    if debt_burden_percent <= 35:
        loan_pressure = "Healthy"
        loan_tone = "success"
    elif debt_burden_percent <= 60:
        loan_pressure = "Watch"
        loan_tone = "warning"
    else:
        loan_pressure = "High"
        loan_tone = "danger"

    interest_tone = "success" if interest_rate <= 10 else "warning" if interest_rate <= 18 else "danger"
    model_risk_tone = "success" if model_risk_percent <= 35 else "warning" if model_risk_percent <= 65 else "danger"
    income_percentile = percentile_rank(income_values, income)
    credit_percentile = percentile_rank(credit_values, application.credit_score)

    portfolio_average_burden = average(burden_values)
    portfolio_average_interest = average(interest_values)
    portfolio_average_credit = average(credit_values)
    portfolio_average_employment = average(employment_values)

    hidden_metrics = [
        {
            "label": "Debt Burden",
            "value": f"{debt_burden_percent:.1f}%",
            "note": f"Portfolio avg {portfolio_average_burden:.1f}%",
            "percent": clamp_percentage(debt_burden_percent / 1.2),
            "tone": loan_tone,
        },
        {
            "label": "Interest Load",
            "value": f"{interest_rate:.1f}%",
            "note": f"Portfolio avg {portfolio_average_interest:.1f}%",
            "percent": clamp_percentage(interest_rate / 0.35),
            "tone": interest_tone,
        },
        {
            "label": "Income Percentile",
            "value": f"{income_percentile:.0f}th",
            "note": "Against stored applications",
            "percent": income_percentile,
            "tone": "success" if income_percentile >= 60 else "warning" if income_percentile >= 35 else "danger",
        },
        {
            "label": "Credit Percentile",
            "value": f"{credit_percentile:.0f}th",
            "note": credit_band,
            "percent": credit_percentile,
            "tone": credit_tone,
        },
        {
            "label": "Model Risk Index",
            "value": f"{model_risk_percent:.0f}%",
            "note": "Hidden model signal",
            "percent": model_risk_percent,
            "tone": model_risk_tone,
        },
    ]

    benchmark_rows = [
        {
            "label": "Debt Burden",
            "applicant": f"{debt_burden_percent:.1f}%",
            "portfolio": f"{portfolio_average_burden:.1f}%",
            "applicant_percent": clamp_percentage(debt_burden_percent / 1.2),
            "portfolio_percent": clamp_percentage(portfolio_average_burden / 1.2),
            "tone": loan_tone,
        },
        {
            "label": "Interest Rate",
            "applicant": f"{interest_rate:.1f}%",
            "portfolio": f"{portfolio_average_interest:.1f}%",
            "applicant_percent": clamp_percentage(interest_rate / 0.35),
            "portfolio_percent": clamp_percentage(portfolio_average_interest / 0.35),
            "tone": interest_tone,
        },
        {
            "label": "Credit Score",
            "applicant": str(application.credit_score),
            "portfolio": f"{portfolio_average_credit:.0f}",
            "applicant_percent": credit_score_percent,
            "portfolio_percent": clamp_percentage((portfolio_average_credit - 300) / 600 * 100),
            "tone": credit_tone,
        },
    ]

    benchmark_chart = {
        "labels": ["Debt", "Interest", "Credit", "Income", "Emp Exp"],
        "applicant": [
            clamp_percentage(debt_burden_percent / 1.2),
            clamp_percentage(interest_rate / 0.35),
            credit_score_percent,
            income_percentile,
            employment_percent,
        ],
        "portfolio": [
            clamp_percentage(portfolio_average_burden / 1.2),
            clamp_percentage(portfolio_average_interest / 0.35),
            clamp_percentage((portfolio_average_credit - 300) / 600 * 100),
            50,
            clamp_percentage(portfolio_average_employment / 10 * 100),
        ],
    }

    risk_composition_chart = {
        "labels": ["Debt burden", "Interest load", "Default history", "Model risk"],
        "values": [
            clamp_percentage(debt_burden_percent / 1.2),
            clamp_percentage(interest_rate / 0.35),
            default_risk_percent,
            model_risk_percent,
        ],
    }

    risk_factor_bars = [
        {
            "label": "Repayment Pressure",
            "value": f"{debt_burden_percent:.1f}%",
            "percent": clamp_percentage(debt_burden_percent / 1.2),
            "tone": loan_tone,
        },
        {
            "label": "Interest Exposure",
            "value": f"{interest_rate:.1f}%",
            "percent": clamp_percentage(interest_rate / 0.35),
            "tone": interest_tone,
        },
        {
            "label": "Default History",
            "value": "Clear" if application.previous_loan_defaults_on_file == 0 else "Found",
            "percent": default_risk_percent,
            "tone": "success" if application.previous_loan_defaults_on_file == 0 else "danger",
        },
        {
            "label": "Model Risk",
            "value": f"{model_risk_percent:.0f}%",
            "percent": model_risk_percent,
            "tone": model_risk_tone,
        },
    ]

    return render_template(
        'review.html',
        applicant_name=application.customer_name,
        application_ref=application.application_ref,
        applicant_email=application.customer_email,
        applicant_income=application.person_income,
        loan_amount=application.loan_amnt,
        loan_term="Calculated / Not Stored",
        credit_score=application.credit_score,
        credit_history_length=application.credit_history_length,
        loan_intent=application.loan_intent,
        home_ownership=application.person_home_ownership,
        education=application.person_education,
        ai_recommendation=ai_recommendation,
        risk_level=risk_level,
        confidence=confidence,
        decision_factors=decision_factors,
        timeline_events=application.timeline_events,
        tracking_status=application.tracking_status,
        review_queue=application.review_queue,
        admin_remarks=application.admin_remarks,
        application_id=application.id,
        final_decision=prediction.final_decision if prediction else "pending",
        has_prediction=bool(prediction),
        email_sent=bool(prediction and prediction.email_sent),
        email_delivery_mode=get_email_delivery_mode(),
        decided_by=prediction.decided_by if prediction else None,
        decision_at=prediction.decision_at if prediction else None,
        hidden_metrics=hidden_metrics,
        benchmark_rows=benchmark_rows,
        risk_factor_bars=risk_factor_bars,
        benchmark_chart=benchmark_chart,
        risk_composition_chart=risk_composition_chart,
        loan_to_income_percent=loan_to_income_percent,
        credit_score_percent=credit_score_percent,
        model_risk_percent=model_risk_percent
    )


@dashboard_bp.route('/review/<int:application_id>/run-ml', methods=['POST'])
def run_ml_analysis(application_id):
    guard = require_credit_manager()
    if guard:
        return guard

    application = Application.query.get_or_404(application_id)
    if not application.verification or not application.verification.verified:
        flash("Customer email must be verified before ML analysis can run.", "info")
        return redirect(url_for('dashboard.review', application_id=application_id))

    try:
        set_application_status(
            application,
            "under_review",
            queue="ml_analysis",
            actor_role="credit_manager",
            description="Credit manager started ML underwriting analysis."
        )
        db.session.commit()
        finalize_prediction(application)
        flash("ML analysis completed and risk category updated.", "success")
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Failed to run ML analysis: %s", exc)
        flash(f"ML analysis failed: {exc}", "error")

    return redirect(url_for('dashboard.review', application_id=application_id))


@dashboard_bp.route('/review/<int:application_id>/decision', methods=['POST'])
def decide_application(application_id):
    guard = require_credit_manager()
    if guard:
        return guard

    prediction = get_latest_prediction(application_id)
    if not prediction:
        return redirect(url_for('dashboard.review', application_id=application_id))

    decision = request.form.get('decision', '').strip().lower()

    if decision not in ("approved", "rejected", "hold"):
        return redirect(url_for('dashboard.review', application_id=application_id))

    try:
        application = Application.query.get(application_id)
        prediction.final_decision = decision
        prediction.decided_by = session.get('user_id')
        prediction.decision_at = datetime.utcnow()
        if application:
            application.admin_remarks = request.form.get('admin_remarks', '').strip()
            if decision == "hold":
                set_application_status(
                    application,
                    "hold",
                    queue="manual_review",
                    actor_role="credit_manager",
                    description=application.admin_remarks or "Application placed on hold for additional review."
                )
            elif decision == "approved":
                set_application_status(
                    application,
                    "approved",
                    queue="approved",
                    actor_role="credit_manager",
                    description=application.admin_remarks or "Application approved by credit manager."
                )
            else:
                set_application_status(
                    application,
                    "rejected",
                    queue="rejected",
                    actor_role="credit_manager",
                    description=application.admin_remarks or "Application rejected by credit manager."
                )
        db.session.commit()

        if decision == "hold":
            flash("Application placed on hold with admin remarks.", "success")
            return redirect(url_for('dashboard.review', application_id=application_id))

        if prediction.email_sent == 0:
            if application:
                reasons, suggestions = get_prediction_notes(
                    result=decision.capitalize(),
                    risk_level=get_risk_level(prediction),
                    confidence_score=prediction.confidence_score or 0.75,
                    credit_score=application.credit_score,
                    previous_loan_defaults_on_file=application.previous_loan_defaults_on_file,
                    loan_percent_income=application.loan_percent_income,
                    person_emp_exp=application.person_emp_exp,
                    person_income=application.person_income,
                )
                explanation_payload = generate_and_store_nlp_explanation(
                    application=application,
                    prediction=prediction,
                    result=decision.capitalize(),
                    risk_level=get_risk_level(prediction),
                    confidence_score=prediction.confidence_score or 0.75,
                    language_code="en",
                    force=True
                )
                delivery = send_decision_notification_email(
                    application=application,
                    prediction=prediction,
                    result=decision.capitalize(),
                    reasons=reasons,
                    suggestions=suggestions,
                    explanation_data=explanation_payload,
                    force=False
                )
                if delivery.get("mode") in ("smtp", "outbox"):
                    prediction.email_sent = 1
                    db.session.commit()
                flash(get_email_delivery_notice(delivery) or "Decision saved and customer email notification sent.", "success")
        elif prediction.email_sent:
            flash("Decision saved. Customer email had already been sent.", "info")
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Failed to save manager decision or send decision email: %s", exc)
        flash(f"Decision saved, but email notification could not be sent: {exc}", "error")

    return redirect(url_for('dashboard.review', application_id=application_id))


@dashboard_bp.route('/review/<int:application_id>/email', methods=['POST'])
def resend_decision_email(application_id):
    guard = require_credit_manager()
    if guard:
        return guard

    prediction = get_latest_prediction(application_id)
    application = Application.query.get_or_404(application_id)

    if not prediction:
        flash("ML prediction is not ready yet, so decision email cannot be sent.", "info")
        return redirect(url_for('dashboard.review', application_id=application_id))

    if prediction.final_decision == "pending":
        flash("Choose a final decision before sending the customer notification.", "info")
        return redirect(url_for('dashboard.review', application_id=application_id))

    try:
        reasons, suggestions = get_prediction_notes(
            result=prediction.final_decision.capitalize(),
            risk_level=get_risk_level(prediction),
            confidence_score=prediction.confidence_score or 0.75,
            credit_score=application.credit_score,
            previous_loan_defaults_on_file=application.previous_loan_defaults_on_file,
            loan_percent_income=application.loan_percent_income,
            person_emp_exp=application.person_emp_exp,
            person_income=application.person_income,
        )
        explanation_payload = generate_and_store_nlp_explanation(
            application=application,
            prediction=prediction,
            result=prediction.final_decision.capitalize(),
            risk_level=get_risk_level(prediction),
            confidence_score=prediction.confidence_score or 0.75,
            language_code="en",
            force=True
        )
        delivery = send_decision_notification_email(
            application=application,
            prediction=prediction,
            result=prediction.final_decision.capitalize(),
            reasons=reasons,
            suggestions=suggestions,
            explanation_data=explanation_payload,
            force=True
        )
        if delivery.get("mode") in ("smtp", "outbox"):
            prediction.email_sent = 1
            db.session.commit()
        flash(get_email_delivery_notice(delivery) or "Decision email sent to customer.", "success")
    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception("Failed to resend decision email: %s", exc)
        flash(f"Could not send decision email: {exc}", "error")

    return redirect(url_for('dashboard.review', application_id=application_id))
