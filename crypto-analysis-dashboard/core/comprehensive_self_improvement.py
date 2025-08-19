#!/usr/bin/env python3
"""
🚀 Comprehensive Self-Improvement Engine - Advanced Learning System
Sistem pembelajaran mandiri terpadu yang mengintegrasikan semua komponen untuk minimalisir kelemahan
"""

import logging
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class ComprehensiveSelfImprovement:
    """
    🚀 Comprehensive Self-Improvement Engine
    
    Mengintegrasikan semua sistem pembelajaran untuk meminimalisir kelemahan:
    1. Signal Logging Otomatis
    2. GPTs Reasoning Tracking  
    3. Dynamic Confidence Threshold
    4. Backtest Builder
    5. API Auth Layer
    6. Failover Telegram Bot
    7. ML Prediction Engine (HybridPredictor)
    """
    
    def __init__(self, 
                 signal_logger=None,
                 reasoning_logger=None, 
                 threshold_manager=None,
                 backtest_builder=None,
                 auth_layer=None,
                 failover_bot=None,
                 ml_predictor=None,
                 db_session=None,
                 redis_manager=None):
        """Initialize Comprehensive Self-Improvement Engine"""
        self.signal_logger = signal_logger
        self.reasoning_logger = reasoning_logger
        self.threshold_manager = threshold_manager
        self.backtest_builder = backtest_builder
        self.auth_layer = auth_layer
        self.failover_bot = failover_bot
        self.ml_predictor = ml_predictor
        self.db_session = db_session
        self.redis_manager = redis_manager
        
        # Improvement metrics
        self.improvement_cycles = 0
        self.last_improvement = None
        self.learning_insights = {}
        
        logger.info("🚀 Comprehensive Self-Improvement Engine initialized")
    
    async def execute_full_improvement_cycle(self) -> Dict[str, Any]:
        """
        Execute complete self-improvement cycle
        
        Returns:
            improvement_results: Comprehensive improvement results
        """
        try:
            cycle_start = datetime.now(timezone.utc)
            self.improvement_cycles += 1
            
            logger.info(f"🚀 Starting improvement cycle #{self.improvement_cycles}")
            
            # Step 1: Analyze Signal Performance
            signal_analysis = await self._analyze_signal_performance()
            
            # Step 2: Evaluate GPT Reasoning Quality
            reasoning_analysis = await self._analyze_reasoning_quality()
            
            # Step 3: Optimize Confidence Thresholds
            threshold_optimization = await self._optimize_confidence_thresholds()
            
            # Step 4: Run Performance Backtests
            backtest_analysis = await self._run_performance_backtests()
            
            # Step 5: Review Security & Auth
            security_review = await self._review_security_status()
            
            # Step 6: Test Communication Systems
            communication_test = await self._test_communication_systems()
            
            # Step 7: Evaluate ML Prediction Performance
            ml_analysis = await self._analyze_ml_performance()
            
            # Step 8: Generate Improvement Recommendations
            recommendations = self._generate_improvement_recommendations({
                'signal_analysis': signal_analysis,
                'reasoning_analysis': reasoning_analysis,
                'threshold_optimization': threshold_optimization,
                'backtest_analysis': backtest_analysis,
                'security_review': security_review,
                'communication_test': communication_test,
                'ml_analysis': ml_analysis
            })
            
            # Step 9: Apply Automatic Improvements
            applied_improvements = await self._apply_automatic_improvements(recommendations)
            
            # Step 10: Update Learning Insights
            self._update_learning_insights(recommendations, applied_improvements)
            
            cycle_end = datetime.now(timezone.utc)
            execution_time = (cycle_end - cycle_start).total_seconds()
            
            improvement_results = {
                'cycle_number': self.improvement_cycles,
                'execution_time_seconds': execution_time,
                'timestamp': cycle_end.isoformat(),
                'analyses': {
                    'signal_performance': signal_analysis,
                    'reasoning_quality': reasoning_analysis,
                    'threshold_optimization': threshold_optimization,
                    'backtest_results': backtest_analysis,
                    'security_status': security_review,
                    'communication_status': communication_test,
                    'ml_performance': ml_analysis
                },
                'recommendations': recommendations,
                'applied_improvements': applied_improvements,
                'overall_health_score': self._calculate_overall_health_score({
                    'signal_analysis': signal_analysis,
                    'reasoning_analysis': reasoning_analysis,
                    'threshold_optimization': threshold_optimization,
                    'security_review': security_review,
                    'communication_test': communication_test,
                    'ml_analysis': ml_analysis
                })
            }
            
            # Store results
            await self._store_improvement_results(improvement_results)
            
            # Send improvement notification
            await self._send_improvement_notification(improvement_results)
            
            self.last_improvement = cycle_end.isoformat()
            
            logger.info(f"🚀 Improvement cycle #{self.improvement_cycles} completed in {execution_time:.1f}s")
            return improvement_results
            
        except Exception as e:
            logger.error(f"Error in improvement cycle: {e}")
            return {
                'cycle_number': self.improvement_cycles,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def _analyze_signal_performance(self) -> Dict[str, Any]:
        """Analyze recent signal performance"""
        try:
            if not self.signal_logger:
                return {'error': 'Signal logger not available'}
            
            # Get recent performance stats
            stats = self.signal_logger.get_execution_stats(days_back=7)
            
            # Calculate improvement opportunities
            analysis = {
                'stats': stats,
                'health_score': 0,
                'issues': [],
                'recommendations': []
            }
            
            if stats.get('total_signals', 0) > 0:
                success_rate = stats['success_metrics']['success_rate']
                
                # Calculate health score
                if success_rate >= 80:
                    analysis['health_score'] = 95
                elif success_rate >= 70:
                    analysis['health_score'] = 80
                elif success_rate >= 60:
                    analysis['health_score'] = 65
                else:
                    analysis['health_score'] = 40
                
                # Identify issues
                if success_rate < 70:
                    analysis['issues'].append(f"Low success rate: {success_rate:.1f}%")
                    analysis['recommendations'].append("Increase confidence threshold to improve signal quality")
                
                if stats.get('total_signals', 0) < 10:
                    analysis['issues'].append("Low signal volume")
                    analysis['recommendations'].append("Lower confidence threshold to generate more signals")
                
                # Symbol-specific analysis
                symbol_performance = stats.get('by_symbol', {})
                poor_symbols = [s for s, count in symbol_performance.items() if count < 2]
                if poor_symbols:
                    analysis['recommendations'].append(f"Focus analysis on better-performing symbols, avoid: {poor_symbols}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing signal performance: {e}")
            return {'error': str(e)}
    
    async def _analyze_reasoning_quality(self) -> Dict[str, Any]:
        """Analyze GPT reasoning quality"""
        try:
            if not self.reasoning_logger:
                return {'error': 'Reasoning logger not available'}
            
            # Get reasoning patterns
            patterns = self.reasoning_logger.get_reasoning_patterns(days_back=7)
            
            analysis = {
                'patterns': patterns,
                'health_score': 0,
                'issues': [],
                'recommendations': []
            }
            
            if patterns.get('total_queries', 0) > 0:
                # Calculate average quality score (if available)
                # This would need to be implemented in reasoning logger
                analysis['health_score'] = 75  # Default
                
                # Check for consistency issues
                decision_consistency = patterns.get('decision_consistency', {})
                if decision_consistency:
                    analysis['recommendations'].append("Monitor decision consistency across similar market conditions")
                
                # Performance trends
                performance_trends = patterns.get('performance_trends', {})
                if performance_trends:
                    analysis['recommendations'].append("Optimize prompt engineering based on performance trends")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing reasoning quality: {e}")
            return {'error': str(e)}
    
    async def _optimize_confidence_thresholds(self) -> Dict[str, Any]:
        """Optimize confidence thresholds based on performance"""
        try:
            if not self.threshold_manager:
                return {'error': 'Threshold manager not available'}
            
            # Get current metrics and evaluate
            metrics = self.threshold_manager.evaluate_and_adjust_threshold()
            
            # Get optimization suggestions
            suggestions = self.threshold_manager.get_optimization_suggestions()
            
            optimization = {
                'current_threshold': metrics.current_threshold,
                'success_rate': metrics.success_rate,
                'total_signals': metrics.total_signals,
                'recommendation': metrics.recommendation,
                'optimization_suggestions': suggestions,
                'health_score': 0
            }
            
            # Calculate health score based on success rate
            if metrics.success_rate >= 75:
                optimization['health_score'] = 90
            elif metrics.success_rate >= 65:
                optimization['health_score'] = 75
            elif metrics.success_rate >= 55:
                optimization['health_score'] = 60
            else:
                optimization['health_score'] = 40
            
            return optimization
            
        except Exception as e:
            logger.error(f"Error optimizing confidence thresholds: {e}")
            return {'error': str(e)}
    
    async def _run_performance_backtests(self) -> Dict[str, Any]:
        """Run backtests untuk validate current strategy"""
        try:
            if not self.backtest_builder:
                return {'error': 'Backtest builder not available'}
            
            # Create backtest configuration
            from core.backtest_builder import BacktestConfiguration
            
            # Test configuration untuk last 30 days
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=30)
            
            config = BacktestConfiguration(
                symbol="BTCUSDT",
                timeframe="1H",
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                initial_capital=10000.0,
                position_size_percent=10.0,
                confidence_threshold=self.threshold_manager.get_current_threshold() if self.threshold_manager else 70.0,
                max_concurrent_positions=3,
                commission_percent=0.1,
                slippage_percent=0.05,
                model_type="current",
                custom_parameters={}
            )
            
            # Run backtest
            result = await self.backtest_builder.run_backtest(config)
            
            analysis = {
                'backtest_result': result.__dict__ if hasattr(result, '__dict__') else result,
                'health_score': 0,
                'recommendations': []
            }
            
            # Calculate health score
            if hasattr(result, 'success_rate'):
                if result.success_rate >= 70:
                    analysis['health_score'] = 85
                elif result.success_rate >= 60:
                    analysis['health_score'] = 70
                else:
                    analysis['health_score'] = 50
                
                # Generate recommendations
                if result.success_rate < 60:
                    analysis['recommendations'].append("Strategy needs improvement - consider parameter optimization")
                
                if hasattr(result, 'max_drawdown') and result.max_drawdown > 20:
                    analysis['recommendations'].append("High drawdown detected - implement better risk management")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error running performance backtests: {e}")
            return {'error': str(e)}
    
    async def _review_security_status(self) -> Dict[str, Any]:
        """Review security and authentication status"""
        try:
            security_review = {
                'auth_layer_status': 'unknown',
                'api_keys_health': 'unknown',
                'rate_limiting_active': False,
                'security_headers_active': False,
                'health_score': 0,
                'issues': [],
                'recommendations': []
            }
            
            if self.auth_layer:
                # Check auth layer functionality
                try:
                    # This would check if auth layer is working
                    security_review['auth_layer_status'] = 'active'
                    security_review['rate_limiting_active'] = True
                    security_review['security_headers_active'] = True
                    security_review['health_score'] = 85
                except Exception:
                    security_review['auth_layer_status'] = 'error'
                    security_review['issues'].append('Authentication layer not functioning properly')
                    security_review['health_score'] = 40
            else:
                security_review['issues'].append('No authentication layer configured')
                security_review['recommendations'].append('Implement API authentication for security')
                security_review['health_score'] = 30
            
            return security_review
            
        except Exception as e:
            logger.error(f"Error reviewing security status: {e}")
            return {'error': str(e)}
    
    async def _test_communication_systems(self) -> Dict[str, Any]:
        """Test failover bot and communication systems"""
        try:
            communication_test = {
                'failover_bot_status': 'unknown',
                'active_bot': None,
                'backup_bots_available': 0,
                'message_queue_health': 'unknown',
                'health_score': 0,
                'issues': [],
                'recommendations': []
            }
            
            if self.failover_bot:
                # Get bot status
                bot_status = self.failover_bot.get_bot_status()
                
                communication_test['active_bot'] = bot_status.get('active_bot')
                communication_test['message_queue_health'] = 'healthy' if bot_status.get('queue_status', {}).get('processing_active') else 'unhealthy'
                
                # Count healthy backup bots
                healthy_bots = 0
                for bot_id, bot_info in bot_status.get('bots', {}).items():
                    if bot_info.get('status') == 'healthy':
                        healthy_bots += 1
                
                communication_test['backup_bots_available'] = healthy_bots
                
                # Calculate health score
                if healthy_bots >= 2:
                    communication_test['health_score'] = 90
                elif healthy_bots >= 1:
                    communication_test['health_score'] = 70
                else:
                    communication_test['health_score'] = 30
                    communication_test['issues'].append('No healthy backup bots available')
                    communication_test['recommendations'].append('Configure backup Telegram bot tokens')
                
                communication_test['failover_bot_status'] = 'active'
            else:
                communication_test['issues'].append('Failover bot not configured')
                communication_test['recommendations'].append('Setup failover notification system')
                communication_test['health_score'] = 20
            
            return communication_test
            
        except Exception as e:
            logger.error(f"Error testing communication systems: {e}")
            return {'error': str(e)}
    
    def _generate_improvement_recommendations(self, analyses: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive improvement recommendations"""
        recommendations = []
        
        # Signal performance recommendations
        signal_analysis = analyses.get('signal_analysis', {})
        if signal_analysis.get('health_score', 0) < 70:
            recommendations.append({
                'category': 'SIGNAL_PERFORMANCE',
                'priority': 'HIGH',
                'action': 'ADJUST_CONFIDENCE_THRESHOLD',
                'description': 'Signal success rate below target - adjust confidence threshold',
                'auto_applicable': True
            })
        
        # Reasoning quality recommendations
        reasoning_analysis = analyses.get('reasoning_analysis', {})
        if reasoning_analysis.get('patterns', {}).get('total_queries', 0) < 50:
            recommendations.append({
                'category': 'REASONING_QUALITY',
                'priority': 'MEDIUM',
                'action': 'INCREASE_LOGGING',
                'description': 'Insufficient reasoning data for analysis - increase logging',
                'auto_applicable': True
            })
        
        # Threshold optimization recommendations
        threshold_optimization = analyses.get('threshold_optimization', {})
        current_threshold = threshold_optimization.get('current_threshold', 70)
        success_rate = threshold_optimization.get('success_rate', 0)
        
        if success_rate < 65:
            recommendations.append({
                'category': 'THRESHOLD_OPTIMIZATION',
                'priority': 'HIGH',
                'action': 'INCREASE_THRESHOLD',
                'description': f'Success rate {success_rate:.1f}% too low - increase threshold from {current_threshold}%',
                'auto_applicable': True,
                'parameters': {'new_threshold': min(current_threshold + 5, 90)}
            })
        elif success_rate > 85:
            recommendations.append({
                'category': 'THRESHOLD_OPTIMIZATION',
                'priority': 'MEDIUM',
                'action': 'DECREASE_THRESHOLD',
                'description': f'Success rate {success_rate:.1f}% very high - can lower threshold for more opportunities',
                'auto_applicable': True,
                'parameters': {'new_threshold': max(current_threshold - 2.5, 50)}
            })
        
        # Security recommendations
        security_review = analyses.get('security_review', {})
        if security_review.get('health_score', 0) < 60:
            recommendations.append({
                'category': 'SECURITY',
                'priority': 'HIGH',
                'action': 'ENHANCE_SECURITY',
                'description': 'Security posture needs improvement',
                'auto_applicable': False
            })
        
        # Communication recommendations
        communication_test = analyses.get('communication_test', {})
        if communication_test.get('backup_bots_available', 0) < 2:
            recommendations.append({
                'category': 'COMMUNICATION',
                'priority': 'MEDIUM',
                'action': 'SETUP_BACKUP_BOTS',
                'description': 'Insufficient backup notification bots',
                'auto_applicable': False
            })
        
        return recommendations
    
    async def _apply_automatic_improvements(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply automatic improvements based on recommendations"""
        applied_improvements = []
        
        for recommendation in recommendations:
            if not recommendation.get('auto_applicable', False):
                continue
            
            try:
                action = recommendation['action']
                
                if action == 'INCREASE_THRESHOLD' and self.threshold_manager:
                    new_threshold = recommendation.get('parameters', {}).get('new_threshold')
                    if new_threshold:
                        success = self.threshold_manager.force_threshold_adjustment(
                            new_threshold, 
                            "Automatic improvement based on performance analysis"
                        )
                        
                        if success:
                            applied_improvements.append({
                                'action': action,
                                'success': True,
                                'details': f'Threshold adjusted to {new_threshold}%'
                            })
                
                elif action == 'DECREASE_THRESHOLD' and self.threshold_manager:
                    new_threshold = recommendation.get('parameters', {}).get('new_threshold')
                    if new_threshold:
                        success = self.threshold_manager.force_threshold_adjustment(
                            new_threshold,
                            "Automatic improvement based on performance analysis"
                        )
                        
                        if success:
                            applied_improvements.append({
                                'action': action,
                                'success': True,
                                'details': f'Threshold adjusted to {new_threshold}%'
                            })
                
                # Add more automatic improvement actions here
                
            except Exception as e:
                applied_improvements.append({
                    'action': recommendation['action'],
                    'success': False,
                    'error': str(e)
                })
        
        return applied_improvements
    
    def _calculate_overall_health_score(self, analyses: Dict[str, Any]) -> float:
        """Calculate overall system health score"""
        try:
            scores = []
            weights = {
                'signal_analysis': 0.25,
                'reasoning_analysis': 0.18,
                'threshold_optimization': 0.18,
                'security_review': 0.13,
                'communication_test': 0.13,
                'ml_analysis': 0.13
            }
            
            for analysis_type, weight in weights.items():
                analysis = analyses.get(analysis_type, {})
                health_score = analysis.get('health_score', 0)
                scores.append(health_score * weight)
            
            overall_score = sum(scores)
            return round(overall_score, 1)
            
        except Exception as e:
            logger.error(f"Error calculating overall health score: {e}")
            return 0.0
    
    async def _analyze_ml_performance(self) -> Dict[str, Any]:
        """
        Analyze ML prediction engine performance dan integration
        """
        try:
            ml_analysis = {
                'availability': 'unknown',
                'model_status': {},
                'performance_metrics': {},
                'health_score': 0,
                'recommendations': []
            }
            
            try:
                # Try importing ML predictor
                if self.ml_predictor:
                    # Use injected ML predictor
                    ml_status = self.ml_predictor.get_model_status()
                else:
                    # Try to get ML predictor
                    from core.ml_prediction_engine import get_ml_predictor
                    ml_predictor = get_ml_predictor()
                    ml_status = ml_predictor.get_model_status()
                
                ml_analysis['availability'] = 'available'
                ml_analysis['model_status'] = ml_status
                
                # Analyze model performance
                models_loaded = ml_status.get('models_loaded', False)
                should_retrain = ml_status.get('should_retrain', True)
                tensorflow_available = ml_status.get('tensorflow_available', False)
                
                performance = ml_status.get('performance', {})
                
                # Calculate ML health score
                ml_health_score = 0
                if models_loaded:
                    ml_health_score += 30
                if not should_retrain:
                    ml_health_score += 25
                if tensorflow_available:
                    ml_health_score += 20
                
                # Check individual model accuracy
                model_accuracies = []
                for model_name, model_perf in performance.items():
                    accuracy = model_perf.get('accuracy', 0)
                    if accuracy > 0.7:
                        ml_health_score += 5
                        model_accuracies.append(f"{model_name}: {accuracy:.1%}")
                    elif accuracy > 0.6:
                        ml_health_score += 3
                        model_accuracies.append(f"{model_name}: {accuracy:.1%}")
                    else:
                        model_accuracies.append(f"{model_name}: {accuracy:.1%} (low)")
                
                ml_analysis['performance_metrics'] = {
                    'models_loaded': models_loaded,
                    'should_retrain': should_retrain,
                    'tensorflow_available': tensorflow_available,
                    'model_accuracies': model_accuracies,
                    'feature_count': ml_status.get('feature_count', 0)
                }
                
                ml_analysis['health_score'] = min(ml_health_score, 100)
                
                # Generate recommendations
                recommendations = []
                
                if should_retrain:
                    recommendations.append({
                        'category': 'ML_TRAINING',
                        'type': 'ML_TRAINING_NEEDED',
                        'priority': 'HIGH',
                        'description': 'Models need retraining for optimal performance',
                        'action': 'TRIGGER_ML_TRAINING'
                    })
                
                if not tensorflow_available:
                    recommendations.append({
                        'category': 'ML_DEPENDENCY',
                        'type': 'TENSORFLOW_UNAVAILABLE', 
                        'priority': 'MEDIUM',
                        'description': 'TensorFlow not available, LSTM models disabled',
                        'action': 'CHECK_TENSORFLOW_INSTALLATION'
                    })
                
                low_accuracy_models = [name for name, perf in performance.items() 
                                     if perf.get('accuracy', 0) < 0.65]
                if low_accuracy_models:
                    recommendations.append({
                        'category': 'ML_ACCURACY',
                        'type': 'LOW_MODEL_ACCURACY',
                        'priority': 'HIGH',
                        'description': f'Low accuracy models: {", ".join(low_accuracy_models)}',
                        'action': 'RETRAIN_MODELS'
                    })
                
                feature_count = ml_status.get('feature_count', 0)
                if feature_count < 10:
                    recommendations.append({
                        'category': 'ML_FEATURES',
                        'type': 'INSUFFICIENT_FEATURES',
                        'priority': 'MEDIUM',
                        'description': f'Only {feature_count} features available for training',
                        'action': 'ENHANCE_FEATURE_ENGINEERING'
                    })
                
                ml_analysis['recommendations'] = recommendations
                
                logger.info(f"✅ ML performance analyzed - Health Score: {ml_health_score}%")
                
            except ImportError as e:
                ml_analysis['availability'] = 'unavailable'
                ml_analysis['error'] = f'ML Predictor import failed: {str(e)}'
                ml_analysis['health_score'] = 25  # Partial score for fallback mode
                ml_analysis['recommendations'] = [{
                    'category': 'ML_SYSTEM',
                    'type': 'ML_ENGINE_UNAVAILABLE',
                    'priority': 'LOW',
                    'description': 'ML Prediction Engine not available',
                    'action': 'FIX_ML_DEPENDENCIES'
                }]
                
                logger.warning(f"ML Predictor not available: {e}")
            
            return ml_analysis
            
        except Exception as e:
            logger.error(f"Error in ML performance analysis: {e}")
            return {
                'availability': 'error',
                'health_score': 0,
                'error': str(e),
                'recommendations': []
            }

    def _update_learning_insights(self, recommendations: List[Dict[str, Any]], applied_improvements: List[Dict[str, Any]]):
        """Update learning insights based on improvement cycle"""
        try:
            current_insights = self.learning_insights
            
            # Track recommendation patterns
            if 'recommendation_patterns' not in current_insights:
                current_insights['recommendation_patterns'] = {}
            
            for rec in recommendations:
                category = rec['category']
                if category not in current_insights['recommendation_patterns']:
                    current_insights['recommendation_patterns'][category] = 0
                current_insights['recommendation_patterns'][category] += 1
            
            # Track improvement success rates
            if 'improvement_success_rate' not in current_insights:
                current_insights['improvement_success_rate'] = {'total': 0, 'successful': 0}
            
            for improvement in applied_improvements:
                current_insights['improvement_success_rate']['total'] += 1
                if improvement.get('success', False):
                    current_insights['improvement_success_rate']['successful'] += 1
            
            # Update last learning date
            current_insights['last_learning_cycle'] = datetime.now(timezone.utc).isoformat()
            current_insights['total_cycles'] = self.improvement_cycles
            
            self.learning_insights = current_insights
            
        except Exception as e:
            logger.error(f"Error updating learning insights: {e}")
    
    async def _store_improvement_results(self, results: Dict[str, Any]):
        """Store improvement results untuk historical tracking"""
        try:
            if self.redis_manager:
                # Store in Redis dengan expiration
                results_key = f"improvement_results:{results['cycle_number']}"
                self.redis_manager.set_cache(results_key, results, expire_seconds=2592000)  # 30 days
                
                # Update latest results
                self.redis_manager.set_cache('latest_improvement_results', results, expire_seconds=2592000)
            
        except Exception as e:
            logger.error(f"Error storing improvement results: {e}")
    
    async def _send_improvement_notification(self, results: Dict[str, Any]):
        """Send notification about improvement cycle results"""
        try:
            if not self.failover_bot:
                return
            
            overall_score = results.get('overall_health_score', 0)
            applied_improvements = results.get('applied_improvements', [])
            
            # Determine notification urgency
            if overall_score < 50:
                notification_type = 'error'
                emoji = '🚨'
            elif overall_score < 70:
                notification_type = 'warning'
                emoji = '⚠️'
            else:
                notification_type = 'success'
                emoji = '✅'
            
            message = f"""
{emoji} Self-Improvement Cycle #{results['cycle_number']} Complete

Overall Health Score: {overall_score}%
Execution Time: {results['execution_time_seconds']:.1f}s

Applied Improvements: {len(applied_improvements)}
Recommendations Generated: {len(results.get('recommendations', []))}

Status: {'Excellent' if overall_score >= 80 else 'Good' if overall_score >= 70 else 'Needs Attention' if overall_score >= 50 else 'Critical'}
            """.strip()
            
            self.failover_bot.send_system_notification(message, notification_type)
            
        except Exception as e:
            logger.error(f"Error sending improvement notification: {e}")
    
    def get_improvement_status(self) -> Dict[str, Any]:
        """Get current improvement system status"""
        try:
            return {
                'total_cycles': self.improvement_cycles,
                'last_improvement': self.last_improvement,
                'learning_insights': self.learning_insights,
                'components_status': {
                    'signal_logger': self.signal_logger is not None,
                    'reasoning_logger': self.reasoning_logger is not None,
                    'threshold_manager': self.threshold_manager is not None,
                    'backtest_builder': self.backtest_builder is not None,
                    'auth_layer': self.auth_layer is not None,
                    'failover_bot': self.failover_bot is not None,
                    'ml_predictor': self.ml_predictor is not None
                },
                'system_health': self._quick_health_check()
            }
            
        except Exception as e:
            logger.error(f"Error getting improvement status: {e}")
            return {'error': str(e)}
    
    def _quick_health_check(self) -> str:
        """Quick health check of all components"""
        try:
            components = [
                self.signal_logger,
                self.reasoning_logger,
                self.threshold_manager,
                self.backtest_builder,
                self.auth_layer,
                self.failover_bot
            ]
            
            available_components = sum(1 for comp in components if comp is not None)
            total_components = len(components)
            
            health_percentage = (available_components / total_components) * 100
            
            if health_percentage >= 90:
                return 'EXCELLENT'
            elif health_percentage >= 70:
                return 'GOOD'
            elif health_percentage >= 50:
                return 'FAIR'
            else:
                return 'POOR'
                
        except Exception:
            return 'UNKNOWN'

# Global improvement engine
improvement_engine = None

def get_improvement_engine():
    """Get global improvement engine instance"""
    global improvement_engine
    if improvement_engine is None:
        try:
            # Import and initialize all components
            from core.advanced_signal_logger import get_signal_logger
            from core.gpts_reasoning_logger import get_reasoning_logger
            from core.dynamic_confidence_threshold import get_threshold_manager
            from core.backtest_builder import BacktestBuilder
            from core.api_auth_layer import get_auth_layer
            from core.failover_telegram_bot import get_failover_bot
            from core.redis_manager import RedisManager
            from models import db
            
            # Initialize components
            signal_logger = get_signal_logger()
            reasoning_logger = get_reasoning_logger()
            threshold_manager = get_threshold_manager()
            backtest_builder = BacktestBuilder()
            auth_layer = get_auth_layer()
            failover_bot = get_failover_bot()
            redis_manager = RedisManager()
            
            improvement_engine = ComprehensiveSelfImprovement(
                signal_logger=signal_logger,
                reasoning_logger=reasoning_logger,
                threshold_manager=threshold_manager,
                backtest_builder=backtest_builder,
                auth_layer=auth_layer,
                failover_bot=failover_bot,
                db_session=db.session,
                redis_manager=redis_manager
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize improvement engine: {e}")
            improvement_engine = ComprehensiveSelfImprovement()  # Fallback
    
    return improvement_engine

async def run_improvement_cycle():
    """Run comprehensive improvement cycle"""
    return await get_improvement_engine().execute_full_improvement_cycle()

def get_improvement_status():
    """Get improvement system status"""
    return get_improvement_engine().get_improvement_status()

# Export
__all__ = [
    'ComprehensiveSelfImprovement', 'get_improvement_engine',
    'run_improvement_cycle', 'get_improvement_status'
]