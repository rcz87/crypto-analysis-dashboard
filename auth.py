# auth.py
import os
from functools import wraps
from flask import request, jsonify

API_KEY = os.environ.get("API_KEY", "your-default-secret")

def require_api_key(func):
    """Decorator untuk memeriksa API key dari header Authorization."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token != f"Bearer {API_KEY}":
            return jsonify({"error": "Unauthorized"}), 401
        return func(*args, **kwargs)
    return wrapper