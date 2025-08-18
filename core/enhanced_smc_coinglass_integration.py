#!/usr/bin/env python3
"""
Enhanced SMC-CoinGlass Integration Module
Combines Smart Money Concept analysis with CoinGlass liquidation data
for superior market structure understanding
"""

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from dataclasses import dataclass

from .coinglass_analyzer import get_coinglass_analyzer, LiquidationZone

@dataclass
class EnhancedSMCZone:
    """SMC Zone enhanced with liquidation data"""
    zone_type: str  # 'OB', 'FVG', 'Liquidity', etc.
    price_level: float
    strength: float
    timeframe: str
    
    # CoinGlass enhancement
    liquidation_confluence: bool
    liquidation_volume: float
    liquidation_side: Optional[str]
    magnet_strength: float
    
    # Risk metrics
    risk_score: float
    confluence_score: float
    
    timestamp: datetime

@dataclass
class LiquidityMap:
    """Complete liquidity picture combining SMC + CoinGlass"""
    symbol: str
    current_price: float
    
    # SMC levels
    smc_zones: List[EnhancedSMCZone]
    key_levels: List[float]
    
    # CoinGlass levels  
    liquidation_zones: List[LiquidationZone]
    high_impact_zones: List[Dict]
    
    # Combined analysis
    confluent_levels: List[Dict]
    liquidity_magnets: List[Dict]
    sweep_probabilities: Dict[str, float]
    
    # Trading implications
    entry_zones: List[Dict]
    invalidation_levels: List[float]
    target_levels: List[float]
    
    timestamp: datetime

class EnhancedSMCCoinGlassIntegration:
    """
    Advanced integration combining SMC structure with CoinGlass liquidity data
    
    This module creates a comprehensive liquidity map by overlaying:
    - SMC Order Blocks, FVGs, and structural levels  
    - CoinGlass liquidation heatmaps and clusters
    - Open Interest positioning data
    - Funding rate extremes
    """
    
    def __init__(self):
        self.coinglass = get_coinglass_analyzer()
        self.logger = logging.getLogger(__name__)
        
        # Configuration
        self.confluence_threshold = 0.003  # 0.3% price proximity for confluence
        self.high_impact_threshold = 50000000  # $50M liquidation volume threshold
        
    def create_enhanced_liquidity_map(self, 
                                    symbol: str = "BTCUSDT", 
                                    timeframe: str = "1h",
                                    current_price: float = None) -> LiquidityMap:
        """
        Create comprehensive liquidity map combining SMC + CoinGlass data
        
        This is the core function that produces actionable trading intelligence
        """
        try:
            # Get current market data
            if current_price is None:
                # Get from OKX or use fallback
                current_price = 50000.0  # Fallback - should get from market data
            
            # Fetch SMC analysis
            smc_data = self._get_smc_structure(symbol, timeframe)
            
            # Fetch CoinGlass data
            liquidation_zones = self.coinglass.get_liquidation_heatmap(symbol)
            oi_data = self.coinglass.get_open_interest_data(symbol)
            
            # Create enhanced SMC zones with liquidation confluence
            enhanced_zones = self._enhance_smc_with_liquidation(
                smc_data.get('zones', []), 
                liquidation_zones,
                current_price
            )
            
            # Identify confluent levels
            confluent_levels = self._find_confluent_levels(
                enhanced_zones,
                liquidation_zones,
                current_price
            )
            
            # Find liquidity magnets (high-probability targets)
            liquidity_magnets = self._identify_liquidity_magnets(
                liquidation_zones,
                enhanced_zones,
                current_price
            )
            
            # Calculate sweep probabilities
            sweep_probabilities = self._calculate_sweep_probabilities(
                liquidation_zones,
                oi_data,
                current_price
            )
            
            # Generate trading zones
            entry_zones = self._generate_entry_zones(
                enhanced_zones,
                confluent_levels,
                current_price
            )
            
            # Set invalidation and target levels
            invalidation_levels = self._calculate_invalidation_levels(enhanced_zones, current_price)
            target_levels = self._calculate_target_levels(liquidity_magnets, current_price)
            
            return LiquidityMap(
                symbol=symbol,
                current_price=current_price,
                smc_zones=enhanced_zones,
                key_levels=[zone.price_level for zone in enhanced_zones],
                liquidation_zones=liquidation_zones,
                high_impact_zones=self._filter_high_impact_zones(liquidation_zones),
                confluent_levels=confluent_levels,
                liquidity_magnets=liquidity_magnets,
                sweep_probabilities=sweep_probabilities,
                entry_zones=entry_zones,
                invalidation_levels=invalidation_levels,
                target_levels=target_levels,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.logger.error(f"Error creating liquidity map: {e}")
            return self._create_fallback_map(symbol, current_price)
    
    def _get_smc_structure(self, symbol: str, timeframe: str) -> Dict:
        """Get SMC structural analysis"""
        try:
            # This would call our SMC analyzer
            # For now, return structured placeholder
            return {
                'zones': [
                    {
                        'type': 'Order_Block',
                        'price': 51000,
                        'strength': 85,
                        'timeframe': timeframe,
                        'direction': 'bullish'
                    },
                    {
                        'type': 'FVG',
                        'price': 49500,
                        'strength': 70,
                        'timeframe': timeframe,
                        'direction': 'bearish'
                    }
                ],
                'structure': {
                    'trend': 'bullish',
                    'choch_level': 50500,
                    'bos_level': 51200
                }
            }
        except Exception as e:
            self.logger.error(f"Error getting SMC structure: {e}")
            return {'zones': [], 'structure': {}}
    
    def _enhance_smc_with_liquidation(self, 
                                    smc_zones: List[Dict],
                                    liquidation_zones: List[LiquidationZone],
                                    current_price: float) -> List[EnhancedSMCZone]:
        """Enhance SMC zones with liquidation confluence data"""
        enhanced_zones = []
        
        for smc_zone in smc_zones:
            zone_price = smc_zone.get('price', 0)
            
            # Find liquidation confluence
            confluence_data = self._find_liquidation_confluence(
                zone_price, 
                liquidation_zones,
                current_price
            )
            
            # Calculate risk and confluence scores
            risk_score = self._calculate_zone_risk_score(
                smc_zone,
                confluence_data,
                current_price
            )
            
            confluence_score = self._calculate_confluence_score(
                smc_zone,
                confluence_data
            )
            
            enhanced_zone = EnhancedSMCZone(
                zone_type=smc_zone.get('type', 'Unknown'),
                price_level=zone_price,
                strength=smc_zone.get('strength', 0),
                timeframe=smc_zone.get('timeframe', '1h'),
                liquidation_confluence=confluence_data['has_confluence'],
                liquidation_volume=confluence_data['volume'],
                liquidation_side=confluence_data['side'],
                magnet_strength=confluence_data['magnet_strength'],
                risk_score=risk_score,
                confluence_score=confluence_score,
                timestamp=datetime.now()
            )
            
            enhanced_zones.append(enhanced_zone)
        
        return enhanced_zones
    
    def _find_liquidation_confluence(self, 
                                   zone_price: float,
                                   liquidation_zones: List[LiquidationZone],
                                   current_price: float) -> Dict:
        """Find liquidation zones that confluence with SMC level"""
        confluence_threshold = current_price * self.confluence_threshold
        
        confluent_zones = [
            zone for zone in liquidation_zones
            if abs(zone.price - zone_price) <= confluence_threshold
        ]
        
        if not confluent_zones:
            return {
                'has_confluence': False,
                'volume': 0,
                'side': None,
                'magnet_strength': 0
            }
        
        # Aggregate confluence data
        total_volume = sum(zone.volume for zone in confluent_zones)
        dominant_side = max(confluent_zones, key=lambda x: x.volume).side
        magnet_strength = sum(zone.strength for zone in confluent_zones) / len(confluent_zones)
        
        return {
            'has_confluence': True,
            'volume': total_volume,
            'side': dominant_side,
            'magnet_strength': magnet_strength,
            'zone_count': len(confluent_zones)
        }
    
    def _calculate_zone_risk_score(self, 
                                 smc_zone: Dict,
                                 confluence_data: Dict,
                                 current_price: float) -> float:
        """Calculate risk score for enhanced SMC zone"""
        base_risk = 50  # Neutral baseline
        
        # SMC strength factor
        smc_strength = smc_zone.get('strength', 50)
        base_risk += (smc_strength - 50) * 0.3
        
        # Liquidation confluence factor
        if confluence_data['has_confluence']:
            if confluence_data['volume'] > self.high_impact_threshold:
                base_risk += 20  # High volume confluence increases risk
            base_risk += confluence_data['magnet_strength'] * 0.2
        
        # Distance from current price factor
        zone_price = smc_zone.get('price', current_price)
        distance_percent = abs(zone_price - current_price) / current_price * 100
        
        if distance_percent > 5:  # Far zones are riskier
            base_risk += distance_percent * 2
        
        return max(0, min(100, base_risk))
    
    def _calculate_confluence_score(self, 
                                  smc_zone: Dict,
                                  confluence_data: Dict) -> float:
        """Calculate confluence score (higher = better confluence)"""
        score = smc_zone.get('strength', 0)
        
        if confluence_data['has_confluence']:
            # Volume boost
            volume_score = min(50, confluence_data['volume'] / 1000000)  # Max 50 points for volume
            score += volume_score
            
            # Magnet strength boost
            score += confluence_data['magnet_strength'] * 0.3
            
            # Multiple zones boost
            if confluence_data.get('zone_count', 0) > 1:
                score += 10
        
        return min(100, score)
    
    def _find_confluent_levels(self, 
                             enhanced_zones: List[EnhancedSMCZone],
                             liquidation_zones: List[LiquidationZone],
                             current_price: float) -> List[Dict]:
        """Find levels with strong SMC + liquidation confluence"""
        confluent_levels = []
        
        # Group by price proximity
        for zone in enhanced_zones:
            if zone.liquidation_confluence and zone.confluence_score > 70:
                confluent_levels.append({
                    'price': zone.price_level,
                    'smc_type': zone.zone_type,
                    'smc_strength': zone.strength,
                    'liquidation_volume': zone.liquidation_volume,
                    'confluence_score': zone.confluence_score,
                    'distance_percent': ((zone.price_level - current_price) / current_price) * 100,
                    'side': zone.liquidation_side,
                    'priority': self._calculate_level_priority(zone, current_price)
                })
        
        # Sort by confluence score descending
        return sorted(confluent_levels, key=lambda x: x['confluence_score'], reverse=True)
    
    def _identify_liquidity_magnets(self, 
                                  liquidation_zones: List[LiquidationZone],
                                  enhanced_zones: List[EnhancedSMCZone],
                                  current_price: float) -> List[Dict]:
        """Identify high-probability liquidity magnet levels"""
        magnets = []
        
        # High-volume liquidation clusters
        high_vol_liquidations = [
            zone for zone in liquidation_zones 
            if zone.volume > self.high_impact_threshold
        ]
        
        for liq_zone in high_vol_liquidations:
            # Check for SMC confluence
            smc_confluence = any(
                abs(smc.price_level - liq_zone.price) <= current_price * 0.002
                for smc in enhanced_zones
            )
            
            magnet_strength = liq_zone.strength
            if smc_confluence:
                magnet_strength *= 1.5  # Boost for SMC confluence
            
            magnets.append({
                'price': liq_zone.price,
                'volume': liq_zone.volume,
                'side': liq_zone.side,
                'magnet_strength': magnet_strength,
                'smc_confluence': smc_confluence,
                'distance_percent': ((liq_zone.price - current_price) / current_price) * 100,
                'probability': self._calculate_magnet_probability(liq_zone, current_price)
            })
        
        # Sort by magnet strength
        return sorted(magnets, key=lambda x: x['magnet_strength'], reverse=True)[:5]
    
    def _calculate_sweep_probabilities(self, 
                                     liquidation_zones: List[LiquidationZone],
                                     oi_data: Optional[Any],
                                     current_price: float) -> Dict[str, float]:
        """Calculate probabilities of liquidity sweeps in each direction"""
        upside_volume = sum(
            zone.volume for zone in liquidation_zones
            if zone.price > current_price and zone.side == 'short'
        )
        
        downside_volume = sum(
            zone.volume for zone in liquidation_zones
            if zone.price < current_price and zone.side == 'long'
        )
        
        total_volume = upside_volume + downside_volume
        
        if total_volume == 0:
            return {'upside_sweep': 50.0, 'downside_sweep': 50.0}
        
        upside_prob = (upside_volume / total_volume) * 100
        downside_prob = (downside_volume / total_volume) * 100
        
        # Factor in OI data if available
        if oi_data:
            if oi_data.long_ratio > 65:  # Heavy long bias
                downside_prob *= 1.2  # Increase downside sweep probability
            elif oi_data.short_ratio > 65:  # Heavy short bias
                upside_prob *= 1.2  # Increase upside sweep probability
        
        # Normalize to 100%
        total_prob = upside_prob + downside_prob
        if total_prob > 0:
            upside_prob = (upside_prob / total_prob) * 100
            downside_prob = (downside_prob / total_prob) * 100
        
        return {
            'upside_sweep': min(100, upside_prob),
            'downside_sweep': min(100, downside_prob)
        }
    
    def _generate_entry_zones(self, 
                            enhanced_zones: List[EnhancedSMCZone],
                            confluent_levels: List[Dict],
                            current_price: float) -> List[Dict]:
        """Generate optimal entry zones based on enhanced analysis"""
        entry_zones = []
        
        # Filter for high-quality zones
        quality_zones = [
            zone for zone in enhanced_zones
            if zone.confluence_score > 60 and zone.risk_score < 70
        ]
        
        for zone in quality_zones:
            entry_type = self._determine_entry_type(zone, current_price)
            if entry_type:
                entry_zones.append({
                    'price': zone.price_level,
                    'type': entry_type,
                    'smc_zone': zone.zone_type,
                    'strength': zone.confluence_score,
                    'risk_level': self._categorize_risk(zone.risk_score),
                    'liquidation_side': zone.liquidation_side,
                    'volume_support': zone.liquidation_volume,
                    'timeframe': zone.timeframe
                })
        
        return sorted(entry_zones, key=lambda x: x['strength'], reverse=True)
    
    def _determine_entry_type(self, zone: EnhancedSMCZone, current_price: float) -> Optional[str]:
        """Determine if zone presents long or short entry opportunity"""
        if zone.price_level > current_price:
            # Resistance zone above - potential short entry
            if zone.zone_type in ['Order_Block', 'Supply_Zone'] and zone.liquidation_side == 'long':
                return 'short'
        else:
            # Support zone below - potential long entry
            if zone.zone_type in ['Order_Block', 'Demand_Zone'] and zone.liquidation_side == 'short':
                return 'long'
        
        return None
    
    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk score into human-readable levels"""
        if risk_score < 30:
            return 'Low'
        elif risk_score < 50:
            return 'Medium-Low'
        elif risk_score < 70:
            return 'Medium'
        elif risk_score < 85:
            return 'Medium-High'
        else:
            return 'High'
    
    def _calculate_invalidation_levels(self, 
                                     enhanced_zones: List[EnhancedSMCZone],
                                     current_price: float) -> List[float]:
        """Calculate key invalidation levels for risk management"""
        invalidation_levels = []
        
        # Find significant structural levels
        for zone in enhanced_zones:
            if zone.zone_type in ['Order_Block', 'BOS', 'CHoCH'] and zone.strength > 70:
                # Add buffer for invalidation
                buffer = current_price * 0.01  # 1% buffer
                
                if zone.price_level > current_price:
                    invalidation_levels.append(zone.price_level + buffer)
                else:
                    invalidation_levels.append(zone.price_level - buffer)
        
        return sorted(list(set(invalidation_levels)))  # Remove duplicates and sort
    
    def _calculate_target_levels(self, 
                               liquidity_magnets: List[Dict],
                               current_price: float) -> List[float]:
        """Calculate target levels based on liquidity magnets"""
        return [magnet['price'] for magnet in liquidity_magnets[:3]]  # Top 3 targets
    
    def _filter_high_impact_zones(self, liquidation_zones: List[LiquidationZone]) -> List[Dict]:
        """Filter for high-impact liquidation zones"""
        return [
            {
                'price': zone.price,
                'volume': zone.volume,
                'side': zone.side,
                'strength': zone.strength
            }
            for zone in liquidation_zones
            if zone.volume > self.high_impact_threshold
        ]
    
    def _calculate_level_priority(self, zone: EnhancedSMCZone, current_price: float) -> float:
        """Calculate priority score for confluent levels"""
        priority = zone.confluence_score
        
        # Boost priority for closer levels
        distance = abs(zone.price_level - current_price) / current_price
        if distance < 0.02:  # Within 2%
            priority += 20
        elif distance < 0.05:  # Within 5%
            priority += 10
        
        return priority
    
    def _calculate_magnet_probability(self, zone: LiquidationZone, current_price: float) -> float:
        """Calculate probability that price will reach liquidation magnet"""
        base_prob = zone.strength
        
        # Distance factor
        distance_percent = abs(zone.price - current_price) / current_price * 100
        
        if distance_percent < 2:
            base_prob += 20
        elif distance_percent < 5:
            base_prob += 10
        elif distance_percent > 10:
            base_prob -= 15
        
        # Volume factor
        if zone.volume > self.high_impact_threshold * 2:
            base_prob += 15
        
        return max(0, min(100, base_prob))
    
    def _create_fallback_map(self, symbol: str, current_price: float) -> LiquidityMap:
        """Create fallback liquidity map when data unavailable"""
        return LiquidityMap(
            symbol=symbol,
            current_price=current_price or 50000,
            smc_zones=[],
            key_levels=[],
            liquidation_zones=[],
            high_impact_zones=[],
            confluent_levels=[],
            liquidity_magnets=[],
            sweep_probabilities={'upside_sweep': 50.0, 'downside_sweep': 50.0},
            entry_zones=[],
            invalidation_levels=[],
            target_levels=[],
            timestamp=datetime.now()
        )
    
    def get_trading_summary(self, liquidity_map: LiquidityMap) -> Dict[str, Any]:
        """Generate actionable trading summary from liquidity map"""
        try:
            summary = {
                'symbol': liquidity_map.symbol,
                'current_price': liquidity_map.current_price,
                'analysis_time': liquidity_map.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                
                # Key insights
                'key_insights': {
                    'confluent_levels_count': len(liquidity_map.confluent_levels),
                    'liquidity_magnets_count': len(liquidity_map.liquidity_magnets),
                    'high_impact_zones': len(liquidity_map.high_impact_zones),
                    'entry_opportunities': len(liquidity_map.entry_zones)
                },
                
                # Directional bias
                'directional_bias': {
                    'upside_sweep_probability': liquidity_map.sweep_probabilities.get('upside_sweep', 50),
                    'downside_sweep_probability': liquidity_map.sweep_probabilities.get('downside_sweep', 50),
                    'bias': 'Bullish' if liquidity_map.sweep_probabilities.get('upside_sweep', 50) > 55 else 'Bearish' if liquidity_map.sweep_probabilities.get('downside_sweep', 50) > 55 else 'Neutral'
                },
                
                # Top opportunities
                'top_entry_zones': liquidity_map.entry_zones[:3],
                'top_targets': liquidity_map.target_levels[:3],
                'critical_invalidation': liquidity_map.invalidation_levels[:2],
                
                # Risk assessment
                'overall_risk': self._assess_overall_risk(liquidity_map),
                
                # Action items
                'action_items': self._generate_action_items(liquidity_map)
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating trading summary: {e}")
            return {'error': str(e)}
    
    def _assess_overall_risk(self, liquidity_map: LiquidityMap) -> str:
        """Assess overall market risk from liquidity perspective"""
        high_risk_factors = 0
        
        # Check for high-impact zones nearby (within 3%)
        current_price = liquidity_map.current_price
        nearby_high_impact = [
            zone for zone in liquidity_map.high_impact_zones
            if abs(zone['price'] - current_price) / current_price <= 0.03
        ]
        
        if len(nearby_high_impact) > 2:
            high_risk_factors += 1
        
        # Check sweep probabilities for extreme readings
        max_sweep_prob = max(
            liquidity_map.sweep_probabilities.get('upside_sweep', 50),
            liquidity_map.sweep_probabilities.get('downside_sweep', 50)
        )
        
        if max_sweep_prob > 75:
            high_risk_factors += 1
        
        # Check for lack of confluent levels (unclear structure)
        if len(liquidity_map.confluent_levels) < 2:
            high_risk_factors += 1
        
        if high_risk_factors >= 2:
            return 'High'
        elif high_risk_factors == 1:
            return 'Medium'
        else:
            return 'Low'
    
    def _generate_action_items(self, liquidity_map: LiquidityMap) -> List[str]:
        """Generate actionable trading recommendations"""
        actions = []
        
        if liquidity_map.entry_zones:
            best_entry = liquidity_map.entry_zones[0]
            actions.append(f"Monitor {best_entry['type']} setup at ${best_entry['price']:.2f}")
        
        if liquidity_map.liquidity_magnets:
            top_magnet = liquidity_map.liquidity_magnets[0]
            actions.append(f"Target liquidity magnet at ${top_magnet['price']:.2f}")
        
        if liquidity_map.invalidation_levels:
            actions.append(f"Key invalidation below ${min(liquidity_map.invalidation_levels):.2f}")
        
        # Sweep warning
        upside_prob = liquidity_map.sweep_probabilities.get('upside_sweep', 50)
        downside_prob = liquidity_map.sweep_probabilities.get('downside_sweep', 50)
        
        if upside_prob > 70:
            actions.append("High probability upside liquidity sweep - monitor short entries")
        elif downside_prob > 70:
            actions.append("High probability downside liquidity sweep - monitor long entries")
        
        return actions

# Global integration instance
enhanced_integration = EnhancedSMCCoinGlassIntegration()

def get_enhanced_smc_coinglass_integration():
    """Get the global enhanced SMC-CoinGlass integration instance"""
    return enhanced_integration

if __name__ == "__main__":
    # Demo the integration
    integration = EnhancedSMCCoinGlassIntegration()
    
    print("Enhanced SMC-CoinGlass Integration Demo")
    print("=" * 50)
    
    # Create liquidity map
    liquidity_map = integration.create_enhanced_liquidity_map("BTCUSDT", "1h", 50000)
    
    print(f"Liquidity Map Created for {liquidity_map.symbol}")
    print(f"Current Price: ${liquidity_map.current_price}")
    print(f"Confluent Levels: {len(liquidity_map.confluent_levels)}")
    print(f"Entry Zones: {len(liquidity_map.entry_zones)}")
    
    # Generate trading summary
    summary = integration.get_trading_summary(liquidity_map)
    
    print("\n" + "=" * 30)
    print("TRADING SUMMARY")
    print("=" * 30)
    print(f"Directional Bias: {summary['directional_bias']['bias']}")
    print(f"Overall Risk: {summary['overall_risk']}")
    print("\nAction Items:")
    for i, action in enumerate(summary['action_items'], 1):
        print(f"{i}. {action}")