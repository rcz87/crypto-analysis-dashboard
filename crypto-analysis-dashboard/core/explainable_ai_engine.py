"""
Explainable AI (XAI) Engine - Mengatasi Black Box Problem
Memberikan penjelasan yang dapat dipahami untuk setiap keputusan AI/ML
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ExplainableAIEngine:
    """
    Engine untuk memberikan penjelasan transparan atas keputusan AI/ML
    Mengimplementasikan SHAP-like analysis dan natural language explanation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.explanation_history = []
        self.feature_importance_cache = {}
        
        # Configuration for explanation types
        self.explanation_config = {
            'technical_indicators': {
                'RSI': 'Relative Strength Index menunjukkan momentum',
                'MACD': 'Moving Average Convergence Divergence untuk trend',
                'BB_upper': 'Bollinger Band atas untuk resistance',
                'BB_lower': 'Bollinger Band bawah untuk support',
                'volume': 'Volume trading untuk konfirmasi',
                'funding_rate': 'Funding rate untuk sentiment futures'
            },
            'market_conditions': {
                'trending': 'Pasar sedang trending',
                'ranging': 'Pasar sedang sideways/ranging',
                'volatile': 'Volatilitas tinggi terdeteksi',
                'low_volume': 'Volume rendah, signal lemah'
            },
            'risk_factors': {
                'high_volatility': 'Volatilitas tinggi = risiko tinggi',
                'low_liquidity': 'Likuiditas rendah = slippage risk',
                'news_impact': 'Berita fundamental mempengaruhi',
                'whale_activity': 'Aktivitas whale terdeteksi'
            }
        }
        
        logger.info("🔍 Explainable AI Engine initialized")
    
    def explain_trading_decision(self, 
                                signal_data: Dict[str, Any],
                                model_prediction: Dict[str, Any],
                                market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Memberikan penjelasan lengkap untuk keputusan trading
        """
        try:
            explanation = {
                'decision_id': f"exp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'signal_type': signal_data.get('signal', 'UNKNOWN'),
                'confidence': model_prediction.get('confidence', 0),
                'explanations': {},
                'risk_assessment': {},
                'actionable_insights': []
            }
            
            # 1. Feature Importance Analysis
            feature_importance = self._calculate_feature_importance(signal_data)
            explanation['explanations']['feature_importance'] = feature_importance
            
            # 2. Technical Analysis Explanation
            technical_explanation = self._explain_technical_indicators(signal_data)
            explanation['explanations']['technical_analysis'] = technical_explanation
            
            # 3. Market Context Explanation
            market_explanation = self._explain_market_context(market_context)
            explanation['explanations']['market_context'] = market_explanation
            
            # 4. Risk Assessment
            risk_assessment = self._assess_decision_risks(signal_data, market_context)
            explanation['risk_assessment'] = risk_assessment
            
            # 5. Natural Language Summary
            narrative = self._generate_narrative_explanation(explanation)
            explanation['natural_language_summary'] = narrative
            
            # 6. Actionable Insights
            insights = self._generate_actionable_insights(explanation)
            explanation['actionable_insights'] = insights
            
            # Store for analysis
            self.explanation_history.append(explanation)
            
            logger.info(f"✅ Generated explanation for {signal_data.get('signal')} signal")
            return explanation
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._generate_fallback_explanation(signal_data)
    
    def _calculate_feature_importance(self, signal_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Menghitung importance setiap feature dalam keputusan
        Menggunakan pendekatan SHAP-like untuk transparansi
        """
        try:
            features = {}
            
            # Technical indicators importance
            if 'technical_indicators' in signal_data:
                indicators = signal_data['technical_indicators']
                
                # RSI importance
                rsi = indicators.get('RSI', 50)
                if rsi < 30 or rsi > 70:
                    features['RSI'] = abs(50 - rsi) / 50 * 0.3
                else:
                    features['RSI'] = 0.1
                
                # MACD importance
                macd = indicators.get('MACD', {})
                if macd.get('signal') == 'bullish' or macd.get('signal') == 'bearish':
                    features['MACD'] = 0.25
                else:
                    features['MACD'] = 0.05
                
                # Volume importance
                volume_ratio = indicators.get('volume_ratio', 1.0)
                features['Volume'] = min(volume_ratio, 2.0) * 0.2
                
                # Bollinger Bands
                bb_position = indicators.get('bb_position', 0.5)
                features['Bollinger_Bands'] = abs(0.5 - bb_position) * 0.2
            
            # Market sentiment importance
            if 'market_sentiment' in signal_data:
                sentiment = signal_data['market_sentiment']
                sentiment_score = sentiment.get('score', 0)
                features['Market_Sentiment'] = abs(sentiment_score) * 0.15
            
            # Funding rate importance
            if 'funding_rate' in signal_data:
                funding = signal_data['funding_rate']
                if abs(funding) > 0.001:  # 0.1% threshold
                    features['Funding_Rate'] = min(abs(funding) * 100, 0.3)
                else:
                    features['Funding_Rate'] = 0.05
            
            # Normalize to sum to 1.0
            total = sum(features.values())
            if total > 0:
                features = {k: v/total for k, v in features.items()}
            
            return features
            
        except Exception as e:
            logger.error(f"Error calculating feature importance: {e}")
            return {}
    
    def _explain_technical_indicators(self, signal_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Memberikan penjelasan teknis untuk setiap indikator
        """
        explanations = {}
        
        try:
            if 'technical_indicators' not in signal_data:
                return explanations
            
            indicators = signal_data['technical_indicators']
            
            # RSI explanation
            rsi = indicators.get('RSI', 50)
            if rsi < 30:
                explanations['RSI'] = f"RSI {rsi:.1f} menunjukkan kondisi oversold - potensi bullish reversal"
            elif rsi > 70:
                explanations['RSI'] = f"RSI {rsi:.1f} menunjukkan kondisi overbought - potensi bearish reversal"
            else:
                explanations['RSI'] = f"RSI {rsi:.1f} dalam zona netral - tidak ada signal ekstrem"
            
            # MACD explanation
            macd = indicators.get('MACD', {})
            if macd.get('signal') == 'bullish':
                explanations['MACD'] = "MACD bullish crossover - momentum naik menguat"
            elif macd.get('signal') == 'bearish':
                explanations['MACD'] = "MACD bearish crossover - momentum turun menguat"
            else:
                explanations['MACD'] = "MACD dalam kondisi netral - belum ada momentum jelas"
            
            # Volume explanation
            volume_ratio = indicators.get('volume_ratio', 1.0)
            if volume_ratio > 1.5:
                explanations['Volume'] = f"Volume {volume_ratio:.1f}x lebih tinggi dari rata-rata - signal kuat"
            elif volume_ratio < 0.5:
                explanations['Volume'] = f"Volume {volume_ratio:.1f}x lebih rendah dari rata-rata - signal lemah"
            else:
                explanations['Volume'] = f"Volume {volume_ratio:.1f}x normal - konfirmasi moderate"
            
            return explanations
            
        except Exception as e:
            logger.error(f"Error explaining technical indicators: {e}")
            return {}
    
    def _explain_market_context(self, market_context: Dict[str, Any]) -> Dict[str, str]:
        """
        Menjelaskan konteks pasar yang mempengaruhi keputusan
        """
        explanations = {}
        
        try:
            # Market trend
            trend = market_context.get('trend', 'unknown')
            if trend == 'uptrend':
                explanations['Trend'] = "Pasar dalam uptrend - bias bullish untuk long positions"
            elif trend == 'downtrend':
                explanations['Trend'] = "Pasar dalam downtrend - bias bearish untuk short positions"
            else:
                explanations['Trend'] = "Pasar sideways - range trading strategy lebih cocok"
            
            # Volatility
            volatility = market_context.get('volatility', 'normal')
            if volatility == 'high':
                explanations['Volatility'] = "Volatilitas tinggi - risiko dan reward meningkat"
            elif volatility == 'low':
                explanations['Volatility'] = "Volatilitas rendah - pergerakan terbatas"
            else:
                explanations['Volatility'] = "Volatilitas normal - kondisi trading standar"
            
            # News sentiment
            if 'news_sentiment' in market_context:
                news = market_context['news_sentiment']
                sentiment = news.get('overall_sentiment', 'NEUTRAL')
                explanations['News'] = f"Sentiment berita {sentiment} - mempengaruhi market psychology"
            
            # Funding rate context
            if 'funding_rate' in market_context:
                funding = market_context['funding_rate']
                if funding > 0.001:
                    explanations['Funding'] = f"Funding rate tinggi {funding:.4f}% - long bias kuat, potensi koreksi"
                elif funding < -0.001:
                    explanations['Funding'] = f"Funding rate negatif {funding:.4f}% - short bias kuat, potensi bounce"
                else:
                    explanations['Funding'] = f"Funding rate normal {funding:.4f}% - sentiment seimbang"
            
            return explanations
            
        except Exception as e:
            logger.error(f"Error explaining market context: {e}")
            return {}
    
    def _assess_decision_risks(self, signal_data: Dict[str, Any], market_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Menilai risiko dari keputusan trading
        """
        try:
            risk_assessment = {
                'overall_risk': 'medium',
                'risk_factors': [],
                'risk_score': 0.5,
                'mitigation_suggestions': []
            }
            
            risk_score = 0.5  # Base risk
            risk_factors = []
            
            # Volatility risk
            volatility = market_context.get('volatility', 'normal')
            if volatility == 'high':
                risk_score += 0.2
                risk_factors.append("High volatility increases position risk")
                risk_assessment['mitigation_suggestions'].append("Reduce position size due to high volatility")
            
            # Volume risk
            if 'technical_indicators' in signal_data:
                volume_ratio = signal_data['technical_indicators'].get('volume_ratio', 1.0)
                if volume_ratio < 0.5:
                    risk_score += 0.15
                    risk_factors.append("Low volume may indicate weak signal")
                    risk_assessment['mitigation_suggestions'].append("Wait for volume confirmation")
            
            # News risk
            if 'news_sentiment' in market_context:
                news_confidence = market_context['news_sentiment'].get('confidence', 0.5)
                if news_confidence < 0.3:
                    risk_score += 0.1
                    risk_factors.append("Uncertain news sentiment")
            
            # Funding rate extremes
            funding = market_context.get('funding_rate', 0)
            if abs(funding) > 0.002:  # 0.2% threshold
                risk_score += 0.15
                risk_factors.append("Extreme funding rate indicates potential reversal")
                risk_assessment['mitigation_suggestions'].append("Monitor for position crowding reversal")
            
            # Determine overall risk level
            if risk_score < 0.3:
                risk_assessment['overall_risk'] = 'low'
            elif risk_score < 0.7:
                risk_assessment['overall_risk'] = 'medium'
            else:
                risk_assessment['overall_risk'] = 'high'
                risk_assessment['mitigation_suggestions'].append("Consider avoiding this trade due to high risk")
            
            risk_assessment['risk_score'] = min(risk_score, 1.0)
            risk_assessment['risk_factors'] = risk_factors
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return {'overall_risk': 'unknown', 'risk_factors': [], 'risk_score': 0.5}
    
    def _generate_narrative_explanation(self, explanation: Dict[str, Any]) -> str:
        """
        Menghasilkan penjelasan dalam bahasa natural yang mudah dipahami
        """
        try:
            signal_type = explanation.get('signal_type', 'UNKNOWN')
            confidence = explanation.get('confidence', 0)
            risk_level = explanation.get('risk_assessment', {}).get('overall_risk', 'medium')
            
            # Base narrative
            narrative = f"Signal {signal_type} dengan confidence {confidence:.1%} dan risk level {risk_level}.\n\n"
            
            # Add technical explanation
            tech_explanations = explanation.get('explanations', {}).get('technical_analysis', {})
            if tech_explanations:
                narrative += "Analisis Teknikal:\n"
                for indicator, desc in tech_explanations.items():
                    narrative += f"• {indicator}: {desc}\n"
                narrative += "\n"
            
            # Add market context
            market_explanations = explanation.get('explanations', {}).get('market_context', {})
            if market_explanations:
                narrative += "Konteks Pasar:\n"
                for context, desc in market_explanations.items():
                    narrative += f"• {context}: {desc}\n"
                narrative += "\n"
            
            # Add risk factors
            risk_factors = explanation.get('risk_assessment', {}).get('risk_factors', [])
            if risk_factors:
                narrative += "Faktor Risiko:\n"
                for risk in risk_factors:
                    narrative += f"• {risk}\n"
                narrative += "\n"
            
            # Add recommendations
            insights = explanation.get('actionable_insights', [])
            if insights:
                narrative += "Rekomendasi:\n"
                for insight in insights:
                    narrative += f"• {insight}\n"
            
            return narrative.strip()
            
        except Exception as e:
            logger.error(f"Error generating narrative: {e}")
            return f"Error generating explanation for {signal_type} signal"
    
    def _generate_actionable_insights(self, explanation: Dict[str, Any]) -> List[str]:
        """
        Menghasilkan insight yang dapat ditindaklanjuti
        """
        insights = []
        
        try:
            signal_type = explanation.get('signal_type', '')
            confidence = explanation.get('confidence', 0)
            risk_level = explanation.get('risk_assessment', {}).get('overall_risk', 'medium')
            
            # Confidence-based insights
            if confidence > 0.8:
                insights.append("High confidence signal - consider larger position size")
            elif confidence < 0.6:
                insights.append("Low confidence signal - reduce position size or wait for confirmation")
            
            # Risk-based insights
            if risk_level == 'high':
                insights.append("High risk detected - use tight stop loss and smaller position")
            elif risk_level == 'low':
                insights.append("Low risk environment - good opportunity for standard position sizing")
            
            # Signal-specific insights
            if signal_type == 'BUY':
                insights.append("Look for support levels for entry and stop loss placement")
            elif signal_type == 'SELL':
                insights.append("Look for resistance levels for entry and stop loss placement")
            
            # Add mitigation suggestions from risk assessment
            mitigation = explanation.get('risk_assessment', {}).get('mitigation_suggestions', [])
            insights.extend(mitigation)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return ["Unable to generate actionable insights"]
    
    def _generate_fallback_explanation(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback explanation jika terjadi error
        """
        return {
            'decision_id': f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'timestamp': datetime.now().isoformat(),
            'signal_type': signal_data.get('signal', 'UNKNOWN'),
            'confidence': signal_data.get('confidence', 0),
            'natural_language_summary': "Unable to generate detailed explanation due to system error",
            'actionable_insights': ["Monitor signal performance and adjust accordingly"],
            'risk_assessment': {'overall_risk': 'unknown', 'risk_score': 0.5}
        }
    
    def get_explanation_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Analisis performa explanation untuk improvement
        """
        try:
            cutoff_date = datetime.now() - pd.Timedelta(days=days)
            recent_explanations = [
                exp for exp in self.explanation_history 
                if datetime.fromisoformat(exp['timestamp']) > cutoff_date
            ]
            
            if not recent_explanations:
                return {'message': 'No explanations in the specified period'}
            
            analytics = {
                'total_explanations': len(recent_explanations),
                'avg_confidence': np.mean([exp.get('confidence', 0) for exp in recent_explanations]),
                'risk_distribution': {},
                'signal_distribution': {},
                'top_features': {}
            }
            
            # Risk distribution
            risks = [exp.get('risk_assessment', {}).get('overall_risk', 'unknown') for exp in recent_explanations]
            analytics['risk_distribution'] = {risk: risks.count(risk) for risk in set(risks)}
            
            # Signal distribution
            signals = [exp.get('signal_type', 'UNKNOWN') for exp in recent_explanations]
            analytics['signal_distribution'] = {signal: signals.count(signal) for signal in set(signals)}
            
            # Feature importance aggregation
            all_features = {}
            for exp in recent_explanations:
                features = exp.get('explanations', {}).get('feature_importance', {})
                for feature, importance in features.items():
                    if feature not in all_features:
                        all_features[feature] = []
                    all_features[feature].append(importance)
            
            analytics['top_features'] = {
                feature: np.mean(importances) 
                for feature, importances in all_features.items()
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating explanation analytics: {e}")
            return {'error': str(e)}

# Create singleton instance
explainable_ai = ExplainableAIEngine()