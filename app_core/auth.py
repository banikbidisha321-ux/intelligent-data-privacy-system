"""Registration, login, logout, and access-control routes."""

from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app_core.extensions import db
from app_core.models import User


auth_bp = Blueprint("auth", __name__)


def current_user():
    """Return the signed-in user, or None when no valid session exists."""
    user_id = session.get("user_id")
    if not user_id:
        return None
    return db.session.get(User, user_id)


def login_required(view):
    """Require an authenticated user before allowing access to a view."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if current_user() is None:
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Create a user account with a safely hashed password."""
    if current_user() is not None:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not full_name or not email or not password:
            flash("Please complete all fields.", "error")
        elif len(full_name) > 100:
            flash("Name must be 100 characters or fewer.", "error")
        elif "@" not in email or len(email) > 255:
            flash("Enter a valid email address.", "error")
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "error")
        elif User.query.filter_by(email=email).first() is not None:
            flash("An account with this email already exists.", "error")
        else:
            user = User(
                full_name=full_name,
                email=email,
                password_hash=generate_password_hash(password),
                role="user",
            )
            db.session.add(user)
            db.session.commit()
            session.clear()
            session["user_id"] = user.id
            flash("Your account has been created.", "success")
            return redirect(url_for("auth.dashboard"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a registered user."""
    if current_user() is not None:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()

        if user is None or not user.is_active or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
        else:
            session.clear()
            session["user_id"] = user.id
            flash("You are logged in.", "success")
            return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """End the current user session."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@auth_bp.route("/dashboard")
@login_required
def dashboard():
    """Show a page available only to signed-in users."""
    return render_template("dashboard.html", user=current_user())
