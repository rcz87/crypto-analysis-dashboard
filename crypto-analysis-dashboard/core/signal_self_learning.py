#!/usr/bin/env python3
"""
🧠 Signal Self-Learning Engine - Auto-Improvement System
Sistem pembelajaran mandiri untuk evaluasi dan peningkatan sinyal trading
"""

import os
import logging
import json
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

# Setup logging
logger = logging.getLogger(__name__)

# Create blueprint
self_learning_bp = Blueprint('self_learning', __name__, url_prefix='/api/gpts/self-learning')

class SignalSelfLearningEngine:
    """
    🧠 Self-Learning Engine untuk evaluasi otomatis performa sinyal
    
    Features:
    - Auto-tracking sinyal yang dikirim
    - Evaluasi hasil berdasarkan data historis OKX
    - Analisis mengapa sinyal gagal menggunakan GPT-4o
    - Penyimpanan results ke PostgreSQL + Redis cache
    - Self-reflection untuk improvement
    """
    
    def __init__(self, okx_fetcher=None, ai_engine=None, db_session=None, redis_manager=None):
        """Initialize Self-Learning Engine"""
        self.okx_fetcher = okx_fetcher
        self.ai_engine = ai_engine
        self.db_session = db_session
        self.redis_manager = redis_manager
        
        logger.info("🧠 Signal Self-Learning Engine initialized")
    
    def track_signal(self, signal_data: Dict[str, Any]) -> str:
        """
        📊 Track sinyal baru untuk evaluasi masa depan
        
        Args:
            signal_data: Dict containing signal details
            
        Returns:
            signal_id: Unique ID untuk tracking
        """
        try:
            # Validate required fields
            required_fields = ['symbol', 'timeframe', 'entry_price', 'take_profit', 'stop_loss', 'confidence']
            for field in required_fields:
                if field not in signal_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Create signal tracking entry
            signal_entry = {
                'signal_id': self._generate_signal_id(),
                'symbol': signal_data['symbol'].upper(),
                'timeframe': signal_data['timeframe'],
                'entry_price': float(signal_data['entry_price']),
                'take_profit': float(signal_data['take_profit']),
                'stop_loss': float(signal_data['stop_loss']),
                'confidence': float(signal_data['confidence']),
                'ai_reasoning': signal_data.get('ai_reasoning', ''),
                'timestamp': signal_data.get('timestamp', datetime.now(timezone.utc).isoformat()),
                'status': 'PENDING',  # PENDING, EVALUATED, EXPIRED
                'outcome': None,  # HIT_TP, HIT_SL, FAILED, UNTOUCHED
                'actual_return': None,
                'evaluation_timestamp': None,
                'self_reflection': None
            }
            
            # Save to database
            if self.db_session:
                self._save_to_database(signal_entry)
            
            # Cache in Redis for quick access
            if self.redis_manager:
                cache_key = f"signal_tracking:{signal_entry['signal_id']}"
                self.redis_manager.set_cache(cache_key, signal_entry, expire_seconds=2592000)  # 30 days
            
            logger.info(f"📊 Signal tracked: {signal_entry['signal_id']} for {signal_entry['symbol']}")
            return signal_entry['signal_id']
            
        except Exception as e:
            logger.error(f"❌ Error tracking signal: {e}")
            raise
    
    def evaluate_signal(self, signal_id: str) -> Dict[str, Any]:
        """
        🔍 Evaluasi hasil sinyal berdasarkan data historis
        
        Args:
            signal_id: ID sinyal yang akan dievaluasi
            
        Returns:
            Dict dengan hasil evaluasi
        """
        try:
            # Get signal data
            signal_data = self._get_signal_data(signal_id)
            if not signal_data:
                raise ValueError(f"Signal {signal_id} not found")
            
            if signal_data['status'] == 'EVALUATED':
                logger.info(f"Signal {signal_id} already evaluated")
                return signal_data
            
            # Get historical price data
            historical_data = self._get_historical_price_data(
                signal_data['symbol'],
                signal_data['timeframe'],
                signal_data['timestamp']
            )
            
            if not historical_data:
                logger.warning(f"No historical data available for {signal_id}")
                return signal_data
            
            # Evaluate signal outcome
            evaluation_result = self._evaluate_signal_outcome(signal_data, historical_data)
            
            # Generate self-reflection using AI
            self_reflection = self._generate_self_reflection(signal_data, evaluation_result)
            
            # Update signal data
            signal_data.update({
                'status': 'EVALUATED',
                'outcome': evaluation_result['outcome'],
                'actual_return': evaluation_result['actual_return'],
                'evaluation_timestamp': datetime.now(timezone.utc).isoformat(),
                'self_reflection': self_reflection,
                'evaluation_details': evaluation_result
            })
            
            # Save updated data
            self._update_signal_data(signal_id, signal_data)
            
            logger.info(f"✅ Signal {signal_id} evaluated: {evaluation_result['outcome']}")
            return signal_data
            
        except Exception as e:
            logger.error(f"❌ Error evaluating signal {signal_id}: {e}")
            raise
    
    def bulk_evaluate_pending_signals(self, max_signals: int = 100) -> Dict[str, Any]:
        """
        📊 Evaluasi batch semua sinyal yang pending
        
        Args:
            max_signals: Maximum number of signals to evaluate
            
        Returns:
            Dict dengan summary hasil evaluasi
        """
        try:
            # Get pending signals
            pending_signals = self._get_pending_signals(max_signals)
            
            results = {
                'total_evaluated': 0,
                'outcomes': {'HIT_TP': 0, 'HIT_SL': 0, 'FAILED': 0, 'UNTOUCHED': 0},
                'errors': [],
                'success_rate': 0.0,
                'avg_return': 0.0
            }
            
            total_return = 0.0
            
            for signal in pending_signals:
                try:
                    evaluation = self.evaluate_signal(signal['signal_id'])
                    results['total_evaluated'] += 1
                    
                    outcome = evaluation.get('outcome')
                    if outcome:
                        results['outcomes'][outcome] += 1
                        
                    actual_return = evaluation.get('actual_return', 0)
                    total_return += actual_return
                    
                except Exception as e:
                    results['errors'].append({
                        'signal_id': signal['signal_id'],
                        'error': str(e)
                    })
            
            # Calculate metrics
            if results['total_evaluated'] > 0:
                successful_signals = results['outcomes']['HIT_TP']
                results['success_rate'] = (successful_signals / results['total_evaluated']) * 100
                results['avg_return'] = total_return / results['total_evaluated']
            
            logger.info(f"📊 Bulk evaluation completed: {results['total_evaluated']} signals")
            return results
            
        except Exception as e:
            logger.error(f"❌ Error in bulk evaluation: {e}")
            raise
    
    def get_learning_insights(self, days_back: int = 30) -> Dict[str, Any]:
        """
        📈 Dapatkan insights pembelajaran dari data historis
        
        Args:
            days_back: Berapa hari ke belakang untuk analisis
            
        Returns:
            Dict dengan learning insights
        """
        try:
            # Get evaluated signals from last N days
            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            evaluated_signals = self._get_evaluated_signals_since(since_date)
            
            if not evaluated_signals:
                return {
                    'total_signals': 0,
                    'message': 'No evaluated signals found for the specified period'
                }
            
            # Analyze patterns
            insights = {
                'total_signals': len(evaluated_signals),
                'period_days': days_back,
                'overall_performance': self._calculate_overall_performance(evaluated_signals),
                'symbol_performance': self._analyze_symbol_performance(evaluated_signals),
                'timeframe_performance': self._analyze_timeframe_performance(evaluated_signals),
                'confidence_analysis': self._analyze_confidence_correlation(evaluated_signals),
                'common_failure_patterns': self._identify_failure_patterns(evaluated_signals),
                'improvement_suggestions': self._generate_improvement_suggestions(evaluated_signals)
            }
            
            logger.info(f"📈 Learning insights generated for {len(evaluated_signals)} signals")
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error generating learning insights: {e}")
            raise
    
    def _generate_signal_id(self) -> str:
        """Generate unique signal ID"""
        from uuid import uuid4
        return f"SIG_{uuid4().hex[:12].upper()}"
    
    def _save_to_database(self, signal_entry: Dict[str, Any]):
        """Save signal entry to database"""
        if not self.db_session:
            return
        
        try:
            # Import here to avoid circular imports
            from models import SignalHistory
            
            history_entry = SignalHistory(
                signal_id=signal_entry['signal_id'],
                symbol=signal_entry['symbol'],
                timeframe=signal_entry['timeframe'],
                entry_price=signal_entry['entry_price'],
                take_profit=signal_entry['take_profit'],
                stop_loss=signal_entry['stop_loss'],
                confidence=signal_entry['confidence'],
                ai_reasoning=signal_entry['ai_reasoning'],
                outcome=signal_entry['outcome'],
                actual_return=signal_entry['actual_return'],
                self_reflection=signal_entry['self_reflection']
            )
            
            self.db_session.add(history_entry)
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Database save error: {e}")
            if self.db_session:
                self.db_session.rollback()
    
    def _get_signal_data(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """Get signal data from cache or database"""
        # Try cache first
        if self.redis_manager:
            cache_key = f"signal_tracking:{signal_id}"
            cached_data = self.redis_manager.get_cache(cache_key)
            if cached_data:
                return cached_data
        
        # Fall back to database
        if self.db_session:
            try:
                from models import SignalHistory
                signal = self.db_session.query(SignalHistory).filter_by(signal_id=signal_id).first()
                if signal:
                    return signal.to_dict()
            except Exception as e:
                logger.error(f"Database query error: {e}")
        
        return None
    
    def _get_historical_price_data(self, symbol: str, timeframe: str, start_timestamp: str) -> Optional[pd.DataFrame]:
        """Get historical price data from OKX"""
        if not self.okx_fetcher:
            return None
        
        try:
            # Convert timestamp to datetime
            start_dt = datetime.fromisoformat(start_timestamp.replace('Z', '+00:00'))
            
            # Get data for evaluation period (e.g., next 24-48 hours)
            end_dt = start_dt + timedelta(hours=48)
            
            # Use OKX fetcher to get candle data
            candles = self.okx_fetcher.get_candles(
                symbol=symbol,
                timeframe=timeframe,
                limit=100,
                start_time=start_dt,
                end_time=end_dt
            )
            
            if candles and len(candles) > 0:
                return pd.DataFrame(candles)
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
        
        return None
    
    def _evaluate_signal_outcome(self, signal_data: Dict[str, Any], historical_data: pd.DataFrame) -> Dict[str, Any]:
        """Evaluate signal outcome based on historical price data"""
        try:
            entry_price = signal_data['entry_price']
            take_profit = signal_data['take_profit']
            stop_loss = signal_data['stop_loss']
            
            # Determine signal direction
            is_long = take_profit > entry_price
            
            outcome = 'UNTOUCHED'
            actual_return = 0.0
            hit_price = None
            hit_timestamp = None
            
            # Check each candle for TP/SL hits
            for _, candle in historical_data.iterrows():
                high = float(candle.get('high', 0))
                low = float(candle.get('low', 0))
                timestamp = candle.get('timestamp')
                
                if is_long:
                    # Long position: check TP first (higher priority)
                    if high >= take_profit:
                        outcome = 'HIT_TP'
                        hit_price = take_profit
                        hit_timestamp = timestamp
                        actual_return = ((take_profit - entry_price) / entry_price) * 100
                        break
                    elif low <= stop_loss:
                        outcome = 'HIT_SL'
                        hit_price = stop_loss
                        hit_timestamp = timestamp
                        actual_return = ((stop_loss - entry_price) / entry_price) * 100
                        break
                else:
                    # Short position: check TP first (lower priority)
                    if low <= take_profit:
                        outcome = 'HIT_TP'
                        hit_price = take_profit
                        hit_timestamp = timestamp
                        actual_return = ((entry_price - take_profit) / entry_price) * 100
                        break
                    elif high >= stop_loss:
                        outcome = 'HIT_SL'
                        hit_price = stop_loss
                        hit_timestamp = timestamp
                        actual_return = ((entry_price - stop_loss) / entry_price) * 100
                        break
            
            return {
                'outcome': outcome,
                'actual_return': round(actual_return, 2),
                'hit_price': hit_price,
                'hit_timestamp': hit_timestamp,
                'evaluation_period_hours': 48,
                'total_candles_analyzed': len(historical_data)
            }
            
        except Exception as e:
            logger.error(f"Error evaluating signal outcome: {e}")
            return {
                'outcome': 'FAILED',
                'actual_return': 0.0,
                'error': str(e)
            }
    
    def _generate_self_reflection(self, signal_data: Dict[str, Any], evaluation_result: Dict[str, Any]) -> str:
        """Generate AI-powered self-reflection on signal performance"""
        if not self.ai_engine:
            return "AI reflection not available - AI Engine not initialized"
        
        try:
            # Build reflection prompt
            prompt = self._build_reflection_prompt(signal_data, evaluation_result)
            
            # Get AI analysis
            reflection = self.ai_engine.generate_ai_snapshot(
                symbol=signal_data['symbol'],
                timeframe=signal_data['timeframe'],
                analysis_result={
                    'signal_data': signal_data,
                    'evaluation_result': evaluation_result,
                    'reflection_prompt': prompt
                },
                quick_mode=True
            )
            
            return reflection
            
        except Exception as e:
            logger.error(f"Error generating self-reflection: {e}")
            return f"Self-reflection generation failed: {str(e)}"
    
    def _build_reflection_prompt(self, signal_data: Dict[str, Any], evaluation_result: Dict[str, Any]) -> str:
        """Build prompt for AI self-reflection"""
        outcome = evaluation_result.get('outcome', 'UNKNOWN')
        actual_return = evaluation_result.get('actual_return', 0)
        confidence = signal_data.get('confidence', 0)
        
        prompt = f"""
        Analyze this trading signal performance and provide insights:
        
        Signal Details:
        - Symbol: {signal_data['symbol']}
        - Timeframe: {signal_data['timeframe']}
        - Entry: ${signal_data['entry_price']}
        - Take Profit: ${signal_data['take_profit']}
        - Stop Loss: ${signal_data['stop_loss']}
        - Confidence: {confidence}%
        - Original Reasoning: {signal_data.get('ai_reasoning', 'Not provided')}
        
        Actual Result:
        - Outcome: {outcome}
        - Return: {actual_return}%
        
        Please analyze:
        1. Why did this signal {'succeed' if outcome == 'HIT_TP' else 'fail'}?
        2. What market conditions might have influenced the outcome?
        3. Was the confidence level appropriate?
        4. What could be improved for future signals?
        
        Provide concise, actionable insights in Indonesian.
        """
        
        return prompt.strip()
    
    def _get_pending_signals(self, limit: int) -> List[Dict[str, Any]]:
        """Get pending signals for evaluation"""
        pending_signals = []
        
        if self.db_session:
            try:
                from models import SignalHistory
                signals = self.db_session.query(SignalHistory).filter_by(outcome=None).limit(limit).all()
                pending_signals = [signal.to_dict() for signal in signals]
            except Exception as e:
                logger.error(f"Error getting pending signals: {e}")
        
        return pending_signals
    
    def _get_evaluated_signals_since(self, since_date: datetime) -> List[Dict[str, Any]]:
        """Get evaluated signals since a specific date"""
        evaluated_signals = []
        
        if self.db_session:
            try:
                from models import SignalHistory
                signals = self.db_session.query(SignalHistory).filter(
                    SignalHistory.created_at >= since_date,
                    SignalHistory.outcome.isnot(None)
                ).all()
                evaluated_signals = [signal.to_dict() for signal in signals]
            except Exception as e:
                logger.error(f"Error getting evaluated signals: {e}")
        
        return evaluated_signals
    
    def _calculate_overall_performance(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall performance metrics"""
        if not signals:
            return {}
        
        outcomes = [s.get('outcome') for s in signals]
        returns = [s.get('actual_return', 0) for s in signals if s.get('actual_return') is not None]
        
        total_signals = len(signals)
        successful_signals = outcomes.count('HIT_TP')
        failed_signals = outcomes.count('HIT_SL')
        untouched_signals = outcomes.count('UNTOUCHED')
        
        return {
            'total_signals': total_signals,
            'success_rate': (successful_signals / total_signals) * 100 if total_signals > 0 else 0,
            'failure_rate': (failed_signals / total_signals) * 100 if total_signals > 0 else 0,
            'untouched_rate': (untouched_signals / total_signals) * 100 if total_signals > 0 else 0,
            'avg_return': sum(returns) / len(returns) if returns else 0,
            'total_return': sum(returns) if returns else 0
        }
    
    def _analyze_symbol_performance(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by symbol"""
        symbol_stats = {}
        
        for signal in signals:
            symbol = signal.get('symbol')
            if not symbol:
                continue
            
            if symbol not in symbol_stats:
                symbol_stats[symbol] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'returns': []
                }
            
            symbol_stats[symbol]['total'] += 1
            
            outcome = signal.get('outcome')
            if outcome == 'HIT_TP':
                symbol_stats[symbol]['successful'] += 1
            elif outcome == 'HIT_SL':
                symbol_stats[symbol]['failed'] += 1
            
            actual_return = signal.get('actual_return')
            if actual_return is not None:
                symbol_stats[symbol]['returns'].append(actual_return)
        
        # Calculate success rates
        for symbol, stats in symbol_stats.items():
            if stats['total'] > 0:
                stats['success_rate'] = (stats['successful'] / stats['total']) * 100
                stats['avg_return'] = sum(stats['returns']) / len(stats['returns']) if stats['returns'] else 0
        
        return symbol_stats
    
    def _analyze_timeframe_performance(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance by timeframe"""
        timeframe_stats = {}
        
        for signal in signals:
            timeframe = signal.get('timeframe')
            if not timeframe:
                continue
            
            if timeframe not in timeframe_stats:
                timeframe_stats[timeframe] = {
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'returns': []
                }
            
            timeframe_stats[timeframe]['total'] += 1
            
            outcome = signal.get('outcome')
            if outcome == 'HIT_TP':
                timeframe_stats[timeframe]['successful'] += 1
            elif outcome == 'HIT_SL':
                timeframe_stats[timeframe]['failed'] += 1
            
            actual_return = signal.get('actual_return')
            if actual_return is not None:
                timeframe_stats[timeframe]['returns'].append(actual_return)
        
        # Calculate success rates
        for timeframe, stats in timeframe_stats.items():
            if stats['total'] > 0:
                stats['success_rate'] = (stats['successful'] / stats['total']) * 100
                stats['avg_return'] = sum(stats['returns']) / len(stats['returns']) if stats['returns'] else 0
        
        return timeframe_stats
    
    def _analyze_confidence_correlation(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlation between confidence and success"""
        confidence_ranges = {
            'high_confidence': {'range': '80-100%', 'signals': []},
            'medium_confidence': {'range': '60-79%', 'signals': []},
            'low_confidence': {'range': '0-59%', 'signals': []}
        }
        
        for signal in signals:
            confidence = signal.get('confidence', 0)
            outcome = signal.get('outcome')
            
            if confidence >= 80:
                confidence_ranges['high_confidence']['signals'].append(signal)
            elif confidence >= 60:
                confidence_ranges['medium_confidence']['signals'].append(signal)
            else:
                confidence_ranges['low_confidence']['signals'].append(signal)
        
        # Calculate statistics for each range
        for range_name, range_data in confidence_ranges.items():
            signals_in_range = range_data['signals']
            total = len(signals_in_range)
            
            if total > 0:
                successful = sum(1 for s in signals_in_range if s.get('outcome') == 'HIT_TP')
                range_data['total_signals'] = total
                range_data['success_rate'] = (successful / total) * 100
                range_data['avg_confidence'] = sum(s.get('confidence', 0) for s in signals_in_range) / total
            else:
                range_data['total_signals'] = 0
                range_data['success_rate'] = 0
                range_data['avg_confidence'] = 0
        
        return confidence_ranges
    
    def _identify_failure_patterns(self, signals: List[Dict[str, Any]]) -> List[str]:
        """Identify common patterns in failed signals"""
        failed_signals = [s for s in signals if s.get('outcome') == 'HIT_SL']
        
        if not failed_signals:
            return ["No failed signals to analyze"]
        
        patterns = []
        
        # Analyze confidence levels of failed signals
        high_conf_failures = [s for s in failed_signals if s.get('confidence', 0) >= 80]
        if len(high_conf_failures) > len(failed_signals) * 0.3:
            patterns.append("High confidence signals are failing frequently - review analysis criteria")
        
        # Analyze by symbol
        symbol_failures = {}
        for signal in failed_signals:
            symbol = signal.get('symbol')
            if symbol:
                symbol_failures[symbol] = symbol_failures.get(symbol, 0) + 1
        
        if symbol_failures:
            worst_symbol = max(symbol_failures, key=symbol_failures.get)
            patterns.append(f"Symbol {worst_symbol} has highest failure rate - review market conditions")
        
        # Analyze by timeframe
        timeframe_failures = {}
        for signal in failed_signals:
            timeframe = signal.get('timeframe')
            if timeframe:
                timeframe_failures[timeframe] = timeframe_failures.get(timeframe, 0) + 1
        
        if timeframe_failures:
            worst_timeframe = max(timeframe_failures, key=timeframe_failures.get)
            patterns.append(f"Timeframe {worst_timeframe} has highest failure rate - adjust strategy")
        
        return patterns if patterns else ["No clear failure patterns identified"]
    
    def _generate_improvement_suggestions(self, signals: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        if not signals:
            return ["Insufficient data for suggestions"]
        
        # Analyze overall performance
        performance = self._calculate_overall_performance(signals)
        success_rate = performance.get('success_rate', 0)
        
        if success_rate < 50:
            suggestions.append("Overall success rate is low - review signal generation criteria")
        elif success_rate > 80:
            suggestions.append("Excellent success rate - consider increasing position sizes")
        
        # Analyze confidence correlation
        confidence_analysis = self._analyze_confidence_correlation(signals)
        high_conf_success = confidence_analysis.get('high_confidence', {}).get('success_rate', 0)
        low_conf_success = confidence_analysis.get('low_confidence', {}).get('success_rate', 0)
        
        if high_conf_success < low_conf_success:
            suggestions.append("High confidence signals performing worse than low confidence - review confidence calculation")
        
        # Check for risk management
        avg_return = performance.get('avg_return', 0)
        if avg_return < 0:
            suggestions.append("Negative average return - tighten stop losses or improve entry timing")
        
        return suggestions if suggestions else ["Performance is stable - continue current strategy"]
    
    def _update_signal_data(self, signal_id: str, updated_data: Dict[str, Any]):
        """Update signal data in database and cache"""
        # Update database
        if self.db_session:
            try:
                from models import SignalHistory
                signal = self.db_session.query(SignalHistory).filter_by(signal_id=signal_id).first()
                if signal:
                    signal.outcome = updated_data.get('outcome')
                    signal.actual_return = updated_data.get('actual_return')
                    signal.self_reflection = updated_data.get('self_reflection')
                    self.db_session.commit()
            except Exception as e:
                logger.error(f"Database update error: {e}")
                if self.db_session:
                    self.db_session.rollback()
        
        # Update cache
        if self.redis_manager:
            cache_key = f"signal_tracking:{signal_id}"
            self.redis_manager.set_cache(cache_key, updated_data, expire_seconds=2592000)  # 30 days

# Initialize global engine instance
self_learning_engine = None

def initialize_self_learning_engine():
    """Initialize self-learning engine with dependencies"""
    global self_learning_engine
    
    if self_learning_engine is not None:
        return self_learning_engine
    
    try:
        # Import dependencies
        from core.okx_fetcher import OKXFetcher
        from core.ai_engine import AIEngine
        from core.redis_manager import RedisManager
        from models import db
        
        # Initialize dependencies
        okx_fetcher = OKXFetcher()
        ai_engine = AIEngine()
        redis_manager = RedisManager()
        db_session = db.session
        
        # Create engine instance
        self_learning_engine = SignalSelfLearningEngine(
            okx_fetcher=okx_fetcher,
            ai_engine=ai_engine,
            db_session=db_session,
            redis_manager=redis_manager
        )
        
        logger.info("🧠 Self-Learning Engine initialized successfully")
        return self_learning_engine
        
    except Exception as e:
        logger.error(f"Failed to initialize Self-Learning Engine: {e}")
        return None

# API Endpoints
@self_learning_bp.route('/track', methods=['POST'])
@cross_origin()
def track_signal():
    """📊 Track new signal for future evaluation"""
    try:
        engine = initialize_self_learning_engine()
        if not engine:
            return jsonify({
                'error': 'INITIALIZATION_ERROR',
                'message': 'Self-learning engine not available'
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'INVALID_INPUT',
                'message': 'JSON data required'
            }), 400
        
        signal_id = engine.track_signal(data)
        
        return jsonify({
            'success': True,
            'signal_id': signal_id,
            'message': 'Signal tracked successfully',
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except ValueError as e:
        return jsonify({
            'error': 'VALIDATION_ERROR',
            'message': str(e)
        }), 400
    except Exception as e:
        logger.error(f"Error in track_signal: {e}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'Signal tracking failed'
        }), 500

@self_learning_bp.route('/evaluate', methods=['POST'])
@cross_origin()
def evaluate_signal():
    """🔍 Evaluate specific signal by ID"""
    try:
        engine = initialize_self_learning_engine()
        if not engine:
            return jsonify({
                'error': 'INITIALIZATION_ERROR',
                'message': 'Self-learning engine not available'
            }), 500
        
        data = request.get_json()
        if not data or 'signal_id' not in data:
            return jsonify({
                'error': 'INVALID_INPUT',
                'message': 'signal_id required'
            }), 400
        
        result = engine.evaluate_signal(data['signal_id'])
        
        return jsonify({
            'success': True,
            'evaluation_result': result,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except ValueError as e:
        return jsonify({
            'error': 'NOT_FOUND',
            'message': str(e)
        }), 404
    except Exception as e:
        logger.error(f"Error in evaluate_signal: {e}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'Signal evaluation failed'
        }), 500

@self_learning_bp.route('/evaluate-batch', methods=['POST'])
@cross_origin()
def evaluate_batch():
    """📊 Bulk evaluate pending signals"""
    try:
        engine = initialize_self_learning_engine()
        if not engine:
            return jsonify({
                'error': 'INITIALIZATION_ERROR',
                'message': 'Self-learning engine not available'
            }), 500
        
        data = request.get_json() or {}
        max_signals = data.get('max_signals', 100)
        
        result = engine.bulk_evaluate_pending_signals(max_signals)
        
        return jsonify({
            'success': True,
            'batch_evaluation': result,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in evaluate_batch: {e}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'Batch evaluation failed'
        }), 500

@self_learning_bp.route('/insights', methods=['GET'])
@cross_origin()
def get_insights():
    """📈 Get learning insights and performance analytics"""
    try:
        engine = initialize_self_learning_engine()
        if not engine:
            return jsonify({
                'error': 'INITIALIZATION_ERROR',
                'message': 'Self-learning engine not available'
            }), 500
        
        days_back = request.args.get('days', 30, type=int)
        
        insights = engine.get_learning_insights(days_back)
        
        return jsonify({
            'success': True,
            'learning_insights': insights,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in get_insights: {e}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'Insights generation failed'
        }), 500

@self_learning_bp.route('/status', methods=['GET'])
@cross_origin()
def get_status():
    """📊 Get self-learning system status"""
    try:
        engine = initialize_self_learning_engine()
        
        status = {
            'engine_available': engine is not None,
            'components': {
                'okx_fetcher': engine.okx_fetcher is not None if engine else False,
                'ai_engine': engine.ai_engine is not None if engine else False,
                'database': engine.db_session is not None if engine else False,
                'redis_cache': engine.redis_manager is not None if engine else False
            },
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error in get_status: {e}")
        return jsonify({
            'error': 'INTERNAL_ERROR',
            'message': 'Status check failed'
        }), 500

# Export blueprint and engine
__all__ = ['self_learning_bp', 'SignalSelfLearningEngine', 'initialize_self_learning_engine']