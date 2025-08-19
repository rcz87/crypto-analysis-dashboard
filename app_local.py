import os
import sys
from pathlib import Path

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

def create_app():
    """
    Create Flask app with environment-aware database configuration
    """
    # create the app
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration with fallback logic
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url and database_url.startswith("postgresql://"):
        # Try PostgreSQL first (production/cloud)
        try:
            print(f"🔗 Attempting PostgreSQL connection...")
            app.config["SQLALCHEMY_DATABASE_URI"] = database_url
            app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                "pool_recycle": 300,
                "pool_pre_ping": True,
                "connect_args": {"connect_timeout": 10}  # 10 second timeout
            }
            
            # Test connection
            db.init_app(app)
            with app.app_context():
                db.engine.connect()
            print("✅ PostgreSQL connection successful!")
            
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            print("🔄 Falling back to SQLite for local development...")
            
            # Fallback to SQLite for local development
            project_root = Path(__file__).parent
            sqlite_path = project_root / "local_development.db"
            app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
            app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                "pool_pre_ping": True
            }
            
            # Reinitialize with SQLite
            db.init_app(app)
            print(f"✅ SQLite fallback initialized: {sqlite_path}")
    else:
        # Default to SQLite for local development
        print("🔧 No PostgreSQL URL found, using SQLite for development...")
        project_root = Path(__file__).parent
        sqlite_path = project_root / "local_development.db"
        app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{sqlite_path}"
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True
        }
        db.init_app(app)
        print(f"✅ SQLite initialized: {sqlite_path}")
    
    with app.app_context():
        # Make sure to import the models here or their tables won't be created
        try:
            import models  # noqa: F401
            db.create_all()
            print("✅ Database tables created successfully!")
        except ImportError:
            print("⚠️ No models.py found, skipping table creation")
            pass
        except Exception as e:
            print(f"⚠️ Error creating tables: {e}")
    
    # Import routes after app is created
    try:
        import routes  # noqa: F401
        print("✅ Routes imported successfully!")
    except ImportError:
        print("⚠️ No routes.py found, skipping route import")
        pass
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    print("🚀 Starting Flask development server...")
    app.run(host="0.0.0.0", port=5000, debug=True)