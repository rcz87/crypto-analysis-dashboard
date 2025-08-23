# error_handlers.py
from flask import jsonify
from app import app

@app.errorhandler(Exception)
def handle_unhandled_exception(e):
    app.logger.error(f"Unhandled error: {e}")
    return jsonify({"error": str(e)}), 500