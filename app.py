"""Entry point for the Intelligent Data Privacy Management System."""

from flask import Flask, render_template

from config import Config


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    @app.route("/")
    def home():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
