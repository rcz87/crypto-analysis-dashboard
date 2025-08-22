"""
API Versioning and Stability Management
Implements versioning with backwards compatibility and deprecation notices
"""

from flask import Blueprint, request, jsonify, redirect, url_for
from flask_cors import cross_origin
from functools import wraps
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

# Create versioned blueprints
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')

# Deprecation tracking
DEPRECATED_ENDPOINTS = {
    '/api/signal': {
        'new_endpoint': '/api/v2/signals/generate',
        'deprecated_date': '2025-08-01',
        'sunset_date': '2026-02-01',
        'message': 'This endpoint is deprecated. Please use /api/v2/signals/generate'
    }
}

# Endpoint aliases for backward compatibility
ENDPOINT_ALIASES = {
    # Old endpoint -> New endpoint mapping
    '/api/signal': '/api/v2/signals/generate',
    '/api/signal/generate': '/api/v2/signals/generate',
    '/api/signal/advanced': '/api/v2/signals/advanced',
    '/api/smc/analysis': '/api/v2/smc/analyze',
    '/api/indicators/all': '/api/v2/technical/indicators',
    '/api/market/candles': '/api/v2/market-data/candles',
    '/api/risk/portfolio': '/api/v2/risk-management/portfolio'
}

class APIVersionManager:
    """
    Manages API versioning, deprecation, and backward compatibility
    """
    
    def __init__(self):
        self.version_history = {
            'v1': {
                'released': '2024-01-01',
                'status': 'stable',
                'description': 'Initial API version',
                'supported': True
            },
            'v2': {
                'released': '2025-08-22',
                'status': 'current',
                'description': 'Enhanced API with improved structure',
                'supported': True
            }
        }
        self.logger = logging.getLogger(f"{__name__}.APIVersionManager")
        self.logger.info("📌 API Version Manager initialized - Ensuring endpoint stability")
    
    def deprecation_warning(self, func: Callable) -> Callable:
        """Decorator to add deprecation warnings to responses"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            
            # Add deprecation headers
            if hasattr(response, 'headers'):
                endpoint = request.path
                if endpoint in DEPRECATED_ENDPOINTS:
                    dep_info = DEPRECATED_ENDPOINTS[endpoint]
                    response.headers['X-Deprecated'] = 'true'
                    response.headers['X-Sunset-Date'] = dep_info['sunset_date']
                    response.headers['X-Alternative-Endpoint'] = dep_info['new_endpoint']
                    
                    # Add warning to JSON response if applicable
                    if response.content_type == 'application/json':
                        data = response.get_json()
                        if isinstance(data, dict):
                            data['_deprecation_warning'] = {
                                'message': dep_info['message'],
                                'sunset_date': dep_info['sunset_date'],
                                'alternative': dep_info['new_endpoint']
                            }
            
            return response
        return wrapper
    
    def create_alias(self, old_endpoint: str, new_endpoint: str) -> Callable:
        """Create an alias that redirects to new endpoint"""
        def alias_handler(*args, **kwargs):
            # Log the usage for monitoring
            self.logger.info(f"Alias used: {old_endpoint} -> {new_endpoint}")
            
            # Add deprecation notice
            response_data = {
                '_notice': f'This endpoint has moved to {new_endpoint}',
                '_redirect': new_endpoint
            }
            
            # Redirect with 308 Permanent Redirect
            return redirect(new_endpoint, code=308)
        
        return alias_handler
    
    def version_selector(self, versions: Dict[str, Callable]) -> Callable:
        """Select appropriate version handler based on request"""
        def handler(*args, **kwargs):
            # Detect requested version
            requested_version = request.headers.get('X-API-Version', 'v2')
            
            # Check if version is supported
            if requested_version not in versions:
                return jsonify({
                    'error': f'API version {requested_version} not supported',
                    'supported_versions': list(versions.keys())
                }), 400
            
            # Execute appropriate version handler
            return versions[requested_version](*args, **kwargs)
        
        return handler

# Initialize version manager
version_manager = APIVersionManager()

# ============= V2 ENDPOINTS (Current) =============

@api_v2.route('/signals/generate', methods=['GET', 'POST'])
@cross_origin()
def v2_generate_signal():
    """V2: Generate trading signal with enhanced features"""
    return jsonify({
        'version': 'v2',
        'endpoint': '/api/v2/signals/generate',
        'status': 'active',
        'data': {
            'signal': 'BUY',
            'confidence': 85,
            'features': ['Enhanced SMC', 'Multi-timeframe', 'Risk Management']
        }
    })

@api_v2.route('/smc/analyze', methods=['GET', 'POST'])
@cross_origin()
def v2_smc_analysis():
    """V2: SMC analysis with advanced features"""
    return jsonify({
        'version': 'v2',
        'endpoint': '/api/v2/smc/analyze',
        'status': 'active',
        'data': {
            'analysis': 'Advanced SMC with CHoCH, FVG, Liquidity'
        }
    })

@api_v2.route('/risk-management/profile', methods=['GET', 'POST'])
@cross_origin()
def v2_risk_profile():
    """V2: Personalized risk profile management"""
    from core.personalized_risk_profiles import PersonalizedRiskProfiles
    
    try:
        # Get parameters
        data = request.get_json() if request.method == 'POST' else {}
        profile = data.get('profile', request.args.get('profile', 'MODERATE'))
        account_balance = float(data.get('account_balance', request.args.get('account_balance', 10000)))
        
        # Initialize risk profiler
        risk_profiler = PersonalizedRiskProfiles(profile, account_balance)
        
        # Get profile summary
        summary = risk_profiler.get_profile_summary()
        
        return jsonify({
            'version': 'v2',
            'endpoint': '/api/v2/risk-management/profile',
            'profile': summary
        })
        
    except Exception as e:
        return jsonify({
            'version': 'v2',
            'error': str(e)
        }), 500

@api_v2.route('/technical/indicators', methods=['GET'])
@cross_origin()
def v2_technical_indicators():
    """V2: Technical indicators with enhanced calculations"""
    return jsonify({
        'version': 'v2',
        'endpoint': '/api/v2/technical/indicators',
        'status': 'active',
        'indicators': ['RSI', 'MACD', 'Bollinger', 'ATR', 'VWAP']
    })

@api_v2.route('/market-data/candles', methods=['GET'])
@cross_origin()
def v2_market_candles():
    """V2: Market candle data with improved structure"""
    return jsonify({
        'version': 'v2',
        'endpoint': '/api/v2/market-data/candles',
        'status': 'active',
        'format': 'OHLCV with metadata'
    })

# ============= V1 ENDPOINTS (Legacy with warnings) =============

@api_v1.route('/signal', methods=['GET', 'POST'])
@cross_origin()
@version_manager.deprecation_warning
def v1_signal():
    """V1: Legacy signal endpoint (deprecated)"""
    return jsonify({
        'version': 'v1',
        'endpoint': '/api/v1/signal',
        'status': 'deprecated',
        'data': {
            'signal': 'BUY',
            'confidence': 75
        },
        '_deprecation': {
            'message': 'Please migrate to /api/v2/signals/generate',
            'sunset_date': '2026-02-01'
        }
    })

# ============= Versioning Information Endpoints =============

@api_v2.route('/version', methods=['GET'])
@cross_origin()
def api_version_info():
    """Get API version information"""
    return jsonify({
        'current_version': 'v2',
        'available_versions': ['v1', 'v2'],
        'deprecation_schedule': DEPRECATED_ENDPOINTS,
        'migration_guide': 'https://docs.api.example.com/migration',
        'changelog': 'https://docs.api.example.com/changelog'
    })

@api_v2.route('/endpoints', methods=['GET'])
@cross_origin()
def list_endpoints():
    """List all available endpoints with their versions"""
    endpoints = {
        'v2': {
            'signals': [
                '/api/v2/signals/generate',
                '/api/v2/signals/advanced',
                '/api/v2/signals/backtest'
            ],
            'smc': [
                '/api/v2/smc/analyze',
                '/api/v2/smc/order-blocks',
                '/api/v2/smc/liquidity'
            ],
            'risk_management': [
                '/api/v2/risk-management/profile',
                '/api/v2/risk-management/calculate',
                '/api/v2/risk-management/portfolio'
            ],
            'market_data': [
                '/api/v2/market-data/candles',
                '/api/v2/market-data/orderbook',
                '/api/v2/market-data/trades'
            ],
            'technical': [
                '/api/v2/technical/indicators',
                '/api/v2/technical/patterns',
                '/api/v2/technical/analysis'
            ]
        },
        'v1': {
            'status': 'deprecated',
            'sunset_date': '2026-02-01',
            'endpoints': list(DEPRECATED_ENDPOINTS.keys())
        }
    }
    
    return jsonify(endpoints)

# ============= Backward Compatibility Handlers =============

def setup_backward_compatibility(app):
    """Setup backward compatibility routes"""
    
    # Create unique handler for each endpoint
    def create_compatibility_handler(old_path, new_path):
        def handler():
            # Log for monitoring
            logger.info(f"Backward compatibility: {old_path} -> {new_path}")
            
            # Return deprecation notice with data
            return jsonify({
                'data': {'message': 'Please update to new endpoint'},
                '_compatibility': {
                    'old_endpoint': old_path,
                    'new_endpoint': new_path,
                    'deprecation_date': '2025-08-22',
                    'sunset_date': '2026-02-01'
                }
            }), 301
        return handler
    
    # Create aliases for old endpoints
    for old_endpoint, new_endpoint in ENDPOINT_ALIASES.items():
        handler = create_compatibility_handler(old_endpoint, new_endpoint)
        handler.__name__ = f"compat_{old_endpoint.replace('/', '_')}"
        app.add_url_rule(old_endpoint, endpoint=handler.__name__, 
                        view_func=handler, methods=['GET', 'POST'])
    
    logger.info(f"✅ Backward compatibility setup for {len(ENDPOINT_ALIASES)} endpoints")

# ============= Deprecation Monitor =============

class DeprecationMonitor:
    """Monitor and report on deprecated endpoint usage"""
    
    def __init__(self):
        self.usage_stats = {}
    
    def track_usage(self, endpoint: str):
        """Track usage of deprecated endpoints"""
        if endpoint not in self.usage_stats:
            self.usage_stats[endpoint] = {
                'count': 0,
                'last_used': None,
                'first_used': datetime.now()
            }
        
        self.usage_stats[endpoint]['count'] += 1
        self.usage_stats[endpoint]['last_used'] = datetime.now()
    
    def get_report(self) -> Dict[str, Any]:
        """Get deprecation usage report"""
        return {
            'deprecated_endpoint_usage': self.usage_stats,
            'total_deprecated_calls': sum(s['count'] for s in self.usage_stats.values()),
            'most_used_deprecated': max(self.usage_stats.items(), 
                                      key=lambda x: x[1]['count'])[0] if self.usage_stats else None
        }

# Initialize deprecation monitor
deprecation_monitor = DeprecationMonitor()