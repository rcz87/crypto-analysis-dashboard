#!/usr/bin/env python3
"""
Production Configuration Manager
Ensures proper database and API configuration for production deployment
"""
import os
import logging

logger = logging.getLogger(__name__)

def verify_production_config():
    """Verify all production configurations are properly set"""
    issues = []
    config_status = {}
    
    # 1. Database Configuration
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        issues.append("DATABASE_URL not set")
        config_status['database'] = 'missing'
    elif 'sqlite' in database_url.lower():
        issues.append("DATABASE_URL points to SQLite (should use PostgreSQL for production)")
        config_status['database'] = 'development'
    else:
        config_status['database'] = 'production'
        logger.info("✅ Database: PostgreSQL production database configured")
    
    # 2. API Key Configuration
    api_key_required = os.environ.get('API_KEY_REQUIRED', 'false').lower()
    api_key = os.environ.get('API_KEY')
    
    if api_key_required == 'true':
        if not api_key:
            issues.append("API_KEY_REQUIRED=true but API_KEY not set")
            config_status['api_security'] = 'broken'
        else:
            config_status['api_security'] = 'secured'
            logger.info("✅ API Security: API key protection enabled")
    else:
        config_status['api_security'] = 'open'
        logger.info("ℹ️ API Security: API key protection disabled (development mode)")
    
    # 3. OKX API Configuration
    okx_api_key = os.environ.get('OKX_API_KEY')
    okx_secret = os.environ.get('OKX_SECRET_KEY') 
    okx_passphrase = os.environ.get('OKX_PASSPHRASE')
    
    if all([okx_api_key, okx_secret, okx_passphrase]):
        config_status['okx_api'] = 'authenticated'
        logger.info("✅ OKX API: Authenticated API configured")
    else:
        missing_okx = []
        if not okx_api_key: missing_okx.append('OKX_API_KEY')
        if not okx_secret: missing_okx.append('OKX_SECRET_KEY')
        if not okx_passphrase: missing_okx.append('OKX_PASSPHRASE')
        
        issues.append(f"OKX API credentials missing: {', '.join(missing_okx)}")
        config_status['okx_api'] = 'public_only'
        logger.warning("⚠️ OKX API: Using public API only (rate limited)")
    
    # 4. OpenAI Configuration
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        config_status['openai'] = 'configured'
        logger.info("✅ OpenAI API: Configured for AI analysis")
    else:
        issues.append("OPENAI_API_KEY not set - AI features will be degraded")
        config_status['openai'] = 'missing'
    
    # 5. Telegram Configuration (optional)
    telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if telegram_token:
        config_status['telegram'] = 'configured'
        logger.info("✅ Telegram Bot: Configured for notifications")
    else:
        config_status['telegram'] = 'not_configured'
        logger.info("ℹ️ Telegram Bot: Not configured (optional)")
    
    return {
        'issues': issues,
        'config_status': config_status,
        'is_production_ready': len(issues) == 0,
        'critical_issues': len([i for i in issues if 'DATABASE_URL' in i or 'API_KEY' in i])
    }

def safe_okx_test():
    """Safely test OKX connection with production considerations"""
    try:
        from core.okx_fetcher import OKXFetcher
        
        # Test with minimal rate limit impact
        okx = OKXFetcher()
        result = okx.test_connection()
        
        if result.get('status') == 'connected':
            logger.info("✅ OKX Connection: Test successful")
            return True
        else:
            logger.warning(f"⚠️ OKX Connection: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ OKX Connection Test Failed: {e}")
        return False

def configure_for_environment(env='development'):
    """Configure system for specific environment"""
    if env == 'development':
        # Development configuration
        os.environ.setdefault('API_KEY_REQUIRED', 'false')
        logger.info("🔧 Development: API key protection disabled")
        
    elif env == 'production':
        # Production configuration
        os.environ.setdefault('API_KEY_REQUIRED', 'true')
        if not os.environ.get('API_KEY'):
            # Generate secure API key if not provided
            import secrets
            api_key = secrets.token_urlsafe(32)
            os.environ['API_KEY'] = api_key
            logger.warning(f"🔑 Production: Generated API key: {api_key}")
        
        logger.info("🔒 Production: API key protection enabled")

if __name__ == "__main__":
    print("🔍 PRODUCTION CONFIGURATION VERIFICATION")
    print("=" * 50)
    
    result = verify_production_config()
    
    print(f"\n📊 Configuration Status:")
    for component, status in result['config_status'].items():
        status_icon = {
            'production': '✅',
            'configured': '✅', 
            'authenticated': '✅',
            'secured': '✅',
            'development': '⚠️',
            'public_only': '⚠️',
            'open': '⚠️',
            'missing': '❌',
            'broken': '❌',
            'not_configured': 'ℹ️'
        }.get(status, '❓')
        
        print(f"   {status_icon} {component.upper()}: {status}")
    
    if result['issues']:
        print(f"\n❌ Configuration Issues Found:")
        for issue in result['issues']:
            print(f"   • {issue}")
    else:
        print(f"\n✅ All configurations verified successfully!")
    
    print(f"\n🎯 Production Ready: {'Yes' if result['is_production_ready'] else 'No'}")
    
    # Test OKX connection safely
    print(f"\n🧪 Testing OKX Connection...")
    okx_ok = safe_okx_test()
    
    exit_code = 0 if result['is_production_ready'] and okx_ok else 1
    print(f"\nExit Code: {exit_code}")