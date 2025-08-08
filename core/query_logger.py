"""
GPT Query Logger
Utility untuk log dan track semua interaksi GPTs
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from flask import request, g
from functools import wraps

from models import GPTQueryLog, db
from core.redis_manager import redis_manager

logger = logging.getLogger(__name__)

class QueryLogger:
    """
    Service untuk logging dan tracking GPT queries
    """
    
    def __init__(self):
        self.redis_client = redis_manager.redis_client
        logger.info("🔍 GPT Query Logger initialized")
    
    def log_query(self, query_text: str, response_text: str = None, 
                  source: str = 'gpts', endpoint: str = None,
                  processing_time_ms: float = None, **kwargs) -> str:
        """
        Log query ke database
        
        Args:
            query_text: Original query text
            response_text: Response yang dikirim
            source: Source dari query (gpts, telegram, api)
            endpoint: Endpoint yang dipanggil
            processing_time_ms: Waktu processing
            **kwargs: Additional metadata
            
        Returns:
            query_id: ID dari log entry
        """
        try:
            # Extract additional info from kwargs
            confidence_score = kwargs.get('confidence_score')
            query_category = kwargs.get('query_category', self._categorize_query(query_text))
            user_id = kwargs.get('user_id')
            session_id = kwargs.get('session_id')
            gpt_model = kwargs.get('gpt_model', 'GPT-4o')
            tokens_used = kwargs.get('tokens_used')
            metadata = kwargs.get('metadata', {})
            
            # Create log entry with correct field mapping
            query_log = GPTQueryLog(
                query_id=f"qry_{int(datetime.utcnow().timestamp() * 1000)}",
                endpoint=endpoint or '/api/gpts/unknown',
                method=getattr(request, 'method', 'POST') if request else 'POST',
                request_params=json.dumps(metadata) if metadata else None,
                user_query=query_text,
                response_status=kwargs.get('response_status', 200),
                response_data=response_text,
                processing_time_ms=int(processing_time_ms) if processing_time_ms else None,
                ai_model_used=gpt_model,
                tokens_used=tokens_used,
                confidence_score=confidence_score,
                session_id=session_id
            )
            
            db.session.add(query_log)
            db.session.commit()
            
            logger.info(f"✅ Query logged: {query_log.id} - {source} - {query_category}")
            
            # Invalidate related cache
            self._invalidate_analytics_cache()
            
            return str(query_log.id)
            
        except Exception as e:
            logger.error(f"❌ Failed to log query: {e}")
            db.session.rollback()
            raise
    
    def get_query_history(self, limit: int = 50, source: str = None, 
                         days: int = 7, category: str = None) -> List[Dict]:
        """
        Get query history dengan filter
        
        Args:
            limit: Max records to return
            source: Filter by source
            days: Filter by days
            category: Filter by category
            
        Returns:
            List of query logs
        """
        try:
            query = db.session.query(GPTQueryLog)
            
            # Apply time filter
            if days:
                date_from = datetime.utcnow() - timedelta(days=days)
                query = query.filter(GPTQueryLog.created_at >= date_from)
            
            # Category filter would need to be added to model in future
            # if category:
            #     query = query.filter(GPTQueryLog.query_category == category)
            
            # Order and limit
            query = query.order_by(GPTQueryLog.created_at.desc()).limit(limit)
            
            results = query.all()
            
            return [log.to_dict() for log in results]
            
        except Exception as e:
            logger.error(f"❌ Failed to get query history: {e}")
            return []
    
    def get_query_analytics(self, days: int = 7, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get analytics untuk queries
        
        Args:
            days: Time period in days
            use_cache: Whether to use cached results
            
        Returns:
            Analytics data
        """
        cache_key = f"query_analytics_{days}d"
        
        # Try cache first
        if use_cache:
            cached_data = self._get_cached_analytics('queries', f"{days}d")
            if cached_data:
                return cached_data
        
        try:
            date_from = datetime.utcnow() - timedelta(days=days)
            
            # Basic stats
            total_queries = db.session.query(GPTQueryLog).filter(
                GPTQueryLog.created_at >= date_from
            ).count()
            
            successful_queries = db.session.query(GPTQueryLog).filter(
                GPTQueryLog.created_at >= date_from,
                GPTQueryLog.response_status < 400
            ).count()
            
            # Success rate
            success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
            
            # Average processing time
            avg_processing_time = db.session.query(
                db.func.avg(GPTQueryLog.processing_time_ms)
            ).filter(
                GPTQueryLog.created_at >= date_from,
                GPTQueryLog.processing_time_ms.isnot(None)
            ).scalar() or 0
            
            # Top sources (using endpoint as source indicator)
            top_sources = db.session.query(
                GPTQueryLog.endpoint,
                db.func.count(GPTQueryLog.id).label('count')
            ).filter(
                GPTQueryLog.created_at >= date_from
            ).group_by(GPTQueryLog.endpoint).order_by(
                db.func.count(GPTQueryLog.id).desc()
            ).limit(10).all()
            
            # Top categories (using endpoint as category proxy)
            top_categories = db.session.query(
                GPTQueryLog.endpoint,
                db.func.count(GPTQueryLog.id).label('count')
            ).filter(
                GPTQueryLog.created_at >= date_from,
                GPTQueryLog.endpoint.isnot(None)
            ).group_by(GPTQueryLog.endpoint).order_by(
                db.func.count(GPTQueryLog.id).desc()
            ).limit(10).all()
            
            # Top endpoints
            top_endpoints = db.session.query(
                GPTQueryLog.endpoint,
                db.func.count(GPTQueryLog.id).label('count')
            ).filter(
                GPTQueryLog.created_at >= date_from,
                GPTQueryLog.endpoint.isnot(None)
            ).group_by(GPTQueryLog.endpoint).order_by(
                db.func.count(GPTQueryLog.id).desc()
            ).limit(10).all()
            
            # Daily stats
            daily_stats = db.session.query(
                db.func.date(GPTQueryLog.created_at).label('date'),
                db.func.count(GPTQueryLog.id).label('count')
            ).filter(
                GPTQueryLog.created_at >= date_from
            ).group_by(
                db.func.date(GPTQueryLog.created_at)
            ).order_by('date').all()
            
            analytics_data = {
                'period_days': days,
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': round(success_rate, 2),
                'avg_processing_time_ms': round(float(avg_processing_time), 2),
                'top_sources': [{'source': s[0] or 'unknown', 'count': s[1]} for s in top_sources],
                'top_categories': [{'category': c[0], 'count': c[1]} for c in top_categories],
                'top_endpoints': [{'endpoint': e[0], 'count': e[1]} for e in top_endpoints],
                'daily_stats': [{'date': str(d[0]), 'count': d[1]} for d in daily_stats]
            }
            
            # Cache results
            if use_cache:
                self._cache_analytics('queries', f"{days}d", analytics_data)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get query analytics: {e}")
            return {'error': str(e)}
    
    def _categorize_query(self, query_text: str) -> str:
        """
        Categorize query berdasarkan content
        
        Args:
            query_text: Query text
            
        Returns:
            Category string
        """
        query_lower = query_text.lower()
        
        if any(word in query_lower for word in ['signal', 'trading', 'buy', 'sell']):
            return 'signal'
        elif any(word in query_lower for word in ['chart', 'price', 'ohlc', 'candle']):
            return 'chart'
        elif any(word in query_lower for word in ['analysis', 'analyze', 'technical', 'smc']):
            return 'analysis'
        elif any(word in query_lower for word in ['narrative', 'story', 'market']):
            return 'narrative'
        elif any(word in query_lower for word in ['status', 'health', 'ping']):
            return 'status'
        elif any(word in query_lower for word in ['risk', 'position', 'calculate']):
            return 'risk'
        else:
            return 'other'
    
    def _get_cached_analytics(self, analytics_type: str, time_period: str) -> Optional[Dict]:
        """Get cached analytics data using Redis"""
        try:
            cache_key = f"analytics:{analytics_type}:{time_period}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"📊 Using cached analytics: {analytics_type} - {time_period}")
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get cached analytics: {e}")
            return None
    
    def _cache_analytics(self, analytics_type: str, time_period: str, 
                        data: Dict, expire_minutes: int = 15):
        """Cache analytics data using Redis"""
        try:
            cache_key = f"analytics:{analytics_type}:{time_period}"
            expire_seconds = expire_minutes * 60
            
            self.redis_client.setex(
                cache_key, 
                expire_seconds, 
                json.dumps(data)
            )
            
            logger.info(f"💾 Analytics cached: {analytics_type} - {time_period}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cache analytics: {e}")
    
    def _invalidate_analytics_cache(self):
        """Invalidate all analytics cache"""
        try:
            # Pattern match for analytics keys
            pattern = "analytics:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"🗑️ Invalidated {len(keys)} analytics cache entries")
            
        except Exception as e:
            logger.error(f"❌ Failed to invalidate cache: {e}")

# Decorator untuk automatic query logging
def log_gpt_query(source: str = 'gpts', category: str = None):
    """
    Decorator untuk automatic logging of GPT queries
    
    Args:
        source: Source of the query
        category: Category of the query
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = datetime.utcnow()
            
            try:
                # Execute the function
                result = f(*args, **kwargs)
                
                # Calculate processing time
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Extract query info from request
                query_text = ""
                if request:
                    if request.method == 'POST' and request.json:
                        query_text = str(request.json)
                    elif request.method == 'GET':
                        query_text = str(request.args)
                
                # Extract confidence from result if available
                confidence_score = None
                if hasattr(result, 'json') and result.json:
                    confidence_score = result.json.get('confidence')
                
                # Log the query
                query_logger = QueryLogger()
                query_logger.log_query(
                    query_text=query_text,
                    response_text=str(result.data) if hasattr(result, 'data') else None,
                    source=source,
                    endpoint=request.endpoint if request else None,
                    processing_time_ms=processing_time,
                    query_category=category or query_logger._categorize_query(query_text),
                    confidence_score=confidence_score,
                    is_successful=True
                )
                
                return result
                
            except Exception as e:
                # Log failed query
                processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                query_logger = QueryLogger()
                query_logger.log_query(
                    query_text=str(request.json) if request and request.json else "",
                    response_text=str(e),
                    source=source,
                    endpoint=request.endpoint if request else None,
                    processing_time_ms=processing_time,
                    query_category=category,
                    is_successful=False,
                    response_status=500
                )
                
                raise
        
        return decorated_function
    return decorator

# Singleton instance
query_logger_instance = None

def get_query_logger() -> QueryLogger:
    """Get singleton instance of QueryLogger"""
    global query_logger_instance
    if query_logger_instance is None:
        query_logger_instance = QueryLogger()
    return query_logger_instance

logger.info("🔍 GPT Query Logger module loaded")