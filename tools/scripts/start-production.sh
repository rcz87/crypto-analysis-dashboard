#!/bin/bash
# Production startup script for deployment

echo "🚀 Starting Crypto Trading AI - Production Mode"

# Set production environment
export FLASK_ENV=production
export PRODUCTION_ONLY=1
export PYTHONPATH=/app:$PYTHONPATH

# Clean up any existing processes
pkill -f gunicorn || true
rm -f /tmp/gunicorn.pid

# Wait a moment for cleanup
sleep 2

# Start with production WSGI
echo "✅ Starting production server..."
exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --timeout 120 \
    --worker-class sync \
    --max-requests 1000 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --capture-output \
    wsgi_production:application