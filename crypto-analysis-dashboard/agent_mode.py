#!/usr/bin/env python3
"""
🤖 Agent Mode - Multi Role Agent System for Cryptocurrency Trading
Modular agent system untuk analisis sinyal trading dengan delegation ke peran spesifik
"""

import json
import random
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TechnicalAnalyst:
    """Agent untuk analisis teknikal & Smart Money Concepts (SMC)"""
    
    def __init__(self):
        self.name = "TechnicalAnalyst"
        logger.info(f"🔍 {self.name} initialized")
    
    def analyze(self, symbol: str, timeframe: str, market_data: Dict) -> Dict[str, Any]:
        """Analisis teknikal lengkap dengan SMC indicators"""
        try:
            price_data = market_data.get('price_data', {})
            current_price = price_data.get('close', 0)
            high = price_data.get('high', 0)
            low = price_data.get('low', 0)
            volume = market_data.get('volume', 0)
            
            # SMC Analysis
            smc_analysis = self._analyze_smc(price_data, timeframe)
            
            # Technical Indicators
            technical_indicators = self._calculate_indicators(price_data)
            
            # Trend Analysis
            trend_analysis = self._analyze_trend(price_data, timeframe)
            
            # Support/Resistance Levels
            sr_levels = self._calculate_support_resistance(price_data)
            
            # Overall Technical Score
            technical_score = self._calculate_technical_score(
                smc_analysis, technical_indicators, trend_analysis
            )
            
            return {
                'agent': self.name,
                'symbol': symbol,
                'timeframe': timeframe,
                'current_price': current_price,
                'smc_analysis': smc_analysis,
                'technical_indicators': technical_indicators,
                'trend_analysis': trend_analysis,
                'support_resistance': sr_levels,
                'technical_score': technical_score,
                'confidence': min(max(technical_score, 0), 100),
                'recommendation': self._get_technical_recommendation(technical_score),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name} analysis error: {e}")
            return self._error_response(symbol, timeframe, str(e))
    
    def _analyze_smc(self, price_data: Dict, timeframe: str) -> Dict[str, Any]:
        """Smart Money Concepts analysis"""
        current_price = price_data.get('close', 0)
        high = price_data.get('high', 0)
        low = price_data.get('low', 0)
        
        # Mock SMC indicators dengan logic realistis
        price_range = high - low if high > low else 1
        volatility_factor = price_range / current_price if current_price > 0 else 0.01
        
        # Change of Character (CHoCH) detection
        choch_detected = volatility_factor > 0.02 and random.random() > 0.6
        
        # Break of Structure (BOS) detection  
        bos_detected = volatility_factor > 0.015 and random.random() > 0.7
        
        # Order Block identification
        order_block_strength = min(volatility_factor * 100, 85) if volatility_factor > 0.01 else 20
        
        # Fair Value Gap (FVG)
        fvg_identified = price_range > (current_price * 0.005) and random.random() > 0.5
        
        # Liquidity levels
        liquidity_sweep = {
            'internal_liquidity': random.choice([True, False]),
            'external_liquidity': random.choice([True, False]),
            'sweep_type': random.choice(['IRL', 'ERL', 'NONE'])
        }
        
        return {
            'choch_detected': choch_detected,
            'bos_detected': bos_detected,
            'order_block_strength': round(order_block_strength, 1),
            'fvg_identified': fvg_identified,
            'liquidity_sweep': liquidity_sweep,
            'market_structure': 'BULLISH' if (choch_detected or bos_detected) and current_price > (high + low) / 2 else 'BEARISH',
            'premium_discount': 'PREMIUM' if current_price > (high + low) / 2 else 'DISCOUNT'
        }
    
    def _calculate_indicators(self, price_data: Dict) -> Dict[str, Any]:
        """Calculate technical indicators"""
        current_price = price_data.get('close', 0)
        high = price_data.get('high', 0)
        low = price_data.get('low', 0)
        
        # Mock indicators dengan nilai realistis
        return {
            'rsi': random.randint(25, 75),
            'macd': {
                'signal': round(random.uniform(-0.5, 0.5), 4),
                'histogram': round(random.uniform(-0.3, 0.3), 4),
                'trend': random.choice(['BULLISH', 'BEARISH', 'NEUTRAL'])
            },
            'bollinger_bands': {
                'upper': round(current_price * random.uniform(1.02, 1.05), 2),
                'middle': current_price,
                'lower': round(current_price * random.uniform(0.95, 0.98), 2),
                'position': random.choice(['UPPER', 'MIDDLE', 'LOWER'])
            },
            'moving_averages': {
                'ema_20': round(current_price * random.uniform(0.98, 1.02), 2),
                'ema_50': round(current_price * random.uniform(0.96, 1.04), 2),
                'sma_200': round(current_price * random.uniform(0.92, 1.08), 2)
            }
        }
    
    def _analyze_trend(self, price_data: Dict, timeframe: str) -> Dict[str, Any]:
        """Analyze market trend"""
        # Simulate trend analysis based on timeframe
        trend_strength = random.randint(40, 95)
        trend_direction = random.choice(['UPTREND', 'DOWNTREND', 'SIDEWAYS'])
        
        return {
            'direction': trend_direction,
            'strength': trend_strength,
            'timeframe': timeframe,
            'duration': random.choice(['SHORT', 'MEDIUM', 'LONG']),
            'momentum': random.choice(['ACCELERATING', 'STEADY', 'WEAKENING'])
        }
    
    def _calculate_support_resistance(self, price_data: Dict) -> Dict[str, Any]:
        """Calculate support and resistance levels"""
        current_price = price_data.get('close', 0)
        
        return {
            'resistance_levels': [
                round(current_price * 1.02, 2),
                round(current_price * 1.05, 2),
                round(current_price * 1.08, 2)
            ],
            'support_levels': [
                round(current_price * 0.98, 2),
                round(current_price * 0.95, 2),
                round(current_price * 0.92, 2)
            ],
            'key_level': round(current_price * random.choice([0.97, 1.03]), 2),
            'level_type': random.choice(['PSYCHOLOGICAL', 'TECHNICAL', 'HISTORICAL'])
        }
    
    def _calculate_technical_score(self, smc: Dict, indicators: Dict, trend: Dict) -> float:
        """Calculate overall technical score (0-100)"""
        score = 50.0  # Base score
        
        # SMC contribution (30%)
        if smc.get('bos_detected'):
            score += 15
        if smc.get('choch_detected'):
            score += 10
        if smc.get('order_block_strength', 0) > 60:
            score += 5
        
        # Trend contribution (40%)
        trend_strength = trend.get('strength', 50)
        score += (trend_strength - 50) * 0.4
        
        # Indicators contribution (30%)
        rsi = indicators.get('rsi', 50)
        if 30 <= rsi <= 70:  # Not oversold/overbought
            score += 10
        
        macd_trend = indicators.get('macd', {}).get('trend', 'NEUTRAL')
        if macd_trend in ['BULLISH', 'BEARISH']:
            score += 5
        
        return min(max(score, 0), 100)
    
    def _get_technical_recommendation(self, score: float) -> str:
        """Get recommendation based on technical score"""
        if score >= 75:
            return 'STRONG_BUY' if random.random() > 0.5 else 'STRONG_SELL'
        elif score >= 60:
            return 'BUY' if random.random() > 0.5 else 'SELL'
        elif score >= 40:
            return 'WEAK_BUY' if random.random() > 0.5 else 'WEAK_SELL'
        else:
            return 'WAIT'
    
    def _error_response(self, symbol: str, timeframe: str, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            'agent': self.name,
            'symbol': symbol,
            'timeframe': timeframe,
            'error': error,
            'confidence': 0,
            'recommendation': 'ERROR',
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }


class SentimentWatcher:
    """Agent untuk analisis sentimen market & funding rate"""
    
    def __init__(self):
        self.name = "SentimentWatcher"
        logger.info(f"📊 {self.name} initialized")
    
    def analyze(self, symbol: str, timeframe: str, market_data: Dict) -> Dict[str, Any]:
        """Analisis sentimen market lengkap"""
        try:
            # Funding rate analysis
            funding_analysis = self._analyze_funding_rate(market_data)
            
            # Open interest analysis
            oi_analysis = self._analyze_open_interest(market_data)
            
            # Market sentiment scoring
            sentiment_score = self._calculate_sentiment_score(funding_analysis, oi_analysis)
            
            # Social sentiment (mock)
            social_sentiment = self._get_social_sentiment()
            
            return {
                'agent': self.name,
                'symbol': symbol,
                'timeframe': timeframe,
                'funding_analysis': funding_analysis,
                'open_interest_analysis': oi_analysis,
                'social_sentiment': social_sentiment,
                'sentiment_score': sentiment_score,
                'confidence': min(max(sentiment_score, 0), 100),
                'recommendation': self._get_sentiment_recommendation(sentiment_score),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name} analysis error: {e}")
            return self._error_response(symbol, timeframe, str(e))
    
    def _analyze_funding_rate(self, market_data: Dict) -> Dict[str, Any]:
        """Analyze funding rate untuk sentiment"""
        # Mock realistic funding rate data
        funding_rate = round(random.uniform(-0.01, 0.05), 6)  # -1% to 5% annualized
        
        # Determine funding pressure
        if funding_rate > 0.03:
            pressure = 'EXTREME_BULLISH'
            warning = True
        elif funding_rate > 0.01:
            pressure = 'BULLISH'
            warning = False
        elif funding_rate > -0.005:
            pressure = 'NEUTRAL'
            warning = False
        else:
            pressure = 'BEARISH'
            warning = False
        
        return {
            'current_rate': funding_rate,
            'pressure': pressure,
            'overheat_warning': warning,
            'historical_percentile': random.randint(15, 95),
            'next_funding_in_hours': random.randint(1, 8),
            'interpretation': self._interpret_funding(funding_rate, pressure)
        }
    
    def _analyze_open_interest(self, market_data: Dict) -> Dict[str, Any]:
        """Analyze open interest trends"""
        current_oi = random.randint(500000, 2000000)  # Mock OI in USD
        oi_change_24h = round(random.uniform(-15, 25), 2)  # % change
        
        trend = 'INCREASING' if oi_change_24h > 5 else 'DECREASING' if oi_change_24h < -5 else 'STABLE'
        
        return {
            'current_oi_usd': current_oi,
            'change_24h_percent': oi_change_24h,
            'trend': trend,
            'significance': 'HIGH' if abs(oi_change_24h) > 15 else 'MEDIUM' if abs(oi_change_24h) > 8 else 'LOW',
            'interpretation': self._interpret_oi(oi_change_24h, trend)
        }
    
    def _get_social_sentiment(self) -> Dict[str, Any]:
        """Get social media sentiment (mock)"""
        sentiment_score = random.randint(20, 80)
        
        return {
            'overall_score': sentiment_score,
            'bias': 'BULLISH' if sentiment_score > 60 else 'BEARISH' if sentiment_score < 40 else 'NEUTRAL',
            'fear_greed_index': random.randint(10, 90),
            'social_volume': random.choice(['HIGH', 'MEDIUM', 'LOW']),
            'trending_topics': random.sample(['breakout', 'accumulation', 'selloff', 'FOMO', 'correction'], 2)
        }
    
    def _calculate_sentiment_score(self, funding: Dict, oi: Dict) -> float:
        """Calculate overall sentiment score"""
        score = 50.0  # Base neutral
        
        # Funding rate impact (40%)
        funding_rate = funding.get('current_rate', 0)
        if funding_rate > 0.02:
            score += 20  # Very bullish funding
        elif funding_rate > 0.005:
            score += 10  # Moderately bullish
        elif funding_rate < -0.005:
            score -= 15  # Bearish funding
        
        # Open interest impact (35%)
        oi_change = oi.get('change_24h_percent', 0)
        if oi_change > 10:
            score += 15  # Strong interest increase
        elif oi_change > 5:
            score += 8
        elif oi_change < -10:
            score -= 12  # Interest declining
        
        # Social sentiment impact (25%)
        social_score = self._get_social_sentiment().get('overall_score', 50)
        score += (social_score - 50) * 0.25
        
        return min(max(score, 0), 100)
    
    def _interpret_funding(self, rate: float, pressure: str) -> str:
        """Interpret funding rate"""
        if pressure == 'EXTREME_BULLISH':
            return "Funding rate sangat tinggi, kemungkinan reversal bearish"
        elif pressure == 'BULLISH':
            return "Funding rate positif, sentiment bullish dominan"
        elif pressure == 'NEUTRAL':
            return "Funding rate normal, sentiment seimbang"
        else:
            return "Funding rate negatif, long bias berkurang"
    
    def _interpret_oi(self, change: float, trend: str) -> str:
        """Interpret open interest"""
        if trend == 'INCREASING' and change > 15:
            return "OI meningkat signifikan, momentum kuat"
        elif trend == 'INCREASING':
            return "OI meningkat, interest growing"
        elif trend == 'DECREASING' and change < -15:
            return "OI turun drastis, momentum melemah"
        elif trend == 'DECREASING':
            return "OI menurun, interest declining"
        else:
            return "OI stabil, market konsolidasi"
    
    def _get_sentiment_recommendation(self, score: float) -> str:
        """Get recommendation based on sentiment score"""
        if score >= 75:
            return 'BULLISH'
        elif score >= 60:
            return 'MODERATE_BULLISH'
        elif score >= 40:
            return 'NEUTRAL'
        elif score >= 25:
            return 'MODERATE_BEARISH'
        else:
            return 'BEARISH'
    
    def _error_response(self, symbol: str, timeframe: str, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            'agent': self.name,
            'symbol': symbol,
            'timeframe': timeframe,
            'error': error,
            'confidence': 0,
            'recommendation': 'ERROR',
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }


class RiskManager:
    """Agent untuk manajemen risiko & position sizing"""
    
    def __init__(self):
        self.name = "RiskManager"
        self.default_account_balance = 1000.0  # Default USD
        self.max_risk_per_trade = 0.02  # 2% max risk
        logger.info(f"⚖️ {self.name} initialized")
    
    def analyze(self, symbol: str, timeframe: str, market_data: Dict, 
                account_balance: float = None, risk_tolerance: float = None) -> Dict[str, Any]:
        """Analisis manajemen risiko lengkap"""
        try:
            balance = account_balance or self.default_account_balance
            risk_pct = risk_tolerance or self.max_risk_per_trade
            
            price_data = market_data.get('price_data', {})
            current_price = price_data.get('close', 0)
            
            # Position sizing calculation
            position_sizing = self._calculate_position_size(balance, risk_pct, current_price)
            
            # Stop loss & take profit levels
            sl_tp_levels = self._calculate_sl_tp_levels(current_price, timeframe)
            
            # Risk metrics
            risk_metrics = self._calculate_risk_metrics(
                balance, position_sizing, sl_tp_levels, current_price
            )
            
            # Leverage recommendations
            leverage_rec = self._recommend_leverage(timeframe, risk_pct)
            
            return {
                'agent': self.name,
                'symbol': symbol,
                'timeframe': timeframe,
                'account_balance': balance,
                'risk_tolerance_percent': risk_pct * 100,
                'position_sizing': position_sizing,
                'sl_tp_levels': sl_tp_levels,
                'risk_metrics': risk_metrics,
                'leverage_recommendation': leverage_rec,
                'confidence': self._calculate_risk_confidence(risk_metrics),
                'recommendation': self._get_risk_recommendation(risk_metrics),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name} analysis error: {e}")
            return self._error_response(symbol, timeframe, str(e))
    
    def _calculate_position_size(self, balance: float, risk_pct: float, price: float) -> Dict[str, Any]:
        """Calculate optimal position size"""
        risk_amount = balance * risk_pct
        
        # Estimate stop loss distance (2-5% depending on volatility)
        sl_distance_pct = random.uniform(0.02, 0.05)
        sl_distance_usd = price * sl_distance_pct
        
        # Position size calculation
        position_size_usd = risk_amount / sl_distance_pct if sl_distance_pct > 0 else balance * 0.1
        position_size_units = position_size_usd / price if price > 0 else 0
        
        return {
            'risk_amount_usd': round(risk_amount, 2),
            'position_size_usd': round(position_size_usd, 2),
            'position_size_units': round(position_size_units, 6),
            'stop_loss_distance_percent': round(sl_distance_pct * 100, 2),
            'stop_loss_distance_usd': round(sl_distance_usd, 2),
            'position_as_percent_of_balance': round((position_size_usd / balance) * 100, 2)
        }
    
    def _calculate_sl_tp_levels(self, current_price: float, timeframe: str) -> Dict[str, Any]:
        """Calculate stop loss and take profit levels"""
        # Timeframe-based risk/reward adjustments
        timeframe_multipliers = {
            '1m': 0.5, '5m': 0.7, '15m': 1.0, '30m': 1.2,
            '1h': 1.5, '4h': 2.0, '1d': 3.0
        }
        
        multiplier = timeframe_multipliers.get(timeframe, 1.0)
        
        # Calculate levels based on volatility
        base_sl_pct = random.uniform(0.015, 0.035) * multiplier
        base_tp_pct = base_sl_pct * random.uniform(1.5, 3.0)  # Risk:Reward 1.5:1 to 3:1
        
        # For both long and short scenarios
        long_levels = {
            'stop_loss': round(current_price * (1 - base_sl_pct), 6),
            'take_profit_1': round(current_price * (1 + base_tp_pct * 0.6), 6),
            'take_profit_2': round(current_price * (1 + base_tp_pct), 6),
            'risk_reward_ratio': round(base_tp_pct / base_sl_pct, 2)
        }
        
        short_levels = {
            'stop_loss': round(current_price * (1 + base_sl_pct), 6),
            'take_profit_1': round(current_price * (1 - base_tp_pct * 0.6), 6),
            'take_profit_2': round(current_price * (1 - base_tp_pct), 6),
            'risk_reward_ratio': round(base_tp_pct / base_sl_pct, 2)
        }
        
        return {
            'current_price': current_price,
            'long_scenario': long_levels,
            'short_scenario': short_levels,
            'timeframe_applied': timeframe,
            'volatility_adjustment': round(multiplier, 2)
        }
    
    def _calculate_risk_metrics(self, balance: float, position: Dict, levels: Dict, price: float) -> Dict[str, Any]:
        """Calculate comprehensive risk metrics"""
        position_size = position.get('position_size_usd', 0)
        risk_amount = position.get('risk_amount_usd', 0)
        
        # Portfolio impact
        portfolio_exposure = (position_size / balance) * 100
        
        # Maximum drawdown potential
        max_loss_pct = (risk_amount / balance) * 100
        
        # Kelly Criterion (simplified)
        win_rate = random.uniform(0.45, 0.65)  # Assume 45-65% win rate
        avg_win_loss_ratio = levels.get('long_scenario', {}).get('risk_reward_ratio', 2.0)
        kelly_percent = ((win_rate * avg_win_loss_ratio) - (1 - win_rate)) / avg_win_loss_ratio
        
        return {
            'portfolio_exposure_percent': round(portfolio_exposure, 2),
            'max_loss_percent': round(max_loss_pct, 2),
            'risk_reward_ratio': avg_win_loss_ratio,
            'kelly_criterion_percent': round(max(0, kelly_percent * 100), 2),
            'position_vs_kelly': round(portfolio_exposure / (kelly_percent * 100), 2) if kelly_percent > 0 else 0,
            'risk_level': self._assess_risk_level(portfolio_exposure, max_loss_pct),
            'warnings': self._generate_risk_warnings(portfolio_exposure, max_loss_pct, kelly_percent)
        }
    
    def _recommend_leverage(self, timeframe: str, risk_pct: float) -> Dict[str, Any]:
        """Recommend leverage based on timeframe and risk tolerance"""
        # Conservative leverage recommendations
        timeframe_max_leverage = {
            '1m': 3, '5m': 5, '15m': 8, '30m': 10,
            '1h': 15, '4h': 20, '1d': 25
        }
        
        max_lev = timeframe_max_leverage.get(timeframe, 10)
        
        # Adjust based on risk tolerance
        if risk_pct > 0.03:  # High risk tolerance
            recommended_leverage = min(max_lev, random.randint(8, 15))
        elif risk_pct > 0.015:  # Medium risk tolerance
            recommended_leverage = min(max_lev, random.randint(3, 8))
        else:  # Conservative
            recommended_leverage = min(max_lev, random.randint(2, 5))
        
        return {
            'recommended_leverage': recommended_leverage,
            'max_safe_leverage': max_lev,
            'justification': f"Leverage {recommended_leverage}x aman untuk {timeframe} dengan risk tolerance {risk_pct*100:.1f}%",
            'liquidation_buffer': random.uniform(15, 35)  # % buffer from liquidation
        }
    
    def _assess_risk_level(self, exposure: float, max_loss: float) -> str:
        """Assess overall risk level"""
        if exposure > 50 or max_loss > 5:
            return 'HIGH'
        elif exposure > 25 or max_loss > 3:
            return 'MEDIUM'
        elif exposure > 10 or max_loss > 1.5:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def _generate_risk_warnings(self, exposure: float, max_loss: float, kelly: float) -> List[str]:
        """Generate risk warnings"""
        warnings = []
        
        if exposure > 30:
            warnings.append("Portfolio exposure tinggi (>30%)")
        if max_loss > 3:
            warnings.append("Maximum loss melebihi 3% portfolio")
        if kelly < 0:
            warnings.append("Kelly Criterion negatif - strategy mungkin tidak profitable")
        if exposure > (kelly * 100 * 1.5) and kelly > 0:
            warnings.append("Position size melebihi 150% Kelly optimal")
        
        return warnings
    
    def _calculate_risk_confidence(self, metrics: Dict) -> float:
        """Calculate confidence in risk management"""
        risk_level = metrics.get('risk_level', 'HIGH')
        warnings_count = len(metrics.get('warnings', []))
        
        base_confidence = 80
        
        # Adjust based on risk level
        if risk_level == 'LOW':
            base_confidence += 15
        elif risk_level == 'MODERATE':
            base_confidence += 5
        elif risk_level == 'MEDIUM':
            base_confidence -= 10
        else:  # HIGH
            base_confidence -= 25
        
        # Reduce confidence for warnings
        base_confidence -= warnings_count * 10
        
        return min(max(base_confidence, 0), 100)
    
    def _get_risk_recommendation(self, metrics: Dict) -> str:
        """Get risk-based recommendation"""
        risk_level = metrics.get('risk_level', 'HIGH')
        warnings = metrics.get('warnings', [])
        
        if risk_level == 'LOW' and len(warnings) == 0:
            return 'OPTIMAL_RISK'
        elif risk_level in ['MODERATE', 'MEDIUM'] and len(warnings) <= 1:
            return 'ACCEPTABLE_RISK'
        elif len(warnings) >= 2:
            return 'REDUCE_POSITION'
        else:
            return 'HIGH_RISK_WARNING'
    
    def _error_response(self, symbol: str, timeframe: str, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            'agent': self.name,
            'symbol': symbol,
            'timeframe': timeframe,
            'error': error,
            'confidence': 0,
            'recommendation': 'ERROR',
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }


class TradeExecutor:
    """Agent untuk mock eksekusi trade (stub untuk OKX integration)"""
    
    def __init__(self):
        self.name = "TradeExecutor"
        self.is_demo = True  # Always demo mode untuk safety
        logger.info(f"🚀 {self.name} initialized (DEMO MODE)")
    
    def analyze(self, symbol: str, timeframe: str, market_data: Dict, 
                trade_signal: Dict = None) -> Dict[str, Any]:
        """Mock trade execution analysis"""
        try:
            if not trade_signal:
                trade_signal = self._generate_mock_signal()
            
            # Execution feasibility check
            execution_check = self._check_execution_feasibility(symbol, trade_signal)
            
            # Order preparation
            order_details = self._prepare_order_details(symbol, trade_signal, market_data)
            
            # Mock execution simulation
            execution_result = self._simulate_execution(order_details)
            
            return {
                'agent': self.name,
                'symbol': symbol,
                'timeframe': timeframe,
                'is_demo_mode': self.is_demo,
                'execution_feasibility': execution_check,
                'order_details': order_details,
                'execution_simulation': execution_result,
                'confidence': execution_check.get('confidence', 0),
                'recommendation': execution_check.get('recommendation', 'WAIT'),
                'analysis_timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ {self.name} analysis error: {e}")
            return self._error_response(symbol, timeframe, str(e))
    
    def _generate_mock_signal(self) -> Dict[str, Any]:
        """Generate mock trading signal"""
        return {
            'action': random.choice(['BUY', 'SELL']),
            'confidence': random.uniform(60, 85),
            'entry_price': random.uniform(40000, 50000),  # Mock BTC price
            'stop_loss': random.uniform(38000, 42000),
            'take_profit': random.uniform(48000, 55000)
        }
    
    def _check_execution_feasibility(self, symbol: str, signal: Dict) -> Dict[str, Any]:
        """Check if trade execution is feasible"""
        # Mock feasibility checks
        checks = {
            'market_hours': True,  # Crypto 24/7
            'liquidity_sufficient': random.choice([True, True, False]),  # Mostly sufficient
            'spread_acceptable': random.choice([True, True, False]),
            'volatility_normal': random.choice([True, False]),
            'api_connection': random.choice([True, True, False])
        }
        
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        confidence = (passed_checks / total_checks) * 100
        
        if confidence >= 80:
            recommendation = 'EXECUTE'
        elif confidence >= 60:
            recommendation = 'EXECUTE_WITH_CAUTION'
        else:
            recommendation = 'WAIT'
        
        return {
            'checks': checks,
            'passed_checks': passed_checks,
            'total_checks': total_checks,
            'confidence': round(confidence, 1),
            'recommendation': recommendation,
            'blocking_issues': [k for k, v in checks.items() if not v]
        }
    
    def _prepare_order_details(self, symbol: str, signal: Dict, market_data: Dict) -> Dict[str, Any]:
        """Prepare order details for execution"""
        current_price = market_data.get('price_data', {}).get('close', signal.get('entry_price', 0))
        
        # Order type determination
        entry_price = signal.get('entry_price', current_price) or current_price
        price_diff_pct = abs(entry_price - current_price) / current_price if current_price > 0 and entry_price else 0
        
        order_type = 'MARKET' if price_diff_pct < 0.001 else 'LIMIT'
        
        return {
            'symbol': symbol,
            'side': signal.get('action', 'BUY').lower(),
            'type': order_type,
            'quantity': round(random.uniform(0.001, 0.1), 6),  # Mock quantity
            'price': entry_price if order_type == 'LIMIT' else None,
            'stop_loss': signal.get('stop_loss'),
            'take_profit': signal.get('take_profit'),
            'time_in_force': 'GTC',  # Good Till Cancelled
            'reduce_only': False,
            'post_only': order_type == 'LIMIT',
            'estimated_fee': round((entry_price or 0) * 0.001 * 0.0004, 6)  # 0.04% fee estimate
        }
    
    def _simulate_execution(self, order: Dict) -> Dict[str, Any]:
        """Simulate order execution"""
        # Random execution outcomes for demo
        execution_scenarios = [
            {'status': 'FILLED', 'fill_rate': 100, 'slippage': 0.02},
            {'status': 'PARTIALLY_FILLED', 'fill_rate': 75, 'slippage': 0.05},
            {'status': 'PENDING', 'fill_rate': 0, 'slippage': 0},
            {'status': 'REJECTED', 'fill_rate': 0, 'slippage': 0}
        ]
        
        # Weight scenarios - mostly successful
        weights = [0.7, 0.15, 0.1, 0.05]
        scenario = random.choices(execution_scenarios, weights=weights)[0]
        
        filled_quantity = order.get('quantity', 0) * (scenario['fill_rate'] / 100)
        
        order_price = order.get('price', 0) or 0
        
        return {
            'status': scenario['status'],
            'filled_quantity': round(filled_quantity, 6),
            'fill_percentage': scenario['fill_rate'],
            'average_fill_price': order_price * (1 + scenario['slippage'] / 100),
            'slippage_percent': scenario['slippage'],
            'execution_time_ms': random.randint(50, 500),
            'order_id': f"DEMO_{random.randint(100000, 999999)}",
            'commission_paid': round(filled_quantity * order_price * 0.0004, 6),
            'execution_note': self._get_execution_note(scenario['status'])
        }
    
    def _get_execution_note(self, status: str) -> str:
        """Get execution note based on status"""
        notes = {
            'FILLED': "Order berhasil dieksekusi sepenuhnya",
            'PARTIALLY_FILLED': "Order dieksekusi sebagian, menunggu fill sisanya",
            'PENDING': "Order menunggu kondisi market yang tepat",
            'REJECTED': "Order ditolak - periksa parameter dan balance"
        }
        return notes.get(status, "Status tidak diketahui")
    
    def _error_response(self, symbol: str, timeframe: str, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            'agent': self.name,
            'symbol': symbol,
            'timeframe': timeframe,
            'error': error,
            'confidence': 0,
            'recommendation': 'ERROR',
            'analysis_timestamp': datetime.now(timezone.utc).isoformat()
        }


class NarrativeMaker:
    """Agent untuk merangkum alasan sinyal dan membuat narasi lengkap"""
    
    def __init__(self):
        self.name = "NarrativeMaker"
        logger.info(f"📝 {self.name} initialized")
    
    def analyze(self, symbol: str, timeframe: str, all_agent_results: Dict) -> str:
        """Buat narasi lengkap dari semua analisis agent"""
        try:
            # Extract data dari semua agents
            technical = all_agent_results.get('TechnicalAnalyst', {})
            sentiment = all_agent_results.get('SentimentWatcher', {})
            risk = all_agent_results.get('RiskManager', {})
            execution = all_agent_results.get('TradeExecutor', {})
            
            # Build comprehensive narrative
            narrative_parts = []
            
            # Opening
            narrative_parts.append(f"📊 **Analisis {symbol} ({timeframe})**")
            narrative_parts.append("")
            
            # Technical Analysis Summary
            narrative_parts.append(self._build_technical_narrative(technical))
            
            # Sentiment Analysis Summary
            narrative_parts.append(self._build_sentiment_narrative(sentiment))
            
            # Risk Management Summary
            narrative_parts.append(self._build_risk_narrative(risk))
            
            # Execution Readiness
            narrative_parts.append(self._build_execution_narrative(execution))
            
            # Final Recommendation
            narrative_parts.append(self._build_final_recommendation(
                technical, sentiment, risk, execution
            ))
            
            return "\n".join(narrative_parts)
            
        except Exception as e:
            logger.error(f"❌ {self.name} narrative error: {e}")
            return f"❌ Error dalam membuat narasi: {str(e)}"
    
    def _build_technical_narrative(self, technical: Dict) -> str:
        """Build technical analysis narrative"""
        if not technical or 'error' in technical:
            return "🔍 **Analisis Teknikal**: Data tidak tersedia"
        
        smc = technical.get('smc_analysis', {})
        indicators = technical.get('technical_indicators', {})
        trend = technical.get('trend_analysis', {})
        
        parts = ["🔍 **Analisis Teknikal**:"]
        
        # SMC Summary
        if smc.get('bos_detected'):
            parts.append("- ✅ Break of Structure (BOS) terdeteksi")
        if smc.get('choch_detected'):
            parts.append("- ✅ Change of Character (CHoCH) terdeteksi")
        
        market_structure = smc.get('market_structure', 'NEUTRAL')
        parts.append(f"- 📈 Market Structure: {market_structure}")
        
        order_block = smc.get('order_block_strength', 0)
        if order_block > 60:
            parts.append(f"- 🎯 Order Block kuat teridentifikasi ({order_block}%)")
        
        # Trend Analysis
        trend_direction = trend.get('direction', 'UNKNOWN')
        trend_strength = trend.get('strength', 0)
        parts.append(f"- 📊 Trend: {trend_direction} (Kekuatan: {trend_strength}%)")
        
        # Technical Score
        technical_score = technical.get('technical_score', 0)
        parts.append(f"- 🎯 Technical Score: {technical_score:.1f}/100")
        
        return "\n".join(parts)
    
    def _build_sentiment_narrative(self, sentiment: Dict) -> str:
        """Build sentiment analysis narrative"""
        if not sentiment or 'error' in sentiment:
            return "\n📊 **Analisis Sentimen**: Data tidak tersedia"
        
        funding = sentiment.get('funding_analysis', {})
        oi = sentiment.get('open_interest_analysis', {})
        social = sentiment.get('social_sentiment', {})
        
        parts = ["\n📊 **Analisis Sentimen**:"]
        
        # Funding Rate
        funding_rate = funding.get('current_rate', 0)
        pressure = funding.get('pressure', 'NEUTRAL')
        parts.append(f"- 💰 Funding Rate: {funding_rate:.4f}% ({pressure})")
        
        if funding.get('overheat_warning'):
            parts.append("- ⚠️ Warning: Funding rate overheat detected")
        
        # Open Interest
        oi_change = oi.get('change_24h_percent', 0)
        oi_trend = oi.get('trend', 'STABLE')
        parts.append(f"- 📈 Open Interest: {oi_change:+.1f}% ({oi_trend})")
        
        # Social Sentiment
        social_bias = social.get('bias', 'NEUTRAL')
        fear_greed = social.get('fear_greed_index', 50)
        parts.append(f"- 🌍 Social Sentiment: {social_bias} (Fear/Greed: {fear_greed})")
        
        # Sentiment Score
        sentiment_score = sentiment.get('sentiment_score', 0)
        parts.append(f"- 🎯 Sentiment Score: {sentiment_score:.1f}/100")
        
        return "\n".join(parts)
    
    def _build_risk_narrative(self, risk: Dict) -> str:
        """Build risk management narrative"""
        if not risk or 'error' in risk:
            return "\n⚖️ **Manajemen Risiko**: Data tidak tersedia"
        
        metrics = risk.get('risk_metrics', {})
        position = risk.get('position_sizing', {})
        leverage = risk.get('leverage_recommendation', {})
        
        parts = ["\n⚖️ **Manajemen Risiko**:"]
        
        # Risk Level
        risk_level = metrics.get('risk_level', 'UNKNOWN')
        max_loss = metrics.get('max_loss_percent', 0)
        parts.append(f"- 📊 Risk Level: {risk_level} (Max Loss: {max_loss:.1f}%)")
        
        # Position Sizing
        position_pct = position.get('position_as_percent_of_balance', 0)
        parts.append(f"- 💼 Position Size: {position_pct:.1f}% dari portfolio")
        
        # Leverage
        rec_leverage = leverage.get('recommended_leverage', 1)
        parts.append(f"- 🔄 Leverage Rekomendasi: {rec_leverage}x")
        
        # Warnings
        warnings = metrics.get('warnings', [])
        if warnings:
            parts.append("- ⚠️ Peringatan:")
            for warning in warnings[:2]:  # Max 2 warnings
                parts.append(f"  • {warning}")
        
        return "\n".join(parts)
    
    def _build_execution_narrative(self, execution: Dict) -> str:
        """Build execution readiness narrative"""
        if not execution or 'error' in execution:
            return "\n🚀 **Kesiapan Eksekusi**: Data tidak tersedia"
        
        feasibility = execution.get('execution_feasibility', {})
        simulation = execution.get('execution_simulation', {})
        
        parts = ["\n🚀 **Kesiapan Eksekusi**:"]
        
        # Execution Confidence
        exec_confidence = feasibility.get('confidence', 0)
        exec_recommendation = feasibility.get('recommendation', 'WAIT')
        parts.append(f"- ✅ Execution Confidence: {exec_confidence:.1f}%")
        parts.append(f"- 🎯 Rekomendasi: {exec_recommendation}")
        
        # Blocking Issues
        blocking_issues = feasibility.get('blocking_issues', [])
        if blocking_issues:
            parts.append("- ⚠️ Issues:")
            for issue in blocking_issues[:2]:
                parts.append(f"  • {issue.replace('_', ' ').title()}")
        
        # Demo Mode Note
        if execution.get('is_demo_mode'):
            parts.append("- 📝 Mode: DEMO (simulasi trading)")
        
        return "\n".join(parts)
    
    def _build_final_recommendation(self, technical: Dict, sentiment: Dict, 
                                   risk: Dict, execution: Dict) -> str:
        """Build final recommendation based on all analyses"""
        parts = ["\n🎯 **Rekomendasi Akhir**:"]
        
        # Collect all confidence scores
        confidences = []
        if technical.get('confidence'):
            confidences.append(technical['confidence'])
        if sentiment.get('confidence'):
            confidences.append(sentiment['confidence'])
        if risk.get('confidence'):
            confidences.append(risk['confidence'])
        if execution.get('confidence'):
            confidences.append(execution['confidence'])
        
        # Calculate overall confidence
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Determine final recommendation
        tech_rec = technical.get('recommendation', 'WAIT')
        risk_level = risk.get('risk_metrics', {}).get('risk_level', 'HIGH')
        exec_rec = execution.get('recommendation', 'WAIT')
        
        # Decision logic
        if overall_confidence >= 75 and risk_level in ['LOW', 'MODERATE'] and exec_rec in ['EXECUTE', 'EXECUTE_WITH_CAUTION']:
            final_rec = 'STRONG_SIGNAL'
            recommendation_text = "Signal kuat terdeteksi - pertimbangkan eksekusi"
        elif overall_confidence >= 60 and risk_level != 'HIGH':
            final_rec = 'MODERATE_SIGNAL'
            recommendation_text = "Signal moderat - eksekusi dengan hati-hati"
        elif overall_confidence >= 40:
            final_rec = 'WEAK_SIGNAL'
            recommendation_text = "Signal lemah - tunggu konfirmasi tambahan"
        else:
            final_rec = 'WAIT'
            recommendation_text = "Kondisi belum ideal - tunggu setup yang lebih baik"
        
        parts.append(f"- 📈 **{final_rec}**")
        parts.append(f"- 💡 {recommendation_text}")
        parts.append(f"- 🎯 Overall Confidence: {overall_confidence:.1f}%")
        
        # Add timing note
        current_time = datetime.now(timezone.utc).strftime("%H:%M UTC")
        parts.append(f"- ⏰ Analisis pada: {current_time}")
        
        return "\n".join(parts)


def mock_market_data(symbol: str = "BTC-USDT") -> Dict[str, Any]:
    """Generate mock market data for testing tanpa koneksi OKX"""
    
    # Generate realistic price data
    base_price = {
        "BTC-USDT": 43000,
        "ETH-USDT": 2300,
        "SOL-USDT": 95,
        "ADA-USDT": 0.45
    }.get(symbol, 40000)
    
    # Add some randomness
    price_variation = random.uniform(0.95, 1.05)
    current_price = base_price * price_variation
    
    mock_data = {
        'symbol': symbol,
        'price_data': {
            'open': round(current_price * random.uniform(0.98, 1.02), 2),
            'high': round(current_price * random.uniform(1.01, 1.05), 2),
            'low': round(current_price * random.uniform(0.95, 0.99), 2),
            'close': round(current_price, 2),
            'volume': random.randint(1000000, 10000000)
        },
        'funding_rate': round(random.uniform(-0.01, 0.05), 6),
        'open_interest': random.randint(500000, 2000000),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'data_source': 'mock_generator'
    }
    
    return mock_data


def run_agents(symbol: str = "BTC-USDT", timeframe: str = "1h", 
               account_balance: float = 1000.0, risk_tolerance: float = 0.02,
               use_mock_data: bool = True) -> Dict[str, Any]:
    """
    Main function untuk menjalankan semua agents dan menggabungkan output
    
    Args:
        symbol: Trading pair (e.g., "BTC-USDT", "ETH-USDT")
        timeframe: Trading timeframe (e.g., "1h", "4h", "1d")
        account_balance: Account balance in USD
        risk_tolerance: Risk tolerance as decimal (0.02 = 2%)
        use_mock_data: Use mock data instead of real API
    
    Returns:
        Dict containing all agent analyses and final recommendation
    """
    
    logger.info(f"🚀 Starting Multi Role Agent Analysis for {symbol} ({timeframe})")
    
    try:
        # Get market data
        if use_mock_data:
            market_data = mock_market_data(symbol)
            logger.info("📊 Using mock market data")
        else:
            # TODO: Integrate with real OKX API
            market_data = mock_market_data(symbol)
            logger.info("⚠️ Real API not implemented, using mock data")
        
        # Initialize all agents
        agents = {
            'TechnicalAnalyst': TechnicalAnalyst(),
            'SentimentWatcher': SentimentWatcher(),
            'RiskManager': RiskManager(),
            'TradeExecutor': TradeExecutor()
        }
        
        # Run all analyses
        agent_results = {}
        overall_confidence_scores = []
        
        for agent_name, agent in agents.items():
            logger.info(f"🔄 Running {agent_name}...")
            
            try:
                if agent_name == 'RiskManager':
                    result = agent.analyze(symbol, timeframe, market_data, account_balance, risk_tolerance)
                elif agent_name == 'TradeExecutor':
                    # Pass previous results as trade signal
                    trade_signal = agent_results.get('TechnicalAnalyst', {})
                    result = agent.analyze(symbol, timeframe, market_data, trade_signal)
                else:
                    result = agent.analyze(symbol, timeframe, market_data)
                
                agent_results[agent_name] = result
                
                # Collect confidence scores
                if result.get('confidence'):
                    overall_confidence_scores.append(result['confidence'])
                
                logger.info(f"✅ {agent_name} completed (Confidence: {result.get('confidence', 0):.1f}%)")
                
            except Exception as e:
                logger.error(f"❌ {agent_name} failed: {e}")
                agent_results[agent_name] = {
                    'agent': agent_name,
                    'error': str(e),
                    'confidence': 0,
                    'recommendation': 'ERROR'
                }
        
        # Generate narrative
        narrative_maker = NarrativeMaker()
        narrative = narrative_maker.analyze(symbol, timeframe, agent_results)
        
        # Calculate overall metrics
        overall_confidence = sum(overall_confidence_scores) / len(overall_confidence_scores) if overall_confidence_scores else 0
        
        # Determine final recommendation
        final_recommendation = determine_final_recommendation(agent_results, overall_confidence)
        
        # Compile final response
        final_response = {
            'symbol': symbol,
            'timeframe': timeframe,
            'recommendation': final_recommendation,
            'confidence': round(overall_confidence, 1),
            'agents': agent_results,
            'narrative': narrative,
            'market_data_source': market_data.get('data_source', 'unknown'),
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'analysis_duration_ms': 0,  # TODO: Add timing
            'api_version': '1.0.0'
        }
        
        logger.info(f"🎯 Analysis completed: {final_recommendation} (Confidence: {overall_confidence:.1f}%)")
        return final_response
        
    except Exception as e:
        logger.error(f"❌ Critical error in run_agents: {e}")
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'recommendation': 'ERROR',
            'confidence': 0,
            'error': str(e),
            'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
            'api_version': '1.0.0'
        }


def determine_final_recommendation(agent_results: Dict, overall_confidence: float) -> str:
    """Determine final trading recommendation based on all agent outputs"""
    
    # Extract individual recommendations
    technical_rec = agent_results.get('TechnicalAnalyst', {}).get('recommendation', 'WAIT')
    sentiment_rec = agent_results.get('SentimentWatcher', {}).get('recommendation', 'NEUTRAL')
    risk_rec = agent_results.get('RiskManager', {}).get('recommendation', 'HIGH_RISK_WARNING')
    execution_rec = agent_results.get('TradeExecutor', {}).get('recommendation', 'WAIT')
    
    # Check for any error states
    if any('ERROR' in rec for rec in [technical_rec, sentiment_rec, risk_rec, execution_rec]):
        return 'ERROR'
    
    # High confidence with aligned signals
    if overall_confidence >= 75:
        if risk_rec in ['OPTIMAL_RISK', 'ACCEPTABLE_RISK'] and execution_rec == 'EXECUTE':
            if technical_rec in ['STRONG_BUY', 'BUY'] and sentiment_rec in ['BULLISH', 'MODERATE_BULLISH']:
                return 'STRONG_BUY'
            elif technical_rec in ['STRONG_SELL', 'SELL'] and sentiment_rec in ['BEARISH', 'MODERATE_BEARISH']:
                return 'STRONG_SELL'
            else:
                return 'BUY' if random.random() > 0.5 else 'SELL'  # Fallback with random bias
    
    # Medium confidence
    elif overall_confidence >= 60:
        if risk_rec == 'ACCEPTABLE_RISK':
            return 'WEAK_BUY' if sentiment_rec in ['BULLISH', 'MODERATE_BULLISH'] else 'WEAK_SELL'
    
    # Low confidence or high risk
    elif overall_confidence >= 40 and risk_rec not in ['HIGH_RISK_WARNING', 'REDUCE_POSITION']:
        return 'WATCH'
    
    # Default to wait
    return 'WAIT'


# Quick test function
def test_agent_mode():
    """Quick test function untuk agent mode"""
    print("🧪 Testing Agent Mode...")
    
    result = run_agents(
        symbol="BTC-USDT",
        timeframe="1h",
        account_balance=1000.0,
        risk_tolerance=0.02,
        use_mock_data=True
    )
    
    print(f"\n📊 Test Result:")
    print(f"Symbol: {result['symbol']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"\nNarrative:\n{result['narrative']}")
    
    return result


if __name__ == "__main__":
    # Run test when executed directly
    test_result = test_agent_mode()