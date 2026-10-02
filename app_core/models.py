"""Database models used by the Flask application."""

from app_core.extensions import db
from sqlalchemy import text


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
    pii_findings = db.relationship(
        "PiiFinding", backref="document", cascade="all, delete-orphan"
    )
    privacy_risk_score = db.relationship(
        "PrivacyRiskScore", backref="document", uselist=False, cascade="all, delete-orphan"
    )
    recommendations = db.relationship(
        "Recommendation", backref="document", cascade="all, delete-orphan"
    )
    access_grants = db.relationship(
        "DocumentAccess", backref="document", cascade="all, delete-orphan"
    )


class PiiFinding(db.Model):
    """A masked sensitive-data item identified in a document."""

    __tablename__ = "pii_findings"

    id = db.Column(db.BigInteger, primary_key=True)
    document_id = db.Column(db.BigInteger, db.ForeignKey("documents.id"), nullable=False)
    pii_type = db.Column(db.String(50), nullable=False)
    redacted_value = db.Column(db.String(255), nullable=False)
    confidence_score = db.Column(db.Numeric(5, 2), nullable=False)
    location_reference = db.Column(db.String(100))


class PrivacyRiskScore(db.Model):
    """The latest calculated privacy risk for one document."""

    __tablename__ = "privacy_risk_scores"

    id = db.Column(db.BigInteger, primary_key=True)
    document_id = db.Column(
        db.BigInteger, db.ForeignKey("documents.id"), nullable=False, unique=True
    )
    score = db.Column(db.SmallInteger, nullable=False)
    risk_level = db.Column(
        db.Enum("low", "medium", "high", "critical"), nullable=False
    )


class Recommendation(db.Model):
    """A risk-based action suggested for a document."""

    __tablename__ = "recommendations"

    id = db.Column(db.BigInteger, primary_key=True)
    document_id = db.Column(db.BigInteger, db.ForeignKey("documents.id"), nullable=False)
    recommendation_text = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Enum("low", "medium", "high"), nullable=False)
    status = db.Column(
        db.Enum("open", "completed", "dismissed"), nullable=False, default="open"
    )


class AuditLog(db.Model):
    """A privacy-safe record of a significant user action."""

    __tablename__ = "audit_logs"

    id = db.Column(db.BigInteger, primary_key=True)
    actor_id = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.BigInteger)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    actor = db.relationship("User", backref="audit_logs")


class DocumentAccess(db.Model):
    """A permission granted to one user for one document."""

    __tablename__ = "document_access"

    id = db.Column(db.BigInteger, primary_key=True)
    document_id = db.Column(db.BigInteger, db.ForeignKey("documents.id"), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id"), nullable=False)
    permission = db.Column(db.Enum("view", "download", "manage"), nullable=False)
    granted_by = db.Column(db.BigInteger, db.ForeignKey("users.id"))
    granted_at = db.Column(
        db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    expires_at = db.Column(db.DateTime)

    user = db.relationship("User", foreign_keys=[user_id], backref="shared_access")
    granted_by_user = db.relationship("User", foreign_keys=[granted_by])
