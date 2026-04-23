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

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

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