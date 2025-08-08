# Deployment Optimization Guide

## Applied Fixes for Deployment Size Issue

### 1. Created .dockerignore File
- Excludes Python cache files (__pycache__/, *.pyc)
- Excludes development dependencies (.cache/, .pytest_cache/)
- Excludes log files (*.log)
- Excludes documentation and test files
- Excludes large ML cache directories
- Excludes IDE and OS files

### 2. Production Requirements (requirements-prod.txt)
- Removed heavy ML libraries (tensorflow, keras, scikit-learn, xgboost)
- Removed development tools (pytest, pytest-cov)
- Kept only essential dependencies for API functionality
- Optimized versions for smaller footprint

### 3. Optimized Dockerfile
- Removed frontend build stage (not needed)
- Used python:3.11-slim base image
- Added --no-cache-dir and --no-compile flags for pip
- Added cleanup commands to remove .pyc files and __pycache__
- Optimized apt packages with --no-install-recommends
- Limited workers to 2 to reduce memory usage

### 4. Port Configuration
- Only exposes port 5000 (removed multiple port forwarding)
- Maps to standard HTTP port 80 in deployment

### 5. Gunicorn Configuration
- Created gunicorn.conf.py with memory-optimized settings
- Limited workers to 2
- Enabled lazy loading to save memory
- Set appropriate timeouts and request limits

### 6. WSGI Production Optimization
- Added PRODUCTION_ONLY environment variable detection
- Optimized Flask configuration for production
- Added file caching headers

## Environment Variables Required

Set these in Replit Secrets (not in files):
- `OKX_API_KEY`: Your OKX API key
- `OKX_SECRET_KEY`: Your OKX secret key  
- `OKX_PASSPHRASE`: Your OKX passphrase
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL connection URL
- `TELEGRAM_BOT_TOKEN`: (Optional) Telegram bot token
- `TELEGRAM_CHAT_ID`: (Optional) Telegram chat ID

## Deployment Command
```bash
# The optimized command is now:
gunicorn --config gunicorn.conf.py wsgi_production:application
```

## Expected Size Reduction
- Removed ~2GB+ of ML libraries (tensorflow, etc.)
- Excluded cache directories (~500MB+)
- Excluded development dependencies (~200MB+)  
- Optimized Docker layers and cleanup

Total expected size reduction: ~3-4GB, bringing deployment under 8GB limit.

## Production Features
- Health checks every 60 seconds
- Automatic worker restarts after 1000 requests
- Optimized logging and monitoring
- Memory-efficient worker configuration
- Proper error handling and startup checks