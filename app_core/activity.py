"""Routes for a signed-in user's activity history."""

from flask import Blueprint, render_template

from app_core.auth import current_user, login_required
from app_core.models import AuditLog


activity_bp = Blueprint("activity", __name__)


@activity_bp.route("/activity")
@login_required
def activity():
    """Show privacy-safe audit events belonging to the signed-in user."""
    events = (
        AuditLog.query.filter_by(actor_id=current_user().id)
        .order_by(AuditLog.created_at.desc())
        .all()
    )
    return render_template("activity.html", events=events)
