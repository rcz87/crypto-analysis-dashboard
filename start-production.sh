#!/bin/bash
# Production startup script for Crypto Trading AI Platform

set -e

echo "🚀 Starting CryptoSage AI Trading Platform - Production Mode"
echo "================================================="

# Set production environment
export FLASK_ENV=production
export FLASK_DEBUG=False
export PRODUCTION_ONLY=1
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Check for required environment variables
required_vars=(
    "DATABASE_URL"
    "OPENAI_API_KEY"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ ERROR: Required environment variable $var is not set"
        echo "🔧 Please check your .env file or Docker environment variables"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python3 -c "
import os
import time
import psycopg2
from urllib.parse import urlparse

db_url = os.environ['DATABASE_URL']
parsed = urlparse(db_url)

for i in range(30):
    try:
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],
            user=parsed.username,
            password=parsed.password
        )
        conn.close()
        print('✅ Database connection established')
        break
    except Exception as e:
        print(f'⏳ Database not ready yet (attempt {i+1}/30), waiting...')
        time.sleep(2)
else:
    print('❌ Failed to connect to database after 30 attempts')
    exit(1)
"

echo "✅ Database ready"

# Create necessary directories
mkdir -p logs tmp

# Initialize database (if needed)
echo "🔄 Initializing database schema..."
python3 -c "
try:
    from main import app, db
    with app.app_context():
        db.create_all()
        print('✅ Database schema initialized')
except Exception as e:
    print(f'⚠️ Database initialization: {e}')
    print('✅ Continuing with existing schema')
"

# Start the production server
echo "🚀 Starting Gunicorn production server..."
echo "📍 Server will be available on port 5000"
echo "================================================="

# Start with optimized production configuration
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --worker-class gevent \
    --worker-connections 1000 \
    --max-requests 5000 \
    --max-requests-jitter 100 \
    --timeout 120 \
    --keep-alive 5 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --log-level info \
    --capture-output \
    --enable-stdio-inheritance \
    --preload \
    wsgi_production:application