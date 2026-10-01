"""Administrator-only dashboard and user-management routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app_core.audit import record_event
from app_core.auth import admin_required, current_user
from app_core.extensions import db
from app_core.models import AuditLog, Document, PrivacyRiskScore, Recommendation, User


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/admin")
@admin_required
def dashboard():
    """Show aggregate project information to an administrator."""
    metrics = {
        "users": User.query.count(),
        "documents": Document.query.count(),
        "high_risk_documents": PrivacyRiskScore.query.filter(
            PrivacyRiskScore.risk_level.in_(["high", "critical"])
        ).count(),
        "open_recommendations": Recommendation.query.filter_by(status="open").count(),
    }
    recent_documents = Document.query.order_by(Document.id.desc()).limit(10).all()
    recent_events = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    return render_template(
        "admin_dashboard.html",
        metrics=metrics,
        recent_documents=recent_documents,
        recent_events=recent_events,
    )


@admin_bp.route("/admin/users")
@admin_required
def users():
    """List all user accounts for an administrator."""
    return render_template("admin_users.html", users=User.query.order_by(User.id.desc()).all())


@admin_bp.route("/admin/users/<int:user_id>/role", methods=["POST"])
@admin_required
def update_role(user_id: int):
    """Update another user's role, while preventing self-role removal."""
    target_user = User.query.get_or_404(user_id)
    requested_role = request.form.get("role")
    admin = current_user()

    if requested_role not in {"user", "admin"}:
        flash("Invalid role.", "error")
    elif target_user.id == admin.id:
        flash("You cannot change your own role here.", "error")
    elif target_user.role == requested_role:
        flash("That user already has this role.", "error")
    else:
        target_user.role = requested_role
        record_event(
            admin.id,
            "admin.user_role_changed",
            "user",
            target_user.id,
            f"Role changed to {requested_role}",
        )
        db.session.commit()
        flash("User role updated.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/admin/users/<int:user_id>/status", methods=["POST"])
@admin_required
def toggle_status(user_id: int):
    """Activate or deactivate another user without allowing self-lockout."""
    target_user = User.query.get_or_404(user_id)
    admin = current_user()

    if target_user.id == admin.id:
        flash("You cannot deactivate your own account.", "error")
    else:
        target_user.is_active = not target_user.is_active
        state = "activated" if target_user.is_active else "deactivated"
        record_event(
            admin.id,
            "admin.user_status_changed",
            "user",
            target_user.id,
            f"Account {state}",
        )
        db.session.commit()
        flash(f"User account {state}.", "success")
    return redirect(url_for("admin.users"))
