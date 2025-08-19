#!/usr/bin/env python3
"""
Local Development Entry Point
Handles database connection fallback from PostgreSQL to SQLite
"""

try:
    from app_local import app
    print("✅ Local development app loaded successfully!")
except Exception as e:
    print(f"❌ Error loading app: {e}")
    import sys
    sys.exit(1)

if __name__ == "__main__":
    print("🚀 Starting local development server...")
    app.run(host="0.0.0.0", port=5000, debug=True)