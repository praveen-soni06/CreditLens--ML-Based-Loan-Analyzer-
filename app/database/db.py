from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(300), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(
        db.Enum('credit_manager', 'loan_assistant'),
        nullable=False,
        default='loan_assistant'
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    loan_applications = db.relationship(
        'Application',
        foreign_keys='Application.loan_assistant_id',
        backref='loan_assistant',
        lazy=True
    )
    decision_history = db.relationship(
        'Prediction',
        foreign_keys='Prediction.decided_by',
        backref='credit_manager',
        lazy=True
    )

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_ref = db.Column(db.String(32), nullable=True, unique=True, index=True)
    loan_assistant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(100), nullable=False)

    person_age = db.Column(db.Integer, nullable=False)
    person_gender = db.Column(db.SmallInteger, nullable=False)
    person_education = db.Column(db.String(50), nullable=False)
    person_income = db.Column(db.Float, nullable=False)
    person_emp_exp = db.Column(db.Integer, nullable=False)
    person_home_ownership = db.Column(db.String(20), nullable=False)

    loan_amnt = db.Column(db.Float, nullable=False)
    loan_intent = db.Column(db.String(30), nullable=False)
    loan_int_rate = db.Column(db.Float, nullable=False)
    loan_percent_income = db.Column(db.Float, nullable=False)

    credit_history_length = db.Column(db.Float, nullable=False)
    credit_score = db.Column(db.Integer, nullable=False)
    previous_loan_defaults_on_file = db.Column(db.SmallInteger, nullable=False)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    tracking_status = db.Column(db.String(40), nullable=False, default='submitted')
    review_queue = db.Column(db.String(40), nullable=False, default='underwriting')
    admin_remarks = db.Column(db.Text, nullable=True)
    status_updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    prediction = db.relationship('Prediction', backref='application', uselist=False)
    verification = db.relationship('EmailVerification', backref='application', uselist=False)
    explanations = db.relationship('LoanDecisionExplanation', backref='application', lazy=True)
    timeline_events = db.relationship('ApplicationTimelineEvent', backref='application', lazy=True)

class EmailVerification(db.Model):
    __tablename__ = 'email_verifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    verification_code = db.Column(db.String(12), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)

    ml_decision = db.Column(db.SmallInteger, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    risk_score = db.Column(db.Float, nullable=True)
    risk_category = db.Column(db.String(20), nullable=True)
    flag = db.Column(db.Enum('clear', 'review'), nullable=False)
    final_decision = db.Column(
        db.Enum('approved', 'rejected', 'pending', 'hold'),
        default='pending'
    )

    decided_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    decision_at = db.Column(db.DateTime, nullable=True)
    email_sent = db.Column(db.SmallInteger, default=0)
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)
    explanations = db.relationship('LoanDecisionExplanation', backref='prediction', lazy=True)


class ApplicationTimelineEvent(db.Model):
    __tablename__ = 'application_timeline_events'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    event_key = db.Column(db.String(60), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    description = db.Column(db.Text, nullable=True)
    actor_role = db.Column(db.String(40), nullable=False, default='system')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class LoanDecisionExplanation(db.Model):
    __tablename__ = 'loan_decision_explanations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=True)

    decision_result = db.Column(db.String(20), nullable=False)
    language_code = db.Column(db.String(10), nullable=False, default='en')
    provider = db.Column(db.String(50), nullable=False, default='rule_based')

    explanation_text = db.Column(db.Text, nullable=False)
    financial_analysis = db.Column(db.Text, nullable=False)
    suggestions_text = db.Column(db.Text, nullable=False)
    risk_explanation = db.Column(db.Text, nullable=False)
    confidence_summary = db.Column(db.Text, nullable=False)
    smart_tips = db.Column(db.Text, nullable=False)

    email_subject = db.Column(db.String(255), nullable=False)
    email_preview = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
