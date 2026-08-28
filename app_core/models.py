"""Database models used by the Flask application."""

from app_core.extensions import db


class User(db.Model):
    """A registered application user stored in the existing users table."""

    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("user", "admin"), nullable=False, default="user")
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Document(db.Model):
    """Metadata for a document owned by a registered user."""

    __tablename__ = "documents"

    id = db.Column(db.BigInteger, primary_key=True)
    owner_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(100), nullable=False)
    file_size_bytes = db.Column(db.BigInteger, nullable=False)
    classification = db.Column(
        db.Enum("public", "internal", "confidential", "restricted"),
        nullable=False,
        default="internal",
    )
    encryption_status = db.Column(
        db.Enum("pending", "encrypted", "failed"),
        nullable=False,
        default="pending",
    )
    scan_status = db.Column(
        db.Enum("pending", "completed", "failed"),
        nullable=False,
        default="pending",
    )

    owner = db.relationship("User", backref="documents")
