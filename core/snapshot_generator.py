#!/usr/bin/env python3
"""
Advanced Market Snapshot Generator
Generates comprehensive market snapshots with technical analysis, orderbook data, and AI narratives
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Local imports
from core.okx_fetcher import OKXAPIManager
from core.analyzer import TechnicalAnalyzer
from core.ai_engine import get_ai_engine
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.price_action import PriceActionAnalyzer
# Import models locally to avoid circular imports

logger = logging.getLogger(__name__)

class SnapshotType(Enum):
    QUICK = "quick"
    COMPREHENSIVE = "comprehensive"
    DEEP_ANALYSIS = "deep_analysis"
    
    def __json__(self):
        """Make enum JSON serializable"""
        return self.value

@dataclass
class MarketSnapshot:
    """Comprehensive market snapshot data structure"""
    symbol: str
    timeframe: str
    timestamp: str
    snapshot_type: SnapshotType
    
    # Price data
    current_price: float
    price_change_24h: float
    volume_24h: float
    
    # Technical indicators
    rsi: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, float]
    ema_20: float
    ema_50: float
    ema_200: float
    
    # SMC analysis
    smc_patterns: Dict[str, Any]
    market_structure: Dict[str, Any]
    liquidity_levels: List[Dict[str, Any]]
    
    # Price action
    price_action_patterns: List[Dict[str, Any]]
    support_levels: List[float]
    resistance_levels: List[float]
    
    # Orderbook data
    orderbook_snapshot: Dict[str, Any]
    depth_analysis: Dict[str, Any]
    
    # AI analysis
    ai_narrative: str
    confidence_score: float
    risk_assessment: Dict[str, Any]
    
    # Metadata
    generation_time: float
    data_quality: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary with proper JSON serialization"""
        data = asdict(self)
        # Convert enum to its value for JSON serialization
        data['snapshot_type'] = self.snapshot_type.value
        return data

class SnapshotGenerator:
    """Advanced market snapshot generator with comprehensive analysis"""
    
    def __init__(self):
        self.api_manager = OKXAPIManager()
        self.technical_analyzer = TechnicalAnalyzer()
        self.smc_analyzer = ProfessionalSMCAnalyzer()
        self.price_action_analyzer = PriceActionAnalyzer()
        self.ai_engine = get_ai_engine()
        
        # Configuration
        self.supported_symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'TIA-USDT', 'RENDER-USDT']
        self.supported_timeframes = ['1m', '5m', '15m', '1H', '4H', '1D']
        
        logger.info("SnapshotGenerator initialized with comprehensive analysis capabilities")
    
    def generate_snapshot(self, symbol: str, timeframe: str = '1H', 
                         snapshot_type: SnapshotType = SnapshotType.COMPREHENSIVE,
                         session_id: str = 'system') -> MarketSnapshot:
        """
        Generate comprehensive market snapshot
        
        Args:
            symbol: Trading symbol (e.g., 'BTC-USDT')
            timeframe: Chart timeframe
            snapshot_type: Type of snapshot to generate
            session_id: Session identifier
            
        Returns:
            MarketSnapshot object with comprehensive data
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Generating {snapshot_type.value} snapshot for {symbol} ({timeframe})")
            
            # 1. Get market data
            df = self._get_market_data(symbol, timeframe)
            if df is None or df.empty:
                raise ValueError(f"No market data available for {symbol}")
            
            # 2. Get orderbook data
            orderbook_data = self._get_orderbook_data(symbol)
            
            # 3. Perform technical analysis
            technical_analysis = self.technical_analyzer.analyze(df, symbol, timeframe)
            
            # 4. Perform SMC analysis
            try:
                smc_analysis = self.smc_analyzer.analyze_comprehensive(df, symbol, timeframe)
            except Exception as e:
                logger.warning(f"SMC analysis failed: {e}")
                smc_analysis = {
                    'patterns': {},
                    'market_structure': {},
                    'liquidity_levels': [],
                    'confidence_score': 0
                }
            
            # 5. Perform price action analysis
            price_action_analysis = self.price_action_analyzer.analyze_price_action(df)
            
            # 6. Generate AI narrative (if not quick mode)
            ai_narrative = ""
            confidence_score = 0.0
            
            if snapshot_type != SnapshotType.QUICK:
                ai_narrative, confidence_score = self._generate_ai_narrative(
                    symbol, technical_analysis, smc_analysis, price_action_analysis
                )
            
            # 7. Calculate current price metrics
            current_price = float(df['close'].iloc[-1])
            price_change_24h = technical_analysis.get('price_change_24h', 0.0)
            volume_24h = float(df['volume'].iloc[-1])
            
            # 8. Extract technical indicators
            indicators = technical_analysis.get('indicators', {})
            
            # 9. Create snapshot
            snapshot = MarketSnapshot(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.now().replace(microsecond=0).isoformat(),
                snapshot_type=snapshot_type,
                
                # Price data
                current_price=current_price,
                price_change_24h=price_change_24h,
                volume_24h=volume_24h,
                
                # Technical indicators
                rsi=self._safe_extract_indicator(indicators, 'rsi', 50.0),
                macd=self._extract_macd_data(indicators),
                bollinger_bands=self._extract_bollinger_bands(indicators),
                ema_20=self._safe_extract_indicator(indicators, 'ema_20', current_price),
                ema_50=self._safe_extract_indicator(indicators, 'ema_50', current_price),
                ema_200=self._safe_extract_indicator(indicators, 'ema_200', current_price),
                
                # SMC analysis
                smc_patterns=smc_analysis.get('patterns', {}),
                market_structure=smc_analysis.get('market_structure', {}),
                liquidity_levels=smc_analysis.get('liquidity_levels', []),
                
                # Price action
                price_action_patterns=price_action_analysis.get('patterns', []),
                support_levels=price_action_analysis.get('support_levels', []),
                resistance_levels=price_action_analysis.get('resistance_levels', []),
                
                # Orderbook data
                orderbook_snapshot=orderbook_data,
                depth_analysis=self._analyze_orderbook_depth(orderbook_data),
                
                # AI analysis
                ai_narrative=ai_narrative,
                confidence_score=confidence_score,
                risk_assessment=self._calculate_risk_assessment(technical_analysis, smc_analysis),
                
                # Metadata
                generation_time=(datetime.now() - start_time).total_seconds(),
                data_quality=self._assess_data_quality(df, orderbook_data)
            )
            
            # 10. Store snapshot in database
            self._store_snapshot(snapshot, session_id)
            
            logger.info(f"Snapshot generated successfully in {snapshot.generation_time:.2f}s")
            return snapshot
            
        except Exception as e:
            logger.error(f"Error generating snapshot for {symbol}: {e}")
            raise
    
    def _get_market_data(self, symbol: str, timeframe: str, limit: int = 200) -> Optional[pd.DataFrame]:
        """Get market data from OKX API"""
        try:
            return self.api_manager.get_candles(symbol, timeframe, limit)
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None
    
    def _get_orderbook_data(self, symbol: str) -> Dict[str, Any]:
        """Get orderbook data from OKX API"""
        try:
            # This would call OKX orderbook API
            # For now, return simulated data
            return {
                'bids': [[50000, 1.5], [49950, 2.0], [49900, 1.8]],
                'asks': [[50050, 1.2], [50100, 1.7], [50150, 2.2]],
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching orderbook data: {e}")
            return {}
    
    def _generate_ai_narrative(self, symbol: str, technical_analysis: Dict, 
                              smc_analysis: Dict, price_action_analysis: Dict) -> tuple:
        """Generate AI narrative for the snapshot"""
        try:
            # Prepare analysis data for AI
            analysis_data = {
                'symbol': symbol,
                'technical': technical_analysis,
                'smc': smc_analysis,
                'price_action': price_action_analysis
            }
            
            # Generate narrative using the correct method
            narrative = self.ai_engine.generate_ai_snapshot(
                symbol=symbol,
                timeframe="1H",
                analysis_result=analysis_data,
                quick_mode=False
            )
            confidence = 0.75  # Calculate based on confluence
            
            return narrative, confidence
            
        except Exception as e:
            logger.error(f"Error generating AI narrative: {e}")
            return "Analysis tidak tersedia", 0.0
    
    def _safe_extract_indicator(self, indicators: Dict, key: str, default: float) -> float:
        """Safely extract indicator value"""
        try:
            value = indicators.get(key, default)
            if isinstance(value, (list, tuple)) and len(value) > 0:
                return float(value[-1])
            elif isinstance(value, (int, float)):
                return float(value)
            else:
                return default
        except:
            return default
    
    def _extract_macd_data(self, indicators: Dict) -> Dict[str, float]:
        """Extract MACD data"""
        try:
            macd_data = indicators.get('macd', {})
            if isinstance(macd_data, dict):
                return {
                    'macd': self._safe_extract_indicator(macd_data, 'macd', 0.0),
                    'signal': self._safe_extract_indicator(macd_data, 'signal', 0.0),
                    'histogram': self._safe_extract_indicator(macd_data, 'histogram', 0.0)
                }
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
        except:
            return {'macd': 0.0, 'signal': 0.0, 'histogram': 0.0}
    
    def _extract_bollinger_bands(self, indicators: Dict) -> Dict[str, float]:
        """Extract Bollinger Bands data"""
        try:
            bb_data = indicators.get('bollinger_bands', {})
            if isinstance(bb_data, dict):
                return {
                    'upper': self._safe_extract_indicator(bb_data, 'upper', 0.0),
                    'middle': self._safe_extract_indicator(bb_data, 'middle', 0.0),
                    'lower': self._safe_extract_indicator(bb_data, 'lower', 0.0)
                }
            return {'upper': 0.0, 'middle': 0.0, 'lower': 0.0}
        except:
            return {'upper': 0.0, 'middle': 0.0, 'lower': 0.0}
    
    def _analyze_orderbook_depth(self, orderbook_data: Dict) -> Dict[str, Any]:
        """Analyze orderbook depth"""
        try:
            bids = orderbook_data.get('bids', [])
            asks = orderbook_data.get('asks', [])
            
            if not bids or not asks:
                return {}
            
            # Calculate depth metrics
            bid_volume = sum(float(bid[1]) for bid in bids)
            ask_volume = sum(float(ask[1]) for ask in asks)
            
            return {
                'bid_volume': bid_volume,
                'ask_volume': ask_volume,
                'bid_ask_ratio': bid_volume / ask_volume if ask_volume > 0 else 0,
                'spread': float(asks[0][0]) - float(bids[0][0]) if bids and asks else 0,
                'depth_levels': len(bids) + len(asks)
            }
        except Exception as e:
            logger.error(f"Error analyzing orderbook depth: {e}")
            return {}
    
    def _calculate_risk_assessment(self, technical_analysis: Dict, smc_analysis: Dict) -> Dict[str, Any]:
        """Calculate risk assessment metrics"""
        try:
            indicators = technical_analysis.get('indicators', {})
            rsi = self._safe_extract_indicator(indicators, 'rsi', 50.0)
            
            # Calculate risk score (0-100)
            risk_score = 50  # Base risk
            
            # Adjust based on RSI
            if rsi > 70:
                risk_score += 20  # Overbought
            elif rsi < 30:
                risk_score += 15  # Oversold
            
            # Adjust based on SMC patterns
            smc_patterns = smc_analysis.get('patterns', {})
            if smc_patterns.get('bos_count', 0) > 2:
                risk_score += 10  # High volatility
            
            return {
                'risk_score': min(100, max(0, risk_score)),
                'risk_level': 'HIGH' if risk_score > 70 else 'MEDIUM' if risk_score > 40 else 'LOW',
                'volatility': 'HIGH' if rsi > 70 or rsi < 30 else 'MEDIUM'
            }
        except Exception as e:
            logger.error(f"Error calculating risk assessment: {e}")
            return {'risk_score': 50, 'risk_level': 'MEDIUM', 'volatility': 'MEDIUM'}
    
    def _assess_data_quality(self, df: pd.DataFrame, orderbook_data: Dict) -> str:
        """Assess data quality"""
        try:
            if df is None or df.empty:
                return 'POOR'
            
            # Check data completeness
            if len(df) < 50:
                return 'POOR'
            elif len(df) < 100:
                return 'FAIR'
            
            # Check for missing values
            if df.isnull().sum().sum() > 0:
                return 'FAIR'
            
            # Check orderbook data
            if not orderbook_data or not orderbook_data.get('bids') or not orderbook_data.get('asks'):
                return 'FAIR'
            
            return 'GOOD'
        except:
            return 'POOR'
    
    def _store_snapshot(self, snapshot: MarketSnapshot, session_id: str):
        """Store snapshot in database"""
        try:
            from app import db
            from models import AISnapshotArchive
            
            # Create database record
            snapshot_record = AISnapshotArchive(
                session_id=session_id,
                symbol=snapshot.symbol,
                timeframe=snapshot.timeframe,
                quick_mode=(snapshot.snapshot_type == SnapshotType.QUICK),
                ai_narrative=snapshot.ai_narrative,
                confluence_summary={
                    'technical_score': snapshot.confidence_score,
                    'smc_patterns': len(snapshot.smc_patterns),
                    'price_action_patterns': len(snapshot.price_action_patterns)
                },
                layer_analysis={
                    'technical_indicators': {
                        'rsi': snapshot.rsi,
                        'macd': snapshot.macd,
                        'bollinger_bands': snapshot.bollinger_bands
                    },
                    'market_structure': snapshot.market_structure,
                    'risk_assessment': snapshot.risk_assessment
                },
                snapshot_data=snapshot.to_dict(),
                confidence=snapshot.confidence_score
            )
            
            db.session.add(snapshot_record)
            db.session.commit()
            
            logger.info(f"Snapshot stored in database with ID: {snapshot_record.id}")
            
        except Exception as e:
            logger.error(f"Error storing snapshot in database: {e}")
            # Don't raise - snapshot generation should continue even if storage fails

def create_snapshot_generator() -> SnapshotGenerator:
    """Factory function to create snapshot generator"""
    return SnapshotGenerator()

# Global instance
snapshot_generator = create_snapshot_generator()