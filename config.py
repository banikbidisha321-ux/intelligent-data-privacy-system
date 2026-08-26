"""Central configuration for the Flask application."""

import os


class Config:
    """Base configuration used during Phase 1."""

    SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-before-deployment")
