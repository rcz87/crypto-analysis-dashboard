# Gunicorn configuration for production deployment
import os
import multiprocessing

# Server socket - simplified for GCE deployment
bind = "0.0.0.0:5000"
backlog = 1024

# Worker processes
workers = min(2, multiprocessing.cpu_count())  # Limit workers to reduce memory usage
worker_class = "sync"
worker_connections = 1000
timeout = 120
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