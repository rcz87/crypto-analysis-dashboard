from flask import Blueprint, jsonify, request
from app import app, db
from models import TradingSignal, TelegramUser
import logging
import os

# Create a main blueprint for core routes
main_bp = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

@main_bp.route('/')
def index():
    """Main index route"""
    return jsonify({
        "message": "Advanced Cryptocurrency GPTs & Telegram Bot API",
        "version": "2.0.0",
        "status": "active",
        "endpoints": [
            "/api/gpts/status",
            "/api/gpts/sinyal/tajam",
            "/api/gpts/market-data", 
            "/api/gpts/smc-analysis",
            "/api/gpts/ticker/<symbol>",
            "/api/gpts/orderbook/<symbol>",
            "/health"
        ]
    })

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Test database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "database": db_status,
        "version": "2.0.0"
    })

# Enhanced GPTs API will be imported from gpts_routes.py

# Import and register the enhanced GPTs blueprint
from gpts_routes import gpts_api

# Register blueprints with the app
app.register_blueprint(main_bp)
app.register_blueprint(gpts_api)  # Use enhanced GPTs API from gpts_routes.py