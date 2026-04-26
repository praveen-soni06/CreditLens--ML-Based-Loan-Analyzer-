from flask import Blueprint, render_template, request, session, redirect, url_for
from datetime import datetime
from app.database.db import db, Application, Prediction

predict_bp = Blueprint('predict', __name__)
@predict_bp.route('/application')
def application():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    current_date = datetime.now().strftime("%d %b %Y")
    application_ref = f"LN-{datetime.now().strftime('%d%m%H%M')}"

    return render_template(
        'index.html',
        current_date=current_date,
        application_ref=application_ref
    )
@predict_bp.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        # -----------------------------
        # Read form fields
        # -----------------------------
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

    # -----------------------------
    # Simple demo ML-style logic
    # -----------------------------
    result = "Approved"
    risk_level = "Low"
    reasons = []
    suggestions = []

    if credit_score < 600:
        result = "Rejected"
        risk_level = "High"
        reasons.append("Credit score is below the preferred lending threshold.")
        suggestions.append("Improve credit score by maintaining timely repayments.")

    if previous_loan_defaults_on_file == 1:
        result = "Rejected"
        risk_level = "High"
        reasons.append("Previous loan default history increases repayment risk.")
        suggestions.append("Provide stronger financial documents and repayment evidence.")

    if loan_percent_income > 0.5:
        if result == "Approved":
            risk_level = "Medium"
        reasons.append("Loan amount is relatively high compared to annual income.")
        suggestions.append("Consider reducing the loan amount for better eligibility.")

    if person_emp_exp < 1 and person_income < 300000:
        if result == "Approved":
            risk_level = "Medium"
        reasons.append("Limited work experience may reduce repayment stability.")
        suggestions.append("Provide employment proof or add a stronger income profile.")

    if result == "Approved" and not reasons:
        reasons = [
            "Income level supports the requested loan amount.",
            "Credit score is within the preferred approval range.",
            "No major default indicators were found in the submitted profile."
        ]

    if result == "Approved" and not suggestions:
        suggestions = [
            "Ensure all submitted documents match the declared values.",
            "Maintain repayment discipline for future credit strength."
        ]

    if result == "Rejected" and not suggestions:
        suggestions = [
            "Review your financial profile and apply again after improving key risk factors."
        ]

    # -----------------------------
    # Save application + prediction
    # -----------------------------
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

        ml_decision = 1 if result == "Approved" else 0

        if result == "Approved":
            confidence_score = 0.87 if risk_level == "Low" else 0.68
        else:
            confidence_score = 0.91 if risk_level == "High" else 0.62

        flag = "clear" if risk_level == "Low" else "review"

        new_prediction = Prediction(
            application_id=new_application.id,
            ml_decision=ml_decision,
            confidence_score=confidence_score,
            flag=flag,
            final_decision="pending",
            decided_by=None,
            decision_at=None,
            email_sent=0,
            predicted_at=datetime.utcnow()
        )

        db.session.add(new_prediction)
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

    # -----------------------------
    # Success result page
    # -----------------------------
    return render_template(
        'result.html',
        result=result,
        reasons=reasons,
        suggestions=suggestions,
        risk_level=risk_level,
        applicant_name=customer_name if customer_name else "Applicant",
        application_id=new_application.id
    )