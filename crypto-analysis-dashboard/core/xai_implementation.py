#!/usr/bin/env python3
"""
XAI (Explainable AI) Implementation using SHAP
Mengatasi Black Box Problem dengan penjelasan yang mudah dipahami
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False
    logging.warning("SHAP not available. Install with: pip install shap")

@dataclass
class ExplanationResult:
    """Hasil penjelasan AI yang user-friendly"""
    decision: str  # BUY/SELL/HOLD
    confidence: float
    top_factors: List[Dict[str, Any]]  # Factor paling berpengaruh
    simple_explanation: str  # Penjelasan dalam bahasa sederhana
    risk_level: str  # LOW/MEDIUM/HIGH
    technical_details: Optional[Dict] = None

class XAIEngine:
    """
    Explainable AI Engine untuk menjelaskan keputusan trading
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feature_names_mapping = {
            'rsi': 'RSI (Relative Strength Index)',
            'macd': 'MACD (Trend Indicator)',
            'volume': 'Volume Perdagangan',
            'price_change': 'Perubahan Harga',
            'bb_position': 'Posisi Bollinger Band',
            'funding_rate': 'Funding Rate',
            'open_interest': 'Open Interest',
            'smc_signal': 'Smart Money Concept',
            'market_sentiment': 'Sentimen Pasar',
            'news_sentiment': 'Sentimen Berita'
        }
        
    def explain_prediction(self, 
                          model,
                          features: np.ndarray,
                          feature_names: List[str],
                          prediction: Dict[str, Any]) -> ExplanationResult:
        """
        Jelaskan prediksi model dengan SHAP atau fallback method
        """
        if SHAP_AVAILABLE and hasattr(model, 'predict'):
            return self._explain_with_shap(model, features, feature_names, prediction)
        else:
            return self._explain_with_feature_importance(features, feature_names, prediction)
    
    def _explain_with_shap(self, model, features: np.ndarray, 
                          feature_names: List[str], 
                          prediction: Dict[str, Any]) -> ExplanationResult:
        """
        Gunakan SHAP untuk penjelasan mendalam
        """
        try:
            # Create SHAP explainer
            if hasattr(model, 'tree_'):  # Tree-based model
                explainer = shap.TreeExplainer(model)
            else:
                explainer = shap.KernelExplainer(model.predict, features[:100])
            
            # Calculate SHAP values
            shap_values = explainer.shap_values(features[-1:])
            
            if isinstance(shap_values, list):
                shap_values = shap_values[0]
            
            # Get feature importance
            feature_importance = []
            for i, (name, value) in enumerate(zip(feature_names, shap_values[0])):
                readable_name = self.feature_names_mapping.get(name, name)
                feature_importance.append({
                    'feature': readable_name,
                    'impact': float(value),
                    'value': float(features[-1][i]),
                    'direction': 'positive' if value > 0 else 'negative'
                })
            
            # Sort by absolute impact
            feature_importance.sort(key=lambda x: abs(x['impact']), reverse=True)
            top_factors = feature_importance[:5]
            
            # Generate explanation
            explanation = self._generate_simple_explanation(
                prediction, top_factors, feature_importance
            )
            
            return ExplanationResult(
                decision=prediction.get('signal', 'HOLD'),
                confidence=prediction.get('confidence', 0.5),
                top_factors=top_factors,
                simple_explanation=explanation,
                risk_level=self._calculate_risk_level(prediction, feature_importance),
                technical_details={'shap_values': shap_values.tolist()}
            )
            
        except Exception as e:
            self.logger.error(f"SHAP explanation failed: {e}")
            return self._explain_with_feature_importance(features, feature_names, prediction)
    
    def _explain_with_feature_importance(self, 
                                       features: np.ndarray,
                                       feature_names: List[str],
                                       prediction: Dict[str, Any]) -> ExplanationResult:
        """
        Fallback explanation menggunakan feature importance sederhana
        """
        # Analisis nilai features
        feature_values = features[-1] if features.ndim > 1 else features
        
        # Create feature importance based on values
        feature_importance = []
        for i, (name, value) in enumerate(zip(feature_names, feature_values)):
            readable_name = self.feature_names_mapping.get(name, name)
            
            # Simple heuristic for importance
            if name == 'rsi':
                importance = abs(value - 50) / 50  # Distance from neutral
                direction = 'oversold' if value < 30 else 'overbought' if value > 70 else 'neutral'
            elif name == 'volume':
                importance = min(value / 2, 1.0)  # Normalize volume impact
                direction = 'high' if value > 1.5 else 'normal'
            elif name == 'funding_rate':
                importance = abs(value) * 10  # Amplify funding rate impact
                direction = 'positive' if value > 0 else 'negative'
            else:
                importance = abs(value) / (abs(value) + 1)  # Sigmoid-like
                direction = 'positive' if value > 0 else 'negative'
            
            feature_importance.append({
                'feature': readable_name,
                'impact': importance,
                'value': float(value),
                'direction': direction
            })
        
        # Sort by impact
        feature_importance.sort(key=lambda x: x['impact'], reverse=True)
        top_factors = feature_importance[:5]
        
        # Generate explanation
        explanation = self._generate_simple_explanation(
            prediction, top_factors, feature_importance
        )
        
        return ExplanationResult(
            decision=prediction.get('signal', 'HOLD'),
            confidence=prediction.get('confidence', 0.5),
            top_factors=top_factors,
            simple_explanation=explanation,
            risk_level=self._calculate_risk_level(prediction, feature_importance)
        )
    
    def _generate_simple_explanation(self, 
                                   prediction: Dict,
                                   top_factors: List[Dict],
                                   all_factors: List[Dict]) -> str:
        """
        Generate penjelasan dalam bahasa sederhana
        """
        signal = prediction.get('signal', 'HOLD')
        confidence = prediction.get('confidence', 0.5)
        
        # Start with signal
        if signal == 'BUY':
            explanation = f"Rekomendasi BELI dengan confidence {confidence:.1%} karena:\n"
        elif signal == 'SELL':
            explanation = f"Rekomendasi JUAL dengan confidence {confidence:.1%} karena:\n"
        else:
            explanation = f"Rekomendasi HOLD (tunggu) dengan confidence {confidence:.1%} karena:\n"
        
        # Add top factors
        for i, factor in enumerate(top_factors[:3], 1):
            feature = factor['feature']
            value = factor['value']
            direction = factor['direction']
            
            if 'RSI' in feature:
                if direction == 'oversold':
                    explanation += f"{i}. RSI menunjukkan oversold ({value:.1f}), potensi rebound\n"
                elif direction == 'overbought':
                    explanation += f"{i}. RSI menunjukkan overbought ({value:.1f}), potensi koreksi\n"
                else:
                    explanation += f"{i}. RSI netral ({value:.1f})\n"
                    
            elif 'Volume' in feature:
                if direction == 'high':
                    explanation += f"{i}. Volume tinggi ({value:.1f}x normal), momentum kuat\n"
                else:
                    explanation += f"{i}. Volume normal, tidak ada tekanan khusus\n"
                    
            elif 'Funding' in feature:
                if direction == 'positive':
                    explanation += f"{i}. Funding rate positif ({value:.4f}), long dominan\n"
                else:
                    explanation += f"{i}. Funding rate negatif ({value:.4f}), short dominan\n"
                    
            elif 'MACD' in feature:
                if direction == 'positive':
                    explanation += f"{i}. MACD bullish, trend naik\n"
                else:
                    explanation += f"{i}. MACD bearish, trend turun\n"
                    
            else:
                explanation += f"{i}. {feature}: {direction}\n"
        
        # Add risk warning if needed
        risk_factors = [f for f in all_factors if f['feature'] in ['Funding Rate', 'Open Interest']]
        if any(abs(f['value']) > 0.01 for f in risk_factors):
            explanation += "\n⚠️ Perhatian: Ada indikasi leverage tinggi di market"
        
        return explanation
    
    def _calculate_risk_level(self, 
                            prediction: Dict,
                            factors: List[Dict]) -> str:
        """
        Hitung level risiko berdasarkan faktor-faktor
        """
        risk_score = 0
        
        # Check confidence
        confidence = prediction.get('confidence', 0.5)
        if confidence < 0.6:
            risk_score += 2
        elif confidence < 0.7:
            risk_score += 1
        
        # Check volatility indicators
        for factor in factors:
            if 'Volume' in factor['feature'] and factor['value'] > 2:
                risk_score += 1
            if 'Funding' in factor['feature'] and abs(factor['value']) > 0.01:
                risk_score += 2
            if 'RSI' in factor['feature']:
                if factor['value'] < 20 or factor['value'] > 80:
                    risk_score += 2
        
        # Determine risk level
        if risk_score <= 2:
            return "LOW"
        elif risk_score <= 4:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def format_for_telegram(self, explanation: ExplanationResult) -> str:
        """
        Format penjelasan untuk Telegram dengan HTML
        """
        html = f"<b>📊 Analisis AI - {explanation.decision}</b>\n"
        html += f"<b>Confidence:</b> {explanation.confidence:.1%}\n"
        html += f"<b>Risk Level:</b> {explanation.risk_level}\n\n"
        
        html += f"<b>📝 Penjelasan:</b>\n{explanation.simple_explanation}\n\n"
        
        html += "<b>🎯 Faktor Utama:</b>\n"
        for factor in explanation.top_factors[:3]:
            impact_bar = "▓" * int(abs(factor['impact']) * 10)
            html += f"• {factor['feature']}: {impact_bar} "
            html += f"({factor['direction']})\n"
        
        return html
    
    def format_for_gpts(self, explanation: ExplanationResult) -> Dict:
        """
        Format penjelasan untuk GPTs API response
        """
        return {
            "decision": explanation.decision,
            "confidence": explanation.confidence,
            "risk_level": explanation.risk_level,
            "explanation": explanation.simple_explanation,
            "top_factors": [
                {
                    "name": f['feature'],
                    "impact": f['impact'],
                    "direction": f['direction']
                } for f in explanation.top_factors[:5]
            ],
            "technical_details": explanation.technical_details if explanation.technical_details else {}
        }

# Singleton instance
xai_engine = XAIEngine()

# Example usage
if __name__ == "__main__":
    # Test dengan dummy data
    features = np.array([[25, 0.5, 1.8, 0.02, -0.3, 0.001, 1000000, 1, 0.7, 0.8]])
    feature_names = ['rsi', 'macd', 'volume', 'price_change', 'bb_position', 
                     'funding_rate', 'open_interest', 'smc_signal', 
                     'market_sentiment', 'news_sentiment']
    
    prediction = {
        'signal': 'BUY',
        'confidence': 0.75,
        'price': 50000
    }
    
    # Explain
    explanation = xai_engine.explain_prediction(
        model=None,  # Would be actual model
        features=features,
        feature_names=feature_names,
        prediction=prediction
    )
    
    # Print results
    print("Simple Explanation:")
    print(explanation.simple_explanation)
    print("\nTelegram Format:")
    print(xai_engine.format_for_telegram(explanation))
    print("\nGPTs Format:")
    print(json.dumps(xai_engine.format_for_gpts(explanation), indent=2))