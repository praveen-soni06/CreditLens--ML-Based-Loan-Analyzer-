from flask import Flask
from app.database.db import db

def create_app():
    app = Flask(__name__)

    # Basic app config
    app.config["SECRET_KEY"] = "Ex_Tracker"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///CreditLens.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    # Import models so SQLAlchemy knows about them
    from app.database.db import User, Application, Prediction

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

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(predict_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)

    return app