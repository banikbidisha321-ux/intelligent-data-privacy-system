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
    pii_findings = db.relationship(
        "PiiFinding", backref="document", cascade="all, delete-orphan"
    )
    privacy_risk_score = db.relationship(
        "PrivacyRiskScore", backref="document", uselist=False, cascade="all, delete-orphan"
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
