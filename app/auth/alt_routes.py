from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from app.models.user import User
from app.extensions import db

alt_auth_bp = Blueprint("alt_auth", __name__)

@alt_auth_bp.route("/alt_login", methods=["GET", "POST"])
def alt_login():
    """Alternative email/password login."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("dashboard.dashboard_view"))
        else:
            flash("Invalid credentials. Please try again.", "danger")
    
    return render_template("alt_login.html")

@alt_auth_bp.route("/alt_register", methods=["GET", "POST"])
def alt_register():
    """Alternative user registration."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for("alt_auth.alt_register"))
        
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("alt_auth.alt_login"))
    
    return render_template("alt_register.html")

@alt_auth_bp.route("/alt_logout")
@login_required
def alt_logout():
    """Alternative logout."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("alt_auth.alt_login"))
