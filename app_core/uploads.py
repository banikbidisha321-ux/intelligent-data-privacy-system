"""Authenticated document upload and listing routes."""

from pathlib import Path
from uuid import uuid4

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from app_core.auth import current_user, login_required
from app_core.extensions import db
from app_core.models import Document


uploads_bp = Blueprint("uploads", __name__)
ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}


def is_allowed_file(filename: str) -> bool:
    """Return True only for the file types accepted by this phase."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@uploads_bp.route("/documents")
@login_required
def documents():
    """Show documents owned by the signed-in user."""
    records = (
        Document.query.filter_by(owner_id=current_user().id)
        .order_by(Document.id.desc())
        .all()
    )
    return render_template("documents.html", documents=records)


@uploads_bp.route("/documents/upload", methods=["POST"])
@login_required
def upload_document():
    """Validate and store one user document with database metadata."""
    uploaded_file = request.files.get("document")
    if uploaded_file is None or not uploaded_file.filename:
        flash("Choose a document to upload.", "error")
        return redirect(url_for("uploads.documents"))

    if not is_allowed_file(uploaded_file.filename):
        flash("Only PDF, TXT, and DOCX files are allowed.", "error")
        return redirect(url_for("uploads.documents"))

    safe_original_name = secure_filename(uploaded_file.filename)
    if not safe_original_name:
        flash("That filename is not valid.", "error")
        return redirect(url_for("uploads.documents"))

    extension = safe_original_name.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid4().hex}.{extension}"
    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)
    file_path = upload_folder / stored_filename

    try:
        uploaded_file.save(file_path)
        file_size_bytes = file_path.stat().st_size
        if file_size_bytes == 0:
            file_path.unlink(missing_ok=True)
            flash("Empty files cannot be uploaded.", "error")
            return redirect(url_for("uploads.documents"))

        document = Document(
            owner_id=current_user().id,
            original_filename=safe_original_name,
            stored_filename=stored_filename,
            file_type=extension,
            file_size_bytes=file_size_bytes,
        )
        db.session.add(document)
        db.session.commit()
    except Exception:
        db.session.rollback()
        file_path.unlink(missing_ok=True)
        current_app.logger.exception("Document upload failed")
        flash("The document could not be saved. Please try again.", "error")
        return redirect(url_for("uploads.documents"))

    flash("Document uploaded successfully. It is waiting for encryption and privacy scanning.", "success")
    return redirect(url_for("uploads.documents"))
