import os
from flask import Flask
from app.database.db import db

def create_app():
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    app = Flask(__name__)

    # Basic app config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "Ex_Tracker")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///CreditLens.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Email settings (use environment variables in production)
    app.config["EMAIL_HOST"] = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
    app.config["EMAIL_PORT"] = int(os.environ.get("EMAIL_PORT", 465))
    app.config["EMAIL_USE_SSL"] = os.environ.get("EMAIL_USE_SSL", "True").lower() in ("1", "true", "yes")
    app.config["EMAIL_HOST_USER"] = os.environ.get("EMAIL_HOST_USER", "")
    app.config["EMAIL_HOST_PASSWORD"] = os.environ.get("EMAIL_HOST_PASSWORD", "")
    app.config["EMAIL_SENDER"] = os.environ.get("EMAIL_SENDER") or app.config["EMAIL_HOST_USER"] or "noreply@creditlens.com"
    app.config["EMAIL_SENDER_NAME"] = os.environ.get("EMAIL_SENDER_NAME", "CreditLens Support")
    app.config["EMAIL_DEV_OUTBOX"] = os.environ.get("EMAIL_DEV_OUTBOX", "True").lower() in ("1", "true", "yes")
    app.config["EMAIL_FALLBACK_TO_OUTBOX"] = os.environ.get("EMAIL_FALLBACK_TO_OUTBOX", "True").lower() in ("1", "true", "yes")
    app.config["SUPPORT_EMAIL"] = os.environ.get("SUPPORT_EMAIL", app.config["EMAIL_SENDER"])
    app.config["SUPPORT_PHONE"] = os.environ.get("SUPPORT_PHONE", "+91-00000-00000")
    app.config["SUPPORT_HOURS"] = os.environ.get("SUPPORT_HOURS", "Mon-Fri, 9:00 AM to 6:00 PM")
    app.config["PORTAL_LOGIN_URL"] = os.environ.get("PORTAL_LOGIN_URL", "http://127.0.0.1:5000/login")
    app.config["DEFAULT_LOAN_TENURE_MONTHS"] = int(os.environ.get("DEFAULT_LOAN_TENURE_MONTHS", 36))
    app.config["MODEL_APPROVAL_CLASS_LABEL"] = int(os.environ.get("MODEL_APPROVAL_CLASS_LABEL", 0))
    app.config["NLP_PROVIDER"] = os.environ.get("NLP_PROVIDER", "auto")
    app.config["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY", "")
    app.config["GEMINI_MODEL_NAME"] = os.environ.get("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    app.config["HUGGINGFACEHUB_API_TOKEN"] = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "")
    app.config["HF_MODEL_NAME"] = os.environ.get("HF_MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.2")

    # Initialize database
    db.init_app(app)

    # Import models so SQLAlchemy knows about them
    from app.database.db import User, Application, Prediction, EmailVerification, LoanDecisionExplanation, ApplicationTimelineEvent

    # Create tables + seed demo users if they don't exist
    with app.app_context():
        db.create_all()

        # Demo Admin User
        if not User.query.filter_by(email="admin@creditlens.com").first():
            admin_user = User(
                name="admin",
                email="admin@creditlens.com",
                password="admin123",
                role="credit_manager"
            )
            db.session.add(admin_user)

        # Demo Loan Assistant User
        if not User.query.filter_by(email="assistant@creditlens.com").first():
            assistant_user = User(
                name="assistant",
                email="assistant@creditlens.com",
                password="assistant123",
                role="loan_assistant"
            )
            db.session.add(assistant_user)

        db.session.commit()

    # Import blueprints
    from app.routes.main import main_bp
    from app.routes.predict import predict_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.auth import auth_bp
    from app.routes.tracking import tracking_bp

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tracking_bp)

    return app
