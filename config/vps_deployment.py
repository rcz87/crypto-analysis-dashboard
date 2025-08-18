"""
VPS Deployment Configuration for Hostinger
Production-ready settings optimized for VPS hosting
"""

import os
import logging

class VPSConfig:
    """Configuration settings optimized for VPS deployment"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False  # Always False for production
    TESTING = False
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Server settings
    HOST = '0.0.0.0'  # Allow external connections
    PORT = int(os.environ.get('PORT', 5000))
    
    # Gunicorn settings for production
    WORKERS = int(os.environ.get('WORKERS', 2))
    WORKER_CLASS = 'sync'
    WORKER_CONNECTIONS = 1000
    TIMEOUT = 120
    KEEPALIVE = 2
    
    # Security headers
    SECURITY_HEADERS = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
    }
    
    # CORS settings for domain
    CORS_ORIGINS = [
        "https://chat.openai.com",
        "https://chatgpt.com", 
        "https://*.openai.com",
        os.environ.get('DOMAIN_URL', '*')  # Your custom domain
    ]
    
    # API rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "1000 per hour"
    
    # Logging configuration
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    @classmethod
    def configure_logging(cls):
        """Configure logging for production"""
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format=cls.LOG_FORMAT,
            handlers=[
                logging.FileHandler('/tmp/app.log'),
                logging.StreamHandler()
            ]
        )
    
    @classmethod
    def get_gunicorn_options(cls):
        """Get Gunicorn configuration options"""
        return {
            'bind': f'{cls.HOST}:{cls.PORT}',
            'workers': cls.WORKERS,
            'worker_class': cls.WORKER_CLASS,
            'worker_connections': cls.WORKER_CONNECTIONS,
            'timeout': cls.TIMEOUT,
            'keepalive': cls.KEEPALIVE,
            'preload_app': True,
            'max_requests': 1000,
            'max_requests_jitter': 100
        }

class DevelopmentConfig:
    """Development configuration for testing"""
    
    SECRET_KEY = 'dev-secret-key'
    DEBUG = True
    TESTING = False
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    HOST = '0.0.0.0'
    PORT = 5000
    
    CORS_ORIGINS = ["*"]
    
    LOG_LEVEL = logging.DEBUG

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'production')
    
    if env == 'development':
        return DevelopmentConfig()
    else:
        return VPSConfig()