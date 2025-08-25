from app import create_app
import os

# Gunakan environment variable FLASK_ENV atau default ke 'production'
environment = os.environ.get("FLASK_ENV", "production")

app = create_app(environment)
