# Gunicorn configuration for production deployment
import os
import multiprocessing

# Server socket - simplified for GCE deployment
bind = "0.0.0.0:5000"
backlog = 1024

# Worker processes - Production optimized
workers = (multiprocessing.cpu_count() * 2) + 1  # Optimal: (CPU * 2) + 1
worker_class = "gthread"  # Use gthread for better concurrency
worker_connections = 1000
threads = 4  # 2-4 threads per worker as specified
timeout = 60  # 60s timeout as specified
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "crypto-trading-ai"

# Server mechanics - Optimized for deployment
daemon = False
pidfile = None  # Disable pidfile for deployment compatibility
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
keyfile = None
certfile = None

# Memory optimization
preload_app = False  # Don't preload to save memory
lazy_apps = True

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'PYTHONPATH=/app'
]