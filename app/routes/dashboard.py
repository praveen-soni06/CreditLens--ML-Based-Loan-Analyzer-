from flask import Blueprint, render_template, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    from app.database.db import Application, Prediction

    applications = Application.query.order_by(Application.id.desc()).all()

    recent_applications = []
    approved_count = 0
    rejected_count = 0
    high_risk_count = 0

    for application in applications:
        prediction = Prediction.query.filter_by(application_id=application.id).first()

        if prediction:
            status = "Approved" if prediction.ml_decision == 1 else "Rejected"

            if status == "Approved":
                approved_count += 1
            else:
                rejected_count += 1

            # Risk mapping
            if prediction.flag == "clear":
                risk = "Low"
            elif prediction.flag == "review":
                risk = "Medium"
            else:
                risk = "High"

            if risk == "High":
                high_risk_count += 1

        else:
            status = "Pending"
            risk = "Medium"

        recent_applications.append({
            "id": application.id,
            "name": application.customer_name,
            "status": status,
            "risk": risk
        })

    stats = {
        "total": len(applications),
        "approved": approved_count,
        "rejected": rejected_count,
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
    from app.database.db import Application

    latest_application = Application.query.order_by(Application.id.desc()).first()

    if latest_application:
        return redirect(url_for('dashboard.review', application_id=latest_application.id))

    return redirect(url_for('predict.application'))


@dashboard_bp.route('/review/<int:application_id>')
def review(application_id):
    from app.database.db import Application, Prediction

    application = Application.query.get_or_404(application_id)
    prediction = Prediction.query.filter_by(application_id=application_id).first()

    ai_recommendation = "Approved"
    risk_level = "Low"
    confidence = 87

    if prediction:
        ai_recommendation = "Approved" if prediction.ml_decision == 1 else "Rejected"

        if prediction.confidence_score is not None:
            confidence = round(prediction.confidence_score * 100)

        if prediction.flag == "clear":
            risk_level = "Low"
        elif prediction.flag == "review":
            risk_level = "Medium"
        else:
            risk_level = "High"

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
        application_id=application.id
    )