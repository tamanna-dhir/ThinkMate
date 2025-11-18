# app/__init__.py
from flask import Flask

def create_app():
    """
    Factory function to create and configure the Flask application.
    """
    app = Flask(__name__)

    # ✅ Import and register blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app
