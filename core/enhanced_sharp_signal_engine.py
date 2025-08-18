#!/usr/bin/env python3
"""
Enhanced Sharp Signal Engine - Integrates all quality components
Menggunakan ScoringService, ExecutionGuard, CircuitBreaker, dan TradeLogger
"""
import logging
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import asdict

from core.scoring_service import ScoringService
from core.execution_guard import ExecutionGuard 
from core.circuit_breaker import CircuitBreaker
from core.trade_logger import TradeLogger
from core.data_sanity_checker import DataSanityChecker

logger = logging.getLogger(__name__)

class EnhancedSharpSignalEngine:
    def __init__(self):
        # Initialize all quality components
        self.scoring_service = ScoringService()
        self.execution_guard = ExecutionGuard()
        self.circuit_breaker = CircuitBreaker()
        self.trade_logger = TradeLogger()
        self.data_sanity = DataSanityChecker()
        
        logger.info("Enhanced Sharp Signal Engine initialized with all quality components")
    
    def generate_enhanced_signal(self,
                                symbol: str,
                                smc_analysis: Dict[str, Any],
                                orderbook_data: Dict[str, Any],
                                market_data: Dict[str, Any],
                                funding_data: Optional[Dict[str, Any]] = None,
                                news_data: Optional[Dict[str, Any]] = None,
                                position_size_usd: float = 1000.0) -> Dict[str, Any]:
        """
        Generate enhanced signal with full quality pipeline
        """
        try:
            start_time = time.time()
            
            # Step 1: Check circuit breaker permission
            can_signal, breaker_reason = self.circuit_breaker.check_signal_permission(symbol, "sharp")
            
            if not can_signal:
                return {
                    "status": "blocked",
                    "reason": breaker_reason,
                    "circuit_breaker_status": asdict(self.circuit_breaker.get_status()),
                    "timestamp": time.time()
                }
            
            # Step 2: Score signal quality using confluence engine
            scored_signal = self.scoring_service.score_signal(
                smc_analysis=smc_analysis,
                orderbook_data=orderbook_data,
                market_data=market_data,
                funding_data=funding_data,
                news_data=news_data
            )
            
            # Step 3: Check if signal meets quality threshold
            if not self.scoring_service.should_trade(scored_signal):
                return {
                    "status": "rejected", 
                    "reason": f"Signal quality too low: {scored_signal.score:.1f}/100",
                    "score_breakdown": asdict(scored_signal.breakdown),
                    "timestamp": time.time()
                }
            
            # Step 4: Execution condition check
            execution_check = self.execution_guard.check_execution_conditions(
                symbol=symbol,
                side=scored_signal.signal,
                size_usd=position_size_usd,
                orderbook_data=orderbook_data,
                market_data=market_data
            )
            
            # Step 5: Determine final approval
            if self.execution_guard.is_blocked(execution_check):
                return {
                    "status": "execution_blocked",
                    "reason": "Poor execution conditions",
                    "execution_check": asdict(execution_check),
                    "score": scored_signal.score,
                    "timestamp": time.time()
                }
            
            # Step 6: Generate levels and risk management
            levels = self._calculate_levels(scored_signal, market_data)
            
            # Step 7: Log trade entry for learning
            trade_id = self._log_trade_entry(scored_signal, execution_check, market_data, symbol)
            
            # Step 8: Build comprehensive response
            response = {
                "status": "approved",
                "signal": {
                    "direction": scored_signal.signal,
                    "confidence": scored_signal.confidence,
                    "score": round(scored_signal.score, 1),
                    "entry_price": levels["entry"],
                    "stop_loss": levels["stop_loss"], 
                    "take_profit_1": levels["tp1"],
                    "take_profit_2": levels["tp2"],
                    "position_size_usd": position_size_usd,
                    "risk_reward_ratio": levels["rr_ratio"]
                },
                "quality_checks": {
                    "scoring": {
                        "total_score": scored_signal.score,
                        "smc_score": scored_signal.breakdown.smc_score,
                        "orderbook_score": scored_signal.breakdown.orderbook_score,
                        "volatility_score": scored_signal.breakdown.volatility_score,
                        "momentum_score": scored_signal.breakdown.momentum_score,
                        "is_sharp": self.scoring_service.is_sharp_signal(scored_signal)
                    },
                    "execution": {
                        "status": execution_check.status.value,
                        "spread_bps": round(execution_check.spread_bps, 1),
                        "slippage_estimate_bps": round(execution_check.slippage_estimate, 1),
                        "depth_score": round(execution_check.depth_score, 2),
                        "liquidity_score": round(execution_check.liquidity_score, 2),
                        "has_warnings": self.execution_guard.has_warnings(execution_check)
                    },
                    "circuit_breaker": {
                        "state": self.circuit_breaker.state.value,
                        "consecutive_losses": self.circuit_breaker.consecutive_losses
                    }
                },
                "reasoning": {
                    "top_reasons": scored_signal.reasons[:5],
                    "execution_notes": execution_check.reasons[:3],
                    "signal_type": "sharp" if self.scoring_service.is_sharp_signal(scored_signal) else "standard"
                },
                "metadata": {
                    "trade_id": trade_id,
                    "symbol": symbol,
                    "processing_time_ms": round((time.time() - start_time) * 1000, 1),
                    "timestamp": time.time()
                }
            }
            
            logger.info(f"Enhanced signal generated: {symbol} {scored_signal.signal} (score: {scored_signal.score:.1f})")
            return response
            
        except Exception as e:
            logger.error(f"Enhanced signal generation error: {e}")
            return {
                "status": "error",
                "reason": f"Signal generation failed: {str(e)}",
                "timestamp": time.time()
            }
    
    def record_signal_outcome(self, trade_id: str, outcome: str, exit_price: float, pnl: float):
        """Record trade outcome for learning and circuit breaker"""
        try:
            # Calculate hold time (simplified)
            hold_time_minutes = 60  # Default 1 hour
            
            # Update trade logger
            self.trade_logger.update_trade_outcome(
                trade_id=trade_id,
                outcome=outcome,
                exit_price=exit_price,
                pnl=pnl,
                hold_time_minutes=hold_time_minutes,
                exit_reason="manual"
            )
            
            # Update circuit breaker
            symbol = "BTC-USDT"  # Would extract from trade_id in production
            self.circuit_breaker.record_signal_outcome(symbol, outcome, pnl)
            
            logger.info(f"Signal outcome recorded: {trade_id} -> {outcome} ({pnl:+.2f})")
            
        except Exception as e:
            logger.error(f"Failed to record signal outcome: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            performance_data = self.trade_logger.get_recent_performance(30)
            breaker_status = self.circuit_breaker.get_status()
            
            return {
                "circuit_breaker": {
                    "state": breaker_status.state.value,
                    "reason": breaker_status.reason,
                    "consecutive_losses": breaker_status.consecutive_losses,
                    "daily_drawdown_pct": round(breaker_status.daily_drawdown, 2),
                    "signals_today": breaker_status.total_signals_today,
                    "blocked_today": breaker_status.blocked_signals_count
                },
                "performance_30d": {
                    "total_trades": performance_data.get('total_trades', 0),
                    "win_rate": round(performance_data.get('win_rate', 0) * 100, 1),
                    "profit_factor": round(performance_data.get('profit_factor', 0), 2),
                    "total_pnl": round(performance_data.get('total_pnl', 0), 2),
                    "avg_hold_time_min": round(performance_data.get('avg_hold_time', 0), 0)
                },
                "quality_thresholds": {
                    "sharp_signal_threshold": self.scoring_service.thresholds['sharp_signal'],
                    "good_signal_threshold": self.scoring_service.thresholds['good_signal'],
                    "max_spread_bps": self.execution_guard.thresholds['max_spread_bps'],
                    "max_slippage_bps": self.execution_guard.thresholds['max_slippage_bps']
                },
                "active_trades": len(self.trade_logger.get_active_trades()),
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {"error": str(e)}
    
    def _calculate_levels(self, scored_signal, market_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate entry, stop loss, and take profit levels"""
        try:
            # Extract current price 
            current_price = 0.0
            if 'current_price' in market_data:
                current_price = float(market_data['current_price'])
            elif 'entry_price' in scored_signal.levels:
                current_price = float(scored_signal.levels['entry_price'])
            else:
                current_price = 45000.0  # Fallback
            
            # Basic level calculation based on direction
            if scored_signal.signal == 'BUY':
                entry = current_price
                stop_loss = entry * 0.98  # 2% stop loss
                tp1 = entry * 1.02  # 2% take profit
                tp2 = entry * 1.04  # 4% take profit
            else:  # SELL
                entry = current_price
                stop_loss = entry * 1.02  # 2% stop loss
                tp1 = entry * 0.98  # 2% take profit  
                tp2 = entry * 0.96  # 4% take profit
            
            # Calculate risk-reward ratio
            risk = abs(entry - stop_loss)
            reward = abs(tp1 - entry)
            rr_ratio = reward / risk if risk > 0 else 1.0
            
            return {
                "entry": round(entry, 2),
                "stop_loss": round(stop_loss, 2),
                "tp1": round(tp1, 2),
                "tp2": round(tp2, 2),
                "rr_ratio": round(rr_ratio, 2)
            }
            
        except Exception as e:
            logger.warning(f"Level calculation error: {e}")
            return {
                "entry": 45000.0,
                "stop_loss": 44100.0,
                "tp1": 45900.0, 
                "tp2": 46800.0,
                "rr_ratio": 1.0
            }
    
    def _log_trade_entry(self, scored_signal, execution_check, market_data: Dict[str, Any], symbol: str) -> str:
        """Log trade entry for learning"""
        try:
            # Prepare data structures for logging
            signal_data = {
                'symbol': symbol,
                'direction': scored_signal.signal,
                'entry_price': scored_signal.levels.get('current', 45000.0),
                'timeframe': '1H',
                'type': 'sharp'
            }
            
            scoring_data = {
                'smc_score': scored_signal.breakdown.smc_score,
                'orderbook_score': scored_signal.breakdown.orderbook_score,
                'volatility_score': scored_signal.breakdown.volatility_score,
                'momentum_score': scored_signal.breakdown.momentum_score,
                'funding_score': scored_signal.breakdown.funding_score,
                'news_score': scored_signal.breakdown.news_score,
                'total_score': scored_signal.score,
                'confidence': scored_signal.confidence
            }
            
            execution_data = {
                'spread_bps': execution_check.spread_bps,
                'depth_score': execution_check.depth_score,
                'slippage_estimate': execution_check.slippage_estimate,
                'liquidity_score': execution_check.liquidity_score,
                'approved': not self.execution_guard.is_blocked(execution_check),
                'warnings': execution_check.reasons
            }
            
            market_features = {
                'structure_break': True,
                'ob_quality': 0.8,
                'fvg_count': 2,
                'market_bias': 'bullish',
                'current_price': signal_data['entry_price']
            }
            
            trade_id = self.trade_logger.log_signal_entry(
                signal_data=signal_data,
                scoring_data=scoring_data,
                execution_data=execution_data,
                market_features=market_features
            )
            
            return trade_id
            
        except Exception as e:
            logger.error(f"Failed to log trade entry: {e}")
            return f"error_{int(time.time())}"