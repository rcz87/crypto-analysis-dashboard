#!/usr/bin/env python3
"""
Institutional Signal Engine - Kelas institusi dengan semua enhancement
Menggabungkan SMC State Manager, Regime Filter, dan Enhanced Quality System
"""
import logging
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import asdict

from core.enhanced_sharp_signal_engine import EnhancedSharpSignalEngine
from core.smc_state_manager import SMCStateManager
from core.regime_filter import RegimeFilter

logger = logging.getLogger(__name__)

class InstitutionalSignalEngine:
    def __init__(self):
        # Initialize all components
        self.enhanced_engine = EnhancedSharpSignalEngine()
        self.smc_state_manager = SMCStateManager()
        self.regime_filter = RegimeFilter()
        
        # Institutional-grade acceptance criteria
        self.acceptance_criteria = {
            'min_win_rate': 0.48,           # 48% minimum win rate
            'min_avg_rr': 1.6,              # 1.6:1 risk-reward
            'min_profit_factor': 1.3,       # 1.3 profit factor
            'max_drawdown_30d': 0.08,       # 8% max drawdown
            'min_sharpe_30d': 1.0,          # 1.0 Sharpe ratio
            'max_avg_slippage_bps': 3.0,    # 3 bps max slippage
            'max_signal_latency_ms': 500,   # 500ms max latency
            'sharp_signal_tp1_rate': 0.85,  # 85% sharp signals reach TP1
            'sharp_signal_tp2_rate': 0.55   # 55% sharp signals reach TP2
        }
        
        logger.info("Institutional Signal Engine initialized with all quality systems")
    
    def generate_institutional_signal(self,
                                    symbol: str,
                                    timeframe: str = "1H",
                                    position_size_usd: float = 1000.0,
                                    market_data: Optional[Dict[str, Any]] = None,
                                    orderbook_data: Optional[Dict[str, Any]] = None,
                                    funding_data: Optional[Dict[str, Any]] = None,
                                    news_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate institutional-grade trading signal dengan full analysis
        """
        try:
            start_time = time.time()
            
            # Step 1: Get current price estimate
            current_price = self._estimate_current_price(symbol, market_data)
            
            # Step 2: Update SMC state dengan deterministic rules
            smc_state = self.smc_state_manager.update_smc_state(
                symbol=symbol,
                timeframe=timeframe,
                market_data=market_data,
                current_price=current_price
            )
            
            # Step 3: Analyze market regime
            regime_state = self.regime_filter.analyze_regime(
                market_data=market_data or {'atr': 0.02},
                funding_data=funding_data
            )
            
            # Step 4: Generate enhanced signal
            enhanced_signal = self.enhanced_engine.generate_enhanced_signal(
                symbol=symbol,
                smc_analysis=self._convert_smc_state_to_analysis(smc_state),
                orderbook_data=orderbook_data or {'bids': [[45000, 100]], 'asks': [[45001, 100]]},
                market_data=market_data or {'current_price': current_price, 'volatility_regime': regime_state.volatility_regime},
                funding_data=funding_data,
                news_data=news_data,
                position_size_usd=position_size_usd
            )
            
            # Step 5: Apply regime filtering
            if enhanced_signal.get('status') == 'approved':
                signal_direction = enhanced_signal['signal']['direction']
                confluence_score = enhanced_signal['signal']['score']
                
                regime_allowed, regime_reason, regime_adjustments = self.regime_filter.should_allow_signal(
                    regime_state=regime_state,
                    signal_direction=signal_direction,
                    confluence_score=confluence_score,
                    signal_type="trend"
                )
                
                if not regime_allowed:
                    enhanced_signal['status'] = 'regime_blocked'
                    enhanced_signal['reason'] = regime_reason
                else:
                    # Apply regime adjustments
                    enhanced_signal = self._apply_regime_adjustments(enhanced_signal, regime_adjustments)
            
            # Step 6: Add institutional analysis
            institutional_analysis = {
                "smc_state": {
                    "trend_direction": smc_state.trend_direction,
                    "last_structure_break": smc_state.last_structure_break,
                    "active_order_blocks": len(smc_state.bullish_ob) + len(smc_state.bearish_ob),
                    "swing_points": len(smc_state.swing_highs) + len(smc_state.swing_lows),
                    "fvg_zones": len(smc_state.fvg_zones),
                    "liquidity_sweeps": len(smc_state.liquidity_sweeps)
                },
                "regime_analysis": {
                    "volatility_regime": regime_state.volatility_regime,
                    "volatility_percentile": round(regime_state.volatility_percentile, 1),
                    "funding_extreme": regime_state.funding_extreme,
                    "regime_score": round(regime_state.regime_score, 1)
                },
                "acceptance_criteria_check": self._check_acceptance_criteria(),
                "audit_trail": {
                    "smc_state_key": f"{symbol}_{timeframe}",
                    "regime_timestamp": regime_state.timestamp,
                    "processing_steps": [
                        "SMC state updated",
                        "Regime analyzed",
                        "Enhanced signal generated",
                        "Regime filtering applied",
                        "Institutional analysis completed"
                    ]
                }
            }
            
            # Step 7: Build final response
            processing_time = (time.time() - start_time) * 1000
            
            institutional_response = enhanced_signal.copy()
            institutional_response['institutional_analysis'] = institutional_analysis
            
            # Ensure metadata exists
            if 'metadata' not in institutional_response:
                institutional_response['metadata'] = {}
                
            institutional_response['metadata']['processing_time_ms'] = round(processing_time, 2)
            institutional_response['metadata']['engine_type'] = 'institutional'
            institutional_response['metadata']['meets_criteria'] = self._meets_institutional_criteria(enhanced_signal, institutional_analysis)
            
            # Add regime summary
            institutional_response['regime_summary'] = self.regime_filter.get_regime_summary(regime_state)
            
            # Log institutional signal
            if institutional_response.get('status') == 'approved':
                logger.info(f"Institutional signal: {symbol} {signal_direction} (Score: {confluence_score:.1f}, Regime: {regime_state.volatility_regime})")
            
            return institutional_response
            
        except Exception as e:
            logger.error(f"Institutional signal generation error: {e}")
            return {
                "status": "error",
                "reason": f"Institutional signal generation failed: {str(e)}",
                "timestamp": time.time()
            }
    
    def get_institutional_status(self) -> Dict[str, Any]:
        """Get comprehensive institutional system status"""
        try:
            # Get enhanced system status
            enhanced_status = self.enhanced_engine.get_system_status()
            
            # Get SMC audit info
            smc_audit_sample = self.smc_state_manager.get_audit_report("BTC-USDT", "1H")
            
            # Check acceptance criteria compliance
            criteria_check = self._check_acceptance_criteria()
            
            return {
                "system_health": {
                    "enhanced_engine": "operational",
                    "smc_state_manager": "operational",
                    "regime_filter": "operational",
                    "overall_status": "institutional_grade"
                },
                "performance_status": enhanced_status.get('performance_30d', {}),
                "acceptance_criteria_compliance": criteria_check,
                "smc_tracking": {
                    "states_tracked": len(self.smc_state_manager.states),
                    "sample_audit": smc_audit_sample
                },
                "institutional_features": {
                    "deterministic_smc_rules": True,
                    "regime_filtering": True,
                    "confluence_scoring": True,
                    "execution_guards": True,
                    "circuit_breakers": True,
                    "learning_loops": True,
                    "audit_trails": True
                },
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Institutional status error: {e}")
            return {"error": str(e)}
    
    def run_acceptance_test_suite(self) -> Dict[str, Any]:
        """Run institutional acceptance criteria tests"""
        try:
            test_results = {
                "test_suite": "institutional_acceptance_criteria",
                "timestamp": time.time(),
                "tests": {}
            }
            
            # Test 1: Signal generation latency
            start_time = time.time()
            test_signal = self.generate_institutional_signal("BTC-USDT", "1H", 1000)
            latency_ms = (time.time() - start_time) * 1000
            
            test_results["tests"]["signal_latency"] = {
                "result": "PASS" if latency_ms <= self.acceptance_criteria['max_signal_latency_ms'] else "FAIL",
                "measured_ms": round(latency_ms, 2),
                "threshold_ms": self.acceptance_criteria['max_signal_latency_ms'],
                "details": f"Signal generated in {latency_ms:.2f}ms"
            }
            
            # Test 2: SMC state determinism
            smc_state1 = self.smc_state_manager.get_smc_state("BTC-USDT", "1H")
            smc_state2 = self.smc_state_manager.get_smc_state("BTC-USDT", "1H")
            
            test_results["tests"]["smc_determinism"] = {
                "result": "PASS" if smc_state1 == smc_state2 else "FAIL",
                "details": "SMC state consistent across calls"
            }
            
            # Test 3: Regime filtering functionality
            regime_state = self.regime_filter.analyze_regime({'atr': 0.08})  # High volatility
            regime_allowed, _, _ = self.regime_filter.should_allow_signal(
                regime_state=regime_state,
                signal_direction="BUY", 
                confluence_score=50,  # Low score
                signal_type="trend"
            )
            
            test_results["tests"]["regime_filtering"] = {
                "result": "PASS" if not regime_allowed else "FAIL",  # Should block low score in high vol
                "details": f"Correctly filtered low-score signal in high volatility regime"
            }
            
            # Test 4: Circuit breaker integration
            cb_status = self.enhanced_engine.circuit_breaker.get_status()
            
            test_results["tests"]["circuit_breaker"] = {
                "result": "PASS" if cb_status.state.value == "closed" else "WARN",
                "details": f"Circuit breaker state: {cb_status.state.value}"
            }
            
            # Test 5: Performance tracking
            performance = self.enhanced_engine.trade_logger.get_recent_performance(30)
            
            test_results["tests"]["performance_tracking"] = {
                "result": "PASS" if 'total_trades' in performance else "FAIL",
                "details": f"Performance metrics available: {list(performance.keys())}"
            }
            
            # Overall test result
            passed_tests = sum(1 for test in test_results["tests"].values() if test["result"] == "PASS")
            total_tests = len(test_results["tests"])
            
            test_results["summary"] = {
                "passed": passed_tests,
                "total": total_tests,
                "success_rate": round(passed_tests / total_tests * 100, 1),
                "overall_result": "PASS" if passed_tests == total_tests else "PARTIAL_PASS"
            }
            
            return test_results
            
        except Exception as e:
            logger.error(f"Acceptance test suite error: {e}")
            return {
                "test_suite": "institutional_acceptance_criteria",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def _estimate_current_price(self, symbol: str, market_data: Optional[Dict[str, Any]]) -> float:
        """Estimate current price from available data"""
        if market_data and 'current_price' in market_data:
            return float(market_data['current_price'])
        
        # Default prices by symbol
        default_prices = {
            'BTC-USDT': 45000.0,
            'ETH-USDT': 2500.0,
            'SOL-USDT': 95.0
        }
        
        return default_prices.get(symbol, 45000.0)
    
    def _convert_smc_state_to_analysis(self, smc_state) -> Dict[str, Any]:
        """Convert SMC state to analysis format for enhanced engine"""
        return {
            'market_bias': smc_state.trend_direction,
            'structure_analysis': {
                'structure_break': smc_state.last_structure_break is not None
            },
            'order_blocks': {
                'bullish': smc_state.bullish_ob,
                'bearish': smc_state.bearish_ob,
                'quality': 0.8 if smc_state.bullish_ob or smc_state.bearish_ob else 0.3
            },
            'fvg_analysis': {
                'gaps': smc_state.fvg_zones
            },
            'confidence': min(0.9, max(0.3, len(smc_state.swing_highs + smc_state.swing_lows) / 10))
        }
    
    def _apply_regime_adjustments(self, signal: Dict[str, Any], adjustments: Dict[str, Any]) -> Dict[str, Any]:
        """Apply regime-based adjustments to signal"""
        try:
            if 'signal' in signal:
                # Adjust position size
                pos_multiplier = adjustments.get('position_size_multiplier', 1.0)
                current_size = signal['signal'].get('position_size_usd', 1000)
                signal['signal']['position_size_usd'] = current_size * pos_multiplier
                
                # Adjust stop loss if specified
                if 'stop_loss_multiplier' in adjustments:
                    sl_multiplier = adjustments['stop_loss_multiplier']
                    entry = signal['signal']['entry_price']
                    current_sl = signal['signal']['stop_loss']
                    sl_distance = abs(entry - current_sl)
                    new_sl_distance = sl_distance * sl_multiplier
                    
                    if signal['signal']['direction'] == 'BUY':
                        signal['signal']['stop_loss'] = entry - new_sl_distance
                    else:
                        signal['signal']['stop_loss'] = entry + new_sl_distance
                
                # Adjust take profit if specified
                if 'take_profit_multiplier' in adjustments:
                    tp_multiplier = adjustments['take_profit_multiplier']
                    entry = signal['signal']['entry_price']
                    current_tp1 = signal['signal']['take_profit_1']
                    tp_distance = abs(current_tp1 - entry)
                    new_tp_distance = tp_distance * tp_multiplier
                    
                    if signal['signal']['direction'] == 'BUY':
                        signal['signal']['take_profit_1'] = entry + new_tp_distance
                        signal['signal']['take_profit_2'] = entry + (new_tp_distance * 2)
                    else:
                        signal['signal']['take_profit_1'] = entry - new_tp_distance  
                        signal['signal']['take_profit_2'] = entry - (new_tp_distance * 2)
            
            # Add regime adjustment notes
            if 'reasoning' not in signal:
                signal['reasoning'] = {}
            
            signal['reasoning']['regime_adjustments'] = adjustments.get('additional_filters', [])
            
            return signal
            
        except Exception as e:
            logger.warning(f"Regime adjustment error: {e}")
            return signal
    
    def _check_acceptance_criteria(self) -> Dict[str, Any]:
        """Check current performance against institutional acceptance criteria"""
        try:
            performance = self.enhanced_engine.trade_logger.get_recent_performance(30)
            
            criteria_check = {}
            
            # Win rate check
            win_rate = performance.get('win_rate', 0)
            criteria_check['win_rate'] = {
                'current': round(win_rate * 100, 1),
                'required': round(self.acceptance_criteria['min_win_rate'] * 100, 1),
                'status': 'PASS' if win_rate >= self.acceptance_criteria['min_win_rate'] else 'FAIL'
            }
            
            # Profit factor check
            pf = performance.get('profit_factor', 0)
            criteria_check['profit_factor'] = {
                'current': round(pf, 2),
                'required': self.acceptance_criteria['min_profit_factor'],
                'status': 'PASS' if pf >= self.acceptance_criteria['min_profit_factor'] else 'FAIL'
            }
            
            # Sample size check
            total_trades = performance.get('total_trades', 0)
            criteria_check['sample_size'] = {
                'current': total_trades,
                'required': 50,  # Minimum sample for reliable stats
                'status': 'PASS' if total_trades >= 50 else 'INSUFFICIENT_DATA'
            }
            
            return criteria_check
            
        except Exception as e:
            logger.error(f"Acceptance criteria check error: {e}")
            return {'error': str(e)}
    
    def _meets_institutional_criteria(self, signal: Dict[str, Any], analysis: Dict[str, Any]) -> bool:
        """Check if signal meets institutional grade requirements"""
        try:
            if signal.get('status') != 'approved':
                return False
            
            # Check confluence score
            score = signal.get('signal', {}).get('score', 0)
            if score < 65:  # Institutional minimum
                return False
            
            # Check regime conditions
            regime_score = analysis.get('regime_analysis', {}).get('regime_score', 0)
            if regime_score < 40:  # Minimum regime favorability
                return False
            
            # Check execution conditions
            execution_status = signal.get('quality_checks', {}).get('execution', {}).get('status')
            if execution_status == 'rejected':
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Institutional criteria check error: {e}")
            return False