from flask import Flask, redirect, url_for
from app.extensions import db, login_manager
from app.auth.routes import auth_bp
from app.auth.alt_routes import alt_auth_bp  # Import the alternative auth blueprint
from app.views.dashboard import dashboard_bp
from app.models.user import User  # Import your User model
from app.config import Config
from flask_dance.contrib.google import make_google_blueprint
import os
from flask_migrate import Migrate
import certifi


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)  # Initialize Flask-Migrate here
    login_manager.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp)          # Google OAuth routes
    app.register_blueprint(dashboard_bp)     # Dashboard routes
    app.register_blueprint(alt_auth_bp, url_prefix="")  # Alternative login routes

    # Path to the custom CA certificate file
    cert_path = os.path.join(os.getcwd(), "certificates", "cacert.pem")
    if not os.path.exists(cert_path):
        raise FileNotFoundError(f"Certificate file not found at {cert_path}")
    print(f"Using cert_path: {cert_path}")
    #google_bp.session.verify = cert_path

    # Google OAuth Blueprint
    google_bp = make_google_blueprint(
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        redirect_to="auth.google_login",
        scope=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"]
    )
    # Override the session's SSL verification to use the custom CA bundle
    print("cert_path", cert_path)
    #google_bp.session.verify = cert_path
    google_bp.session.verify = certifi.where()  # Using certifi's default cacert.pem
    
    #google_bp.session.verify = False
    app.register_blueprint(google_bp, url_prefix="")

    # Redirect root to the alternative login page for now
    @app.route('/')
    def home():
        return redirect(url_for('auth.login'))  # Default to alternative login

    # Add user_loader to load user from session
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Load user by ID, using your User model

    with app.app_context():
        db.create_all()

    return app
