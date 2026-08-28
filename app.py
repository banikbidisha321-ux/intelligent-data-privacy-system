"""Entry point for the Intelligent Data Privacy Management System."""

from flask import Flask, jsonify, render_template
from sqlalchemy import text

from app_core.auth import auth_bp, current_user
from app_core.extensions import db
from config import Config


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    if app.config["SQLALCHEMY_DATABASE_URI"]:
        db.init_app(app)

    app.register_blueprint(auth_bp)

    @app.context_processor
    def inject_current_user():
        """Make the signed-in user available to every HTML template."""
        return {"current_user": current_user()}

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/database-status")
    def database_status():
        """Confirm whether Flask can reach the configured MySQL database."""
        if not app.config["SQLALCHEMY_DATABASE_URI"]:
            return jsonify(
                status="not_configured",
                message="Create a .env file and set DATABASE_URL before checking MySQL.",
            ), 503

        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="connected", message="Flask is connected to MySQL."), 200
        except Exception:
            app.logger.exception("Database connection check failed")
            return jsonify(
                status="unavailable",
                message="Flask could not connect to MySQL. Check DATABASE_URL and MySQL Server.",
            ), 503

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
