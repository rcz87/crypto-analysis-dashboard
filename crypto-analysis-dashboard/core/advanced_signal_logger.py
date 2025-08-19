#!/usr/bin/env python3
"""
💾 Advanced Signal Logging System - Auto-Track & Audit All Signals
Sistem otomatis untuk melacak setiap sinyal yang tereksekusi
"""

import os
import logging
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import threading
from queue import Queue, Empty

logger = logging.getLogger(__name__)

@dataclass
class SignalExecution:
    """Data class untuk signal execution tracking"""
    signal_id: str
    symbol: str
    timeframe: str
    action: str  # BUY, SELL, HOLD
    entry_price: float
    take_profit: Optional[float]
    stop_loss: Optional[float]
    confidence: float
    reasoning: str
    source: str  # GPT, AGENT, MANUAL
    user_agent: Optional[str]
    ip_address: Optional[str]
    executed_at: str
    correlation_id: str  # Link to original GPT query
    risk_level: str  # LOW, MEDIUM, HIGH
    market_conditions: Dict[str, Any]
    technical_indicators: Dict[str, Any]

class AdvancedSignalLogger:
    """
    💾 Advanced Signal Logger untuk tracking semua signal executions
    
    Features:
    - Real-time signal logging ke database
    - Audit trail untuk compliance
    - Performance tracking
    - Error detection dan alerting
    - Data integrity validation
    """
    
    def __init__(self, db_session=None, redis_manager=None):
        """Initialize Advanced Signal Logger"""
        self.db_session = db_session
        self.redis_manager = redis_manager
        self.log_queue = Queue()
        self.processing_thread = None
        self.is_running = False
        
        # Start background processing
        self._start_background_processor()
        
        logger.info("💾 Advanced Signal Logger initialized")
    
    def log_signal_execution(self, signal_data: Dict[str, Any], execution_context: Dict[str, Any] = None) -> str:
        """
        Log signal execution dengan comprehensive tracking
        
        Args:
            signal_data: Complete signal information
            execution_context: Additional context (user, IP, etc.)
            
        Returns:
            execution_id: Unique execution tracking ID
        """
        try:
            # Generate unique execution ID
            execution_id = self._generate_execution_id(signal_data)
            
            # Create execution record
            execution = SignalExecution(
                signal_id=signal_data.get('signal_id', execution_id),
                symbol=signal_data['symbol'],
                timeframe=signal_data['timeframe'],
                action=signal_data['action'],
                entry_price=float(signal_data['entry_price']),
                take_profit=signal_data.get('take_profit'),
                stop_loss=signal_data.get('stop_loss'),
                confidence=float(signal_data['confidence']),
                reasoning=signal_data.get('reasoning', ''),
                source=signal_data.get('source', 'UNKNOWN'),
                user_agent=execution_context.get('user_agent') if execution_context else None,
                ip_address=execution_context.get('ip_address') if execution_context else None,
                executed_at=datetime.now(timezone.utc).isoformat(),
                correlation_id=signal_data.get('correlation_id', ''),
                risk_level=self._calculate_risk_level(signal_data),
                market_conditions=signal_data.get('market_conditions', {}),
                technical_indicators=signal_data.get('technical_indicators', {})
            )
            
            # Queue for background processing
            self.log_queue.put({
                'type': 'SIGNAL_EXECUTION',
                'data': execution,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Immediate cache for quick access
            if self.redis_manager:
                cache_key = f"signal_execution:{execution_id}"
                self.redis_manager.set_cache(cache_key, asdict(execution), expire_seconds=86400)
            
            logger.info(f"💾 Signal execution logged: {execution_id} - {signal_data['symbol']} {signal_data['action']}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Failed to log signal execution: {e}")
            # Critical error - save to emergency log
            self._emergency_log(signal_data, str(e))
            raise
    
    def log_signal_update(self, execution_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update signal execution dengan new information (TP hit, SL hit, etc.)
        
        Args:
            execution_id: Original execution ID
            update_data: Update information
            
        Returns:
            success: Boolean indicating success
        """
        try:
            update_record = {
                'execution_id': execution_id,
                'update_type': update_data.get('type', 'UNKNOWN'),
                'update_data': update_data,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Queue for processing
            self.log_queue.put({
                'type': 'SIGNAL_UPDATE',
                'data': update_record,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"💾 Signal update logged: {execution_id} - {update_data.get('type')}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log signal update: {e}")
            return False
    
    def get_execution_history(self, symbol: str = None, timeframe: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get execution history dengan filtering"""
        try:
            if not self.db_session:
                return []
            
            from models import SignalHistory
            
            query = self.db_session.query(SignalHistory)
            
            if symbol:
                query = query.filter(SignalHistory.symbol == symbol.upper())
            if timeframe:
                query = query.filter(SignalHistory.timeframe == timeframe)
            
            signals = query.order_by(SignalHistory.created_at.desc()).limit(limit).all()
            return [signal.to_dict() for signal in signals]
            
        except Exception as e:
            logger.error(f"Failed to get execution history: {e}")
            return []
    
    def get_execution_stats(self, days_back: int = 7) -> Dict[str, Any]:
        """Get comprehensive execution statistics"""
        try:
            if not self.db_session:
                return {'error': 'Database not available'}
            
            from models import SignalHistory
            from datetime import timedelta
            
            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            signals = self.db_session.query(SignalHistory).filter(
                SignalHistory.created_at >= since_date
            ).all()
            
            if not signals:
                return {'total_signals': 0, 'period_days': days_back}
            
            # Calculate comprehensive stats
            stats = {
                'total_signals': len(signals),
                'period_days': days_back,
                'by_symbol': {},
                'by_timeframe': {},
                'by_action': {'BUY': 0, 'SELL': 0, 'HOLD': 0},
                'confidence_distribution': {'high': 0, 'medium': 0, 'low': 0},
                'execution_sources': {},
                'success_metrics': {
                    'total_successful': 0,
                    'total_failed': 0,
                    'success_rate': 0.0,
                    'avg_confidence': 0.0
                }
            }
            
            total_confidence = 0
            successful_signals = 0
            
            for signal in signals:
                # By symbol
                symbol = signal.symbol
                if symbol not in stats['by_symbol']:
                    stats['by_symbol'][symbol] = 0
                stats['by_symbol'][symbol] += 1
                
                # By timeframe
                tf = signal.timeframe
                if tf not in stats['by_timeframe']:
                    stats['by_timeframe'][tf] = 0
                stats['by_timeframe'][tf] += 1
                
                # By action
                action = signal.action or 'UNKNOWN'
                if action in stats['by_action']:
                    stats['by_action'][action] += 1
                
                # Confidence distribution
                confidence = signal.confidence or 0
                total_confidence += confidence
                
                if confidence >= 80:
                    stats['confidence_distribution']['high'] += 1
                elif confidence >= 60:
                    stats['confidence_distribution']['medium'] += 1
                else:
                    stats['confidence_distribution']['low'] += 1
                
                # Success tracking
                outcome = signal.outcome
                if outcome and outcome in ['WIN', 'HIT_TP']:
                    successful_signals += 1
                
                # Execution sources
                source = signal.execution_source or 'UNKNOWN'
                if source not in stats['execution_sources']:
                    stats['execution_sources'][source] = 0
                stats['execution_sources'][source] += 1
            
            # Calculate final metrics
            stats['success_metrics']['total_successful'] = successful_signals
            stats['success_metrics']['total_failed'] = len(signals) - successful_signals
            stats['success_metrics']['success_rate'] = (successful_signals / len(signals)) * 100 if signals else 0
            stats['success_metrics']['avg_confidence'] = total_confidence / len(signals) if signals else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get execution stats: {e}")
            return {'error': str(e)}
    
    def audit_trail_report(self, execution_id: str) -> Dict[str, Any]:
        """Generate comprehensive audit trail untuk specific execution"""
        try:
            # Get execution from cache or database
            execution_data = self._get_execution_data(execution_id)
            if not execution_data:
                return {'error': 'Execution not found'}
            
            # Get all related updates
            updates = self._get_execution_updates(execution_id)
            
            # Build comprehensive audit trail
            audit_trail = {
                'execution_id': execution_id,
                'original_signal': execution_data,
                'updates': updates,
                'timeline': self._build_execution_timeline(execution_data, updates),
                'integrity_check': self._verify_data_integrity(execution_data, updates),
                'compliance_flags': self._check_compliance_issues(execution_data, updates)
            }
            
            return audit_trail
            
        except Exception as e:
            logger.error(f"Failed to generate audit trail: {e}")
            return {'error': str(e)}
    
    def _start_background_processor(self):
        """Start background thread untuk processing logs"""
        if self.processing_thread and self.processing_thread.is_alive():
            return
        
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_log_queue, daemon=True)
        self.processing_thread.start()
        logger.info("💾 Background log processor started")
    
    def _process_log_queue(self):
        """Background processor untuk log queue"""
        while self.is_running:
            try:
                # Get item from queue dengan timeout
                item = self.log_queue.get(timeout=1.0)
                
                if item['type'] == 'SIGNAL_EXECUTION':
                    self._save_execution_to_db(item['data'])
                elif item['type'] == 'SIGNAL_UPDATE':
                    self._save_update_to_db(item['data'])
                
                self.log_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing log queue: {e}")
    
    def _save_execution_to_db(self, execution: SignalExecution):
        """Save execution to database"""
        if not self.db_session:
            return
        
        try:
            from models import SignalHistory
            
            # Convert to database model
            signal_record = SignalHistory(
                signal_id=execution.signal_id,
                symbol=execution.symbol,
                timeframe=execution.timeframe,
                action=execution.action,
                confidence=execution.confidence,
                entry_price=execution.entry_price,
                take_profit=execution.take_profit,
                stop_loss=execution.stop_loss,
                ai_reasoning=execution.reasoning,
                execution_source=execution.source,
                user_agent=execution.user_agent,
                ip_address=execution.ip_address,
                is_executed=True,
                executed_at=datetime.fromisoformat(execution.executed_at.replace('Z', '+00:00')),
                smc_analysis=json.dumps(execution.market_conditions) if execution.market_conditions else None,
                technical_indicators=json.dumps(execution.technical_indicators) if execution.technical_indicators else None
            )
            
            self.db_session.add(signal_record)
            self.db_session.commit()
            
            logger.debug(f"💾 Execution saved to database: {execution.signal_id}")
            
        except Exception as e:
            logger.error(f"Failed to save execution to database: {e}")
            if self.db_session:
                self.db_session.rollback()
    
    def _save_update_to_db(self, update_record: Dict[str, Any]):
        """Save update to database"""
        if not self.db_session:
            return
        
        try:
            from models import SignalHistory
            
            # Find original signal
            signal = self.db_session.query(SignalHistory).filter_by(
                signal_id=update_record['execution_id']
            ).first()
            
            if signal:
                # Update based on update type
                update_data = update_record['update_data']
                update_type = update_record['update_type']
                
                if update_type == 'OUTCOME':
                    signal.outcome = update_data.get('outcome')
                    signal.pnl_percentage = update_data.get('pnl_percentage')
                    signal.closed_at = datetime.now(timezone.utc)
                elif update_type == 'PRICE_UPDATE':
                    signal.execution_price = update_data.get('current_price')
                
                signal.updated_at = datetime.now(timezone.utc)
                self.db_session.commit()
                
                logger.debug(f"💾 Signal updated in database: {update_record['execution_id']}")
            
        except Exception as e:
            logger.error(f"Failed to save update to database: {e}")
            if self.db_session:
                self.db_session.rollback()
    
    def _generate_execution_id(self, signal_data: Dict[str, Any]) -> str:
        """Generate unique execution ID"""
        data_str = f"{signal_data['symbol']}{signal_data['timeframe']}{signal_data['action']}{datetime.now(timezone.utc).isoformat()}"
        hash_obj = hashlib.md5(data_str.encode())
        return f"EXE_{hash_obj.hexdigest()[:12].upper()}"
    
    def _calculate_risk_level(self, signal_data: Dict[str, Any]) -> str:
        """Calculate risk level untuk signal"""
        confidence = signal_data.get('confidence', 0)
        
        # Calculate risk-reward ratio if available
        entry = signal_data.get('entry_price', 0)
        tp = signal_data.get('take_profit', 0)
        sl = signal_data.get('stop_loss', 0)
        
        if entry and tp and sl:
            if signal_data.get('action') == 'BUY':
                reward = abs(tp - entry)
                risk = abs(entry - sl)
            else:
                reward = abs(entry - tp)
                risk = abs(sl - entry)
            
            rr_ratio = reward / risk if risk > 0 else 0
            
            # Risk assessment based on confidence and RR ratio
            if confidence >= 80 and rr_ratio >= 2:
                return 'LOW'
            elif confidence >= 60 and rr_ratio >= 1.5:
                return 'MEDIUM'
            else:
                return 'HIGH'
        
        # Fallback to confidence-based assessment
        if confidence >= 80:
            return 'LOW'
        elif confidence >= 60:
            return 'MEDIUM'
        else:
            return 'HIGH'
    
    def _emergency_log(self, signal_data: Dict[str, Any], error: str):
        """Emergency logging kalau database fail"""
        try:
            emergency_file = 'logs/emergency_signals.log'
            os.makedirs(os.path.dirname(emergency_file), exist_ok=True)
            
            with open(emergency_file, 'a') as f:
                emergency_record = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'signal_data': signal_data,
                    'error': error
                }
                f.write(json.dumps(emergency_record) + '\n')
                
        except Exception as e:
            logger.critical(f"Emergency logging failed: {e}")
    
    def _get_execution_data(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution data from cache or database"""
        # Try cache first
        if self.redis_manager:
            cache_key = f"signal_execution:{execution_id}"
            cached_data = self.redis_manager.get_cache(cache_key)
            if cached_data:
                return cached_data
        
        # Fallback to database
        if self.db_session:
            try:
                from models import SignalHistory
                signal = self.db_session.query(SignalHistory).filter_by(signal_id=execution_id).first()
                if signal:
                    return signal.to_dict()
            except Exception as e:
                logger.error(f"Database query error: {e}")
        
        return None
    
    def _get_execution_updates(self, execution_id: str) -> List[Dict[str, Any]]:
        """Get all updates untuk specific execution"""
        # Implementation untuk getting updates
        # For now, return empty list
        return []
    
    def _build_execution_timeline(self, execution_data: Dict[str, Any], updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build chronological timeline of execution events"""
        timeline = []
        
        # Add initial execution
        timeline.append({
            'timestamp': execution_data.get('executed_at'),
            'event': 'SIGNAL_EXECUTED',
            'data': execution_data
        })
        
        # Add updates
        for update in updates:
            timeline.append({
                'timestamp': update.get('updated_at'),
                'event': update.get('update_type'),
                'data': update
            })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'] or '')
        
        return timeline
    
    def _verify_data_integrity(self, execution_data: Dict[str, Any], updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify data integrity untuk audit purposes"""
        integrity_check = {
            'status': 'VALID',
            'issues': [],
            'last_verified': datetime.now(timezone.utc).isoformat()
        }
        
        # Check required fields
        required_fields = ['signal_id', 'symbol', 'action', 'entry_price', 'confidence']
        for field in required_fields:
            if field not in execution_data or execution_data[field] is None:
                integrity_check['issues'].append(f"Missing required field: {field}")
        
        # Check data consistency
        if execution_data.get('confidence', 0) < 0 or execution_data.get('confidence', 0) > 100:
            integrity_check['issues'].append("Invalid confidence value")
        
        if integrity_check['issues']:
            integrity_check['status'] = 'INVALID'
        
        return integrity_check
    
    def _check_compliance_issues(self, execution_data: Dict[str, Any], updates: List[Dict[str, Any]]) -> List[str]:
        """Check untuk compliance issues"""
        compliance_flags = []
        
        # Check untuk high-risk executions without proper documentation
        if execution_data.get('risk_level') == 'HIGH' and not execution_data.get('reasoning'):
            compliance_flags.append("High-risk execution without reasoning")
        
        # Check untuk missing audit trail
        if not execution_data.get('ip_address') and not execution_data.get('user_agent'):
            compliance_flags.append("Missing user identification data")
        
        return compliance_flags
    
    def shutdown(self):
        """Gracefully shutdown background processor"""
        self.is_running = False
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
        logger.info("💾 Advanced Signal Logger shutdown completed")

# Global logger instance
signal_logger = None

def get_signal_logger():
    """Get global signal logger instance"""
    global signal_logger
    if signal_logger is None:
        try:
            from models import db
            from core.redis_manager import RedisManager
            
            redis_manager = RedisManager()
            signal_logger = AdvancedSignalLogger(
                db_session=db.session,
                redis_manager=redis_manager
            )
        except Exception as e:
            logger.error(f"Failed to initialize signal logger: {e}")
            signal_logger = AdvancedSignalLogger()  # Fallback without dependencies
    
    return signal_logger

def log_signal_execution(signal_data: Dict[str, Any], execution_context: Dict[str, Any] = None) -> str:
    """Convenience function untuk logging signal execution"""
    return get_signal_logger().log_signal_execution(signal_data, execution_context)

def log_signal_update(execution_id: str, update_data: Dict[str, Any]) -> bool:
    """Convenience function untuk logging signal updates"""
    return get_signal_logger().log_signal_update(execution_id, update_data)

# Export
__all__ = [
    'AdvancedSignalLogger', 'SignalExecution', 'get_signal_logger',
    'log_signal_execution', 'log_signal_update'
]