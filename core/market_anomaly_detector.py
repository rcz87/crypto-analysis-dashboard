#!/usr/bin/env python3
"""
Market Anomaly Detector - Advanced Real-time Market Manipulation Detection
Deteksi volume spike, price manipulation, wash trading, dan anomali pasar lainnya
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import time
import json
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class AnomalyType(Enum):
    VOLUME_SPIKE = "volume_spike"
    PRICE_MANIPULATION = "price_manipulation"
    WASH_TRADING = "wash_trading"
    LIQUIDATION_CASCADE = "liquidation_cascade"
    PUMP_AND_DUMP = "pump_and_dump"
    STOP_HUNTING = "stop_hunting"
    FUNDING_RATE_EXTREME = "funding_rate_extreme"
    FLASH_CRASH = "flash_crash"

@dataclass
class AnomalyAlert:
    timestamp: float
    symbol: str
    anomaly_type: AnomalyType
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: float  # 0-1
    description: str
    metrics: Dict[str, Any]
    recommended_action: str

class MarketAnomalyDetector:
    """
    Advanced detector untuk anomali pasar cryptocurrency
    Real-time detection dengan machine learning patterns
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.anomaly_history = []
        self.baseline_metrics = {}
        self.detection_thresholds = {
            # Volume anomalies
            'volume_spike_multiplier': 10.0,      # 10x volume normal
            'volume_spike_duration': 300,         # 5 minutes
            'volume_drop_threshold': 0.1,         # 90% drop
            
            # Price anomalies  
            'price_spike_percentage': 15.0,       # 15% dalam 1 menit
            'flash_crash_percentage': 20.0,       # 20% drop dalam 2 menit
            'price_recovery_time': 600,           # 10 minutes recovery
            
            # Manipulation patterns
            'wash_trading_correlation': 0.95,     # 95% correlation
            'pump_dump_velocity': 25.0,           # 25% dalam 5 menit
            'stop_hunt_spike_ratio': 3.0,         # 3x normal spike
            
            # Liquidation cascades
            'liquidation_threshold': 50_000_000,  # $50M liquidations
            'cascade_time_window': 300,           # 5 minutes window
            
            # Funding rate extremes
            'funding_rate_extreme': 0.01,         # 1% funding rate
            'funding_rate_change': 0.005          # 0.5% change
        }
        
        # Historical data untuk baseline calculation
        self.baseline_data = {}
        self.baseline_window = 3600  # 1 hour baseline
        
        self.logger.info("🔍 Market Anomaly Detector initialized")
    
    def detect_real_time_anomalies(self, 
                                  market_data: Dict[str, Any],
                                  symbol: str) -> List[AnomalyAlert]:
        """
        Real-time detection semua jenis anomali pasar
        """
        alerts = []
        
        try:
            # Update baseline untuk symbol ini
            self._update_baseline(symbol, market_data)
            
            # 1. Volume Spike Detection
            volume_alerts = self._detect_volume_anomalies(symbol, market_data)
            alerts.extend(volume_alerts)
            
            # 2. Price Manipulation Detection
            price_alerts = self._detect_price_manipulation(symbol, market_data)
            alerts.extend(price_alerts)
            
            # 3. Wash Trading Detection
            wash_alerts = self._detect_wash_trading(symbol, market_data)
            alerts.extend(wash_alerts)
            
            # 4. Liquidation Cascade Detection
            if 'liquidations' in market_data:
                liq_alerts = self._detect_liquidation_cascade(symbol, market_data)
                alerts.extend(liq_alerts)
            
            # 5. Pump and Dump Detection
            pump_alerts = self._detect_pump_and_dump(symbol, market_data)
            alerts.extend(pump_alerts)
            
            # 6. Flash Crash Detection
            crash_alerts = self._detect_flash_crash(symbol, market_data)
            alerts.extend(crash_alerts)
            
            # 7. Funding Rate Extreme Detection
            if 'funding_rate' in market_data:
                funding_alerts = self._detect_funding_extremes(symbol, market_data)
                alerts.extend(funding_alerts)
            
            # Store alerts dalam history
            for alert in alerts:
                self.anomaly_history.append(alert)
                self.logger.warning(f"🚨 {alert.severity} anomaly detected: {alert.description}")
            
            # Limit history size
            if len(self.anomaly_history) > 1000:
                self.anomaly_history = self.anomaly_history[-500:]
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error in anomaly detection for {symbol}: {e}")
            return []
    
    def _detect_volume_anomalies(self, symbol: str, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Deteksi anomali volume"""
        alerts = []
        
        try:
            current_volume = float(data.get('volume', 0))
            if current_volume == 0:
                return alerts
            
            # Get baseline volume
            baseline = self.baseline_data.get(symbol, {}).get('avg_volume', current_volume)
            
            # Volume spike detection
            if current_volume > baseline * self.detection_thresholds['volume_spike_multiplier']:
                severity = "HIGH" if current_volume > baseline * 20 else "MEDIUM"
                
                alert = AnomalyAlert(
                    timestamp=time.time(),
                    symbol=symbol,
                    anomaly_type=AnomalyType.VOLUME_SPIKE,
                    severity=severity,
                    confidence=min(0.95, current_volume / (baseline * 5)),
                    description=f"Volume spike detected: {current_volume/baseline:.1f}x normal volume",
                    metrics={
                        'current_volume': current_volume,
                        'baseline_volume': baseline,
                        'spike_ratio': current_volume / baseline
                    },
                    recommended_action="Monitor for price manipulation or major news"
                )
                alerts.append(alert)
            
            # Volume drop detection
            elif current_volume < baseline * self.detection_thresholds['volume_drop_threshold']:
                alert = AnomalyAlert(
                    timestamp=time.time(),
                    symbol=symbol,
                    anomaly_type=AnomalyType.VOLUME_SPIKE,
                    severity="LOW",
                    confidence=0.7,
                    description=f"Unusual volume drop: {(1-current_volume/baseline)*100:.1f}% below normal",
                    metrics={
                        'current_volume': current_volume,
                        'baseline_volume': baseline,
                        'drop_percentage': (1 - current_volume/baseline) * 100
                    },
                    recommended_action="Check for market closure or technical issues"
                )
                alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Error detecting volume anomalies: {e}")
        
        return alerts
    
    def _detect_price_manipulation(self, symbol: str, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Deteksi manipulasi harga"""
        alerts = []
        
        try:
            # Check untuk price data
            if 'ohlcv' not in data:
                return alerts
            
            ohlcv = data['ohlcv']
            if len(ohlcv) < 5:  # Need minimal data
                return alerts
            
            # Konversi ke numpy arrays
            prices = np.array([float(candle[4]) for candle in ohlcv[-10:]])  # Close prices
            volumes = np.array([float(candle[5]) for candle in ohlcv[-10:]])  # Volumes
            
            # Price spike detection
            if len(prices) >= 2:
                recent_change = abs(prices[-1] - prices[-2]) / prices[-2] * 100
                
                if recent_change > self.detection_thresholds['price_spike_percentage']:
                    # Check if volume supports the move
                    volume_ratio = volumes[-1] / np.mean(volumes[:-1]) if len(volumes) > 1 else 1
                    
                    if volume_ratio < 2:  # Low volume price spike = suspicious
                        severity = "HIGH" if recent_change > 30 else "MEDIUM"
                        
                        alert = AnomalyAlert(
                            timestamp=time.time(),
                            symbol=symbol,
                            anomaly_type=AnomalyType.PRICE_MANIPULATION,
                            severity=severity,
                            confidence=0.8 if volume_ratio < 1 else 0.6,
                            description=f"Suspicious price spike: {recent_change:.1f}% with low volume",
                            metrics={
                                'price_change_percentage': recent_change,
                                'volume_ratio': volume_ratio,
                                'current_price': prices[-1],
                                'previous_price': prices[-2]
                            },
                            recommended_action="Investigate for potential manipulation"
                        )
                        alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Error detecting price manipulation: {e}")
        
        return alerts
    
    def _detect_wash_trading(self, symbol: str, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Deteksi wash trading patterns"""
        alerts = []
        
        try:
            if 'ohlcv' not in data:
                return alerts
            
            ohlcv = data['ohlcv']
            if len(ohlcv) < 10:
                return alerts
            
            # Analisis correlation antara volume dan price movement
            prices = np.array([float(candle[4]) for candle in ohlcv[-20:]])
            volumes = np.array([float(candle[5]) for candle in ohlcv[-20:]])
            
            # Calculate price volatility vs volume correlation
            if len(prices) >= 10:
                price_changes = np.diff(prices) / prices[:-1]
                volume_changes = np.diff(volumes) / volumes[:-1]
                
                # Remove outliers and calculate correlation
                mask = (~np.isnan(price_changes)) & (~np.isnan(volume_changes))
                if np.sum(mask) > 5:
                    correlation = np.corrcoef(np.abs(price_changes[mask]), volume_changes[mask])[0, 1]
                    
                    # High volume with low price movement = potential wash trading
                    avg_volume = np.mean(volumes)
                    price_volatility = np.std(price_changes[mask]) * 100
                    
                    if (avg_volume > np.median(volumes) * 3 and 
                        price_volatility < 0.5 and 
                        not np.isnan(correlation) and correlation > self.detection_thresholds['wash_trading_correlation']):
                        
                        alert = AnomalyAlert(
                            timestamp=time.time(),
                            symbol=symbol,
                            anomaly_type=AnomalyType.WASH_TRADING,
                            severity="MEDIUM",
                            confidence=0.7,
                            description=f"Potential wash trading: High volume ({avg_volume:.0f}) with low volatility ({price_volatility:.2f}%)",
                            metrics={
                                'volume_volume_ratio': avg_volume / np.median(volumes),
                                'price_volatility': price_volatility,
                                'correlation': correlation if not np.isnan(correlation) else 0
                            },
                            recommended_action="Monitor for artificial volume inflation"
                        )
                        alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Error detecting wash trading: {e}")
        
        return alerts
    
    def _detect_liquidation_cascade(self, symbol: str, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Deteksi liquidation cascade events"""
        alerts = []
        
        try:
            liquidations = data.get('liquidations', [])
            if not liquidations:
                return alerts
            
            # Calculate total liquidations dalam time window
            current_time = time.time()
            recent_liquidations = []
            total_loss = 0
            
            for liq in liquidations:
                liq_time = float(liq.get('timestamp', 0)) / 1000  # Convert ms to seconds
                if current_time - liq_time <= self.detection_thresholds['cascade_time_window']:
                    recent_liquidations.append(liq)
                    total_loss += float(liq.get('total_loss', 0))
            
            if total_loss > self.detection_thresholds['liquidation_threshold']:
                severity = "CRITICAL" if total_loss > 100_000_000 else "HIGH"
                
                alert = AnomalyAlert(
                    timestamp=time.time(),
                    symbol=symbol,
                    anomaly_type=AnomalyType.LIQUIDATION_CASCADE,
                    severity=severity,
                    confidence=0.9,
                    description=f"Liquidation cascade detected: ${total_loss:,.0f} in {len(recent_liquidations)} liquidations",
                    metrics={
                        'total_liquidations': len(recent_liquidations),
                        'total_loss_usd': total_loss,
                        'time_window_seconds': self.detection_thresholds['cascade_time_window']
                    },
                    recommended_action="Expect high volatility and potential price gaps"
                )
                alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Error detecting liquidation cascade: {e}")
        
        return alerts
    
    def _detect_pump_and_dump(self, symbol: str, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Deteksi pump and dump schemes"""
        alerts = []
        
        try:
            if 'ohlcv' not in data:
                return alerts
            
            ohlcv = data['ohlcv']
            if len(ohlcv) < 15:  # Need enough data for pattern detection
                return alerts
            
            # Analisis pattern: rapid increase followed by decrease
            prices = np.array([float(candle[4]) for candle in ohlcv[-15:]])
            volumes = np.array([float(candle[5]) for candle in ohlcv[-15:]])
            
            # Check for rapid price increase in recent candles
            recent_prices = prices[-5:]  # Last 5 candles
            if len(recent_prices) >= 5:
                # Calculate price velocity
                total_increase = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
                
                if total_increase > self.detection_thresholds['pump_dump_velocity']:
                    # Check if followed by volume spike
                    recent_volume = np.mean(volumes[-5:])
                    baseline_volume = np.mean(volumes[-15:-5])
                    
                    if recent_volume > baseline_volume * 3:  # 3x volume increase
                        # Check if starting to dump (recent candles showing decline)
                        if len(recent_prices) >= 3 and recent_prices[-1] < recent_prices[-2]:
                            alert = AnomalyAlert(
                                timestamp=time.time(),
                                symbol=symbol,
                                anomaly_type=AnomalyType.PUMP_AND_DUMP,
                                severity="HIGH",
                                confidence=0.75,
                                description=f"Potential pump and dump: {total_increase:.1f}% increase with volume spike, now declining",
                                metrics={
                                    'price_increase_percentage': total_increase,
                                    'volume_spike_ratio': recent_volume / baseline_volume,
                                    'current_trend': 'declining'
                                },
                                recommended_action="Avoid buying, potential dump in progress"
                            )
                            alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Error detecting pump and dump: {e}")
        
        return alerts
    
    def _detect_flash_crash(self, symbol: str, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Deteksi flash crash events"""
        alerts = []
        
        try:
            if 'ohlcv' not in data:
                return alerts
            
            ohlcv = data['ohlcv']
            if len(ohlcv) < 5:
                return alerts
            
            # Check untuk rapid price drop
            prices = np.array([float(candle[4]) for candle in ohlcv[-5:]])
            
            if len(prices) >= 3:
                # Calculate maximum drop dalam recent candles
                max_price = np.max(prices[:-1])  # Exclude current price
                current_price = prices[-1]
                drop_percentage = (max_price - current_price) / max_price * 100
                
                if drop_percentage > self.detection_thresholds['flash_crash_percentage']:
                    # Check if this happened quickly (dalam few candles)
                    timeframe_minutes = len(prices) * 1  # Assume 1min candles
                    
                    if timeframe_minutes <= 5:  # Flash crash dalam 5 minutes
                        severity = "CRITICAL" if drop_percentage > 40 else "HIGH"
                        
                        alert = AnomalyAlert(
                            timestamp=time.time(),
                            symbol=symbol,
                            anomaly_type=AnomalyType.FLASH_CRASH,
                            severity=severity,
                            confidence=0.9,
                            description=f"Flash crash detected: {drop_percentage:.1f}% drop in {timeframe_minutes} minutes",
                            metrics={
                                'drop_percentage': drop_percentage,
                                'time_minutes': timeframe_minutes,
                                'peak_price': max_price,
                                'current_price': current_price
                            },
                            recommended_action="Check for technical issues or major news, potential buying opportunity"
                        )
                        alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Error detecting flash crash: {e}")
        
        return alerts
    
    def _detect_funding_extremes(self, symbol: str, data: Dict[str, Any]) -> List[AnomalyAlert]:
        """Deteksi extreme funding rates"""
        alerts = []
        
        try:
            funding_rate = float(data.get('funding_rate', 0))
            
            if abs(funding_rate) > self.detection_thresholds['funding_rate_extreme']:
                severity = "HIGH" if abs(funding_rate) > 0.02 else "MEDIUM"
                
                direction = "Longs paying shorts" if funding_rate > 0 else "Shorts paying longs"
                
                alert = AnomalyAlert(
                    timestamp=time.time(),
                    symbol=symbol,
                    anomaly_type=AnomalyType.FUNDING_RATE_EXTREME,
                    severity=severity,
                    confidence=0.95,
                    description=f"Extreme funding rate: {funding_rate*100:.2f}% ({direction})",
                    metrics={
                        'funding_rate': funding_rate,
                        'funding_rate_percentage': funding_rate * 100,
                        'direction': direction
                    },
                    recommended_action="Potential market reversal signal due to extreme positioning"
                )
                alerts.append(alert)
        
        except Exception as e:
            self.logger.error(f"Error detecting funding extremes: {e}")
        
        return alerts
    
    def _update_baseline(self, symbol: str, data: Dict[str, Any]):
        """Update baseline metrics untuk symbol"""
        try:
            current_time = time.time()
            
            if symbol not in self.baseline_data:
                self.baseline_data[symbol] = {
                    'prices': [],
                    'volumes': [],
                    'timestamps': [],
                    'avg_price': 0,
                    'avg_volume': 0,
                    'last_update': current_time
                }
            
            baseline = self.baseline_data[symbol]
            
            # Add current data
            if 'price' in data:
                baseline['prices'].append(float(data['price']))
            if 'volume' in data:
                baseline['volumes'].append(float(data['volume']))
            baseline['timestamps'].append(current_time)
            
            # Clean old data (keep only baseline_window)
            cutoff_time = current_time - self.baseline_window
            while (baseline['timestamps'] and 
                   baseline['timestamps'][0] < cutoff_time):
                baseline['timestamps'].pop(0)
                if baseline['prices']:
                    baseline['prices'].pop(0)
                if baseline['volumes']:
                    baseline['volumes'].pop(0)
            
            # Update averages
            if baseline['prices']:
                baseline['avg_price'] = np.mean(baseline['prices'])
            if baseline['volumes']:
                baseline['avg_volume'] = np.mean(baseline['volumes'])
            
            baseline['last_update'] = current_time
        
        except Exception as e:
            self.logger.error(f"Error updating baseline for {symbol}: {e}")
    
    def get_anomaly_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary anomali dalam timeframe tertentu"""
        try:
            cutoff_time = time.time() - (hours * 3600)
            recent_alerts = [alert for alert in self.anomaly_history 
                           if alert.timestamp > cutoff_time]
            
            # Group by type and severity
            summary = {
                'total_anomalies': len(recent_alerts),
                'by_type': {},
                'by_severity': {},
                'by_symbol': {},
                'most_recent': None
            }
            
            for alert in recent_alerts:
                # By type
                type_name = alert.anomaly_type.value
                summary['by_type'][type_name] = summary['by_type'].get(type_name, 0) + 1
                
                # By severity
                summary['by_severity'][alert.severity] = summary['by_severity'].get(alert.severity, 0) + 1
                
                # By symbol
                summary['by_symbol'][alert.symbol] = summary['by_symbol'].get(alert.symbol, 0) + 1
            
            # Most recent alert
            if recent_alerts:
                most_recent = max(recent_alerts, key=lambda x: x.timestamp)
                summary['most_recent'] = {
                    'timestamp': most_recent.timestamp,
                    'symbol': most_recent.symbol,
                    'type': most_recent.anomaly_type.value,
                    'severity': most_recent.severity,
                    'description': most_recent.description
                }
            
            return summary
        
        except Exception as e:
            self.logger.error(f"Error generating anomaly summary: {e}")
            return {'error': str(e)}
    
    def get_market_health_score(self, symbol: str) -> Dict[str, Any]:
        """Calculate market health score berdasarkan recent anomalies"""
        try:
            recent_time = time.time() - 3600  # Last hour
            symbol_alerts = [alert for alert in self.anomaly_history 
                           if alert.symbol == symbol and alert.timestamp > recent_time]
            
            # Base score
            health_score = 100.0
            
            # Deduct points berdasarkan severity
            for alert in symbol_alerts:
                if alert.severity == "CRITICAL":
                    health_score -= 30
                elif alert.severity == "HIGH":
                    health_score -= 20
                elif alert.severity == "MEDIUM":
                    health_score -= 10
                elif alert.severity == "LOW":
                    health_score -= 5
            
            health_score = max(0, min(100, health_score))
            
            # Determine health status
            if health_score >= 90:
                status = "EXCELLENT"
            elif health_score >= 75:
                status = "GOOD"
            elif health_score >= 50:
                status = "FAIR"
            elif health_score >= 25:
                status = "POOR"
            else:
                status = "CRITICAL"
            
            return {
                'symbol': symbol,
                'health_score': health_score,
                'status': status,
                'recent_anomalies': len(symbol_alerts),
                'evaluation_window_hours': 1,
                'timestamp': time.time()
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating market health score: {e}")
            return {'error': str(e)}

# Global instance
market_anomaly_detector = MarketAnomalyDetector()

def get_market_anomaly_detector():
    """Get global market anomaly detector instance"""
    return market_anomaly_detector