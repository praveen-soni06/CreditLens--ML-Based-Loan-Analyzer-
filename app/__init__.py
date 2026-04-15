from flask import Flask

def create_app():
    app = Flask(__name__)

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