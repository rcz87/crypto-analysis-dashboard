"""
Stateful Signal Helper - Integration dengan existing signal engines
Helper functions untuk integrasi Stateful AI Signal Engine dengan system yang ada
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps

from services.state_manager import get_state_manager
from core.redis_manager import redis_manager

logger = logging.getLogger(__name__)


def track_signal_generation(endpoint_name: str = None):
    """
    Decorator untuk automatically track signal generation
    
    Args:
        endpoint_name: Nama endpoint yang generate signal
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute original function
                result = func(*args, **kwargs)
                
                # Extract signal data dari result jika berhasil
                if isinstance(result, tuple) and len(result) >= 1:
                    response_data = result[0].get_json() if hasattr(result[0], 'get_json') else None
                elif hasattr(result, 'get_json'):
                    response_data = result.get_json()
                else:
                    response_data = None
                
                # Track jika ada signal data
                if response_data and 'signal' in response_data:
                    try:
                        signal_data = response_data['signal']
                        signal_data['endpoint'] = endpoint_name or func.__name__
                        
                        # Get state manager dan track
                        state_manager = get_state_manager(redis_manager.redis_client)
                        signal_id = state_manager.save_signal_history(signal_data)
                        
                        # Add signal_id ke response
                        if isinstance(response_data, dict):
                            response_data['signal_id'] = signal_id
                        
                        logger.info(f"✅ Signal tracked: {signal_id} from {endpoint_name}")
                        
                    except Exception as track_error:
                        logger.warning(f"⚠️ Signal tracking failed: {track_error}")
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Function execution failed: {e}")
                raise
        
        return wrapper
    return decorator


def track_gpt_query(endpoint: str, method: str = 'POST'):
    """
    Decorator untuk automatically track GPT queries
    
    Args:
        endpoint: Nama endpoint
        method: HTTP method
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Capture request data (jika ada request context)
            try:
                from flask import request
                request_params = dict(request.args) if hasattr(request, 'args') else {}
                if hasattr(request, 'get_json'):
                    json_data = request.get_json() or {}
                    request_params.update(json_data)
            except:
                request_params = {}
            
            query_data = {
                'endpoint': endpoint,
                'method': method,
                'params': request_params,
                'user_query': request_params.get('user_query', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            try:
                # Execute original function
                result = func(*args, **kwargs)
                processing_time = int((time.time() - start_time) * 1000)
                
                # Extract response data
                if isinstance(result, tuple) and len(result) >= 1:
                    response_data = result[0].get_json() if hasattr(result[0], 'get_json') else {}
                    status_code = result[1] if len(result) > 1 else 200
                elif hasattr(result, 'get_json'):
                    response_data = result.get_json()
                    status_code = 200
                else:
                    response_data = {}
                    status_code = 200
                
                # Prepare response data untuk logging
                response_log_data = {
                    'status_code': status_code,
                    'data': response_data,
                    'processing_time_ms': processing_time,
                    'ai_model': 'GPT-4o',
                    'confidence_score': response_data.get('confidence') if isinstance(response_data, dict) else None
                }
                
                # Log query
                try:
                    state_manager = get_state_manager(redis_manager.redis_client)
                    query_id = state_manager.log_gpt_query(query_data, response_log_data)
                    
                    # Add query_id ke response jika memungkinkan
                    if isinstance(response_data, dict):
                        response_data['query_id'] = query_id
                    
                    logger.info(f"✅ GPT query tracked: {query_id} from {endpoint}")
                    
                except Exception as track_error:
                    logger.warning(f"⚠️ GPT query tracking failed: {track_error}")
                
                return result
                
            except Exception as e:
                # Log error
                processing_time = int((time.time() - start_time) * 1000)
                error_response_data = {
                    'status_code': 500,
                    'data': {'error': str(e)},
                    'processing_time_ms': processing_time,
                    'error_message': str(e)
                }
                
                try:
                    state_manager = get_state_manager(redis_manager.redis_client)
                    state_manager.log_gpt_query(query_data, error_response_data)
                except:
                    pass
                
                raise
        
        return wrapper
    return decorator


def log_user_interaction(signal_id: str, interaction_type: str, 
                        interaction_source: str, user_id: str = None,
                        additional_data: Dict = None):
    """
    Helper function untuk log user interaction
    
    Args:
        signal_id: ID signal yang di-interact
        interaction_type: Type interaction (CLICK, EXECUTE, FEEDBACK, etc.)
        interaction_source: Source (TELEGRAM, CHAT_GPT, API)
        user_id: User identifier
        additional_data: Data tambahan
    """
    try:
        interaction_data = {
            'type': interaction_type.upper(),
            'source': interaction_source.upper(),
            'data': additional_data or {},
            'user_id': user_id
        }
        
        # Get request context jika ada
        request_context = {}
        try:
            from flask import request
            request_context = {
                'user_agent': request.headers.get('User-Agent'),
                'ip_address': request.remote_addr,
                'referer': request.headers.get('Referer')
            }
        except:
            pass
        
        # Track interaction
        state_manager = get_state_manager(redis_manager.redis_client)
        interaction_id = state_manager.track_user_interaction(
            signal_id, interaction_data, request_context
        )
        
        logger.info(f"✅ User interaction tracked: {interaction_id} - {interaction_type}")
        return interaction_id
        
    except Exception as e:
        logger.error(f"❌ Failed to log user interaction: {e}")
        return None


def update_signal_outcome(signal_id: str, outcome: str, pnl_percentage: float = None):
    """
    Helper function untuk update outcome signal
    
    Args:
        signal_id: ID signal
        outcome: WIN, LOSS, BREAKEVEN
        pnl_percentage: Profit/Loss percentage
    """
    try:
        from models import SignalHistory, db
        
        signal = db.session.query(SignalHistory).filter_by(signal_id=signal_id).first()
        if signal:
            signal.outcome = outcome.upper()
            signal.pnl_percentage = pnl_percentage
            signal.closed_at = datetime.now()
            signal.updated_at = datetime.now()
            
            db.session.commit()
            
            logger.info(f"✅ Signal outcome updated: {signal_id} - {outcome}")
            return True
        else:
            logger.warning(f"⚠️ Signal not found: {signal_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to update signal outcome: {e}")
        return False


def get_signal_analytics_summary():
    """
    Helper function untuk get quick analytics summary
    
    Returns:
        Dict dengan summary analytics
    """
    try:
        state_manager = get_state_manager(redis_manager.redis_client)
        
        # Get analytics untuk berbagai periode
        daily_stats = state_manager.get_signal_performance_stats(1)
        weekly_stats = state_manager.get_signal_performance_stats(7)
        monthly_stats = state_manager.get_signal_performance_stats(30)
        
        # Get query analytics
        query_stats = state_manager.get_query_analytics(7)
        
        # Get interaction stats
        interaction_stats = state_manager.get_user_interaction_stats(7)
        
        return {
            'signals': {
                'daily': daily_stats,
                'weekly': weekly_stats,
                'monthly': monthly_stats
            },
            'queries': query_stats,
            'interactions': interaction_stats,
            'summary': {
                'total_signals_today': daily_stats.get('total_signals', 0),
                'total_signals_week': weekly_stats.get('total_signals', 0),
                'execution_rate_week': weekly_stats.get('execution_rate', 0),
                'win_rate_month': monthly_stats.get('win_rate', 0),
                'query_success_rate': query_stats.get('success_rate', 0),
                'total_interactions_week': interaction_stats.get('total_interactions', 0)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get analytics summary: {e}")
        return {}


# Redis key helpers
def get_signal_cache_key(signal_id: str) -> str:
    """Generate cache key untuk signal"""
    return f"signal:{signal_id}"


def get_analytics_cache_key(analytics_type: str, period: int) -> str:
    """Generate cache key untuk analytics"""
    return f"analytics:{analytics_type}:{period}d"


def cache_analytics_data(analytics_type: str, period: int, data: Dict, expire_seconds: int = 300):
    """
    Cache analytics data untuk performance
    
    Args:
        analytics_type: Type analytics (signals, queries, interactions)
        period: Period dalam hari
        data: Data untuk di-cache
        expire_seconds: Expiry time dalam detik
    """
    try:
        if redis_manager.redis_client:
            cache_key = get_analytics_cache_key(analytics_type, period)
            redis_manager.redis_client.setex(
                cache_key, expire_seconds, json.dumps(data)
            )
            logger.debug(f"✅ Analytics cached: {cache_key}")
    except Exception as e:
        logger.warning(f"⚠️ Failed to cache analytics: {e}")


def get_cached_analytics_data(analytics_type: str, period: int) -> Optional[Dict]:
    """
    Get cached analytics data
    
    Args:
        analytics_type: Type analytics
        period: Period dalam hari
        
    Returns:
        Cached data atau None
    """
    try:
        if redis_manager.redis_client:
            cache_key = get_analytics_cache_key(analytics_type, period)
            cached_data = redis_manager.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
    except Exception as e:
        logger.warning(f"⚠️ Failed to get cached analytics: {e}")
    
    return None


# Initialize
logger.info("🔧 Stateful Signal Helper initialized")