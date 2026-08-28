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
