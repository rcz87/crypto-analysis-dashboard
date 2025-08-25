# Optimized single-stage Dockerfile for Crypto Trading AI Platform

# Multi-stage build for minimal size
FROM python:3.11-slim as builder

# Build stage - install minimal dependencies
WORKDIR /build
COPY requirements-prod.txt .

# Ensure .local directory exists and install packages
RUN mkdir -p /root/.local \
    && pip install --no-cache-dir --user -r requirements-prod.txt \
    && find /root/.local -name "*.pyc" -delete 2>/dev/null || true \
    && find /root/.local -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "*.dist-info" -type d -exec rm -rf {} + 2>/dev/null || true \
    && find /root/.local -name "tests" -type d -exec rm -rf {} + 2>/dev/null || true

# Production stage - minimal final image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PRODUCTION_ONLY=1

# Install minimal system dependencies - further optimized
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/cache/apt/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Copy dependencies from builder stage (with error handling)
COPY --from=builder /root/.local /usr/local

# Create application directory
WORKDIR /app

# Copy only essential application files (minimal set)
# Exclude heavy directories via .dockerignore: .pythonlibs/, .cache/, .local/
COPY wsgi_production.py .
COPY main.py .
COPY gpts_api_simple.py .
COPY gunicorn.conf.py .
COPY start-production.sh .
COPY models.py .
COPY core/ ./core/
COPY api/ ./api/

# Beri hak eksekusi pada skrip startup
RUN chmod +x start-production.sh

# Verify no heavy directories were copied (debug step)
RUN echo "=== Verifying .dockerignore exclusions ===" \
    && echo "Checking if heavy directories were excluded..." \
    && test ! -d ".pythonlibs" || (echo "ERROR: .pythonlibs was copied!" && exit 1) \
    && test ! -d ".cache" || (echo "ERROR: .cache was copied!" && exit 1) \
    && test ! -d ".local" || (echo "ERROR: .local was copied!" && exit 1) \
    && echo "✅ Heavy directories successfully excluded"

# Aggressive cleanup and optimization
RUN mkdir -p logs tmp \
    && find . -name "*.pyc" -delete \
    && find . -name "__pycache__" -type d -exec rm -rf {} + || true \
    && find /usr/local -name "*.pyc" -delete \
    && find /usr/local -name "__pycache__" -type d -exec rm -rf {} + || true \
    && find /usr/local -name "tests" -type d -exec rm -rf {} + || true \
    && find /usr/local -name "test" -type d -exec rm -rf {} + || true \
    && find /usr/local -name "*.dist-info" -type d -exec rm -rf {} + || true \
    && rm -rf /usr/local/lib/python*/site-packages/pip \
    && rm -rf /usr/local/lib/python*/site-packages/setuptools \
    && rm -rf /tmp/* /var/tmp/* /root/.cache

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

# Expose only port 5000 for GCE deployment
EXPOSE 5000

# Simplified health check
HEALTHCHECK --interval=60s --timeout=15s --start-period=120s --retries=2 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start application with production WSGI - deployment ready
CMD ["./start-production.sh"]
