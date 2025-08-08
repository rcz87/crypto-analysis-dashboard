"""
Volume Profile Analyzer
Analyzes volume distribution across price levels to identify high-activity zones
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class VolumeProfileAnalyzer:
    """
    Analyzes volume profile to identify:
    - Point of Control (POC): Price level with highest volume
    - Value Area (VA): Range containing 70% of volume
    - High Volume Nodes (HVN): Areas of high trading activity
    - Low Volume Nodes (LVN): Potential support/resistance areas
    """
    
    def __init__(self):
        self.profile_periods = {
            '1D': 24,     # 24 hours for daily profile
            '1W': 168,    # 7 days for weekly profile
            '1M': 720     # 30 days for monthly profile
        }
        
        logger.info("📊 Volume Profile Analyzer initialized")
    
    def analyze_volume_profile(self, df: pd.DataFrame, num_bins: int = 50) -> Dict[str, Any]:
        """
        Analyze volume distribution across price levels
        """
        try:
            if df is None or df.empty:
                return self._get_default_profile()
            
            # Calculate price range
            price_range = df['high'].max() - df['low'].min()
            min_price = df['low'].min()
            max_price = df['high'].max()
            
            # Create price bins
            price_bins = np.linspace(min_price, max_price, num_bins + 1)
            bin_size = price_range / num_bins
            
            # Initialize volume profile
            volume_profile = np.zeros(num_bins)
            
            # Distribute volume across price levels
            for idx, row in df.iterrows():
                # Find which bins this candle spans
                low_bin = int((row['low'] - min_price) / bin_size)
                high_bin = int((row['high'] - min_price) / bin_size)
                
                # Ensure bins are within range
                low_bin = max(0, min(low_bin, num_bins - 1))
                high_bin = max(0, min(high_bin, num_bins - 1))
                
                # Distribute volume equally across bins
                if high_bin > low_bin:
                    vol_per_bin = row['volume'] / (high_bin - low_bin + 1)
                    for bin_idx in range(low_bin, high_bin + 1):
                        volume_profile[bin_idx] += vol_per_bin
                else:
                    volume_profile[low_bin] += row['volume']
            
            # Find Point of Control (POC)
            poc_idx = np.argmax(volume_profile)
            poc_price = price_bins[poc_idx] + (bin_size / 2)
            poc_volume = volume_profile[poc_idx]
            
            # Calculate Value Area (70% of volume)
            value_area = self._calculate_value_area(volume_profile, price_bins, bin_size)
            
            # Identify High/Low Volume Nodes
            hvn_lvn = self._identify_volume_nodes(volume_profile, price_bins, bin_size)
            
            # Calculate volume-weighted average price (VWAP)
            vwap = self._calculate_vwap(df)
            
            # Identify volume imbalances
            imbalances = self._identify_volume_imbalances(df)
            
            # Generate trading insights
            insights = self._generate_volume_insights(
                poc_price, value_area, hvn_lvn, df['close'].iloc[-1]
            )
            
            return {
                'poc': {
                    'price': round(poc_price, 6),
                    'volume': round(poc_volume, 2),
                    'strength': self._calculate_poc_strength(volume_profile, poc_idx)
                },
                'value_area': {
                    'high': round(value_area['high'], 6),
                    'low': round(value_area['low'], 6),
                    'percentage': value_area['percentage']
                },
                'high_volume_nodes': hvn_lvn['hvn'],
                'low_volume_nodes': hvn_lvn['lvn'],
                'vwap': round(vwap, 6),
                'volume_imbalances': imbalances,
                'insights': insights,
                'profile_data': {
                    'prices': [round(price_bins[i] + bin_size/2, 6) for i in range(num_bins)],
                    'volumes': [round(vol, 2) for vol in volume_profile]
                }
            }
            
        except Exception as e:
            logger.error(f"Volume profile analysis error: {e}")
            return self._get_default_profile()
    
    def _calculate_value_area(self, volume_profile: np.ndarray, price_bins: np.ndarray, 
                             bin_size: float, target_pct: float = 0.7) -> Dict[str, Any]:
        """Calculate the value area containing target percentage of volume"""
        try:
            total_volume = np.sum(volume_profile)
            target_volume = total_volume * target_pct
            
            # Start from POC and expand outward
            poc_idx = np.argmax(volume_profile)
            low_idx = poc_idx
            high_idx = poc_idx
            accumulated_volume = volume_profile[poc_idx]
            
            # Expand alternately above and below POC
            while accumulated_volume < target_volume:
                # Check which side has higher volume
                expand_up = expand_down = False
                
                if high_idx < len(volume_profile) - 1:
                    expand_up = True
                    up_volume = volume_profile[high_idx + 1] if high_idx < len(volume_profile) - 1 else 0
                else:
                    up_volume = 0
                
                if low_idx > 0:
                    expand_down = True
                    down_volume = volume_profile[low_idx - 1] if low_idx > 0 else 0
                else:
                    down_volume = 0
                
                # Expand in direction of higher volume
                if expand_up and (not expand_down or up_volume >= down_volume):
                    high_idx += 1
                    accumulated_volume += volume_profile[high_idx]
                elif expand_down:
                    low_idx -= 1
                    accumulated_volume += volume_profile[low_idx]
                else:
                    break
            
            value_area_high = price_bins[high_idx] + bin_size
            value_area_low = price_bins[low_idx]
            
            return {
                'high': value_area_high,
                'low': value_area_low,
                'percentage': round((accumulated_volume / total_volume) * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"Value area calculation error: {e}")
            return {'high': 0, 'low': 0, 'percentage': 0}
    
    def _identify_volume_nodes(self, volume_profile: np.ndarray, price_bins: np.ndarray, 
                              bin_size: float) -> Dict[str, List[Dict]]:
        """Identify high and low volume nodes"""
        try:
            # Calculate thresholds
            avg_volume = np.mean(volume_profile)
            std_volume = np.std(volume_profile)
            
            hvn_threshold = avg_volume + std_volume
            lvn_threshold = avg_volume - std_volume * 0.5
            
            hvn_nodes = []
            lvn_nodes = []
            
            for i in range(len(volume_profile)):
                price = price_bins[i] + (bin_size / 2)
                volume = volume_profile[i]
                
                if volume >= hvn_threshold:
                    hvn_nodes.append({
                        'price': round(price, 6),
                        'volume': round(volume, 2),
                        'strength': round((volume - avg_volume) / std_volume, 2)
                    })
                elif volume <= lvn_threshold and volume > 0:
                    lvn_nodes.append({
                        'price': round(price, 6),
                        'volume': round(volume, 2),
                        'gap_strength': round((avg_volume - volume) / std_volume, 2)
                    })
            
            # Sort by strength/importance
            hvn_nodes.sort(key=lambda x: x['volume'], reverse=True)
            lvn_nodes.sort(key=lambda x: x['gap_strength'], reverse=True)
            
            return {
                'hvn': hvn_nodes[:5],  # Top 5 HVN
                'lvn': lvn_nodes[:5]   # Top 5 LVN
            }
            
        except Exception as e:
            logger.error(f"Volume nodes identification error: {e}")
            return {'hvn': [], 'lvn': []}
    
    def _calculate_vwap(self, df: pd.DataFrame) -> float:
        """Calculate Volume Weighted Average Price"""
        try:
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            vwap = np.sum(typical_price * df['volume']) / np.sum(df['volume'])
            return vwap
        except:
            return 0
    
    def _identify_volume_imbalances(self, df: pd.DataFrame) -> List[Dict]:
        """Identify significant volume imbalances"""
        try:
            imbalances = []
            avg_volume = df['volume'].mean()
            
            for idx in range(1, len(df)):
                current_vol = df['volume'].iloc[idx]
                prev_vol = df['volume'].iloc[idx-1]
                
                # Check for significant volume spike
                if current_vol > avg_volume * 2 and current_vol > prev_vol * 1.5:
                    price_change = (df['close'].iloc[idx] - df['close'].iloc[idx-1]) / df['close'].iloc[idx-1] * 100
                    
                    imbalances.append({
                        'timestamp': df.index[idx].isoformat() if hasattr(df.index[idx], 'isoformat') else str(df.index[idx]),
                        'price': round(float(df['close'].iloc[idx]), 6),
                        'volume_ratio': round(current_vol / avg_volume, 2),
                        'price_change': round(price_change, 2),
                        'type': 'absorption' if abs(price_change) < 0.5 else 'expansion'
                    })
            
            # Return last 5 imbalances
            return imbalances[-5:]
            
        except Exception as e:
            logger.error(f"Volume imbalance identification error: {e}")
            return []
    
    def _calculate_poc_strength(self, volume_profile: np.ndarray, poc_idx: int) -> str:
        """Calculate POC strength based on volume concentration"""
        try:
            poc_volume = volume_profile[poc_idx]
            avg_volume = np.mean(volume_profile)
            
            ratio = poc_volume / avg_volume
            
            if ratio > 3:
                return "VERY_STRONG"
            elif ratio > 2:
                return "STRONG"
            elif ratio > 1.5:
                return "MODERATE"
            else:
                return "WEAK"
        except:
            return "UNKNOWN"
    
    def _generate_volume_insights(self, poc_price: float, value_area: Dict, 
                                 hvn_lvn: Dict, current_price: float) -> Dict[str, Any]:
        """Generate trading insights based on volume profile"""
        insights = {
            'price_position': '',
            'support_resistance': [],
            'trade_recommendation': '',
            'risk_level': ''
        }
        
        try:
            # Determine price position relative to value area
            if current_price > value_area['high']:
                insights['price_position'] = 'ABOVE_VALUE'
                insights['trade_recommendation'] = 'Look for pullback to value area high for long entries'
            elif current_price < value_area['low']:
                insights['price_position'] = 'BELOW_VALUE'
                insights['trade_recommendation'] = 'Look for bounce from value area low for short entries'
            else:
                insights['price_position'] = 'WITHIN_VALUE'
                insights['trade_recommendation'] = 'Wait for breakout from value area for directional trades'
            
            # Identify key support/resistance levels
            for hvn in hvn_lvn['hvn'][:3]:
                if hvn['price'] < current_price:
                    insights['support_resistance'].append({
                        'level': hvn['price'],
                        'type': 'SUPPORT',
                        'strength': 'STRONG'
                    })
                else:
                    insights['support_resistance'].append({
                        'level': hvn['price'],
                        'type': 'RESISTANCE',
                        'strength': 'STRONG'
                    })
            
            # Add LVN as potential breakout levels
            for lvn in hvn_lvn['lvn'][:2]:
                insights['support_resistance'].append({
                    'level': lvn['price'],
                    'type': 'BREAKOUT_LEVEL',
                    'strength': 'MODERATE'
                })
            
            # Determine risk level
            distance_from_poc = abs(current_price - poc_price) / poc_price * 100
            if distance_from_poc > 5:
                insights['risk_level'] = 'HIGH'
            elif distance_from_poc > 2:
                insights['risk_level'] = 'MODERATE'
            else:
                insights['risk_level'] = 'LOW'
            
        except Exception as e:
            logger.error(f"Volume insights generation error: {e}")
        
        return insights
    
    def _get_default_profile(self) -> Dict[str, Any]:
        """Return default volume profile when analysis fails"""
        return {
            'poc': {'price': 0, 'volume': 0, 'strength': 'UNKNOWN'},
            'value_area': {'high': 0, 'low': 0, 'percentage': 0},
            'high_volume_nodes': [],
            'low_volume_nodes': [],
            'vwap': 0,
            'volume_imbalances': [],
            'insights': {
                'price_position': 'UNKNOWN',
                'support_resistance': [],
                'trade_recommendation': 'Insufficient data for analysis',
                'risk_level': 'UNKNOWN'
            },
            'profile_data': {'prices': [], 'volumes': []}
        }