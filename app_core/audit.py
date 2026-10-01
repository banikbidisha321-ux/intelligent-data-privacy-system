"""Helpers for creating privacy-safe audit log entries."""

from app_core.extensions import db
from app_core.models import AuditLog


def record_event(
    actor_id: int | None,
    action: str,
    target_type: str | None = None,
    target_id: int | None = None,
    details: str | None = None,
    ip_address: str | None = None,
) -> None:
    """Add an audit entry to the current transaction without committing it."""
    db.session.add(
        AuditLog(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=ip_address,
        )
    )
