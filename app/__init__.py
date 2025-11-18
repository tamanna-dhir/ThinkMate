# app/__init__.py
from flask import Flask
import os

def create_app():
    """
    Factory function to create and configure the Flask application.
    """
    app = Flask(
        __name__,
        static_folder='static',
        template_folder='templates'
    )

    # ✅ Import and register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
