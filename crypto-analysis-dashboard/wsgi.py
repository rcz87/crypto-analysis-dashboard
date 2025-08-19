#!/usr/bin/env python3
"""
Simple WSGI entry point for Replit deployment
"""
from main import app

application = app

if __name__ == "__main__":
    application.run()