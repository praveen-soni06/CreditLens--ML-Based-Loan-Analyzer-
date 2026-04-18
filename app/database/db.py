from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "Ex_Tracker"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///CreditLens.db"
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(300), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum('credit_manager', 'loan_assistant'),
    nullable=False,
    default='loan_assistant')
    created_at = db.Column(db.DateTime, nullable = False, default=datetime.utcnow)

    loan_applications = db.relationship('Application', foreign_keys='Application.loan_assistant_id', backref='loan_assistant', lazy=True)
    decision_history = db.relationship('Prediction', foreign_keys='Prediction.decided_by', backref='credit_manager', lazy=True)

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    prediction = db.relationship('Prediction', backref='application', uselist=False)


class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    ml_decision = db.Column(db.SmallInteger, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    flag = db.Column(db.Enum('clear', 'review'), nullable=False)
    final_decision = db.Column(db.Enum('approved', 'rejected', 'pending'), default='pending')
    decided_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    decision_at = db.Column(db.DateTime, nullable=True)
    email_sent = db.Column(db.SmallInteger, default=0)
    predicted_at = db.Column(db.DateTime, default=datetime.utcnow)
