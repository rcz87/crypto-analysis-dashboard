#!/usr/bin/env python3
"""
🧬 Dynamic Confidence Threshold System - Auto-Adjust Based on Performance
Sistem otomatis untuk menyesuaikan confidence threshold berdasarkan performa real-time
"""

import logging
import json
import math
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class ConfidenceMetrics:
    """Metrics untuk confidence threshold adjustment"""
    current_threshold: float
    success_rate: float
    total_signals: int
    successful_signals: int
    failed_signals: int
    avg_confidence: float
    recommendation: str
    last_updated: str

class DynamicConfidenceThreshold:
    """
    🧬 Dynamic Confidence Threshold System
    
    Features:
    - Real-time performance monitoring
    - Automatic threshold adjustment based on success rates
    - Adaptive learning dari market conditions
    - Performance-based optimization
    - Risk management integration
    """
    
    def __init__(self, db_session=None, redis_manager=None, initial_threshold: float = 70.0):
        """Initialize Dynamic Confidence Threshold System"""
        self.db_session = db_session
        self.redis_manager = redis_manager
        self.current_threshold = initial_threshold
        self.min_threshold = 50.0  # Minimum threshold
        self.max_threshold = 95.0  # Maximum threshold
        self.adjustment_step = 2.5  # Step size for adjustments
        self.evaluation_window = 24  # Hours to look back for evaluation
        self.min_signals_for_adjustment = 10  # Minimum signals needed for adjustment
        
        # Performance targets
        self.target_success_rate = 70.0  # Target success rate %
        self.success_rate_tolerance = 5.0  # Tolerance for success rate
        
        # Monitoring thread
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Load saved threshold
        self._load_saved_threshold()
        
        # Start monitoring
        self._start_monitoring()
        
        logger.info(f"🧬 Dynamic Confidence Threshold initialized at {self.current_threshold}%")
    
    def get_current_threshold(self) -> float:
        """Get current confidence threshold"""
        return self.current_threshold
    
    def should_execute_signal(self, confidence: float, signal_data: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Determine if signal should be executed based on current threshold
        
        Args:
            confidence: Signal confidence level
            signal_data: Additional signal data for context
            
        Returns:
            (should_execute, reason): Execution decision and reason
        """
        try:
            # Basic threshold check
            if confidence >= self.current_threshold:
                return True, f"Confidence {confidence}% meets threshold {self.current_threshold}%"
            
            # Context-based adjustments
            if signal_data:
                adjusted_threshold = self._apply_contextual_adjustments(signal_data)
                if confidence >= adjusted_threshold:
                    return True, f"Confidence {confidence}% meets adjusted threshold {adjusted_threshold}% for market conditions"
            
            return False, f"Confidence {confidence}% below threshold {self.current_threshold}%"
            
        except Exception as e:
            logger.error(f"Error evaluating signal execution: {e}")
            return False, f"Error in threshold evaluation: {str(e)}"
    
    def evaluate_and_adjust_threshold(self) -> ConfidenceMetrics:
        """
        Evaluate recent performance and adjust threshold accordingly
        
        Returns:
            ConfidenceMetrics: Current metrics and adjustment results
        """
        try:
            # Get recent performance data
            performance_data = self._get_recent_performance()
            
            if performance_data['total_signals'] < self.min_signals_for_adjustment:
                logger.info(f"Insufficient signals ({performance_data['total_signals']}) for threshold adjustment")
                return self._build_confidence_metrics(performance_data, "Insufficient data for adjustment")
            
            # Calculate success rate
            success_rate = (performance_data['successful_signals'] / performance_data['total_signals']) * 100
            
            # Determine adjustment needed
            adjustment_decision = self._calculate_threshold_adjustment(success_rate, performance_data)
            
            # Apply adjustment
            old_threshold = self.current_threshold
            self.current_threshold = self._apply_threshold_adjustment(adjustment_decision)
            
            # Save new threshold
            self._save_threshold()
            
            # Log adjustment
            if abs(self.current_threshold - old_threshold) > 0.1:
                logger.info(f"🧬 Threshold adjusted: {old_threshold}% → {self.current_threshold}% (Success rate: {success_rate:.1f}%)")
            
            return self._build_confidence_metrics(performance_data, adjustment_decision['reason'])
            
        except Exception as e:
            logger.error(f"Error in threshold evaluation: {e}")
            return ConfidenceMetrics(
                current_threshold=self.current_threshold,
                success_rate=0.0,
                total_signals=0,
                successful_signals=0,
                failed_signals=0,
                avg_confidence=0.0,
                recommendation=f"Error: {str(e)}",
                last_updated=datetime.now(timezone.utc).isoformat()
            )
    
    def get_threshold_history(self, days_back: int = 7) -> List[Dict[str, Any]]:
        """Get history of threshold adjustments"""
        try:
            if not self.redis_manager:
                return []
            
            history_key = "confidence_threshold_history"
            history_data = self.redis_manager.get_cache(history_key)
            
            if not history_data:
                return []
            
            # Filter by date range
            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            filtered_history = []
            for entry in history_data:
                entry_date = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                if entry_date >= since_date:
                    filtered_history.append(entry)
            
            return filtered_history
            
        except Exception as e:
            logger.error(f"Error getting threshold history: {e}")
            return []
    
    def force_threshold_adjustment(self, new_threshold: float, reason: str = "Manual adjustment") -> bool:
        """
        Force threshold adjustment (manual override)
        
        Args:
            new_threshold: New threshold value
            reason: Reason for adjustment
            
        Returns:
            success: Boolean indicating success
        """
        try:
            if not self.min_threshold <= new_threshold <= self.max_threshold:
                logger.warning(f"Threshold {new_threshold} outside valid range ({self.min_threshold}-{self.max_threshold})")
                return False
            
            old_threshold = self.current_threshold
            self.current_threshold = new_threshold
            
            # Save adjustment
            self._save_threshold()
            self._log_threshold_change(old_threshold, new_threshold, reason, manual=True)
            
            logger.info(f"🧬 Manual threshold adjustment: {old_threshold}% → {new_threshold}% ({reason})")
            return True
            
        except Exception as e:
            logger.error(f"Error in manual threshold adjustment: {e}")
            return False
    
    def get_optimization_suggestions(self) -> Dict[str, Any]:
        """Get suggestions untuk optimizing confidence thresholds"""
        try:
            # Analyze performance patterns
            performance_data = self._get_recent_performance()
            confidence_distribution = self._analyze_confidence_distribution()
            
            suggestions = {
                'current_status': self._assess_current_performance(performance_data),
                'optimization_opportunities': [],
                'risk_factors': [],
                'recommended_actions': []
            }
            
            # Performance-based suggestions
            if performance_data['total_signals'] > 0:
                success_rate = (performance_data['successful_signals'] / performance_data['total_signals']) * 100
                
                if success_rate < self.target_success_rate - self.success_rate_tolerance:
                    suggestions['optimization_opportunities'].append({
                        'type': 'INCREASE_THRESHOLD',
                        'description': f"Success rate {success_rate:.1f}% below target {self.target_success_rate}%",
                        'suggested_threshold': min(self.current_threshold + 5, self.max_threshold),
                        'expected_improvement': "Higher success rate, fewer signals"
                    })
                elif success_rate > self.target_success_rate + self.success_rate_tolerance:
                    suggestions['optimization_opportunities'].append({
                        'type': 'DECREASE_THRESHOLD',
                        'description': f"Success rate {success_rate:.1f}% above target, missing opportunities",
                        'suggested_threshold': max(self.current_threshold - 2.5, self.min_threshold),
                        'expected_improvement': "More signals, maintained quality"
                    })
            
            # Distribution-based suggestions
            if confidence_distribution:
                high_conf_signals = confidence_distribution.get('high_confidence', 0)
                total_above_threshold = confidence_distribution.get('above_threshold', 0)
                
                if high_conf_signals > total_above_threshold * 0.8:
                    suggestions['optimization_opportunities'].append({
                        'type': 'DYNAMIC_ADJUSTMENT',
                        'description': "Many high-confidence signals suggest room for threshold reduction",
                        'suggested_action': "Consider gradual threshold reduction for more opportunities"
                    })
            
            # Risk factor analysis
            if performance_data['total_signals'] < self.min_signals_for_adjustment:
                suggestions['risk_factors'].append("Insufficient signal volume for reliable optimization")
            
            if self.current_threshold >= self.max_threshold * 0.9:
                suggestions['risk_factors'].append("Threshold very high - may miss profitable opportunities")
            
            if self.current_threshold <= self.min_threshold * 1.1:
                suggestions['risk_factors'].append("Threshold very low - increased risk of poor signals")
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting optimization suggestions: {e}")
            return {'error': str(e)}
    
    def _get_recent_performance(self) -> Dict[str, Any]:
        """Get recent signal performance data"""
        try:
            if not self.db_session:
                return {'total_signals': 0, 'successful_signals': 0, 'failed_signals': 0}
            
            from models import SignalHistory
            
            # Get signals from last evaluation window
            since_time = datetime.now(timezone.utc) - timedelta(hours=self.evaluation_window)
            
            signals = self.db_session.query(SignalHistory).filter(
                SignalHistory.created_at >= since_time,
                SignalHistory.outcome.isnot(None)  # Only evaluated signals
            ).all()
            
            total_signals = len(signals)
            successful_signals = sum(1 for s in signals if s.outcome in ['WIN', 'HIT_TP'])
            failed_signals = sum(1 for s in signals if s.outcome in ['LOSS', 'HIT_SL'])
            
            # Calculate average confidence of executed signals
            confidences = [s.confidence for s in signals if s.confidence is not None]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'total_signals': total_signals,
                'successful_signals': successful_signals,
                'failed_signals': failed_signals,
                'avg_confidence': avg_confidence,
                'evaluation_window_hours': self.evaluation_window
            }
            
        except Exception as e:
            logger.error(f"Error getting recent performance: {e}")
            return {'total_signals': 0, 'successful_signals': 0, 'failed_signals': 0}
    
    def _calculate_threshold_adjustment(self, success_rate: float, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate required threshold adjustment"""
        adjustment_decision = {
            'action': 'MAINTAIN',
            'adjustment': 0.0,
            'reason': 'Performance within target range'
        }
        
        # Calculate deviation from target
        deviation = success_rate - self.target_success_rate
        
        if abs(deviation) <= self.success_rate_tolerance:
            return adjustment_decision
        
        # Determine adjustment direction and magnitude
        if deviation < -self.success_rate_tolerance:
            # Success rate too low - increase threshold
            adjustment_magnitude = min(
                abs(deviation) / 10 * self.adjustment_step,  # Scale based on deviation
                self.adjustment_step * 2  # Max adjustment per cycle
            )
            adjustment_decision.update({
                'action': 'INCREASE',
                'adjustment': adjustment_magnitude,
                'reason': f'Success rate {success_rate:.1f}% below target {self.target_success_rate}%'
            })
        
        elif deviation > self.success_rate_tolerance:
            # Success rate too high - decrease threshold for more opportunities
            adjustment_magnitude = min(
                deviation / 15 * self.adjustment_step,  # Smaller adjustments when reducing
                self.adjustment_step
            )
            adjustment_decision.update({
                'action': 'DECREASE',
                'adjustment': adjustment_magnitude,
                'reason': f'Success rate {success_rate:.1f}% above target, can lower threshold'
            })
        
        return adjustment_decision
    
    def _apply_threshold_adjustment(self, adjustment_decision: Dict[str, Any]) -> float:
        """Apply calculated threshold adjustment"""
        if adjustment_decision['action'] == 'MAINTAIN':
            return self.current_threshold
        
        if adjustment_decision['action'] == 'INCREASE':
            new_threshold = self.current_threshold + adjustment_decision['adjustment']
        else:  # DECREASE
            new_threshold = self.current_threshold - adjustment_decision['adjustment']
        
        # Apply bounds
        new_threshold = max(self.min_threshold, min(self.max_threshold, new_threshold))
        
        # Log adjustment
        if abs(new_threshold - self.current_threshold) > 0.1:
            self._log_threshold_change(
                self.current_threshold, 
                new_threshold, 
                adjustment_decision['reason']
            )
        
        return new_threshold
    
    def _apply_contextual_adjustments(self, signal_data: Dict[str, Any]) -> float:
        """Apply contextual adjustments to threshold based on market conditions"""
        adjusted_threshold = self.current_threshold
        
        # Market volatility adjustment
        volatility = signal_data.get('market_conditions', {}).get('volatility', 'NORMAL')
        if volatility == 'HIGH':
            adjusted_threshold += 5  # Higher threshold in volatile markets
        elif volatility == 'LOW':
            adjusted_threshold -= 2  # Lower threshold in stable markets
        
        # Timeframe adjustment
        timeframe = signal_data.get('timeframe', '')
        if timeframe in ['5M', '15M']:
            adjusted_threshold += 3  # Higher threshold for shorter timeframes
        elif timeframe in ['4H', '1D']:
            adjusted_threshold -= 2  # Lower threshold for longer timeframes
        
        # Symbol-specific adjustment
        symbol = signal_data.get('symbol', '')
        if 'BTC' in symbol:
            adjusted_threshold -= 1  # Slightly lower for BTC (more reliable)
        
        # Apply bounds
        return max(self.min_threshold, min(self.max_threshold, adjusted_threshold))
    
    def _analyze_confidence_distribution(self) -> Dict[str, Any]:
        """Analyze distribution of confidence levels"""
        try:
            if not self.db_session:
                return {}
            
            from models import SignalHistory
            
            # Get recent signals
            since_time = datetime.now(timezone.utc) - timedelta(hours=self.evaluation_window * 2)
            signals = self.db_session.query(SignalHistory).filter(
                SignalHistory.created_at >= since_time
            ).all()
            
            if not signals:
                return {}
            
            distribution = {
                'total_signals': len(signals),
                'above_threshold': 0,
                'high_confidence': 0,  # >90%
                'medium_confidence': 0,  # 70-90%
                'low_confidence': 0,  # <70%
                'avg_confidence': 0.0
            }
            
            confidences = []
            for signal in signals:
                confidence = signal.confidence or 0
                confidences.append(confidence)
                
                if confidence >= self.current_threshold:
                    distribution['above_threshold'] += 1
                
                if confidence >= 90:
                    distribution['high_confidence'] += 1
                elif confidence >= 70:
                    distribution['medium_confidence'] += 1
                else:
                    distribution['low_confidence'] += 1
            
            distribution['avg_confidence'] = sum(confidences) / len(confidences) if confidences else 0
            
            return distribution
            
        except Exception as e:
            logger.error(f"Error analyzing confidence distribution: {e}")
            return {}
    
    def _build_confidence_metrics(self, performance_data: Dict[str, Any], recommendation: str) -> ConfidenceMetrics:
        """Build ConfidenceMetrics object"""
        total_signals = performance_data.get('total_signals', 0)
        successful_signals = performance_data.get('successful_signals', 0)
        failed_signals = performance_data.get('failed_signals', 0)
        
        success_rate = (successful_signals / total_signals * 100) if total_signals > 0 else 0.0
        
        return ConfidenceMetrics(
            current_threshold=self.current_threshold,
            success_rate=success_rate,
            total_signals=total_signals,
            successful_signals=successful_signals,
            failed_signals=failed_signals,
            avg_confidence=performance_data.get('avg_confidence', 0.0),
            recommendation=recommendation,
            last_updated=datetime.now(timezone.utc).isoformat()
        )
    
    def _assess_current_performance(self, performance_data: Dict[str, Any]) -> str:
        """Assess current performance status"""
        total_signals = performance_data.get('total_signals', 0)
        
        if total_signals == 0:
            return "NO_DATA"
        
        success_rate = (performance_data.get('successful_signals', 0) / total_signals) * 100
        
        if success_rate >= self.target_success_rate + self.success_rate_tolerance:
            return "EXCELLENT"
        elif success_rate >= self.target_success_rate - self.success_rate_tolerance:
            return "GOOD"
        elif success_rate >= self.target_success_rate - 10:
            return "FAIR"
        else:
            return "POOR"
    
    def _start_monitoring(self):
        """Start background monitoring thread"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("🧬 Threshold monitoring started")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                # Sleep for monitoring interval (30 minutes)
                time.sleep(1800)
                
                # Perform evaluation and adjustment
                self.evaluate_and_adjust_threshold()
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(300)  # Wait 5 minutes before retry
    
    def _save_threshold(self):
        """Save current threshold to persistent storage"""
        try:
            if self.redis_manager:
                threshold_data = {
                    'threshold': self.current_threshold,
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
                self.redis_manager.set_cache('dynamic_confidence_threshold', threshold_data)
                
        except Exception as e:
            logger.error(f"Error saving threshold: {e}")
    
    def _load_saved_threshold(self):
        """Load saved threshold from persistent storage"""
        try:
            if self.redis_manager:
                threshold_data = self.redis_manager.get_cache('dynamic_confidence_threshold')
                if threshold_data and 'threshold' in threshold_data:
                    self.current_threshold = threshold_data['threshold']
                    logger.info(f"🧬 Loaded saved threshold: {self.current_threshold}%")
                    
        except Exception as e:
            logger.error(f"Error loading saved threshold: {e}")
    
    def _log_threshold_change(self, old_threshold: float, new_threshold: float, reason: str, manual: bool = False):
        """Log threshold change to history"""
        try:
            if not self.redis_manager:
                return
            
            # Get existing history
            history_key = "confidence_threshold_history"
            history = self.redis_manager.get_cache(history_key) or []
            
            # Add new entry
            change_entry = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'old_threshold': old_threshold,
                'new_threshold': new_threshold,
                'change': new_threshold - old_threshold,
                'reason': reason,
                'manual': manual
            }
            
            history.append(change_entry)
            
            # Keep only last 100 entries
            if len(history) > 100:
                history = history[-100:]
            
            # Save updated history
            self.redis_manager.set_cache(history_key, history)
            
        except Exception as e:
            logger.error(f"Error logging threshold change: {e}")
    
    def shutdown(self):
        """Gracefully shutdown monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5.0)
        logger.info("🧬 Dynamic Confidence Threshold shutdown completed")

# Global threshold manager instance
threshold_manager = None

def get_threshold_manager():
    """Get global threshold manager instance"""
    global threshold_manager
    if threshold_manager is None:
        try:
            from models import db
            from core.redis_manager import RedisManager
            
            redis_manager = RedisManager()
            threshold_manager = DynamicConfidenceThreshold(
                db_session=db.session,
                redis_manager=redis_manager
            )
        except Exception as e:
            logger.error(f"Failed to initialize threshold manager: {e}")
            threshold_manager = DynamicConfidenceThreshold()  # Fallback without dependencies
    
    return threshold_manager

def get_current_confidence_threshold() -> float:
    """Get current confidence threshold"""
    return get_threshold_manager().get_current_threshold()

def should_execute_signal(confidence: float, signal_data: Dict[str, Any] = None) -> Tuple[bool, str]:
    """Check if signal should be executed based on confidence threshold"""
    return get_threshold_manager().should_execute_signal(confidence, signal_data)

# Export
__all__ = [
    'DynamicConfidenceThreshold', 'ConfidenceMetrics', 'get_threshold_manager',
    'get_current_confidence_threshold', 'should_execute_signal'
]