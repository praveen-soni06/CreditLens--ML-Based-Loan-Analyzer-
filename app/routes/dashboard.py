from flask import Blueprint, render_template

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    stats = {
        "total": 124,
        "approved": 78,
        "rejected": 46,
        "high_risk": 19
    }

    rejection_reasons = [
        "Low credit score",
        "High loan-to-income ratio",
        "Weak credit history",
        "Low combined household income"
    ]

    recent_applications = [
        {"name": "Rahul Sharma", "status": "Approved", "risk": "Low"},
        {"name": "Anjali Verma", "status": "Rejected", "risk": "High"},
        {"name": "Aman Khan", "status": "Approved", "risk": "Medium"},
        {"name": "Priya Singh", "status": "Rejected", "risk": "High"},
    ]

    return render_template(
        'dashboard.html',
        stats=stats,
        rejection_reasons=rejection_reasons,
        recent_applications=recent_applications
    )

@dashboard_bp.route('/review')
def review():
    review_data = {
        "applicant_name": "Rahul Sharma",
        "recommendation": "Approved",
        "risk_level": "Low",
        "confidence": 87,
        "income": "₹70,000",
        "coapp_income": "₹30,000",
        "loan_amount": "₹4,00,000",
        "loan_term": "180 months",
        "credit_score": 760,
        "loan_intent": "Home Improvement",
        "reasons": [
            "Combined income supports the requested loan amount.",
            "Credit score is strong and within a preferred approval range.",
            "Credit history indicates lower repayment risk."
        ]
    }

    return render_template('review.html', review=review_data)