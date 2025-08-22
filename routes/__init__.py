from flask import Flask
from flask_sqlalchemy import SQLAlchemy

def init_routes(app: Flask, db: SQLAlchemy):
    """Initialize essential route blueprints"""
    
    # Only register health routes - avoid all conflicts
    from .health import health_bp
    
    # Check if health blueprint is not already registered
    if 'health' not in app.blueprints:
        app.register_blueprint(health_bp)
        
    # Note: Main routes.py will handle its own blueprints
    # This function only handles the new health endpoints