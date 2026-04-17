from flask import Blueprint, render_template, request

predict_bp = Blueprint('predict', __name__)

@predict_bp.route('/application')
def application():
    return render_template('index.html')

@predict_bp.route('/predict', methods=['POST'])
def predict():
    try:
        # Personal Information
        full_name = request.form.get('full_name', '').strip()
        gender = request.form.get('gender', '')
        marital_status = request.form.get('marital_status', '')
        dependents = request.form.get('dependents', '')
        education = request.form.get('education', '')

        # Financial Details
        income = float(request.form.get('income', 0) or 0)
        coapp_income = float(request.form.get('coapp_income', 0) or 0)
        employment_type = request.form.get('employment_type', '')
        credit_history = request.form.get('credit_history', '')
        credit_score = int(request.form.get('credit_score', 0) or 0)

        # Loan Details
        loan_amount = float(request.form.get('loan_amount', 0) or 0)
        loan_term = int(request.form.get('loan_term', 0) or 0)
        property_area = request.form.get('property_area', '')
        loan_intent = request.form.get('loan_intent', '')

        # Optional AI/NLP text
        loan_reason = request.form.get('loan_reason', '').strip()

    except ValueError:
        return render_template(
            'result.html',
            result="Rejected",
            reasons=["Invalid input values. Please enter valid numeric data."]
        )

    # ----------------------------
    # Smart rule-based evaluation
    # ----------------------------
    reasons = []
    suggestions = []
    result = "Approved"
    risk_level = "Low"

    total_income = income + coapp_income

    # Rule 1: Very low income
    if total_income < 20000:
        result = "Rejected"
        reasons.append("Combined monthly income is too low for stable loan servicing.")
        suggestions.append("Increase declared household income or apply with a stronger co-applicant.")

    # Rule 2: Low credit score
    if credit_score < 600:
        result = "Rejected"
        reasons.append("Credit score is below the preferred lending threshold.")
        suggestions.append("Improve repayment history and reduce outstanding dues to raise your credit score.")
    elif 600 <= credit_score < 700:
        risk_level = "Medium"

    # Rule 3: Poor credit history
    if credit_history == "0":
        result = "Rejected"
        reasons.append("Credit history is weak or unavailable, increasing repayment uncertainty.")
        suggestions.append("Build a stronger credit history through smaller timely repayments.")

    # Rule 4: Loan burden too high
    if total_income > 0 and loan_amount > total_income * 10:
        result = "Rejected"
        reasons.append("Requested loan amount is too high compared to total household income.")
        suggestions.append("Reduce the loan amount or increase applicant/co-applicant income.")
    elif total_income > 0 and loan_amount > total_income * 7 and result == "Approved":
        risk_level = "Medium"

    # Rule 5: High dependents + low income
    if dependents in ["3+"] and total_income < 40000:
        result = "Rejected"
        reasons.append("Higher dependent load with limited income increases repayment risk.")
        suggestions.append("Consider reducing loan amount or adding a financially stronger co-applicant.")

    # Rule 6: Employment stability
    if employment_type in ["freelancer"] and total_income < 50000:
        if result == "Approved":
            risk_level = "Medium"
        reasons.append("Freelance income may be considered less stable for loan approval.")
        suggestions.append("Provide stronger income proof or banking statements for better evaluation.")

    # Rule 7: Very long term + weak profile
    if loan_term >= 360 and credit_score < 650:
        result = "Rejected"
        reasons.append("Long loan tenure with a weak credit profile increases long-term lending risk.")
        suggestions.append("Choose a shorter loan term or improve your credit profile.")

    # Rule 8: Optional AI/NLP-like hint (simple keyword-based for now)
    if loan_reason:
        positive_keywords = ["home", "family", "business", "education", "medical", "house"]
        if any(word in loan_reason.lower() for word in positive_keywords):
            if result == "Approved":
                reasons.append("Loan purpose appears practical and financially justifiable.")

    # If approved and no detailed reasons yet
    if result == "Approved":
        if not reasons:
            reasons = [
                "Income and repayment capacity appear acceptable.",
                "Credit profile meets the basic eligibility threshold.",
                "Loan request falls within a manageable financial range."
            ]

        if not suggestions:
            suggestions = [
                "Keep your repayment record strong to maintain eligibility.",
                "Ensure submitted documents match declared financial details."
            ]

    # If rejected and no suggestions somehow
    if result == "Rejected" and not suggestions:
        suggestions = [
            "Review your financial profile and apply again after improving eligibility factors."
        ]

    return render_template(
        'result.html',
        result=result,
        reasons=reasons,
        suggestions=suggestions,
        risk_level=risk_level,
        applicant_name=full_name if full_name else "Applicant"
    )