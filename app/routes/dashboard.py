from datetime import datetime

from flask import Blueprint, render_template, redirect, request, session, url_for

from app.database.db import Application, Prediction, db

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

    if prediction.flag == "clear":
        return "Low"

    if prediction.ml_decision == 0:
        return "High"

    return "Medium"


def get_final_status(prediction):
    if not prediction:
        return "Pending Review"

    if prediction.final_decision == "approved":
        return "Approved"

    if prediction.final_decision == "rejected":
        return "Rejected"

    return "Pending Review"


@dashboard_bp.route('/dashboard')
def dashboard():
    guard = require_credit_manager()
    if guard:
        return guard

    applications = Application.query.order_by(Application.id.desc()).all()

    recent_applications = []
    approved_count = 0
    rejected_count = 0
    pending_count = 0
    high_risk_count = 0

    for application in applications:
        prediction = Prediction.query.filter_by(application_id=application.id).first()

        status = get_final_status(prediction)
        risk = get_risk_level(prediction)
        if prediction:
            ml_recommendation = "Approved" if prediction.ml_decision == 1 else "Rejected"
        else:
            ml_recommendation = "Pending"

        if status == "Approved":
            approved_count += 1
        elif status == "Rejected":
            rejected_count += 1
        else:
            pending_count += 1

        if risk == "High":
            high_risk_count += 1

        recent_applications.append({
            "id": application.id,
            "name": application.customer_name,
            "status": status,
            "risk": risk,
            "ml_recommendation": ml_recommendation
        })

    stats = {
        "total": len(applications),
        "approved": approved_count,
        "rejected": rejected_count,
        "pending": pending_count,
        "high_risk": high_risk_count
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
        recent_applications=recent_applications
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
    prediction = Prediction.query.filter_by(application_id=application_id).first()

    ai_recommendation = "Approved"
    risk_level = "Low"
    confidence = 87

    if prediction:
        ai_recommendation = "Approved" if prediction.ml_decision == 1 else "Rejected"

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

    return render_template(
        'review.html',
        applicant_name=application.customer_name,
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
        application_id=application.id,
        final_decision=prediction.final_decision if prediction else "pending",
        decided_by=prediction.decided_by if prediction else None,
        decision_at=prediction.decision_at if prediction else None
    )


@dashboard_bp.route('/review/<int:application_id>/decision', methods=['POST'])
def decide_application(application_id):
    guard = require_credit_manager()
    if guard:
        return guard

    prediction = Prediction.query.filter_by(application_id=application_id).first_or_404()
    decision = request.form.get('decision', '').strip().lower()

    if decision not in ("approved", "rejected"):
        return redirect(url_for('dashboard.review', application_id=application_id))

    prediction.final_decision = decision
    prediction.decided_by = session.get('user_id')
    prediction.decision_at = datetime.utcnow()

    db.session.commit()

    return redirect(url_for('dashboard.review', application_id=application_id))
