"""
Stateful AI Signal Engine - State Manager
Mengelola penyimpanan dan pengambilan data signal history, GPT queries, dan user interactions
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, func, and_, or_

# Import models (akan di-import dalam function untuk avoid circular import)
# from models import SignalHistory, GPTQueryLog, UserInteraction, db

logger = logging.getLogger(__name__)


class StateManager:
    """
    Mengelola state dan history untuk AI Signal Engine
    Menggunakan PostgreSQL sebagai storage utama dengan Redis untuk caching
    """
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        logger.info("🗄️ State Manager initialized")
    
    # ============================================================================
    # SIGNAL HISTORY MANAGEMENT
    # ============================================================================
    
    def save_signal_history(self, signal_data: Dict[str, Any], 
                          request_context: Optional[Dict] = None) -> str:
        """
        Menyimpan history signal yang dihasilkan AI
        
        Args:
            signal_data: Data signal dari AI engine
            request_context: Context dari request (user agent, IP, dll)
            
        Returns:
            signal_id: Unique identifier untuk signal
        """
        try:
            # Import models here untuk avoid circular import
            from models import SignalHistory, db
            
            # Generate unique signal ID
            signal_id = f"sig_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}"
            
            # Prepare SMC analysis data
            smc_data = None
            if 'smc_analysis' in signal_data:
                smc_data = json.dumps(signal_data['smc_analysis'])
            
            # Prepare technical indicators data
            tech_data = None
            if 'technical_indicators' in signal_data:
                tech_data = json.dumps(signal_data['technical_indicators'])
            
            # Create signal history record
            signal_history = SignalHistory(
                signal_id=signal_id,
                symbol=signal_data.get('symbol', '').upper(),
                timeframe=signal_data.get('timeframe', '1H'),
                action=signal_data.get('action', 'HOLD').upper(),
                confidence=float(signal_data.get('confidence', 0.0)),
                entry_price=float(signal_data.get('entry_price', 0.0)),
                take_profit=signal_data.get('take_profit'),
                stop_loss=signal_data.get('stop_loss'),
                risk_reward_ratio=signal_data.get('risk_reward_ratio'),
                ai_reasoning=signal_data.get('ai_reasoning', ''),
                smc_analysis=smc_data,
                technical_indicators=tech_data,
                market_conditions=signal_data.get('market_conditions', 'UNKNOWN'),
                user_agent=request_context.get('user_agent') if request_context else None,
                ip_address=request_context.get('ip_address') if request_context else None
            )
            
            # Save to database
            db.session.add(signal_history)
            db.session.commit()
            
            # Cache in Redis (jika tersedia)
            if self.redis_client:
                try:
                    cache_key = f"signal:{signal_id}"
                    cache_data = signal_history.to_dict()
                    self.redis_client.setex(cache_key, 3600, json.dumps(cache_data))
                except Exception as redis_error:
                    logger.warning(f"Redis cache failed: {redis_error}")
            
            logger.info(f"✅ Signal history saved: {signal_id} - {signal_data.get('symbol')} {signal_data.get('action')}")
            return signal_id
            
        except Exception as e:
            logger.error(f"❌ Failed to save signal history: {e}")
            db.session.rollback()
            raise
    
    def get_signal_history(self, limit: int = 50, symbol: Optional[str] = None,
                         timeframe: Optional[str] = None, 
                         date_from: Optional[datetime] = None) -> List[Dict]:
        """
        Mengambil history signal dengan filter
        
        Args:
            limit: Jumlah maximum records
            symbol: Filter by trading pair
            timeframe: Filter by timeframe
            date_from: Filter from date
            
        Returns:
            List of signal history records
        """
        try:
            from models import SignalHistory, db
            query = db.session.query(SignalHistory)
            
            # Apply filters
            if symbol:
                query = query.filter(SignalHistory.symbol == symbol.upper())
            if timeframe:
                query = query.filter(SignalHistory.timeframe == timeframe)
            if date_from:
                query = query.filter(SignalHistory.created_at >= date_from)
            
            # Order by created_at descending and limit
            signals = query.order_by(desc(SignalHistory.created_at)).limit(limit).all()
            
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logger.error(f"❌ Failed to get signal history: {e}")
            return []
    
    def update_signal_execution(self, signal_id: str, execution_data: Dict[str, Any]) -> bool:
        """
        Update signal ketika dieksekusi oleh user
        
        Args:
            signal_id: ID signal yang dieksekusi
            execution_data: Data eksekusi (price, source, dll)
            
        Returns:
            True jika berhasil update
        """
        try:
            from models import SignalHistory, db
            signal = db.session.query(SignalHistory).filter_by(signal_id=signal_id).first()
            if not signal:
                logger.warning(f"Signal not found: {signal_id}")
                return False
            
            # Update execution data
            signal.is_executed = True
            signal.executed_at = datetime.now()
            signal.execution_price = execution_data.get('execution_price')
            signal.execution_source = execution_data.get('source', 'UNKNOWN')
            
            db.session.commit()
            
            # Update cache
            if self.redis_client:
                try:
                    cache_key = f"signal:{signal_id}"
                    self.redis_client.delete(cache_key)
                except Exception:
                    pass
            
            logger.info(f"✅ Signal execution updated: {signal_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update signal execution: {e}")
            db.session.rollback()
            return False
    
    # ============================================================================
    # GPT QUERY LOGGING
    # ============================================================================
    
    def log_gpt_query(self, query_data: Dict[str, Any], 
                     response_data: Dict[str, Any],
                     request_context: Optional[Dict] = None) -> str:
        """
        Log query dan response GPT untuk analytics
        
        Args:
            query_data: Data request/query
            response_data: Data response dari AI
            request_context: Context request
            
        Returns:
            query_id: Unique identifier untuk query log
        """
        try:
            from models import GPTQueryLog, db
            
            # Generate unique query ID
            query_id = f"qry_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}"
            
            # Create query log record
            query_log = GPTQueryLog(
                query_id=query_id,
                endpoint=query_data.get('endpoint', '/unknown'),
                method=query_data.get('method', 'GET'),
                request_params=json.dumps(query_data.get('params', {})),
                user_query=query_data.get('user_query', ''),
                response_status=response_data.get('status_code', 200),
                response_data=json.dumps(response_data.get('data', {})),
                processing_time_ms=response_data.get('processing_time_ms', 0),
                ai_model_used=response_data.get('ai_model', 'GPT-4o'),
                tokens_used=response_data.get('tokens_used'),
                ai_reasoning_time_ms=response_data.get('ai_reasoning_time_ms'),
                confidence_score=response_data.get('confidence_score'),
                user_agent=request_context.get('user_agent') if request_context else None,
                ip_address=request_context.get('ip_address') if request_context else None,
                session_id=request_context.get('session_id') if request_context else None,
                referer=request_context.get('referer') if request_context else None,
                is_successful=response_data.get('status_code', 200) < 400,
                error_message=response_data.get('error_message')
            )
            
            # Save to database
            db.session.add(query_log)
            db.session.commit()
            
            logger.info(f"✅ GPT query logged: {query_id} - {query_data.get('endpoint')}")
            return query_id
            
        except Exception as e:
            logger.error(f"❌ Failed to log GPT query: {e}")
            db.session.rollback()
            raise
    
    def get_query_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Ambil analytics untuk GPT queries
        
        Args:
            days: Jumlah hari untuk analytics
            
        Returns:
            Dictionary dengan analytics data
        """
        try:
            from models import GPTQueryLog, db
            date_from = datetime.now() - timedelta(days=days)
            
            # Basic stats
            total_queries = db.session.query(GPTQueryLog).filter(
                GPTQueryLog.created_at >= date_from
            ).count()
            
            successful_queries = db.session.query(GPTQueryLog).filter(
                and_(GPTQueryLog.created_at >= date_from, GPTQueryLog.is_successful == True)
            ).count()
            
            # Average processing time
            avg_processing_time = db.session.query(
                func.avg(GPTQueryLog.processing_time_ms)
            ).filter(GPTQueryLog.created_at >= date_from).scalar() or 0
            
            # Top endpoints
            top_endpoints = db.session.query(
                GPTQueryLog.endpoint,
                func.count(GPTQueryLog.id).label('count')
            ).filter(
                GPTQueryLog.created_at >= date_from
            ).group_by(GPTQueryLog.endpoint).order_by(desc('count')).limit(10).all()
            
            # Success rate
            success_rate = (successful_queries / total_queries * 100) if total_queries > 0 else 0
            
            return {
                'period_days': days,
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': round(success_rate, 2),
                'avg_processing_time_ms': round(avg_processing_time, 2),
                'top_endpoints': [
                    {'endpoint': endpoint, 'count': count} 
                    for endpoint, count in top_endpoints
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get query analytics: {e}")
            return {}
    
    # ============================================================================
    # USER INTERACTION TRACKING
    # ============================================================================
    
    def track_user_interaction(self, signal_id: str, interaction_data: Dict[str, Any],
                             request_context: Optional[Dict] = None) -> str:
        """
        Track user interaction dengan signal (click, execute, feedback)
        
        Args:
            signal_id: ID signal yang di-interact
            interaction_data: Data interaction
            request_context: Context request
            
        Returns:
            interaction_id: Unique identifier untuk interaction
        """
        try:
            from models import UserInteraction, db
            
            # Generate unique interaction ID
            interaction_id = f"int_{uuid.uuid4().hex[:12]}_{int(datetime.now().timestamp())}"
            
            # Create interaction record
            interaction = UserInteraction(
                interaction_id=interaction_id,
                signal_id=signal_id,
                interaction_type=interaction_data.get('type', 'UNKNOWN').upper(),
                interaction_source=interaction_data.get('source', 'UNKNOWN').upper(),
                interaction_data=json.dumps(interaction_data.get('data', {})),
                user_id=interaction_data.get('user_id'),
                user_agent=request_context.get('user_agent') if request_context else None,
                ip_address=request_context.get('ip_address') if request_context else None
            )
            
            # Save to database
            db.session.add(interaction)
            db.session.commit()
            
            logger.info(f"✅ User interaction tracked: {interaction_id} - {interaction_data.get('type')}")
            return interaction_id
            
        except Exception as e:
            logger.error(f"❌ Failed to track user interaction: {e}")
            db.session.rollback()
            raise
    
    # ============================================================================
    # ANALYTICS & REPORTING
    # ============================================================================
    
    def get_signal_performance_stats(self, days: int = 30) -> Dict[str, Any]:
        """
        Ambil statistik performance signal
        
        Args:
            days: Jumlah hari untuk analisis
            
        Returns:
            Dictionary dengan performance stats
        """
        try:
            from models import SignalHistory, db
            date_from = datetime.now() - timedelta(days=days)
            
            # Total signals generated
            total_signals = db.session.query(SignalHistory).filter(
                SignalHistory.created_at >= date_from
            ).count()
            
            # Executed signals
            executed_signals = db.session.query(SignalHistory).filter(
                and_(
                    SignalHistory.created_at >= date_from,
                    SignalHistory.is_executed == True
                )
            ).count()
            
            # Win rate (jika ada outcome data)
            winning_signals = db.session.query(SignalHistory).filter(
                and_(
                    SignalHistory.created_at >= date_from,
                    SignalHistory.outcome == 'WIN'
                )
            ).count()
            
            closed_signals = db.session.query(SignalHistory).filter(
                and_(
                    SignalHistory.created_at >= date_from,
                    SignalHistory.outcome.in_(['WIN', 'LOSS'])
                )
            ).count()
            
            # Top performing symbols
            top_symbols = db.session.query(
                SignalHistory.symbol,
                func.count(SignalHistory.id).label('count'),
                func.avg(SignalHistory.confidence).label('avg_confidence')
            ).filter(
                SignalHistory.created_at >= date_from
            ).group_by(SignalHistory.symbol).order_by(desc('count')).limit(10).all()
            
            # Execution rate
            execution_rate = (executed_signals / total_signals * 100) if total_signals > 0 else 0
            
            # Win rate
            win_rate = (winning_signals / closed_signals * 100) if closed_signals > 0 else 0
            
            return {
                'period_days': days,
                'total_signals': total_signals,
                'executed_signals': executed_signals,
                'execution_rate': round(execution_rate, 2),
                'winning_signals': winning_signals,
                'closed_signals': closed_signals,
                'win_rate': round(win_rate, 2),
                'top_symbols': [
                    {
                        'symbol': symbol, 
                        'count': count, 
                        'avg_confidence': round(float(avg_confidence), 2)
                    } 
                    for symbol, count, avg_confidence in top_symbols
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get signal performance stats: {e}")
            return {}
    
    def get_user_interaction_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Ambil statistik user interaction
        
        Args:
            days: Jumlah hari untuk analisis
            
        Returns:
            Dictionary dengan interaction stats
        """
        try:
            from models import UserInteraction, db
            date_from = datetime.now() - timedelta(days=days)
            
            # Total interactions
            total_interactions = db.session.query(UserInteraction).filter(
                UserInteraction.created_at >= date_from
            ).count()
            
            # Interaction by type
            interaction_types = db.session.query(
                UserInteraction.interaction_type,
                func.count(UserInteraction.id).label('count')
            ).filter(
                UserInteraction.created_at >= date_from
            ).group_by(UserInteraction.interaction_type).all()
            
            # Interaction by source
            interaction_sources = db.session.query(
                UserInteraction.interaction_source,
                func.count(UserInteraction.id).label('count')
            ).filter(
                UserInteraction.created_at >= date_from
            ).group_by(UserInteraction.interaction_source).all()
            
            return {
                'period_days': days,
                'total_interactions': total_interactions,
                'by_type': [
                    {'type': int_type, 'count': count} 
                    for int_type, count in interaction_types
                ],
                'by_source': [
                    {'source': source, 'count': count} 
                    for source, count in interaction_sources
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user interaction stats: {e}")
            return {}
    
    # ============================================================================
    # CLEANUP & MAINTENANCE
    # ============================================================================
    
    def cleanup_old_data(self, days_to_keep: int = 90) -> Dict[str, int]:
        """
        Bersihkan data lama untuk maintenance
        
        Args:
            days_to_keep: Jumlah hari data yang dipertahankan
            
        Returns:
            Dictionary dengan jumlah records yang dihapus
        """
        try:
            from models import SignalHistory, GPTQueryLog, UserInteraction, db
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # Delete old signal history
            deleted_signals = db.session.query(SignalHistory).filter(
                SignalHistory.created_at < cutoff_date
            ).delete()
            
            # Delete old query logs
            deleted_queries = db.session.query(GPTQueryLog).filter(
                GPTQueryLog.created_at < cutoff_date
            ).delete()
            
            # Delete old interactions
            deleted_interactions = db.session.query(UserInteraction).filter(
                UserInteraction.created_at < cutoff_date
            ).delete()
            
            db.session.commit()
            
            logger.info(f"✅ Cleanup completed: {deleted_signals} signals, {deleted_queries} queries, {deleted_interactions} interactions")
            
            return {
                'deleted_signals': deleted_signals,
                'deleted_queries': deleted_queries,
                'deleted_interactions': deleted_interactions,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old data: {e}")
            db.session.rollback()
            return {}


# Singleton instance
state_manager = None


def get_state_manager(redis_client=None) -> StateManager:
    """
    Get singleton instance of StateManager
    
    Args:
        redis_client: Optional Redis client for caching
        
    Returns:
        StateManager instance
    """
    global state_manager
    if state_manager is None:
        state_manager = StateManager(redis_client)
    return state_manager