"""Document sharing, permission checks, and authorized encrypted downloads."""

from datetime import datetime
from io import BytesIO
import mimetypes

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_file, url_for
from sqlalchemy import func, or_

from app_core.audit import record_event
from app_core.auth import current_user, login_required
from app_core.encryption import EncryptionConfigurationError, decrypt_file
from app_core.extensions import db
from app_core.models import Document, DocumentAccess, User


access_bp = Blueprint("access", __name__)
PERMISSION_LEVELS = {"view": 1, "download": 2, "manage": 3}


def get_active_grant(document_id: int, user_id: int) -> DocumentAccess | None:
    """Return the user's current, non-expired grant for a document."""
    grant = DocumentAccess.query.filter_by(
        document_id=document_id, user_id=user_id
    ).first()
    if grant is not None and grant.expires_at is not None and grant.expires_at <= datetime.now():
        return None
    return grant


def can_access(document: Document, minimum_permission: str) -> bool:
    """Check ownership, admin role, or a grant against a required permission level."""
    user = current_user()
    if user is None:
        return False
    if user.role == "admin" or document.owner_id == user.id:
        return True
    grant = get_active_grant(document.id, user.id)
    return grant is not None and PERMISSION_LEVELS[grant.permission] >= PERMISSION_LEVELS[minimum_permission]


def manage_required(document: Document) -> None:
    """Abort when the current user cannot change this document's permissions."""
    if not can_access(document, "manage"):
        abort(403)


@access_bp.route("/documents/<int:document_id>/access")
@login_required
def manage_access(document_id: int):
    """Show a document's current access grants to its manager."""
    document = Document.query.get_or_404(document_id)
    manage_required(document)
    grants = DocumentAccess.query.filter_by(document_id=document.id).all()
    eligible_users = User.query.filter(
        User.is_active.is_(True), User.id != document.owner_id
    ).order_by(User.full_name).all()
    return render_template(
        "document_access.html", document=document, grants=grants, eligible_users=eligible_users
    )


@access_bp.route("/documents/<int:document_id>/access", methods=["POST"])
@login_required
def grant_access(document_id: int):
    """Create or update a user's permission for a document."""
    document = Document.query.get_or_404(document_id)
    manage_required(document)
    target_user = User.query.get_or_404(request.form.get("user_id", type=int))
    permission = request.form.get("permission")

    if target_user.id == document.owner_id:
        flash("The document owner already has full access.", "error")
    elif not target_user.is_active:
        flash("Access cannot be granted to an inactive account.", "error")
    elif permission not in PERMISSION_LEVELS:
        flash("Choose a valid permission.", "error")
    else:
        grant = DocumentAccess.query.filter_by(
            document_id=document.id, user_id=target_user.id
        ).first()
        if grant is None:
            grant = DocumentAccess(
                document_id=document.id,
                user_id=target_user.id,
                permission=permission,
                granted_by=current_user().id,
            )
            db.session.add(grant)
        else:
            grant.permission = permission
            grant.granted_by = current_user().id
            grant.expires_at = None

        record_event(
            current_user().id,
            "document.access_granted",
            "document",
            document.id,
            f"{permission} permission granted to user ID {target_user.id}",
        )
        db.session.commit()
        flash("Document permission saved.", "success")
    return redirect(url_for("access.manage_access", document_id=document.id))


@access_bp.route("/documents/<int:document_id>/access/<int:grant_id>/revoke", methods=["POST"])
@login_required
def revoke_access(document_id: int, grant_id: int):
    """Remove a user's document-specific permission."""
    document = Document.query.get_or_404(document_id)
    manage_required(document)
    grant = DocumentAccess.query.filter_by(id=grant_id, document_id=document.id).first_or_404()
    target_user_id = grant.user_id
    db.session.delete(grant)
    record_event(
        current_user().id,
        "document.access_revoked",
        "document",
        document.id,
        f"Permission revoked from user ID {target_user_id}",
    )
    db.session.commit()
    flash("Document permission revoked.", "success")
    return redirect(url_for("access.manage_access", document_id=document.id))


@access_bp.route("/documents/<int:document_id>/download")
@login_required
def download_document(document_id: int):
    """Download an authorized encrypted document without writing plaintext to disk."""
    document = Document.query.get_or_404(document_id)
    if not can_access(document, "download"):
        abort(403)
    if document.encryption_status != "encrypted":
        abort(409, "This document must be encrypted before it can be downloaded.")

    from pathlib import Path

    file_path = Path(current_app.config["UPLOAD_FOLDER"]) / Path(document.stored_filename).name
    try:
        plaintext = decrypt_file(file_path)
    except (EncryptionConfigurationError, ValueError):
        abort(503, "The document cannot be decrypted right now.")

    record_event(
        current_user().id,
        "document.downloaded",
        "document",
        document.id,
        "Authorized encrypted document download",
    )
    db.session.commit()
    mime_type = mimetypes.guess_type(document.original_filename)[0] or "application/octet-stream"
    return send_file(
        BytesIO(plaintext),
        as_attachment=True,
        download_name=document.original_filename,
        mimetype=mime_type,
    )


def shared_document_grants_for(user_id: int):
    """Return active grants for documents shared with a normal user."""
    return (
        DocumentAccess.query.join(Document)
        .filter(
            DocumentAccess.user_id == user_id,
            or_(DocumentAccess.expires_at.is_(None), DocumentAccess.expires_at > func.now()),
        )
        .order_by(DocumentAccess.id.desc())
        .all()
    )
