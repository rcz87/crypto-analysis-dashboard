"""
Sharp Signal Engine - Sinyal BUY/SELL Tajam dengan AI
Mengombinasikan semua metode analisis dan diproses oleh GPT untuk sinyal presisi
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from .professional_smc_analyzer import ProfessionalSMCAnalyzer
from .analyzer import TechnicalAnalyzer
from .enhanced_ai_engine import EnhancedAIEngine
from .multi_timeframe_analyzer import MultiTimeframeAnalyzer
from .risk_manager import RiskManager
from .signal_tracker import SignalPerformanceTracker
from .alert_manager import AlertManager
from .volume_profile_analyzer import VolumeProfileAnalyzer
from .xai_implementation import xai_engine
from .performance_metrics_tracker import performance_tracker

logger = logging.getLogger(__name__)

class SharpSignalEngine:
    """
    Engine untuk menghasilkan sinyal BUY/SELL yang tajam
    Menggabungkan multiple analisis dan AI untuk keputusan presisi
    """
    
    def __init__(self, okx_fetcher=None, ai_engine=None, db_session=None, telegram_notifier=None, redis_manager=None):
        self.okx_fetcher = okx_fetcher
        self.ai_engine = ai_engine or EnhancedAIEngine()
        self.smc_analyzer = ProfessionalSMCAnalyzer()
        self.technical_analyzer = TechnicalAnalyzer()
        
        # Initialize new components
        self.mtf_analyzer = MultiTimeframeAnalyzer(okx_fetcher)
        self.risk_manager = RiskManager()
        self.signal_tracker = SignalPerformanceTracker(db_session)
        self.alert_manager = AlertManager(telegram_notifier, redis_manager)
        self.volume_profile = VolumeProfileAnalyzer()
        
        # Thresholds untuk sinyal tajam
        self.signal_thresholds = {
            'strong_buy': 80,
            'buy': 65,
            'neutral': 35,
            'sell': 35,
            'strong_sell': 20
        }
        
        logger.info("🎯 Sharp Signal Engine initialized with MTF, Risk Management, Performance Tracking & Alert System")
    
    def generate_sharp_signal(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        Generate sinyal BUY/SELL yang tajam dengan Enhanced Signal Logic
        Menggunakan weight matrix, scoring system, dan transparent reasoning
        """
        try:
            logger.info(f"🎯 Generating enhanced sharp signal for {symbol} on {timeframe}")
            
            # 1. Technical Analysis Deep Dive
            technical_data = self._deep_technical_analysis(df)
            
            # 2. SMC Professional Analysis  
            smc_data = self._deep_smc_analysis(df, symbol, timeframe)
            
            # 3. Enhanced Signal Logic dengan Weight Matrix & Transparent Reasoning
            from core.enhanced_signal_logic import enhanced_signal_logic
            enhanced_result = enhanced_signal_logic.analyze_signal_with_reasoning(
                df, symbol, technical_data, smc_data
            )
            
            # 4. Price Action & Volume Analysis
            price_volume_data = self._analyze_price_volume_action(df)
            
            # 5. Multi-Timeframe Analysis (NEW)
            mtf_analysis = self.mtf_analyzer.analyze_multiple_timeframes(symbol, timeframe)
            
            # 6. Volume Profile Analysis (NEW)
            volume_profile = self.volume_profile.analyze_volume_profile(df)
            
            # 7. Risk Assessment
            risk_data = self._assess_trading_risk(df, technical_data)
            
            # 8. AI Enhanced Analysis dengan Enhanced Reasoning
            ai_analysis = self._ai_enhanced_signal_processing_v2(
                df, symbol, timeframe, enhanced_result, smc_data, risk_data
            )
            
            # 9. Generate Final Sharp Signal dengan Enhanced Logic Results
            final_signal = self._generate_enhanced_final_signal(
                enhanced_result, ai_analysis, risk_data, df, smc_data, mtf_analysis, volume_profile
            )
            
            # 10. Track Signal Performance
            if final_signal['action'] not in ['NEUTRAL', 'WAIT']:
                signal_id = self.signal_tracker.record_signal({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'direction': final_signal['action'],
                    'entry_price': final_signal['entry_price'],
                    'stop_loss': final_signal['stop_loss'],
                    'take_profit': final_signal.get('take_profit_1'),
                    'confidence': final_signal['confidence']
                })
                final_signal['signal_id'] = signal_id
                
                # 11. Evaluate and Send Alerts
                triggered_alerts = self.alert_manager.evaluate_signal(final_signal)
                if triggered_alerts:
                    alert_results = self.alert_manager.send_alerts(triggered_alerts)
                    final_signal['alerts_sent'] = alert_results
                    logger.info(f"📢 Sent {alert_results['sent']} alerts for {symbol}")
            
            logger.info(f"🎯 Enhanced sharp signal generated: {final_signal['action']} with {final_signal['confidence']}% confidence")
            logger.info(f"📊 Reasoning: {len(enhanced_result.get('reasoning', {}).get('decision_factors', []))} decision factors analyzed")
            
            return final_signal
            
        except Exception as e:
            logger.error(f"Error generating enhanced sharp signal: {e}")
            return {
                'action': 'NEUTRAL',
                'confidence': 0,
                'error': str(e),
                'reason': 'Signal generation failed',
                'timestamp': datetime.now().isoformat(),
                'symbol': symbol,
                'timeframe': timeframe
            }
    
    def _deep_technical_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis teknikal mendalam"""
        try:
            analysis = self.technical_analyzer.analyze(df, 'BTC-USDT', '1H')
            
            indicators = analysis.get('indicators', {})
            
            # Extract dan standardize indicators
            rsi = self._safe_extract_indicator(indicators.get('rsi'), 50)
            macd = indicators.get('macd', {})
            ema_data = {
                'ema9': self._safe_extract_indicator(indicators.get('ema9')),
                'ema21': self._safe_extract_indicator(indicators.get('ema21')),
                'ema50': self._safe_extract_indicator(indicators.get('ema50')),
                'ema200': self._safe_extract_indicator(indicators.get('ema200'))
            }
            
            # Calculate technical score
            tech_score = self._calculate_technical_score(rsi, macd, ema_data, df)
            
            return {
                'rsi': rsi,
                'macd': macd,
                'ema_data': ema_data,
                'score': tech_score,
                'trend_strength': self._calculate_trend_strength(ema_data, df),
                'momentum': self._calculate_momentum(rsi, macd),
                'signals': analysis.get('signals', [])
            }
            
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            return {'score': 50, 'error': str(e)}
    
    def _deep_smc_analysis(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Analisis SMC mendalam dengan semua indikator"""
        try:
            smc_result = self.smc_analyzer.analyze_comprehensive(df, symbol, timeframe)
            
            # Extract key SMC components - all indicators requested
            choch_bos_signals = smc_result.get('choch_bos_signals', [])
            bos_signals = [s for s in choch_bos_signals if s.get('pattern_type') == 'BOS']
            choch_signals = [s for s in choch_bos_signals if s.get('pattern_type') == 'CHoCH']
            order_blocks = smc_result.get('order_blocks', [])
            fvg_signals = smc_result.get('fvg_signals', [])
            
            # Get derivatives data (Open Interest & Funding Rate)
            derivatives_data = self._get_derivatives_data(symbol)
            
            # Calculate SMC score with all indicators
            smc_score = self._calculate_smc_score(bos_signals, choch_signals, order_blocks, fvg_signals)
            
            # Format indicators for display
            smc_indicators = self._format_smc_indicators(
                bos_signals, choch_signals, order_blocks, fvg_signals, derivatives_data
            )
            
            return {
                'bos_count': len(bos_signals),
                'choch_count': len(choch_signals),
                'order_blocks_count': len(order_blocks),
                'fvg_count': len(fvg_signals),
                'derivatives_data': derivatives_data,
                'smc_indicators': smc_indicators,
                'score': smc_score,
                'market_structure': smc_result.get('market_structure', 'neutral'),
                'liquidity_analysis': smc_result.get('liquidity_analysis', {}),
                'confluence_score': smc_result.get('confluence_score', 50)
            }
            
        except Exception as e:
            logger.error(f"SMC analysis error: {e}")
            return {'score': 50, 'error': str(e)}
    
    def _analyze_price_volume_action(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis price action dan volume dengan data OKX authenticated"""
        try:
            # Enhanced price action signals with OKX data
            support_resistance = self._identify_support_resistance(df)
            breakout_signals = self._detect_breakouts(df)
            
            # Enhanced volume analysis dengan data authentic
            volume_trend = self._analyze_volume_trend(df)
            volume_confirmation = self._check_volume_confirmation(df)
            
            # Add volume spike detection for authenticated data
            volume_spike = self._detect_volume_spikes(df)
            
            # Calculate enhanced price/volume score
            pv_score = self._calculate_price_volume_score(
                support_resistance, breakout_signals, volume_trend, 
                volume_confirmation, volume_spike
            )
            
            return {
                'support_resistance': support_resistance,
                'breakout_signals': breakout_signals,
                'volume_trend': volume_trend,
                'volume_confirmation': volume_confirmation,
                'volume_spike': volume_spike,
                'score': pv_score,
                'data_source': 'okx_authenticated'
            }
            
        except Exception as e:
            logger.error(f"Price/Volume analysis error: {e}")
            return {'score': 50, 'error': str(e)}
    
    def _analyze_market_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analisis struktur pasar"""
        try:
            # Trend analysis
            trend_direction = self._determine_trend_direction(df)
            trend_strength = self._calculate_trend_strength_detailed(df)
            
            # Market phase
            market_phase = self._identify_market_phase(df)
            
            # Volatility analysis
            volatility = self._calculate_volatility(df)
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'market_phase': market_phase,
                'volatility': volatility,
                'score': self._calculate_structure_score(trend_direction, trend_strength, market_phase)
            }
            
        except Exception as e:
            logger.error(f"Market structure analysis error: {e}")
            return {'score': 50, 'error': str(e)}
    
    def _assess_trading_risk(self, df: pd.DataFrame, technical_data: Dict) -> Dict[str, Any]:
        """Penilaian risiko trading"""
        try:
            current_price = float(df['close'].iloc[-1])
            
            # Calculate ATR for stop loss
            atr = self._calculate_atr(df)
            
            # Support/Resistance levels
            support_level = self._find_nearest_support(df, current_price)
            resistance_level = self._find_nearest_resistance(df, current_price)
            
            # Risk/Reward calculation
            stop_loss = current_price - (atr * 2)  # 2x ATR stop
            take_profit_1 = current_price + (atr * 3)  # 3x ATR target
            take_profit_2 = current_price + (atr * 5)  # 5x ATR target
            
            risk_reward_ratio = abs(take_profit_1 - current_price) / abs(current_price - stop_loss)
            
            return {
                'atr': atr,
                'support_level': support_level,
                'resistance_level': resistance_level,
                'stop_loss': stop_loss,
                'take_profit_1': take_profit_1,
                'take_profit_2': take_profit_2,
                'risk_reward_ratio': risk_reward_ratio,
                'risk_level': 'LOW' if risk_reward_ratio > 2 else 'MEDIUM' if risk_reward_ratio > 1.5 else 'HIGH'
            }
            
        except Exception as e:
            logger.error(f"Risk assessment error: {e}")
            return {'risk_level': 'HIGH', 'error': str(e)}
    
    def _calculate_signal_score(self, technical_data: Dict, smc_data: Dict, 
                               pv_data: Dict, structure_data: Dict, mtf_data: Optional[Dict] = None, 
                               volume_profile: Optional[Dict] = None) -> float:
        """Calculate raw signal score berdasarkan semua analisis + MTF + Volume Profile"""
        
        # Calculate volume profile score
        vp_score = 50  # Default score
        if volume_profile and 'insights' in volume_profile:
            insights = volume_profile['insights']
            
            # Price position relative to value area
            if insights.get('price_position') == 'ABOVE_VALUE':
                vp_score += 10  # Bullish bias when above value
            elif insights.get('price_position') == 'BELOW_VALUE':
                vp_score -= 10  # Bearish bias when below value
            
            # POC strength influence
            poc_strength = volume_profile.get('poc', {}).get('strength', 'WEAK')
            if poc_strength == 'VERY_STRONG':
                vp_score += 8
            elif poc_strength == 'STRONG':
                vp_score += 5
            
            # Risk level adjustment
            if insights.get('risk_level') == 'LOW':
                vp_score += 5
            elif insights.get('risk_level') == 'HIGH':
                vp_score -= 5
        
        # Updated weighted scores with MTF and Volume Profile
        if mtf_data and mtf_data.get('confluence_score') and volume_profile:
            # With MTF and Volume Profile - redistribute weights
            tech_score = technical_data.get('score', 50) * 0.20
            smc_score = smc_data.get('score', 50) * 0.25
            pv_score = pv_data.get('score', 50) * 0.15
            structure_score = structure_data.get('score', 50) * 0.10
            mtf_score = mtf_data.get('confluence_score', 50) * 0.20
            vp_score = vp_score * 0.10
            
            raw_score = tech_score + smc_score + pv_score + structure_score + mtf_score + vp_score
        elif mtf_data and mtf_data.get('confluence_score'):
            # With MTF only - original MTF weights
            tech_score = technical_data.get('score', 50) * 0.25
            smc_score = smc_data.get('score', 50) * 0.25
            pv_score = pv_data.get('score', 50) * 0.20
            structure_score = structure_data.get('score', 50) * 0.10
            mtf_score = mtf_data.get('confluence_score', 50) * 0.20
            
            raw_score = tech_score + smc_score + pv_score + structure_score + mtf_score
        else:
            # Original weights without MTF
            tech_score = technical_data.get('score', 50) * 0.3
            smc_score = smc_data.get('score', 50) * 0.3
            pv_score = pv_data.get('score', 50) * 0.25
            structure_score = structure_data.get('score', 50) * 0.15
            
            raw_score = tech_score + smc_score + pv_score + structure_score
        
        # Ensure score is between 0-100
        return max(0, min(100, raw_score))
    
    def _ai_enhanced_signal_processing(self, df: pd.DataFrame, symbol: str, timeframe: str,
                                     technical_data: Dict, smc_data: Dict, pv_data: Dict,
                                     structure_data: Dict, risk_data: Dict, raw_score: float) -> Dict[str, Any]:
        """AI enhanced processing - the 'cooking' process"""
        
        try:
            current_price = float(df['close'].iloc[-1])
            
            # Prepare comprehensive data for AI
            market_context = {
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'raw_signal_score': raw_score,
                'technical_analysis': {
                    'rsi': technical_data.get('rsi', 50),
                    'trend_strength': technical_data.get('trend_strength', 'neutral'),
                    'momentum': technical_data.get('momentum', 'neutral')
                },
                'smc_analysis': {
                    'market_structure': smc_data.get('market_structure', 'neutral'),
                    'confluence_score': smc_data.get('confluence_score', 50),
                    'order_blocks': smc_data.get('order_blocks_count', 0),
                    'fvg_signals': smc_data.get('fvg_count', 0)
                },
                'price_volume': {
                    'volume_confirmation': pv_data.get('volume_confirmation', False),
                    'breakout_signals': pv_data.get('breakout_signals', {})
                },
                'market_structure': {
                    'trend_direction': structure_data.get('trend_direction', 'sideways'),
                    'market_phase': structure_data.get('market_phase', 'consolidation')
                },
                'risk_assessment': {
                    'risk_level': risk_data.get('risk_level', 'MEDIUM'),
                    'risk_reward_ratio': risk_data.get('risk_reward_ratio', 1.0)
                }
            }
            
            # AI analysis for signal enhancement
            ai_result = self.ai_engine.generate_ai_snapshot(
                symbol, market_context, language="indonesian", quick_mode=True
            )
            
            # Format AI result untuk Sharp Signal
            return {
                'ai_confidence_adjustment': self._extract_confidence_adjustment(ai_result),
                'ai_reasoning': ai_result[:500] if isinstance(ai_result, str) else str(ai_result)[:500],
                'final_recommendation': self._extract_recommendation_from_ai(ai_result, raw_score)
            }
            
        except Exception as e:
            logger.error(f"AI processing error: {e}")
            return {
                'ai_confidence_adjustment': 0,
                'ai_reasoning': f"AI analysis failed: {str(e)}",
                'final_recommendation': 'NEUTRAL'
            }
    
    def _generate_final_sharp_signal(self, raw_score: float, ai_analysis: Dict, 
                                   risk_data: Dict, df: pd.DataFrame, smc_data: Optional[Dict] = None, 
                                   mtf_data: Optional[Dict] = None, volume_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate final sharp BUY/SELL signal with enhanced confidence alerts"""
        
        # AI confidence adjustment
        ai_adjustment = ai_analysis.get('ai_confidence_adjustment', 0)
        final_score = max(0, min(100, raw_score + ai_adjustment))
        
        # Determine action based on final score
        if final_score >= self.signal_thresholds['strong_buy']:
            action = 'STRONG_BUY'
        elif final_score >= self.signal_thresholds['buy']:
            action = 'BUY'
        elif final_score <= self.signal_thresholds['strong_sell']:
            action = 'STRONG_SELL'
        elif final_score <= self.signal_thresholds['sell']:
            action = 'SELL'
        else:
            action = 'NEUTRAL'
        
        current_price = float(df['close'].iloc[-1])
        
        # Generate XAI explanation
        xai_explanation = self._generate_xai_explanation(df, action, final_score, smc_data, mtf_data, volume_profile)
        
        # Generate risk management report
        risk_report = None
        if action not in ['NEUTRAL', 'WAIT']:
            signal_for_risk = {
                'entry_price': current_price,
                'stop_loss': risk_data.get('stop_loss', current_price * 0.97),
                'take_profit': risk_data.get('take_profit_1', current_price * 1.03),
                'atr': float(df['high'].iloc[-14:].std()),  # Simple ATR approximation
                'direction': action
            }
            risk_report = self.risk_manager.generate_risk_report(signal_for_risk)
        
        # Determine confidence level and emoji
        confidence_emoji = ""
        confidence_level = ""
        if final_score >= 90:
            confidence_emoji = "🔥"
            confidence_level = "ULTRA HIGH"
        elif final_score >= 80:
            confidence_emoji = "💎"
            confidence_level = "HIGH"
        elif final_score >= 75:
            confidence_emoji = "✅"
            confidence_level = "STANDARD"
        else:
            confidence_emoji = "⚠️"
            confidence_level = "LOW"
        
        # Include SMC indicators in signal output
        signal_data = {
            'action': action,
            'confidence': round(final_score, 1),
            'confidence_emoji': confidence_emoji,
            'confidence_level': confidence_level,
            'raw_score': round(raw_score, 1),
            'ai_adjustment': round(ai_adjustment, 1),
            'current_price': current_price,
            'entry_price': current_price,
            'stop_loss': risk_data.get('stop_loss'),
            'take_profit_1': risk_data.get('take_profit_1'),
            'take_profit_2': risk_data.get('take_profit_2'),
            'risk_reward_ratio': risk_data.get('risk_reward_ratio'),
            'risk_level': risk_data.get('risk_level'),
            'ai_reasoning': ai_analysis.get('ai_reasoning', 'AI analysis not available'),
            'timestamp': datetime.now().isoformat(),
            'timeframe': '1H',
            'symbol': 'BTC-USDT'
        }
        
        # Add risk management recommendations
        if risk_report and 'recommendations' in risk_report:
            signal_data['risk_management'] = {
                'position_size': risk_report['recommendations']['position_size'],
                'recommended_leverage': risk_report['recommendations']['leverage'],
                'max_loss_usd': risk_report['recommendations']['max_loss_usd'],
                'risk_per_trade': risk_report['recommendations']['risk_per_trade'],
                'warnings': risk_report.get('warnings', [])
            }
        
        # Add MTF analysis if available
        if mtf_data:
            signal_data['mtf_analysis'] = {
                'confluence_score': mtf_data.get('confluence_score'),
                'confluence_details': mtf_data.get('confluence_details'),
                'recommendation': mtf_data.get('recommendation', {}),
                'timeframe_alignment': mtf_data.get('timeframe_analysis', {})
            }
        
        # Add Volume Profile analysis if available
        if volume_profile:
            signal_data['volume_profile'] = {
                'poc': {
                    'price': volume_profile.get('poc', {}).get('price'),
                    'volume': volume_profile.get('poc', {}).get('volume'),
                    'strength': volume_profile.get('poc', {}).get('strength')
                },
                'value_area': {
                    'vah': volume_profile.get('value_area', {}).get('vah'),
                    'val': volume_profile.get('value_area', {}).get('val'),
                    'volume_percentage': volume_profile.get('value_area', {}).get('volume_percentage')
                },
                'insights': volume_profile.get('insights', {}),
                'skew': volume_profile.get('skew'),
                'imbalance': volume_profile.get('imbalance')
            }
        
        # Add SMC indicators to output
        if smc_data:
            signal_data['smc_analysis'] = {
                'choch_count': smc_data.get('choch_count', 0),
                'bos_count': smc_data.get('bos_count', 0),
                'order_blocks': smc_data.get('order_blocks_count', 0),
                'fvg_count': smc_data.get('fvg_count', 0),
                'smc_indicators': smc_data.get('smc_indicators', []),
                'derivatives_data': smc_data.get('derivatives_data', {}),
                'market_structure': smc_data.get('market_structure', 'neutral')
            }
            
            # Format indicators for display
            indicators_text = "\n".join([f"• {indicator}" for indicator in smc_data.get('smc_indicators', [])])
            signal_data['indicators_triggered'] = indicators_text
        
        # Add XAI explanation
        signal_data['xai_explanation'] = xai_explanation
        
        return signal_data
    
    def _generate_xai_explanation(self, df: pd.DataFrame, action: str, confidence: float, 
                                  smc_data: Optional[Dict] = None, mtf_data: Optional[Dict] = None, 
                                  volume_profile: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate explainable AI explanation for the signal"""
        try:
            # Prepare features for XAI
            features = []
            feature_names = []
            
            # Technical indicators
            rsi = float(df['rsi'].iloc[-1]) if 'rsi' in df.columns else 50
            features.append(rsi)
            feature_names.append('rsi')
            
            # Volume ratio
            volume_ratio = float(df['volume'].iloc[-1] / df['volume'].mean()) if 'volume' in df.columns else 1.0
            features.append(volume_ratio)
            feature_names.append('volume')
            
            # Price change
            price_change = float(df['close'].pct_change().iloc[-1]) if 'close' in df.columns else 0
            features.append(price_change)
            feature_names.append('price_change')
            
            # SMC indicators
            if smc_data:
                bos_count = smc_data.get('bos_count', 0)
                features.append(float(bos_count or 0))
                feature_names.append('smc_signal')
                
                derivatives_data = smc_data.get('derivatives_data') or {}
                funding_rate = derivatives_data.get('funding_rate', 0)
                features.append(float(funding_rate or 0))
                feature_names.append('funding_rate')
                
                open_interest = derivatives_data.get('open_interest', 0)
                features.append(float(open_interest or 0) / 1000000)  # Normalize
                feature_names.append('open_interest')
            
            # MTF confirmation
            if mtf_data:
                mtf_score = (mtf_data.get('overall_score') or 50) / 100
                features.append(float(mtf_score))
                feature_names.append('market_sentiment')
            
            # Convert to numpy array
            import numpy as np
            features_array = np.array([features])
            
            # Create prediction dict
            prediction = {
                'signal': action,
                'confidence': confidence / 100  # Convert to 0-1 scale
            }
            
            # Get XAI explanation
            explanation = xai_engine.explain_prediction(
                model=None,  # Using feature importance method
                features=features_array,
                feature_names=feature_names,
                prediction=prediction
            )
            
            # Format for API response
            return xai_engine.format_for_gpts(explanation)
            
        except Exception as e:
            logger.error(f"XAI explanation generation failed: {e}")
            return {
                'decision': action,
                'confidence': confidence,
                'explanation': f"Signal: {action} dengan confidence {confidence:.1f}%",
                'risk_level': 'MEDIUM',
                'top_factors': []
            }
    
    # Helper methods for calculations
    def _safe_extract_indicator(self, indicator_data, default=None):
        """Safely extract indicator value"""
        if indicator_data is None:
            return default
        if isinstance(indicator_data, (list, tuple)) and len(indicator_data) > 0:
            return indicator_data[-1]
        if isinstance(indicator_data, (int, float)):
            return indicator_data
        return default
    
    def _calculate_technical_score(self, rsi, macd, ema_data, df):
        """Calculate technical analysis score"""
        score = 50  # Base neutral score
        
        # RSI scoring
        if rsi:
            if rsi < 30:  # Oversold - bullish
                score += 15
            elif rsi > 70:  # Overbought - bearish
                score -= 15
            elif 40 <= rsi <= 60:  # Neutral zone
                score += 0
        
        # EMA trend scoring
        if all(ema_data.values()):
            if ema_data['ema9'] > ema_data['ema21'] > ema_data['ema50']:
                score += 20  # Strong uptrend
            elif ema_data['ema9'] < ema_data['ema21'] < ema_data['ema50']:
                score -= 20  # Strong downtrend
        
        return score
    
    def _calculate_smc_score(self, bos_signals, choch_signals, order_blocks, fvg_signals):
        """Calculate SMC analysis score"""
        score = 50
        
        # BOS signals (bullish structure)
        score += len(bos_signals) * 5
        
        # CHoCH signals (bearish structure)  
        score -= len(choch_signals) * 5
        
        # Order blocks and FVG
        score += (len(order_blocks) + len(fvg_signals)) * 3
        
        return score
    
    def _get_derivatives_data(self, symbol: str) -> Dict[str, Any]:
        """Ambil data derivatives (OI & Funding Rate)"""
        derivatives: Dict[str, Any] = {
            'funding_rate': None,
            'open_interest': None
        }
        
        try:
            if self.okx_fetcher:
                # Ambil funding rate
                funding_data = self.okx_fetcher.get_funding_rate(symbol)
                if funding_data and 'funding_rate' in funding_data:
                    derivatives['funding_rate'] = {
                        'rate': float(funding_data['funding_rate']) * 100,  # Convert to percentage
                        'next_funding_time': funding_data.get('next_funding_time'),
                        'status': 'bullish' if funding_data['funding_rate'] > 0 else 'bearish'
                    }
                
                # Ambil open interest
                oi_data = self.okx_fetcher.get_open_interest(symbol)
                if oi_data and 'open_interest' in oi_data:
                    derivatives['open_interest'] = {
                        'value': float(oi_data['open_interest']),
                        'ccy_value': float(oi_data.get('open_interest_ccy', 0)),
                        'timestamp': oi_data.get('timestamp')
                    }
        except Exception as e:
            logger.error(f"Error fetching derivatives data for {symbol}: {e}")
        
        return derivatives
    
    def _format_smc_indicators(self, bos_signals, choch_signals, order_blocks, fvg_signals, derivatives_data):
        """Format SMC indicators untuk tampilan"""
        indicators = []
        
        # CHoCH indicators
        if choch_signals:
            latest_choch = choch_signals[-1]
            direction = latest_choch.get('direction', 'unknown')
            indicators.append(f"CHoCH: {direction.title()}")
        
        # BOS indicators 
        if bos_signals:
            latest_bos = bos_signals[-1]
            direction = latest_bos.get('direction', 'unknown')
            indicators.append(f"BOS: {direction.title()}")
        
        # Order Blocks
        if order_blocks:
            ob_count = len([ob for ob in order_blocks if ob.get('active', True)])
            indicators.append(f"Order Blocks: {ob_count} Active")
        
        # FVG
        if fvg_signals:
            unfilled_fvg = len([fvg for fvg in fvg_signals if not fvg.get('filled', False)])
            if unfilled_fvg > 0:
                indicators.append(f"FVG: {unfilled_fvg} Unfilled")
        
        # Open Interest
        if derivatives_data.get('open_interest'):
            oi_value = derivatives_data['open_interest']['value']
            indicators.append(f"OI: {oi_value/1000000:.1f}M")
        
        # Funding Rate
        if derivatives_data.get('funding_rate'):
            fr_rate = derivatives_data['funding_rate']['rate']
            fr_status = derivatives_data['funding_rate']['status']
            indicators.append(f"Funding Rate: {fr_rate:.4f}% ({fr_status})")
            
            # Check if funding rate > 0.03 (3%)
            if fr_rate > 3.0:  # fr_rate is already in percentage
                indicators.append("🔥 Funding Rate Tinggi: Potensi Overheat")
        
        return indicators
    
    def _calculate_price_volume_score(self, support_resistance, breakout_signals, volume_trend, volume_confirmation, volume_spike=None):
        """Calculate enhanced price/volume score with OKX data"""
        score = 50
        
        # Volume confirmation boost
        if volume_confirmation:
            score += 15
        
        # Breakout signals with volume support
        if breakout_signals.get('bullish_breakout'):
            score += 20
            if volume_spike and volume_spike.get('high_volume'):
                score += 10  # Extra boost for volume-confirmed breakout
        elif breakout_signals.get('bearish_breakout'):
            score -= 20
            if volume_spike and volume_spike.get('high_volume'):
                score -= 10  # Extra penalty for volume-confirmed breakdown
        
        # Volume trend analysis
        if volume_trend == 'increasing':
            score += 8
        elif volume_trend == 'decreasing':
            score -= 5
        
        # Support/resistance quality
        if support_resistance:
            current_distance = support_resistance.get('distance_to_support', 0)
            if current_distance < 0.02:  # Within 2% of support
                score += 5
                
        return score
    
    def _calculate_structure_score(self, trend_direction, trend_strength, market_phase):
        """Calculate market structure score"""
        score = 50
        
        if trend_direction == 'uptrend':
            score += 15
        elif trend_direction == 'downtrend':
            score -= 15
            
        if trend_strength == 'strong':
            score += 10
        elif trend_strength == 'weak':
            score -= 5
            
        return score
    
    def _calculate_trend_strength(self, ema_data, df):
        """Calculate trend strength"""
        if not all(ema_data.values()):
            return 'neutral'
        
        # Simple trend strength calculation
        if ema_data['ema9'] > ema_data['ema21'] > ema_data['ema50']:
            return 'strong_bullish'
        elif ema_data['ema9'] < ema_data['ema21'] < ema_data['ema50']:
            return 'strong_bearish'
        else:
            return 'neutral'
    
    def _calculate_momentum(self, rsi, macd):
        """Calculate momentum"""
        if rsi and rsi > 60:
            return 'bullish'
        elif rsi and rsi < 40:
            return 'bearish'
        return 'neutral'
    
    def _identify_support_resistance(self, df):
        """Identify support and resistance levels"""
        try:
            highs = df['high'].rolling(window=20).max()
            lows = df['low'].rolling(window=20).min()
            return {
                'resistance': float(highs.iloc[-1]),
                'support': float(lows.iloc[-1])
            }
        except:
            return {'resistance': None, 'support': None}
    
    def _detect_breakouts(self, df):
        """Detect breakout signals"""
        try:
            current_price = float(df['close'].iloc[-1])
            recent_high = float(df['high'].rolling(window=20).max().iloc[-1])
            recent_low = float(df['low'].rolling(window=20).min().iloc[-1])
            
            return {
                'bullish_breakout': current_price > recent_high * 1.001,
                'bearish_breakout': current_price < recent_low * 0.999
            }
        except:
            return {'bullish_breakout': False, 'bearish_breakout': False}
    
    def _analyze_volume_trend(self, df):
        """Analyze volume trend"""
        try:
            recent_volume = df['volume'].rolling(window=10).mean().iloc[-1]
            past_volume = df['volume'].rolling(window=10).mean().iloc[-20]
            
            if recent_volume > past_volume * 1.2:
                return 'increasing'
            elif recent_volume < past_volume * 0.8:
                return 'decreasing'
            return 'stable'
        except:
            return 'stable'
    
    def _check_volume_confirmation(self, df):
        """Check volume confirmation"""
        try:
            price_change = (df['close'].iloc[-1] - df['close'].iloc[-2]) / df['close'].iloc[-2]
            volume_ratio = df['volume'].iloc[-1] / df['volume'].rolling(window=20).mean().iloc[-1]
            
            return abs(price_change) > 0.005 and volume_ratio > 1.2
        except:
            return False
    
    def _determine_trend_direction(self, df):
        """Determine trend direction"""
        try:
            sma_20 = df['close'].rolling(window=20).mean()
            sma_50 = df['close'].rolling(window=50).mean()
            
            if sma_20.iloc[-1] > sma_50.iloc[-1]:
                return 'uptrend'
            elif sma_20.iloc[-1] < sma_50.iloc[-1]:
                return 'downtrend'
            return 'sideways'
        except:
            return 'sideways'
    
    def _calculate_trend_strength_detailed(self, df):
        """Calculate detailed trend strength"""
        try:
            # ADX-like calculation
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift(1))
            low_close = abs(df['low'] - df['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=14).mean()
            
            price_range = df['close'].rolling(window=14).std()
            if hasattr(price_range, 'iloc') and hasattr(atr, 'iloc'):
                strength_ratio = price_range.iloc[-1] / atr.iloc[-1] if atr.iloc[-1] > 0 else 0
            else:
                strength_ratio = 0
            
            if strength_ratio > 1.5:
                return 'strong'
            elif strength_ratio > 1.0:
                return 'moderate'
            return 'weak'
        except:
            return 'moderate'
    
    def _identify_market_phase(self, df):
        """Identify market phase"""
        try:
            volatility = df['close'].rolling(window=20).std()
            volume_sma = df['volume'].rolling(window=20).mean()
            
            recent_vol = volatility.iloc[-5:].mean()
            past_vol = volatility.iloc[-20:-5].mean()
            
            if recent_vol > past_vol * 1.3:
                return 'breakout'
            elif recent_vol < past_vol * 0.7:
                return 'consolidation'
            return 'trending'
        except:
            return 'consolidation'
    
    def _calculate_volatility(self, df):
        """Calculate volatility"""
        try:
            return float(df['close'].rolling(window=20).std().iloc[-1])
        except:
            return 0.0
    
    def _calculate_atr(self, df, period=14):
        """Calculate Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = abs(df['high'] - df['close'].shift(1))
            low_close = abs(df['low'] - df['close'].shift(1))
            
            true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
            atr = true_range.rolling(window=period).mean()
            
            if hasattr(atr, 'iloc'):
                return float(atr.iloc[-1])
            else:
                return 0.0
        except:
            return 0.0
    
    def _find_nearest_support(self, df, current_price):
        """Find nearest support level"""
        try:
            lows = df['low'].rolling(window=20, center=True).min()
            support_levels = lows[lows == df['low']].dropna()
            
            valid_supports = support_levels[support_levels < current_price]
            return float(valid_supports.iloc[-1]) if len(valid_supports) > 0 else current_price * 0.95
        except:
            return current_price * 0.95
    
    def _find_nearest_resistance(self, df, current_price):
        """Find nearest resistance level"""
        try:
            highs = df['high'].rolling(window=20, center=True).max()
            resistance_levels = highs[highs == df['high']].dropna()
            
            valid_resistances = resistance_levels[resistance_levels > current_price]
            return float(valid_resistances.iloc[0]) if len(valid_resistances) > 0 else current_price * 1.05
        except:
            return current_price * 1.05
    
    def _detect_volume_spikes(self, df):
        """Detect volume spikes using OKX authenticated data"""
        try:
            if 'volume' not in df.columns:
                return {'high_volume': False, 'spike_ratio': 1.0}
            
            current_volume = float(df['volume'].iloc[-1])
            avg_volume = float(df['volume'].rolling(window=20).mean().iloc[-1])
            
            spike_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            return {
                'high_volume': spike_ratio > 2.0,  # 2x average volume
                'spike_ratio': spike_ratio,
                'current_volume': current_volume,
                'avg_volume': avg_volume
            }
        except Exception as e:
            logger.error(f"Volume spike detection error: {e}")
            return {'high_volume': False, 'spike_ratio': 1.0}
    
    def _extract_confidence_adjustment(self, ai_result):
        """Extract confidence adjustment from AI analysis"""
        if isinstance(ai_result, str):
            # Simple AI-based confidence boost
            if 'strong' in ai_result.lower() or 'excellent' in ai_result.lower():
                return 10
            elif 'good' in ai_result.lower() or 'bullish' in ai_result.lower():
                return 5
            elif 'bearish' in ai_result.lower() or 'weak' in ai_result.lower():
                return -5
            elif 'very bearish' in ai_result.lower() or 'dangerous' in ai_result.lower():
                return -10
        return 0
    
    def _extract_recommendation_from_ai(self, ai_result, raw_score):
        """Extract final recommendation from AI analysis"""
        if isinstance(ai_result, str):
            if 'buy' in ai_result.lower() and raw_score > 60:
                return 'BUY'
            elif 'sell' in ai_result.lower() and raw_score < 40:
                return 'SELL'
        return 'NEUTRAL'