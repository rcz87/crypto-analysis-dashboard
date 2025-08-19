#!/usr/bin/env python3
"""
ExecutionLogicEngine: SMC Entry Validation Module
Memverifikasi validitas entry dengan CHoCH + FVG + delta/RSI/orderflow confirmation
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class EntryValidationResult(Enum):
    """Entry validation results"""
    VALID = "valid"
    INVALID = "invalid"
    PENDING = "pending"
    REJECTED = "rejected"

@dataclass
class ExecutionSignal:
    """Structure for execution validation signals"""
    symbol: str
    direction: str  # LONG/SHORT
    validation_result: EntryValidationResult
    confidence: float  # 0.0 - 1.0
    entry_price: float
    timestamp: int
    timeframe: str
    
    # Validation components
    choch_confirmed: bool
    fvg_confirmed: bool
    delta_confirmed: bool
    rsi_confirmed: bool
    orderflow_confirmed: bool
    
    # Confirmation details
    choch_details: Dict[str, Any]
    fvg_details: Dict[str, Any]
    delta_details: Dict[str, Any]
    rsi_details: Dict[str, Any]
    orderflow_details: Dict[str, Any]
    
    validation_score: float
    rejection_reasons: List[str]
    description: str

class ExecutionLogicEngine:
    """
    ⚡ SMC Execution Logic Engine
    
    Memverifikasi validitas entry point melalui confluence analysis:
    - CHoCH (Change of Character) confirmation
    - FVG (Fair Value Gap) presence
    - Volume delta confirmation
    - RSI divergence/confluence
    - Order flow analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ExecutionLogicEngine")
        
        # Validation thresholds
        self.min_confidence_threshold = 0.7
        self.choch_weight = 0.3
        self.fvg_weight = 0.25
        self.delta_weight = 0.2
        self.rsi_weight = 0.15
        self.orderflow_weight = 0.1
        
        # RSI parameters
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        self.rsi_period = 14
        
        self.logger.info("⚡ ExecutionLogicEngine initialized with SMC validation")
    
    def validate_entry_signal(self, symbol: str, direction: str, current_price: float,
                            choch_signals: List[Dict], fvg_signals: List[Dict],
                            volume_data: List[Dict], price_data: List[Dict],
                            timeframe: str = "1H") -> ExecutionSignal:
        """
        Validate entry signal using comprehensive SMC logic
        
        Args:
            symbol: Trading symbol
            direction: LONG or SHORT
            current_price: Current market price
            choch_signals: CHoCH pattern signals
            fvg_signals: Fair Value Gap signals
            volume_data: Volume and delta data
            price_data: OHLCV price data
            timeframe: Analysis timeframe
            
        Returns:
            ExecutionSignal with complete validation results
        """
        try:
            self.logger.info(f"⚡ Validating {direction} entry signal for {symbol} at ${current_price}")
            
            # 1. CHoCH Confirmation
            choch_confirmed, choch_details = self._validate_choch_confirmation(
                direction, choch_signals, current_price
            )
            
            # 2. FVG Confirmation
            fvg_confirmed, fvg_details = self._validate_fvg_confirmation(
                direction, fvg_signals, current_price
            )
            
            # 3. Volume Delta Confirmation
            delta_confirmed, delta_details = self._validate_delta_confirmation(
                direction, volume_data, current_price
            )
            
            # 4. RSI Confirmation
            rsi_confirmed, rsi_details = self._validate_rsi_confirmation(
                direction, price_data
            )
            
            # 5. Order Flow Confirmation
            orderflow_confirmed, orderflow_details = self._validate_orderflow_confirmation(
                direction, volume_data, price_data
            )
            
            # Calculate validation score
            validation_score = self._calculate_validation_score(
                choch_confirmed, fvg_confirmed, delta_confirmed,
                rsi_confirmed, orderflow_confirmed
            )
            
            # Determine validation result
            validation_result = self._determine_validation_result(validation_score)
            
            # Calculate confidence
            confidence = min(validation_score, 1.0)
            
            # Identify rejection reasons
            rejection_reasons = self._identify_rejection_reasons(
                choch_confirmed, fvg_confirmed, delta_confirmed,
                rsi_confirmed, orderflow_confirmed
            )
            
            # Create execution signal
            execution_signal = ExecutionSignal(
                symbol=symbol,
                direction=direction,
                validation_result=validation_result,
                confidence=confidence,
                entry_price=current_price,
                timestamp=int(datetime.now().timestamp() * 1000),
                timeframe=timeframe,
                choch_confirmed=choch_confirmed,
                fvg_confirmed=fvg_confirmed,
                delta_confirmed=delta_confirmed,
                rsi_confirmed=rsi_confirmed,
                orderflow_confirmed=orderflow_confirmed,
                choch_details=choch_details,
                fvg_details=fvg_details,
                delta_details=delta_details,
                rsi_details=rsi_details,
                orderflow_details=orderflow_details,
                validation_score=validation_score,
                rejection_reasons=rejection_reasons,
                description=self._generate_execution_description(
                    validation_result, confidence, direction, rejection_reasons
                )
            )
            
            self.logger.info(f"✅ Entry validation completed: {validation_result.value.upper()} ({confidence:.1%})")
            
            return execution_signal
            
        except Exception as e:
            self.logger.error(f"❌ Error validating entry signal: {e}")
            return self._get_default_execution_signal(symbol, direction, current_price, timeframe)
    
    def _validate_choch_confirmation(self, direction: str, choch_signals: List[Dict], 
                                   current_price: float) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate CHoCH confirmation for entry
        
        Returns:
            Tuple of (confirmed, details)
        """
        try:
            # Filter recent CHoCH signals (last 24 hours)
            recent_timestamp = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
            recent_choch = [
                signal for signal in choch_signals 
                if signal.get('timestamp', 0) > recent_timestamp
            ]
            
            if not recent_choch:
                return False, {"reason": "No recent CHoCH signals", "count": 0}
            
            # Look for CHoCH in trade direction
            direction_match = direction.lower() == 'long' and 'bullish' or 'bearish'
            matching_choch = [
                signal for signal in recent_choch
                if signal.get('direction', '').lower() == direction_match
            ]
            
            if not matching_choch:
                return False, {
                    "reason": f"No {direction_match} CHoCH signals found",
                    "total_choch": len(recent_choch),
                    "matching_choch": 0
                }
            
            # Find most relevant CHoCH near current price
            closest_choch = None
            min_distance = float('inf')
            
            for signal in matching_choch:
                signal_price = signal.get('price', 0)
                if signal_price > 0:
                    distance = abs(current_price - signal_price) / current_price
                    if distance < min_distance:
                        min_distance = distance
                        closest_choch = signal
            
            if closest_choch and min_distance < 0.02:  # Within 2% price range
                return True, {
                    "confirmed": True,
                    "choch_price": closest_choch.get('price'),
                    "distance": min_distance,
                    "timestamp": closest_choch.get('timestamp'),
                    "strength": closest_choch.get('strength', 0.5),
                    "total_signals": len(matching_choch)
                }
            else:
                return False, {
                    "reason": "CHoCH too far from current price",
                    "min_distance": min_distance,
                    "threshold": 0.02
                }
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error validating CHoCH: {e}")
            return False, {"reason": f"CHoCH validation error: {str(e)}"}
    
    def _validate_fvg_confirmation(self, direction: str, fvg_signals: List[Dict],
                                 current_price: float) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate FVG confirmation for entry
        
        Returns:
            Tuple of (confirmed, details)
        """
        try:
            # Filter recent FVG signals
            recent_timestamp = int((datetime.now() - timedelta(hours=12)).timestamp() * 1000)
            recent_fvg = [
                signal for signal in fvg_signals
                if signal.get('timestamp', 0) > recent_timestamp
            ]
            
            if not recent_fvg:
                return False, {"reason": "No recent FVG signals", "count": 0}
            
            # Look for FVG in appropriate zone for trade direction
            relevant_fvg = []
            
            for fvg in recent_fvg:
                fvg_high = fvg.get('gap_high', 0)
                fvg_low = fvg.get('gap_low', 0)
                
                # Check if current price is near or within FVG
                if fvg_low <= current_price <= fvg_high:
                    relevant_fvg.append(fvg)
                elif abs(current_price - fvg_high) / current_price < 0.01:  # Within 1%
                    relevant_fvg.append(fvg)
                elif abs(current_price - fvg_low) / current_price < 0.01:  # Within 1%
                    relevant_fvg.append(fvg)
            
            if relevant_fvg:
                best_fvg = max(relevant_fvg, key=lambda x: x.get('confidence', 0))
                return True, {
                    "confirmed": True,
                    "fvg_high": best_fvg.get('gap_high'),
                    "fvg_low": best_fvg.get('gap_low'),
                    "confidence": best_fvg.get('confidence', 0.5),
                    "gap_size": best_fvg.get('gap_size', 0),
                    "total_fvg": len(relevant_fvg)
                }
            else:
                return False, {
                    "reason": "No relevant FVG near current price",
                    "total_fvg": len(recent_fvg),
                    "current_price": current_price
                }
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error validating FVG: {e}")
            return False, {"reason": f"FVG validation error: {str(e)}"}
    
    def _validate_delta_confirmation(self, direction: str, volume_data: List[Dict],
                                   current_price: float) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate volume delta confirmation
        
        Returns:
            Tuple of (confirmed, details)
        """
        try:
            if len(volume_data) < 10:  # Need minimum data
                return False, {"reason": "Insufficient volume data", "count": len(volume_data)}
            
            # Get recent volume deltas
            recent_deltas = volume_data[-10:]  # Last 10 periods
            
            # Calculate average volume delta
            total_delta = sum(candle.get('volume_delta', 0) for candle in recent_deltas)
            avg_delta = total_delta / len(recent_deltas)
            
            # Get latest delta
            latest_delta = recent_deltas[-1].get('volume_delta', 0)
            
            # Check direction alignment
            if direction.upper() == 'LONG':
                # For LONG: Look for positive delta (buying pressure)
                delta_aligned = latest_delta > 0 and avg_delta > 0
                strength = min(abs(latest_delta / max(abs(avg_delta), 1)), 2.0)  # Cap at 2.0
            else:
                # For SHORT: Look for negative delta (selling pressure)
                delta_aligned = latest_delta < 0 and avg_delta < 0
                strength = min(abs(latest_delta / max(abs(avg_delta), 1)), 2.0)  # Cap at 2.0
            
            if delta_aligned:
                return True, {
                    "confirmed": True,
                    "latest_delta": latest_delta,
                    "avg_delta": avg_delta,
                    "strength": strength,
                    "direction_alignment": direction.upper()
                }
            else:
                return False, {
                    "reason": f"Delta not aligned with {direction} direction",
                    "latest_delta": latest_delta,
                    "avg_delta": avg_delta,
                    "required_direction": direction.upper()
                }
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error validating delta: {e}")
            return False, {"reason": f"Delta validation error: {str(e)}"}
    
    def _validate_rsi_confirmation(self, direction: str, price_data: List[Dict]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate RSI confirmation
        
        Returns:
            Tuple of (confirmed, details)
        """
        try:
            if len(price_data) < self.rsi_period + 5:
                return False, {"reason": "Insufficient price data for RSI", "required": self.rsi_period + 5}
            
            # Calculate RSI
            rsi_values = self._calculate_rsi(price_data, self.rsi_period)
            
            if not rsi_values:
                return False, {"reason": "RSI calculation failed"}
            
            current_rsi = rsi_values[-1]
            
            # Check RSI conditions based on direction
            if direction.upper() == 'LONG':
                # For LONG: RSI should not be overbought, preferably in oversold or neutral
                rsi_confirmed = current_rsi < self.rsi_overbought
                bias = "bullish" if current_rsi < 50 else "bearish"
            else:
                # For SHORT: RSI should not be oversold, preferably in overbought or neutral
                rsi_confirmed = current_rsi > self.rsi_oversold
                bias = "bearish" if current_rsi > 50 else "bullish"
            
            return rsi_confirmed, {
                "confirmed": rsi_confirmed,
                "current_rsi": current_rsi,
                "bias": bias,
                "overbought_level": self.rsi_overbought,
                "oversold_level": self.rsi_oversold,
                "direction": direction.upper()
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error validating RSI: {e}")
            return False, {"reason": f"RSI validation error: {str(e)}"}
    
    def _validate_orderflow_confirmation(self, direction: str, volume_data: List[Dict],
                                       price_data: List[Dict]) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate order flow confirmation
        
        Returns:
            Tuple of (confirmed, details)
        """
        try:
            if len(volume_data) < 5 or len(price_data) < 5:
                return False, {"reason": "Insufficient data for order flow analysis"}
            
            # Analyze recent order flow patterns
            recent_volume = volume_data[-5:]
            recent_price = price_data[-5:]
            
            # Calculate volume-weighted price movement
            total_volume = sum(candle.get('volume', 0) for candle in recent_volume)
            
            if total_volume == 0:
                return False, {"reason": "No volume data available"}
            
            # Calculate volume distribution
            buying_volume = sum(
                candle.get('volume', 0) for i, candle in enumerate(recent_volume)
                if i < len(recent_price) and recent_price[i].get('close', 0) > recent_price[i].get('open', 0)
            )
            
            selling_volume = total_volume - buying_volume
            
            # Calculate order flow bias
            if total_volume > 0:
                buying_ratio = buying_volume / total_volume
                selling_ratio = selling_volume / total_volume
            else:
                buying_ratio = selling_ratio = 0.5
            
            # Check alignment with trade direction
            if direction.upper() == 'LONG':
                orderflow_confirmed = buying_ratio > 0.55  # 55% buying pressure
                flow_strength = buying_ratio
            else:
                orderflow_confirmed = selling_ratio > 0.55  # 55% selling pressure  
                flow_strength = selling_ratio
            
            return orderflow_confirmed, {
                "confirmed": orderflow_confirmed,
                "buying_ratio": buying_ratio,
                "selling_ratio": selling_ratio,
                "flow_strength": flow_strength,
                "total_volume": total_volume,
                "direction": direction.upper()
            }
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error validating order flow: {e}")
            return False, {"reason": f"Order flow validation error: {str(e)}"}
    
    def _calculate_rsi(self, price_data: List[Dict], period: int = 14) -> List[float]:
        """Calculate RSI indicator"""
        try:
            closes = [float(candle.get('close', 0)) for candle in price_data]
            
            if len(closes) < period + 1:
                return []
            
            deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
            
            gains = [delta if delta > 0 else 0 for delta in deltas]
            losses = [-delta if delta < 0 else 0 for delta in deltas]
            
            rsi_values = []
            
            # Calculate initial average gain and loss
            avg_gain = sum(gains[:period]) / period
            avg_loss = sum(losses[:period]) / period
            
            if avg_loss == 0:
                rsi_values.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
            
            # Calculate subsequent RSI values
            for i in range(period, len(gains)):
                avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                avg_loss = (avg_loss * (period - 1) + losses[i]) / period
                
                if avg_loss == 0:
                    rsi_values.append(100)
                else:
                    rs = avg_gain / avg_loss
                    rsi = 100 - (100 / (1 + rs))
                    rsi_values.append(rsi)
            
            return rsi_values
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error calculating RSI: {e}")
            return []
    
    def _calculate_validation_score(self, choch_confirmed: bool, fvg_confirmed: bool,
                                  delta_confirmed: bool, rsi_confirmed: bool,
                                  orderflow_confirmed: bool) -> float:
        """Calculate weighted validation score"""
        score = 0.0
        
        if choch_confirmed:
            score += self.choch_weight
        if fvg_confirmed:
            score += self.fvg_weight
        if delta_confirmed:
            score += self.delta_weight
        if rsi_confirmed:
            score += self.rsi_weight
        if orderflow_confirmed:
            score += self.orderflow_weight
        
        return score
    
    def _determine_validation_result(self, validation_score: float) -> EntryValidationResult:
        """Determine validation result based on score"""
        if validation_score >= self.min_confidence_threshold:
            return EntryValidationResult.VALID
        elif validation_score >= 0.5:
            return EntryValidationResult.PENDING
        else:
            return EntryValidationResult.INVALID
    
    def _identify_rejection_reasons(self, choch_confirmed: bool, fvg_confirmed: bool,
                                  delta_confirmed: bool, rsi_confirmed: bool,
                                  orderflow_confirmed: bool) -> List[str]:
        """Identify reasons for signal rejection"""
        reasons = []
        
        if not choch_confirmed:
            reasons.append("CHoCH not confirmed")
        if not fvg_confirmed:
            reasons.append("FVG not present")
        if not delta_confirmed:
            reasons.append("Volume delta not aligned")
        if not rsi_confirmed:
            reasons.append("RSI not favorable")
        if not orderflow_confirmed:
            reasons.append("Order flow not confirmed")
        
        return reasons
    
    def _generate_execution_description(self, validation_result: EntryValidationResult,
                                      confidence: float, direction: str,
                                      rejection_reasons: List[str]) -> str:
        """Generate human-readable execution description"""
        if validation_result == EntryValidationResult.VALID:
            return f"{direction} entry signal VALIDATED with {confidence:.1%} confidence. All key SMC criteria met."
        elif validation_result == EntryValidationResult.PENDING:
            return f"{direction} entry signal PENDING with {confidence:.1%} confidence. Some criteria need confirmation."
        else:
            reasons_text = ", ".join(rejection_reasons[:3])  # Top 3 reasons
            return f"{direction} entry signal REJECTED with {confidence:.1%} confidence. Issues: {reasons_text}"
    
    def _get_default_execution_signal(self, symbol: str, direction: str, 
                                    current_price: float, timeframe: str) -> ExecutionSignal:
        """Get default execution signal for error cases"""
        return ExecutionSignal(
            symbol=symbol,
            direction=direction,
            validation_result=EntryValidationResult.INVALID,
            confidence=0.0,
            entry_price=current_price,
            timestamp=int(datetime.now().timestamp() * 1000),
            timeframe=timeframe,
            choch_confirmed=False,
            fvg_confirmed=False,
            delta_confirmed=False,
            rsi_confirmed=False,
            orderflow_confirmed=False,
            choch_details={"reason": "Validation error"},
            fvg_details={"reason": "Validation error"},
            delta_details={"reason": "Validation error"},
            rsi_details={"reason": "Validation error"},
            orderflow_details={"reason": "Validation error"},
            validation_score=0.0,
            rejection_reasons=["System error during validation"],
            description="Unable to validate entry signal due to system error"
        )
    
    def get_execution_summary(self, execution_signal: ExecutionSignal) -> Dict[str, Any]:
        """
        Get summary of execution validation for external use
        
        Returns:
            Dictionary with execution summary
        """
        return {
            "symbol": execution_signal.symbol,
            "direction": execution_signal.direction,
            "validation_result": execution_signal.validation_result.value,
            "confidence": execution_signal.confidence,
            "entry_price": execution_signal.entry_price,
            "timestamp": execution_signal.timestamp,
            "timeframe": execution_signal.timeframe,
            "validation_score": execution_signal.validation_score,
            "confirmations": {
                "choch": execution_signal.choch_confirmed,
                "fvg": execution_signal.fvg_confirmed,
                "delta": execution_signal.delta_confirmed,
                "rsi": execution_signal.rsi_confirmed,
                "orderflow": execution_signal.orderflow_confirmed
            },
            "rejection_reasons": execution_signal.rejection_reasons,
            "description": execution_signal.description,
            "trade_recommendation": self._get_trade_recommendation(execution_signal),
            "risk_assessment": self._assess_execution_risk(execution_signal)
        }
    
    def _get_trade_recommendation(self, execution_signal: ExecutionSignal) -> str:
        """Get trade recommendation based on validation"""
        if execution_signal.validation_result == EntryValidationResult.VALID:
            return "EXECUTE"
        elif execution_signal.validation_result == EntryValidationResult.PENDING:
            return "WAIT"
        else:
            return "REJECT"
    
    def _assess_execution_risk(self, execution_signal: ExecutionSignal) -> str:
        """Assess execution risk level"""
        if execution_signal.confidence > 0.8 and execution_signal.validation_score > 0.8:
            return "LOW"
        elif execution_signal.confidence > 0.6 and execution_signal.validation_score > 0.6:
            return "MEDIUM"
        else:
            return "HIGH"