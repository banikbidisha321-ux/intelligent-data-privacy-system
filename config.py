"""Central configuration for the Flask application."""

import os

from dotenv import load_dotenv


load_dotenv()


class Config:
    """Base configuration for local development."""

    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-before-deployment")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
