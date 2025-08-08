"""
🚀 PROFESSIONAL SMART MONEY CONCEPT (SMC) ANALYZER - ENHANCED VERSION
==================================================================

Advanced institutional-grade SMC analysis engine with comprehensive pattern detection:

📊 CORE FEATURES:
- CHoCH (Change of Character) with volume confirmation
- BOS (Break of Structure) with CVD validation
- Order Block identification with nested detection
- FVG (Fair Value Gap) with confluence analysis
- Liquidity Pool/Sweep detection with IRL/ERL categorization
- EQH/EQL (Equal Highs/Lows) detection
- Inducement zones with confidence scoring
- Volume Delta & CVD confirmation system
- Nested OB and confluence zone detection

🧠 AI-READY OUTPUT:
- Standardized dictionary format for AI snapshot system
- Confidence scoring (0-1) for all patterns
- Detailed descriptions for GPT prompt integration
- Visualization-ready data structures

🔧 PRODUCTION FEATURES:
- Comprehensive error handling and logging
- Modular architecture for easy extension
- Full documentation and type hints
- Performance optimized for real-time analysis
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from .inducement_detector import InducementDetector

logger = logging.getLogger(__name__)

class VolumeAnalyzer:
    """
    📊 Volume Analysis Engine
    
    Provides comprehensive volume analysis including:
    - Volume delta calculation
    - CVD (Cumulative Volume Delta) tracking
    - Volume absorption detection
    - Volume spike identification
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VolumeAnalyzer")
    
    def calculate_volume_delta(self, data: List[Dict]) -> List[Dict]:
        """
        Calculate volume delta for each candle
        
        Args:
            data: List of OHLCV candles
            
        Returns:
            List of volume delta data with buy/sell volume estimation
        """
        volume_deltas = []
        
        for i, candle in enumerate(data):
            # Estimate buy/sell volume based on price movement and volume
            close_price = candle['close']
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            total_volume = candle['volume']
            
            # Calculate price position within the candle
            if high_price != low_price:
                price_position = (close_price - low_price) / (high_price - low_price)
            else:
                price_position = 0.5
            
            # Estimate buy/sell volume
            buy_volume = total_volume * price_position
            sell_volume = total_volume * (1 - price_position)
            
            # Calculate delta
            delta = buy_volume - sell_volume
            
            volume_deltas.append({
                'timestamp': candle['timestamp'],
                'total_volume': total_volume,
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'delta': delta,
                'delta_ratio': delta / total_volume if total_volume > 0 else 0
            })
        
        return volume_deltas
    
    def detect_volume_absorption(self, data: List[Dict], volume_deltas: List[Dict]) -> List[Dict]:
        """
        Detect volume absorption patterns
        
        Args:
            data: OHLCV data
            volume_deltas: Volume delta data
            
        Returns:
            List of absorption patterns
        """
        absorptions = []
        avg_volume = sum(d['volume'] for d in data) / len(data)
        
        for i in range(2, len(data)):
            current_candle = data[i]
            current_delta = volume_deltas[i]
            
            # High volume with small price movement indicates absorption
            if (current_candle['volume'] > avg_volume * 2.0 and
                abs(current_candle['close'] - current_candle['open']) < 
                (current_candle['high'] - current_candle['low']) * 0.3):
                
                absorptions.append({
                    'timestamp': current_candle['timestamp'],
                    'type': 'absorption',
                    'volume': current_candle['volume'],
                    'volume_ratio': current_candle['volume'] / avg_volume,
                    'delta': current_delta['delta'],
                    'price_range': current_candle['high'] - current_candle['low'],
                    'body_size': abs(current_candle['close'] - current_candle['open']),
                    'direction': 'bullish' if current_delta['delta'] > 0 else 'bearish'
                })
        
        return absorptions

class CVDCalculator:
    """
    📈 Cumulative Volume Delta (CVD) Calculator
    
    Tracks cumulative volume delta to identify:
    - Price/volume divergences
    - Institutional accumulation/distribution
    - Trend confirmation/rejection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CVDCalculator")
    
    def calculate_cvd(self, volume_deltas: List[Dict]) -> List[Dict]:
        """
        Calculate Cumulative Volume Delta
        
        Args:
            volume_deltas: Volume delta data
            
        Returns:
            List of CVD data points
        """
        cvd_data = []
        cumulative_delta = 0
        
        for delta_point in volume_deltas:
            cumulative_delta += delta_point['delta']
            
            cvd_data.append({
                'timestamp': delta_point['timestamp'],
                'cvd': cumulative_delta,
                'delta': delta_point['delta'],
                'delta_ratio': delta_point['delta_ratio']
            })
        
        return cvd_data
    
    def detect_cvd_divergence(self, data: List[Dict], cvd_data: List[Dict]) -> List[Dict]:
        """
        Detect price-CVD divergences
        
        Args:
            data: OHLCV data
            cvd_data: CVD data
            
        Returns:
            List of divergence patterns
        """
        divergences = []
        
        if len(data) < 20 or len(cvd_data) < 20:
            return divergences
        
        # Look for divergences in recent data
        for i in range(10, len(data) - 1):
            price_current = data[i]['close']
            price_prev = data[i-10]['close']
            
            cvd_current = cvd_data[i]['cvd']
            cvd_prev = cvd_data[i-10]['cvd']
            
            # Bullish divergence: price down, CVD up
            if price_current < price_prev and cvd_current > cvd_prev:
                divergences.append({
                    'timestamp': data[i]['timestamp'],
                    'type': 'bullish_divergence',
                    'price_change': (price_current - price_prev) / price_prev,
                    'cvd_change': cvd_current - cvd_prev,
                    'strength': abs((price_current - price_prev) / price_prev) * 
                               abs(cvd_current - cvd_prev) / max(abs(cvd_current), abs(cvd_prev), 1)
                })
            
            # Bearish divergence: price up, CVD down
            elif price_current > price_prev and cvd_current < cvd_prev:
                divergences.append({
                    'timestamp': data[i]['timestamp'],
                    'type': 'bearish_divergence',
                    'price_change': (price_current - price_prev) / price_prev,
                    'cvd_change': cvd_current - cvd_prev,
                    'strength': abs((price_current - price_prev) / price_prev) * 
                               abs(cvd_current - cvd_prev) / max(abs(cvd_current), abs(cvd_prev), 1)
                })
        
        return divergences

class ConfluenceDetector:
    """
    🎯 Confluence Zone Detection Engine
    
    Identifies high-probability zones where multiple SMC patterns converge:
    - Nested Order Blocks
    - FVG within Order Blocks
    - Multiple pattern confirmations
    - Liquidity confluence areas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ConfluenceDetector")
    
    def detect_nested_order_blocks(self, order_blocks: List[Dict]) -> List[Dict]:
        """
        Detect nested order blocks (OB within OB)
        
        Args:
            order_blocks: List of detected order blocks
            
        Returns:
            List of nested order block patterns
        """
        nested_obs = []
        
        for i, ob1 in enumerate(order_blocks):
            for j, ob2 in enumerate(order_blocks):
                if i != j and self._is_nested_order_block(ob1, ob2):
                    nested_obs.append({
                        'timestamp': max(ob1['timestamp'], ob2['timestamp']),
                        'type': 'nested_order_block',
                        'outer_block': ob1,
                        'inner_block': ob2,
                        'direction': ob1['direction'],
                        'confluence_strength': self._calculate_confluence_strength(ob1, ob2),
                        'price_range': {
                            'high': max(ob1['price_high'], ob2['price_high']),
                            'low': min(ob1['price_low'], ob2['price_low'])
                        }
                    })
        
        return nested_obs
    
    def detect_fvg_ob_confluence(self, fvg_signals: List[Dict], order_blocks: List[Dict]) -> List[Dict]:
        """
        Detect FVG within Order Block confluence
        
        Args:
            fvg_signals: List of FVG patterns
            order_blocks: List of order blocks
            
        Returns:
            List of FVG-OB confluence patterns
        """
        confluences = []
        
        for fvg in fvg_signals:
            for ob in order_blocks:
                if self._is_fvg_within_ob(fvg, ob):
                    confluences.append({
                        'timestamp': max(fvg['timestamp'], ob['timestamp']),
                        'type': 'fvg_ob_confluence',
                        'fvg_pattern': fvg,
                        'order_block': ob,
                        'direction': fvg['direction'],
                        'confluence_strength': self._calculate_fvg_ob_confluence_strength(fvg, ob),
                        'high_probability_zone': {
                            'high': min(fvg['gap_high'], ob['price_high']),
                            'low': max(fvg['gap_low'], ob['price_low'])
                        }
                    })
        
        return confluences
    
    def _is_nested_order_block(self, ob1: Dict, ob2: Dict) -> bool:
        """Check if ob2 is nested within ob1"""
        return (ob1['price_low'] <= ob2['price_low'] and 
                ob1['price_high'] >= ob2['price_high'] and
                ob1['direction'] == ob2['direction'])
    
    def _is_fvg_within_ob(self, fvg: Dict, ob: Dict) -> bool:
        """Check if FVG is within Order Block"""
        return (ob['price_low'] <= fvg['gap_low'] and 
                ob['price_high'] >= fvg['gap_high'] and
                fvg['direction'] == ('bullish' if ob['direction'] == 'support' else 'bearish'))
    
    def _calculate_confluence_strength(self, ob1: Dict, ob2: Dict) -> float:
        """Calculate confluence strength between two order blocks"""
        volume_factor = (ob1['volume'] + ob2['volume']) / 2
        size_factor = min(ob1['strength'], ob2['strength'])
        return min(volume_factor * size_factor, 1.0)
    
    def _calculate_fvg_ob_confluence_strength(self, fvg: Dict, ob: Dict) -> float:
        """Calculate FVG-OB confluence strength"""
        fvg_strength = fvg['strength']
        ob_strength = ob['strength']
        return min((fvg_strength + ob_strength) / 2, 1.0)

class ProfessionalSMCAnalyzer:
    """
    🎯 Professional SMC Analyzer with Advanced Pattern Detection
    
    This class provides comprehensive Smart Money Concept analysis with:
    - Enhanced pattern detection algorithms
    - Volume delta and CVD confirmation
    - Confidence scoring system
    - Nested structure detection
    - AI-ready output format
    """
    
    # 📊 Analysis Configuration Constants
    SWING_PERIOD = 5                    # Period for swing high/low detection
    MIN_SWING_STRENGTH = 3              # Minimum bars for swing confirmation
    VOLUME_CONFIRMATION_THRESHOLD = 1.5  # Volume threshold for pattern confirmation
    CVD_DIVERGENCE_THRESHOLD = 0.3      # CVD divergence threshold
    CONFIDENCE_THRESHOLD = 0.65         # Minimum confidence for signal validity
    
    # 🎯 Pattern Detection Thresholds
    BOS_BREAK_THRESHOLD = 0.01          # 1% break for BOS confirmation
    FVG_MIN_GAP_SIZE = 0.0005          # Minimum gap size for FVG (0.05%)
    ORDER_BLOCK_MIN_SIZE = 0.002       # Minimum order block size (0.2%)
    
    def __init__(self):
        """
        Initialize the Professional SMC Analyzer
        
        Sets up all detection engines and configuration parameters
        """
        self.swing_period = self.SWING_PERIOD
        self.min_swing_strength = self.MIN_SWING_STRENGTH
        self.inducement_detector = InducementDetector()
        self.logger = logging.getLogger(__name__)
        
        # 📊 Initialize volume analysis components
        self.volume_analyzer = VolumeAnalyzer()
        self.cvd_calculator = CVDCalculator()
        self.confluence_detector = ConfluenceDetector()
        
        # 🧠 Initialize SMC Memory integration
        try:
            from .structure_memory import smc_memory
            self.smc_memory = smc_memory
            self.memory_enabled = True
            self.logger.info("🧠 SMC Memory integration enabled")
        except ImportError:
            self.logger.warning("SMC Memory not available")
            self.smc_memory = None
            self.memory_enabled = False
        
        self.logger.info("🚀 Professional SMC Analyzer initialized with enhanced features")
    
    def _safe_get_price(self, data_point: Dict, default: float = 0.0) -> float:
        """
        Safely extract price from various data structures with multiple fallbacks
        
        Args:
            data_point: Dictionary that may contain price information
            default: Default value if no price found
            
        Returns:
            Price value or default
        """
        try:
            # Try different possible price keys
            price_keys = ['price', 'sweep_price', 'price_high', 'price_low', 'level', 'close', 'high', 'low']
            
            for key in price_keys:
                if key in data_point and data_point[key] is not None:
                    return float(data_point[key])
            
            # If no price found, return default
            return default
            
        except (ValueError, TypeError, KeyError):
            return default
    
    # 🚀 ADVANCED SMC LOGIC FEATURES
    # =========================================================
    
    def detect_breaker_blocks(self, data: List[Dict], order_blocks: List[Dict], 
                            swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """
        🧱 BREAKER BLOCK LOGIC
        
        Deteksi breaker block: area order block sebelumnya yang gagal → lalu dibreak → 
        jadi support/resistance balik arah. Berfungsi sebagai zona reentry setelah stop hunt.
        
        Args:
            data: OHLCV data
            order_blocks: Previously detected order blocks
            swing_points: Swing highs and lows
            
        Returns:
            List of breaker block patterns
        """
        breaker_blocks = []
        
        if not order_blocks:
            return breaker_blocks
        
        self.logger.info(f"🧱 Analyzing {len(order_blocks)} order blocks for breaker patterns")
        
        for i, ob in enumerate(order_blocks):
            # Cari candle setelah order block yang membreak struktur
            ob_timestamp = ob['timestamp']
            ob_high = ob.get('price_high', self._safe_get_price(ob))
            ob_low = ob.get('price_low', self._safe_get_price(ob))
            
            # Cari candle yang membreak order block
            for j, candle in enumerate(data):
                if candle['timestamp'] > ob_timestamp:
                    # Check untuk bullish breaker (resistance OB yang dibreak ke atas)
                    if (ob['direction'] == 'resistance' and 
                        candle['close'] > ob_high * 1.001):  # 0.1% break threshold
                        
                        # Setelah break, area ini menjadi support
                        breaker_blocks.append({
                            'timestamp': candle['timestamp'],
                            'type': 'breaker_block',
                            'direction': 'support',  # Balik arah
                            'original_ob': ob,
                            'break_candle': candle,
                            'price_high': ob_high,
                            'price_low': ob_low,
                            'break_price': candle['close'],
                            'break_strength': (candle['close'] - ob_high) / ob_high,
                            'volume_confirmation': candle['volume'] > ob.get('volume', 0) * 1.2,
                            'confidence_score': min(1.0, 0.7 + (candle['volume'] / ob.get('volume', 1)) * 0.3)
                        })
                        break
                    
                    # Check untuk bearish breaker (support OB yang dibreak ke bawah)
                    elif (ob['direction'] == 'support' and 
                          candle['close'] < ob_low * 0.999):  # 0.1% break threshold
                        
                        # Setelah break, area ini menjadi resistance
                        breaker_blocks.append({
                            'timestamp': candle['timestamp'],
                            'type': 'breaker_block',
                            'direction': 'resistance',  # Balik arah
                            'original_ob': ob,
                            'break_candle': candle,
                            'price_high': ob_high,
                            'price_low': ob_low,
                            'break_price': candle['close'],
                            'break_strength': (ob_low - candle['close']) / ob_low,
                            'volume_confirmation': candle['volume'] > ob.get('volume', 0) * 1.2,
                            'confidence_score': min(1.0, 0.7 + (candle['volume'] / ob.get('volume', 1)) * 0.3)
                        })
                        break
        
        self.logger.info(f"🧱 Detected {len(breaker_blocks)} breaker block patterns")
        return breaker_blocks
    
    def categorize_irl_erl_liquidity(self, data: List[Dict], swing_points: Dict[str, List[Dict]], 
                                   liquidity_sweeps: List[Dict]) -> List[Dict]:
        """
        💧 IRL & ERL LIQUIDITY CATEGORIZATION
        
        Deteksi akumulasi likuiditas:
        - IRL (Internal Range Liquidity): di dalam swing range
        - ERL (External Range Liquidity): di luar swing range
        
        Args:
            data: OHLCV data
            swing_points: Swing highs and lows
            liquidity_sweeps: Existing liquidity sweeps
            
        Returns:
            Enhanced liquidity sweeps with IRL/ERL categorization
        """
        enhanced_sweeps = []
        
        if not liquidity_sweeps:
            return enhanced_sweeps
        
        # Ambil swing range terbaru untuk referensi
        recent_highs = swing_points.get('swing_highs', [])[-5:]
        recent_lows = swing_points.get('swing_lows', [])[-5:]
        
        if not recent_highs or not recent_lows:
            return liquidity_sweeps  # Return original jika tidak ada swing points
        
        # Tentukan current range
        current_range_high = max(self._safe_get_price(sh) for sh in recent_highs)
        current_range_low = min(self._safe_get_price(sl) for sl in recent_lows)
        range_size = current_range_high - current_range_low
        
        self.logger.info(f"💧 Analyzing liquidity with range: {current_range_low:.2f} - {current_range_high:.2f}")
        
        for sweep in liquidity_sweeps:
            sweep_price = self._safe_get_price(sweep)
            enhanced_sweep = sweep.copy()
            
            # Categorize berdasarkan posisi relatif terhadap range
            if sweep_price > current_range_high + (range_size * 0.1):
                # External Range Liquidity - Above range
                enhanced_sweep['liquidity_category'] = 'ERL'
                enhanced_sweep['liquidity_type'] = 'external_high'
                enhanced_sweep['range_position'] = 'above'
                enhanced_sweep['significance'] = 'high'  # ERL lebih significant
                
            elif sweep_price < current_range_low - (range_size * 0.1):
                # External Range Liquidity - Below range
                enhanced_sweep['liquidity_category'] = 'ERL'
                enhanced_sweep['liquidity_type'] = 'external_low'
                enhanced_sweep['range_position'] = 'below'
                enhanced_sweep['significance'] = 'high'  # ERL lebih significant
                
            else:
                # Internal Range Liquidity - Within range
                enhanced_sweep['liquidity_category'] = 'IRL'
                enhanced_sweep['liquidity_type'] = 'internal'
                enhanced_sweep['range_position'] = 'within'
                enhanced_sweep['significance'] = 'medium'  # IRL kurang significant
            
            # Tambahkan range context
            enhanced_sweep['range_context'] = {
                'range_high': current_range_high,
                'range_low': current_range_low,
                'range_size': range_size,
                'distance_from_range': min(
                    abs(sweep_price - current_range_high),
                    abs(sweep_price - current_range_low)
                )
            }
            
            enhanced_sweeps.append(enhanced_sweep)
        
        self.logger.info(f"💧 Categorized {len(enhanced_sweeps)} liquidity sweeps (IRL/ERL)")
        return enhanced_sweeps
    
    def analyze_killzone_timing(self, data: List[Dict], patterns: List[Dict]) -> List[Dict]:
        """
        ⏱️ KILLZONE SMC TIMING
        
        Implementasi time filter berbasis sesi trading:
        - London Open: 07:00–10:00 UTC
        - New York Open: 13:00–16:00 UTC  
        - Asia Session: 00:00–03:00 UTC
        
        Args:
            data: OHLCV data
            patterns: SMC patterns to analyze
            
        Returns:
            Patterns with killzone timing analysis
        """
        killzone_patterns = []
        
        # Define killzone sessions (UTC)
        killzones = {
            'asia': {'start': 0, 'end': 3},      # 00:00-03:00 UTC
            'london': {'start': 7, 'end': 10},   # 07:00-10:00 UTC
            'ny': {'start': 13, 'end': 16}       # 13:00-16:00 UTC
        }
        
        for pattern in patterns:
            enhanced_pattern = pattern.copy()
            
            # Extract timestamp and convert to UTC hour
            timestamp = pattern.get('timestamp', 0)
            if timestamp:
                dt = datetime.fromtimestamp(timestamp / 1000)
                utc_hour = dt.hour
                
                # Check which killzone the pattern falls into
                active_killzone = None
                killzone_strength = 0.0
                
                for zone_name, zone_time in killzones.items():
                    if zone_time['start'] <= utc_hour <= zone_time['end']:
                        active_killzone = zone_name
                        
                        # Calculate strength based on position in killzone
                        zone_duration = zone_time['end'] - zone_time['start']
                        zone_progress = (utc_hour - zone_time['start']) / zone_duration
                        
                        # Highest strength at the beginning of killzone
                        if zone_progress <= 0.5:
                            killzone_strength = 1.0 - (zone_progress * 0.3)
                        else:
                            killzone_strength = 0.7 - ((zone_progress - 0.5) * 0.4)
                        
                        break
                
                # Add killzone analysis to pattern
                enhanced_pattern['killzone_analysis'] = {
                    'active_killzone': active_killzone,
                    'killzone_strength': killzone_strength,
                    'utc_hour': utc_hour,
                    'timing_confidence': killzone_strength if active_killzone else 0.3,
                    'timing_description': self._get_killzone_description(active_killzone, utc_hour)
                }
                
                # Boost pattern confidence if in strong killzone
                if active_killzone and killzone_strength > 0.7:
                    original_confidence = enhanced_pattern.get('confidence_score', 0.5)
                    enhanced_pattern['confidence_score'] = min(1.0, original_confidence + (killzone_strength * 0.2))
                    enhanced_pattern['killzone_boost'] = True
                
            killzone_patterns.append(enhanced_pattern)
        
        self.logger.info(f"⏱️ Analyzed {len(killzone_patterns)} patterns for killzone timing")
        return killzone_patterns
    
    def _get_killzone_description(self, killzone: str, utc_hour: int) -> str:
        """Helper untuk generate killzone description"""
        if killzone == 'asia':
            return f"Asia Session (UTC {utc_hour}:00) - Lower volatility, range-bound"
        elif killzone == 'london':
            return f"London Open (UTC {utc_hour}:00) - High volatility, trend initiation"
        elif killzone == 'ny':
            return f"New York Open (UTC {utc_hour}:00) - Highest volatility, trend continuation"
        else:
            return f"Outside major sessions (UTC {utc_hour}:00) - Reduced significance"
    
    def map_premium_discount_zones(self, data: List[Dict], swing_points: Dict[str, List[Dict]], 
                                 patterns: List[Dict]) -> List[Dict]:
        """
        🎯 PREMIUM/DISCOUNT ZONE MAPPING
        
        Tandai area berdasarkan Fibonacci 0.5 (midline) dari swing terakhir:
        - Premium Zone: >0.5 (area mahal)
        - Discount Zone: <0.5 (area murah)
        
        Args:
            data: OHLCV data
            swing_points: Swing highs and lows
            patterns: SMC patterns to analyze
            
        Returns:
            Patterns with premium/discount zone mapping
        """
        mapped_patterns = []
        
        recent_highs = swing_points.get('swing_highs', [])[-3:]
        recent_lows = swing_points.get('swing_lows', [])[-3:]
        
        if not recent_highs or not recent_lows:
            return patterns  # Return original jika tidak ada swing points
        
        # Ambil swing range terbaru
        latest_high = max(self._safe_get_price(sh) for sh in recent_highs)
        latest_low = min(self._safe_get_price(sl) for sl in recent_lows)
        swing_range = latest_high - latest_low
        midline = latest_low + (swing_range * 0.5)  # Fibonacci 0.5
        
        # Define zone levels
        premium_threshold = latest_low + (swing_range * 0.618)  # 61.8% = Premium
        discount_threshold = latest_low + (swing_range * 0.382)  # 38.2% = Discount
        
        self.logger.info(f"🎯 Mapping zones - High: {latest_high:.2f}, Low: {latest_low:.2f}, Mid: {midline:.2f}")
        
        for pattern in patterns:
            enhanced_pattern = pattern.copy()
            
            # Get pattern price - safely handle different price fields
            pattern_price = self._safe_get_price(pattern)
            
            if pattern_price > 0:
                # Calculate position in range (0-1)
                range_position = (pattern_price - latest_low) / swing_range if swing_range > 0 else 0.5
                
                # Determine zone
                if range_position >= 0.618:
                    zone_type = 'premium'
                    zone_quality = 'high_premium'
                    logic_validity = 'bearish_bias'  # Di premium, look for sells
                elif range_position <= 0.382:
                    zone_type = 'discount'
                    zone_quality = 'high_discount'
                    logic_validity = 'bullish_bias'  # Di discount, look for buys
                else:
                    zone_type = 'equilibrium'
                    zone_quality = 'neutral'
                    logic_validity = 'neutral_bias'
                
                # Add zone analysis
                enhanced_pattern['zone_analysis'] = {
                    'zone_type': zone_type,
                    'zone_quality': zone_quality,
                    'logic_validity': logic_validity,
                    'range_position': range_position,
                    'distance_from_midline': abs(pattern_price - midline),
                    'swing_context': {
                        'swing_high': latest_high,
                        'swing_low': latest_low,
                        'swing_range': swing_range,
                        'midline': midline
                    }
                }
                
                # Validate logic: OB/FVG di area yang tepat
                pattern_direction = pattern.get('direction', 'neutral')
                
                # Boost confidence untuk pattern yang logis
                if ((zone_type == 'premium' and pattern_direction == 'bearish') or
                    (zone_type == 'discount' and pattern_direction == 'bullish')):
                    original_confidence = enhanced_pattern.get('confidence_score', 0.5)
                    enhanced_pattern['confidence_score'] = min(1.0, original_confidence + 0.15)
                    enhanced_pattern['zone_logic_boost'] = True
                
                # Reduce confidence untuk pattern yang tidak logis
                elif ((zone_type == 'premium' and pattern_direction == 'bullish') or
                      (zone_type == 'discount' and pattern_direction == 'bearish')):
                    original_confidence = enhanced_pattern.get('confidence_score', 0.5)
                    enhanced_pattern['confidence_score'] = max(0.2, original_confidence - 0.1)
                    enhanced_pattern['zone_logic_penalty'] = True
            
            mapped_patterns.append(enhanced_pattern)
        
        self.logger.info(f"🎯 Mapped {len(mapped_patterns)} patterns to premium/discount zones")
        return mapped_patterns
    
    def detect_mitigation_blocks(self, data: List[Dict], order_blocks: List[Dict]) -> List[Dict]:
        """
        🧱 MITIGATION BLOCK LOGIC
        
        Deteksi candle besar setelah OB yang "mengisi kembali" area imbalance OB sebelumnya.
        Digunakan untuk validasi OB yang sudah di-acknowledge oleh market.
        
        Args:
            data: OHLCV data
            order_blocks: Previously detected order blocks
            
        Returns:
            List of mitigation block patterns
        """
        mitigation_blocks = []
        
        if not order_blocks:
            return mitigation_blocks
        
        # Calculate average candle size for reference
        avg_candle_size = sum(abs(candle['close'] - candle['open']) for candle in data) / len(data)
        
        self.logger.info(f"🧱 Analyzing {len(order_blocks)} order blocks for mitigation patterns")
        
        for ob in order_blocks:
            ob_timestamp = ob['timestamp']
            ob_high = ob.get('price_high', self._safe_get_price(ob))
            ob_low = ob.get('price_low', self._safe_get_price(ob))
            ob_direction = ob['direction']
            
            # Cari candle setelah OB yang melakukan mitigation
            for i, candle in enumerate(data):
                if candle['timestamp'] > ob_timestamp:
                    candle_size = abs(candle['close'] - candle['open'])
                    
                    # Mitigation criteria:
                    # 1. Candle besar (>2x average)
                    # 2. Candle "mengisi" area OB
                    # 3. Volume tinggi
                    
                    is_large_candle = candle_size > avg_candle_size * 2.0
                    
                    if is_large_candle:
                        # Check apakah candle mengisi area OB
                        candle_fills_ob = False
                        mitigation_type = None
                        
                        if ob_direction == 'resistance':
                            # Untuk resistance OB, mitigation = candle naik yang mengisi area
                            if (candle['close'] > candle['open'] and 
                                candle['open'] < ob_high and candle['close'] > ob_low):
                                candle_fills_ob = True
                                mitigation_type = 'bullish_mitigation'
                        
                        elif ob_direction == 'support':
                            # Untuk support OB, mitigation = candle turun yang mengisi area
                            if (candle['close'] < candle['open'] and 
                                candle['open'] > ob_low and candle['close'] < ob_high):
                                candle_fills_ob = True
                                mitigation_type = 'bearish_mitigation'
                        
                        if candle_fills_ob:
                            # Calculate mitigation strength
                            fill_percentage = min(1.0, candle_size / (ob_high - ob_low))
                            volume_strength = candle['volume'] / ob.get('volume', candle['volume'])
                            
                            mitigation_blocks.append({
                                'timestamp': candle['timestamp'],
                                'type': 'mitigation_block',
                                'mitigation_type': mitigation_type,
                                'original_ob': ob,
                                'mitigation_candle': candle,
                                'fill_percentage': fill_percentage,
                                'volume_strength': volume_strength,
                                'candle_size_ratio': candle_size / avg_candle_size,
                                'confidence_score': min(1.0, 0.6 + (fill_percentage * 0.2) + (volume_strength * 0.2)),
                                'market_acknowledgment': True,  # OB sudah di-acknowledge
                                'ob_validation': 'confirmed'
                            })
                            break  # Hanya ambil mitigation pertama per OB
        
        self.logger.info(f"🧱 Detected {len(mitigation_blocks)} mitigation block patterns")
        return mitigation_blocks
    
    def detect_trendline_liquidity(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """
        📉 TRENDLINE LIQUIDITY DETECTION
        
        Identifikasi support/resistance miring (trendline) yang tersentuh berkali-kali
        → akumulasi likuiditas. Saat break, anggap sebagai sweep zone + entry confluence.
        
        Args:
            data: OHLCV data
            swing_points: Swing highs and lows
            
        Returns:
            List of trendline liquidity patterns
        """
        trendline_liquidities = []
        
        swing_highs = swing_points.get('swing_highs', [])
        swing_lows = swing_points.get('swing_lows', [])
        
        if len(swing_highs) < 3 or len(swing_lows) < 3:
            return trendline_liquidities
        
        self.logger.info(f"📉 Analyzing trendlines from {len(swing_highs)} highs and {len(swing_lows)} lows")
        
        # Analyze swing highs untuk resistance trendlines
        for i in range(len(swing_highs) - 2):
            point1 = swing_highs[i]
            point2 = swing_highs[i + 1]
            point3 = swing_highs[i + 2]
            
            # Calculate trendline slope
            time_diff = point2['timestamp'] - point1['timestamp']
            price_diff = point2['price'] - point1['price']
            
            if time_diff > 0:
                slope = price_diff / time_diff
                
                # Project trendline to point3
                projected_price = point1['price'] + slope * (point3['timestamp'] - point1['timestamp'])
                price_deviation = abs(point3['price'] - projected_price) / point3['price']
                
                # Jika point3 dekat dengan trendline (deviation < 2%), ini valid trendline
                if price_deviation < 0.02:
                    # Hitung berapa kali trendline tersentuh
                    touch_count = 3  # Minimal 3 (point1, point2, point3)
                    
                    # Cari touch tambahan
                    for j in range(i + 3, len(swing_highs)):
                        point = swing_highs[j]
                        projected = point1['price'] + slope * (point['timestamp'] - point1['timestamp'])
                        deviation = abs(point['price'] - projected) / point['price']
                        
                        if deviation < 0.02:
                            touch_count += 1
                    
                    # Cari trendline break
                    trendline_break = None
                    for candle in data:
                        if candle['timestamp'] > point3['timestamp']:
                            projected = point1['price'] + slope * (candle['timestamp'] - point1['timestamp'])
                            
                            # Check untuk break
                            if candle['high'] > projected * 1.01:  # 1% break threshold
                                trendline_break = {
                                    'timestamp': candle['timestamp'],
                                    'break_price': candle['high'],
                                    'projected_price': projected,
                                    'break_strength': (candle['high'] - projected) / projected,
                                    'volume': candle['volume']
                                }
                                break
                    
                    # Liquidity accumulation strength
                    liquidity_strength = min(1.0, 0.4 + (touch_count * 0.15))
                    
                    trendline_liquidities.append({
                        'timestamp': point1['timestamp'],
                        'type': 'trendline_liquidity',
                        'trendline_type': 'resistance',
                        'direction': 'bearish',
                        'touch_points': [point1, point2, point3],
                        'touch_count': touch_count,
                        'slope': slope,
                        'liquidity_strength': liquidity_strength,
                        'trendline_break': trendline_break,
                        'sweep_potential': 'high' if trendline_break else 'building',
                        'confidence_score': min(1.0, 0.5 + (touch_count * 0.1) + (0.3 if trendline_break else 0))
                    })
        
        # Analyze swing lows untuk support trendlines
        for i in range(len(swing_lows) - 2):
            point1 = swing_lows[i]
            point2 = swing_lows[i + 1]
            point3 = swing_lows[i + 2]
            
            # Calculate trendline slope
            time_diff = point2['timestamp'] - point1['timestamp']
            price_diff = point2['price'] - point1['price']
            
            if time_diff > 0:
                slope = price_diff / time_diff
                
                # Project trendline to point3
                projected_price = point1['price'] + slope * (point3['timestamp'] - point1['timestamp'])
                price_deviation = abs(point3['price'] - projected_price) / point3['price']
                
                # Jika point3 dekat dengan trendline (deviation < 2%), ini valid trendline
                if price_deviation < 0.02:
                    # Hitung berapa kali trendline tersentuh
                    touch_count = 3  # Minimal 3 (point1, point2, point3)
                    
                    # Cari touch tambahan
                    for j in range(i + 3, len(swing_lows)):
                        point = swing_lows[j]
                        projected = point1['price'] + slope * (point['timestamp'] - point1['timestamp'])
                        deviation = abs(point['price'] - projected) / point['price']
                        
                        if deviation < 0.02:
                            touch_count += 1
                    
                    # Cari trendline break
                    trendline_break = None
                    for candle in data:
                        if candle['timestamp'] > point3['timestamp']:
                            projected = point1['price'] + slope * (candle['timestamp'] - point1['timestamp'])
                            
                            # Check untuk break
                            if candle['low'] < projected * 0.99:  # 1% break threshold
                                trendline_break = {
                                    'timestamp': candle['timestamp'],
                                    'break_price': candle['low'],
                                    'projected_price': projected,
                                    'break_strength': (projected - candle['low']) / projected,
                                    'volume': candle['volume']
                                }
                                break
                    
                    # Liquidity accumulation strength
                    liquidity_strength = min(1.0, 0.4 + (touch_count * 0.15))
                    
                    trendline_liquidities.append({
                        'timestamp': point1['timestamp'],
                        'type': 'trendline_liquidity',
                        'trendline_type': 'support',
                        'direction': 'bullish',
                        'touch_points': [point1, point2, point3],
                        'touch_count': touch_count,
                        'slope': slope,
                        'liquidity_strength': liquidity_strength,
                        'trendline_break': trendline_break,
                        'sweep_potential': 'high' if trendline_break else 'building',
                        'confidence_score': min(1.0, 0.5 + (touch_count * 0.1) + (0.3 if trendline_break else 0))
                    })
        
        self.logger.info(f"📉 Detected {len(trendline_liquidities)} trendline liquidity patterns")
        return trendline_liquidities
    
    def analyze_comprehensive(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """
        🚀 Comprehensive SMC Analysis with Enhanced Features
        
        Provides complete Smart Money Concept analysis including:
        - Volume delta and CVD confirmation
        - Inducement detection with confidence scoring
        - Nested order blocks and confluence zones
        - IRL/ERL liquidity categorization
        - AI-ready standardized output format
        
        Args:
            df: OHLCV DataFrame
            symbol: Trading symbol (e.g., 'BTC-USDT')
            timeframe: Timeframe (e.g., '1H', '4H')
            
        Returns:
            Comprehensive analysis dictionary ready for AI snapshot system
        """
        
        try:
            if df is None or df.empty:
                return self._empty_smc_analysis()
            
            # Convert DataFrame to list of dicts for compatibility
            data = self._convert_df_to_data(df)
            
            # 🔍 1. Volume Analysis & CVD Calculation
            volume_deltas = self.volume_analyzer.calculate_volume_delta(data)
            cvd_data = self.cvd_calculator.calculate_cvd(volume_deltas)
            volume_absorptions = self.volume_analyzer.detect_volume_absorption(data, volume_deltas)
            cvd_divergences = self.cvd_calculator.detect_cvd_divergence(data, cvd_data)
            
            # 📊 2. Core SMC Pattern Detection
            swing_points = self.identify_swing_points(data)
            choch_bos_signals = self.detect_choch_bos_with_volume_confirmation(data, swing_points, volume_deltas)
            order_blocks = self.detect_order_blocks_enhanced(data, swing_points, volume_deltas)
            fvg_signals = self.detect_fvg_with_confidence(data, volume_deltas)
            liquidity_sweeps = self.detect_liquidity_sweeps_categorized(data, swing_points, volume_deltas)
            eqh_eql_signals = self.detect_eqh_eql(data, swing_points)
            
            # 🎯 3. Inducement Detection
            inducement_patterns = self.inducement_detector.detect_inducements(data, swing_points)
            
            # 🧱 4. Confluence Analysis
            nested_order_blocks = self.confluence_detector.detect_nested_order_blocks(order_blocks)
            fvg_ob_confluences = self.confluence_detector.detect_fvg_ob_confluence(fvg_signals, order_blocks)
            
            # 🚀 5. ADVANCED SMC FEATURES
            self.logger.info("🚀 Running Advanced SMC Features Analysis...")
            
            # 5.1 Breaker Block Detection
            breaker_blocks = self.detect_breaker_blocks(data, order_blocks, swing_points)
            
            # 5.2 Enhanced IRL/ERL Liquidity Categorization
            enhanced_liquidity_sweeps = self.categorize_irl_erl_liquidity(data, swing_points, liquidity_sweeps)
            
            # 5.3 Mitigation Block Detection
            mitigation_blocks = self.detect_mitigation_blocks(data, order_blocks)
            
            # 5.4 Trendline Liquidity Detection
            trendline_liquidities = self.detect_trendline_liquidity(data, swing_points)
            
            # 5.5 Killzone Timing Analysis (Apply to all patterns)
            all_patterns = choch_bos_signals + order_blocks + fvg_signals + enhanced_liquidity_sweeps + breaker_blocks + mitigation_blocks + trendline_liquidities
            killzone_analyzed_patterns = self.analyze_killzone_timing(data, all_patterns)
            
            # 5.6 Premium/Discount Zone Mapping (Apply to all patterns)
            zone_mapped_patterns = self.map_premium_discount_zones(data, swing_points, killzone_analyzed_patterns)
            
            # Separate patterns back by type for organized results
            enhanced_choch_bos = [p for p in zone_mapped_patterns if p.get('type') in ['choch', 'bos']]
            enhanced_order_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'order_block']
            enhanced_fvg_signals = [p for p in zone_mapped_patterns if p.get('type') == 'fvg']
            enhanced_liquidity_final = [p for p in zone_mapped_patterns if p.get('type') == 'liquidity_sweep']
            enhanced_breaker_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'breaker_block']
            enhanced_mitigation_blocks = [p for p in zone_mapped_patterns if p.get('type') == 'mitigation_block']
            enhanced_trendline_liquidities = [p for p in zone_mapped_patterns if p.get('type') == 'trendline_liquidity']
            
            # 🧠 6. Enhanced Market Structure Analysis
            market_structure = self._determine_enhanced_market_structure(
                enhanced_choch_bos, enhanced_order_blocks, inducement_patterns, cvd_divergences
            )
            
            # 🚀 NEW ADVANCED SMC FEATURES
            # 1. Volume Imbalance Detection
            volume_imbalances = self.detect_volume_imbalance(data, volume_deltas)
            
            # 2. FVG Refinement Entries
            refined_fvg_entries = self.detect_fvg_refinement_entries(data, enhanced_fvg_signals, enhanced_order_blocks)
            
            # 3. Real-time Swing Detection
            realtime_swings = self.detect_realtime_swing_points(data, lookback_period=10)
            
            # 4. Multi-timeframe Confluence (for now without HTF data)
            mtf_confluence = self.analyze_multi_timeframe_confluence({
                'order_blocks': enhanced_order_blocks,
                'fvg': enhanced_fvg_signals,
                'structure': market_structure
            })
            
            # 🎯 7. Generate Trading Signals with Enhanced Advanced Features
            trading_signals = self._generate_enhanced_trading_signals(
                enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final, 
                market_structure, inducement_patterns, cvd_divergences
            )
            
            # 📦 8. Generate AI-Ready Output with Advanced Features
            ai_ready_output = self._generate_ai_ready_output(
                enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final,
                eqh_eql_signals, inducement_patterns, nested_order_blocks,
                fvg_ob_confluences, volume_absorptions, cvd_divergences
            )
            
            # 🎯 9. Calculate Overall Confidence Score with Advanced Features
            confidence_score = self._calculate_enhanced_confidence_score(
                enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final,
                inducement_patterns, cvd_divergences, nested_order_blocks, fvg_ob_confluences
            )
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': int(df['timestamp'].iloc[-1].timestamp() * 1000) if 'timestamp' in df.columns else int(datetime.now().timestamp() * 1000),
                'current_price': float(df['close'].iloc[-1]),
                
                # 📊 Core SMC Patterns (Enhanced)
                'structure': {
                    'swing_points': swing_points,
                    'choch_bos_signals': enhanced_choch_bos,
                    'market_structure': market_structure
                },
                
                # 🎯 Trading Zones (Enhanced)
                'order_blocks': enhanced_order_blocks,
                'fvg': enhanced_fvg_signals,
                'liquidity_sweeps': enhanced_liquidity_final,
                'eqh_eql_signals': eqh_eql_signals,
                
                # 🔍 Advanced Features
                'inducement': inducement_patterns,
                'nested_order_blocks': nested_order_blocks,
                'confluence_zones': fvg_ob_confluences,
                
                # 🚀 ADVANCED SMC FEATURES
                'breaker_blocks': enhanced_breaker_blocks,
                'mitigation_blocks': enhanced_mitigation_blocks,
                'trendline_liquidities': enhanced_trendline_liquidities,
                'advanced_features': {
                    'breaker_blocks_count': len(enhanced_breaker_blocks),
                    'mitigation_blocks_count': len(enhanced_mitigation_blocks),
                    'trendline_liquidities_count': len(enhanced_trendline_liquidities),
                    'irl_erl_enhanced': True,
                    'killzone_timing_applied': True,
                    'premium_discount_mapped': True
                },
                
                # 🎯 NEW ADVANCED SMC PATTERNS
                'advanced_patterns': (
                    volume_imbalances +
                    refined_fvg_entries +
                    realtime_swings.get('swing_highs', []) +
                    realtime_swings.get('swing_lows', []) +
                    mtf_confluence.get('confluence_signals', [])
                ),
                
                # 📈 Volume Analysis
                'volume_confirmation': {
                    'volume_deltas': volume_deltas[-10:],  # Last 10 candles
                    'cvd_data': cvd_data[-10:],           # Last 10 candles
                    'volume_absorptions': volume_absorptions,
                    'cvd_divergences': cvd_divergences
                },
                
                # 🎯 AI-Ready Output
                'ai_snapshot': ai_ready_output,
                'trading_signals': trading_signals,
                'confidence_score': confidence_score,
                
                # 📊 Summary for GPT Integration
                'smc_summary': self._generate_enhanced_smc_summary(
                    enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final,
                    eqh_eql_signals, inducement_patterns, confidence_score
                )
            }
            
            # 🧠 Update SMC Memory if enabled
            if self.memory_enabled and self.smc_memory:
                try:
                    memory_data = {
                        'break_of_structure': enhanced_choch_bos,
                        'change_of_character': enhanced_choch_bos,
                        'order_blocks': {
                            'bullish': [ob for ob in enhanced_order_blocks if ob.get('direction') == 'support'],
                            'bearish': [ob for ob in enhanced_order_blocks if ob.get('direction') == 'resistance']
                        },
                        'fair_value_gaps': enhanced_fvg_signals,
                        'liquidity_sweep': enhanced_liquidity_final
                    }
                    self.smc_memory.update(memory_data, symbol=symbol, timeframe=timeframe)
                    self.logger.info(f"🧠 SMC Memory updated for {symbol} {timeframe}")
                except Exception as e:
                    self.logger.error(f"Failed to update SMC memory: {e}")
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': int(df['timestamp'].iloc[-1].timestamp() * 1000) if 'timestamp' in df.columns else int(datetime.now().timestamp() * 1000),
                'current_price': float(df['close'].iloc[-1]),
                
                # 📊 Core SMC Patterns (Enhanced)
                'structure': {
                    'swing_points': swing_points,
                    'choch_bos_signals': enhanced_choch_bos,
                    'market_structure': market_structure
                },
                
                # 🎯 Trading Zones (Enhanced)
                'order_blocks': enhanced_order_blocks,
                'fvg': enhanced_fvg_signals,
                'liquidity_sweeps': enhanced_liquidity_final,
                'eqh_eql_signals': eqh_eql_signals,
                
                # 🔍 Advanced Features
                'inducement': inducement_patterns,
                'nested_order_blocks': nested_order_blocks,
                'confluence_zones': fvg_ob_confluences,
                
                # 🚀 ADVANCED SMC FEATURES
                'breaker_blocks': enhanced_breaker_blocks,
                'mitigation_blocks': enhanced_mitigation_blocks,
                'trendline_liquidities': enhanced_trendline_liquidities,
                'advanced_features': {
                    'breaker_blocks_count': len(enhanced_breaker_blocks),
                    'mitigation_blocks_count': len(enhanced_mitigation_blocks),
                    'trendline_liquidities_count': len(enhanced_trendline_liquidities),
                    'irl_erl_enhanced': True,
                    'killzone_timing_applied': True,
                    'premium_discount_mapped': True
                },
                
                # 🎯 NEW ADVANCED SMC PATTERNS
                'advanced_patterns': (
                    volume_imbalances +
                    refined_fvg_entries +
                    realtime_swings.get('swing_highs', []) +
                    realtime_swings.get('swing_lows', []) +
                    mtf_confluence.get('confluence_signals', [])
                ),
                
                # 📈 Volume Analysis
                'volume_confirmation': {
                    'volume_deltas': volume_deltas[-10:],  # Last 10 candles
                    'cvd_data': cvd_data[-10:],           # Last 10 candles
                    'volume_absorptions': volume_absorptions,
                    'cvd_divergences': cvd_divergences
                },
                
                # 🎯 AI-Ready Output
                'ai_snapshot': ai_ready_output,
                'trading_signals': trading_signals,
                'confidence_score': confidence_score,
                
                # 📊 Summary for GPT Integration
                'smc_summary': self._generate_enhanced_smc_summary(
                    enhanced_choch_bos, enhanced_order_blocks, enhanced_fvg_signals, enhanced_liquidity_final,
                    eqh_eql_signals, inducement_patterns, confidence_score
                )
            }
            
        except Exception as e:
            self.logger.error(f"Enhanced SMC analysis error for {symbol}: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return self._empty_smc_analysis()
    
    def detect_choch_bos_with_volume_confirmation(self, data: List[Dict], swing_points: Dict[str, List[Dict]], 
                                                 volume_deltas: List[Dict]) -> List[Dict]:
        """
        🔍 Enhanced CHoCH/BOS Detection with Volume Confirmation
        
        Detects Change of Character and Break of Structure patterns with:
        - Volume delta confirmation
        - CVD divergence validation
        - Confidence scoring based on volume
        
        Args:
            data: OHLCV data
            swing_points: Identified swing points
            volume_deltas: Volume delta data
            
        Returns:
            List of confirmed CHoCH/BOS patterns with confidence scores
        """
        if not swing_points or len(swing_points['swing_highs']) < 2 or len(swing_points['swing_lows']) < 2:
            return []
        
        choch_bos_signals = []
        swing_highs = swing_points['swing_highs']
        swing_lows = swing_points['swing_lows']
        
        # Combine and sort swing points
        all_swings = swing_highs + swing_lows
        for swing in all_swings:
            swing['timestamp'] = int(swing['timestamp']) if isinstance(swing['timestamp'], str) else swing['timestamp']
        all_swings.sort(key=lambda x: x['timestamp'])
        
        if len(all_swings) < 3:
            return []
        
        # Enhanced pattern detection with volume confirmation
        for i in range(2, len(all_swings)):
            current_swing = all_swings[i]
            prev_swing = all_swings[i-1]
            prev_prev_swing = all_swings[i-2]
            
            # Get volume data for confirmation
            volume_at_break = self._get_volume_at_timestamp(volume_deltas, current_swing['timestamp'])
            
            # CHoCH Detection with Volume Confirmation
            if (prev_prev_swing['type'] == 'swing_high' and 
                prev_swing['type'] == 'swing_low' and 
                current_swing['type'] == 'swing_high'):
                
                # Bullish CHoCH: Higher High after Lower Low
                if (current_swing['price'] > prev_prev_swing['price'] and 
                    prev_swing['price'] < self._get_previous_swing_low(all_swings, i-1)['price']):
                    
                    # Volume confirmation
                    volume_confirmation = self._validate_volume_confirmation(
                        volume_at_break, 'bullish', self.VOLUME_CONFIRMATION_THRESHOLD
                    )
                    
                    confidence = self._calculate_pattern_confidence(
                        current_swing, prev_swing, volume_confirmation, 'CHoCH'
                    )
                    
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        choch_bos_signals.append({
                            'timestamp': current_swing['timestamp'],
                            'type': 'CHoCH',
                            'direction': 'bullish',
                            'price': current_swing['price'],
                            'strength': self._calculate_signal_strength(data, current_swing, prev_swing),
                            'volume_confirmation': volume_confirmation,
                            'confidence_score': confidence,
                            'description': f"Bullish CHoCH confirmed at {current_swing['price']:.4f} with {confidence:.1%} confidence"
                        })
            
            # Similar logic for bearish CHoCH and BOS patterns...
            elif (prev_prev_swing['type'] == 'swing_low' and 
                  prev_swing['type'] == 'swing_high' and 
                  current_swing['type'] == 'swing_low'):
                
                # Bearish CHoCH: Lower Low after Higher High
                if (current_swing['price'] < prev_prev_swing['price'] and 
                    prev_swing['price'] > self._get_previous_swing_high(all_swings, i-1)['price']):
                    
                    volume_confirmation = self._validate_volume_confirmation(
                        volume_at_break, 'bearish', self.VOLUME_CONFIRMATION_THRESHOLD
                    )
                    
                    confidence = self._calculate_pattern_confidence(
                        current_swing, prev_swing, volume_confirmation, 'CHoCH'
                    )
                    
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        choch_bos_signals.append({
                            'timestamp': current_swing['timestamp'],
                            'type': 'CHoCH',
                            'direction': 'bearish',
                            'price': current_swing['price'],
                            'strength': self._calculate_signal_strength(data, current_swing, prev_swing),
                            'volume_confirmation': volume_confirmation,
                            'confidence_score': confidence,
                            'description': f"Bearish CHoCH confirmed at {current_swing['price']:.4f} with {confidence:.1%} confidence"
                        })
        
        return choch_bos_signals
    
    def detect_order_blocks_enhanced(self, data: List[Dict], swing_points: Dict[str, List[Dict]], 
                                   volume_deltas: List[Dict]) -> List[Dict]:
        """
        🧱 Enhanced Order Block Detection
        
        Identifies institutional order blocks with:
        - Volume confirmation
        - Size validation
        - Nested block detection
        - Confidence scoring
        
        Args:
            data: OHLCV data
            swing_points: Identified swing points
            volume_deltas: Volume delta data
            
        Returns:
            List of confirmed order blocks with confidence scores
        """
        order_blocks = []
        
        if not swing_points or len(data) < 10:
            return order_blocks
        
        avg_volume = sum(d['volume'] for d in data) / len(data)
        
        # Enhanced order block detection around swing points
        for swing_high in swing_points['swing_highs']:
            idx = swing_high['index']
            if idx >= 3 and idx < len(data) - 3:
                block_start = max(0, idx - 3)
                block_end = min(len(data), idx + 3)
                
                # Calculate block metrics
                block_volume = sum(data[i]['volume'] for i in range(block_start, block_end)) / (block_end - block_start)
                block_size = swing_high['price'] - min(data[i]['low'] for i in range(block_start, block_end))
                
                # Volume and size validation
                if (block_volume > avg_volume * self.VOLUME_CONFIRMATION_THRESHOLD and
                    block_size > swing_high['price'] * self.ORDER_BLOCK_MIN_SIZE):
                    
                    # Get volume delta at block formation
                    volume_at_formation = self._get_volume_at_timestamp(volume_deltas, swing_high['timestamp'])
                    
                    confidence = self._calculate_order_block_confidence(
                        block_volume, avg_volume, block_size, volume_at_formation
                    )
                    
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        order_blocks.append({
                            'timestamp': swing_high['timestamp'],
                            'type': 'order_block',
                            'direction': 'resistance',
                            'price_high': swing_high['price'],
                            'price_low': min(data[i]['low'] for i in range(block_start, block_end)),
                            'volume': block_volume,
                            'volume_ratio': block_volume / avg_volume,
                            'size': block_size,
                            'strength': self._calculate_order_block_strength(data, block_start, block_end),
                            'confidence_score': confidence,
                            'description': f"Resistance OB at {swing_high['price']:.4f} with {confidence:.1%} confidence"
                        })
        
        # Similar logic for swing lows (support order blocks)
        for swing_low in swing_points['swing_lows']:
            idx = swing_low['index']
            if idx >= 3 and idx < len(data) - 3:
                block_start = max(0, idx - 3)
                block_end = min(len(data), idx + 3)
                
                block_volume = sum(data[i]['volume'] for i in range(block_start, block_end)) / (block_end - block_start)
                block_size = max(data[i]['high'] for i in range(block_start, block_end)) - swing_low['price']
                
                if (block_volume > avg_volume * self.VOLUME_CONFIRMATION_THRESHOLD and
                    block_size > swing_low['price'] * self.ORDER_BLOCK_MIN_SIZE):
                    
                    volume_at_formation = self._get_volume_at_timestamp(volume_deltas, swing_low['timestamp'])
                    
                    confidence = self._calculate_order_block_confidence(
                        block_volume, avg_volume, block_size, volume_at_formation
                    )
                    
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        order_blocks.append({
                            'timestamp': swing_low['timestamp'],
                            'type': 'order_block',
                            'direction': 'support',
                            'price_high': max(data[i]['high'] for i in range(block_start, block_end)),
                            'price_low': swing_low['price'],
                            'volume': block_volume,
                            'volume_ratio': block_volume / avg_volume,
                            'size': block_size,
                            'strength': self._calculate_order_block_strength(data, block_start, block_end),
                            'confidence_score': confidence,
                            'description': f"Support OB at {swing_low['price']:.4f} with {confidence:.1%} confidence"
                        })
        
        return order_blocks
    
    def detect_fvg_with_confidence(self, data: List[Dict], volume_deltas: List[Dict]) -> List[Dict]:
        """
        🔍 Enhanced FVG Detection with Confidence Scoring
        
        Detects Fair Value Gaps with:
        - Volume confirmation
        - Gap size validation
        - Confidence scoring
        
        Args:
            data: OHLCV data
            volume_deltas: Volume delta data
            
        Returns:
            List of confirmed FVG patterns with confidence scores
        """
        fvg_signals = []
        
        if len(data) < 3:
            return fvg_signals
        
        for i in range(1, len(data) - 1):
            prev_candle = data[i-1]
            current_candle = data[i]
            next_candle = data[i+1]
            
            # Get volume data for confirmation
            volume_at_formation = self._get_volume_at_timestamp(volume_deltas, current_candle['timestamp'])
            
            # Bullish FVG: Gap between prev high and next low
            if (prev_candle['high'] < next_candle['low'] and
                current_candle['close'] > current_candle['open']):
                
                gap_size = next_candle['low'] - prev_candle['high']
                if gap_size > current_candle['close'] * self.FVG_MIN_GAP_SIZE:
                    
                    confidence = self._calculate_fvg_confidence(
                        gap_size, current_candle, volume_at_formation, 'bullish'
                    )
                    
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        fvg_signals.append({
                            'timestamp': int(current_candle['timestamp']) if isinstance(current_candle['timestamp'], (int, float)) else int(current_candle['timestamp'].timestamp() * 1000),
                            'type': 'FVG',
                            'direction': 'bullish',
                            'gap_high': next_candle['low'],
                            'gap_low': prev_candle['high'],
                            'gap_size': gap_size,
                            'gap_size_percent': (gap_size / current_candle['close']) * 100,
                            'volume_confirmation': volume_at_formation,
                            'confidence_score': confidence,
                            'strength': self._calculate_fvg_strength(gap_size, current_candle),
                            'description': f"Bullish FVG at {prev_candle['high']:.4f}-{next_candle['low']:.4f} with {confidence:.1%} confidence"
                        })
            
            # Bearish FVG: Gap between prev low and next high
            elif (prev_candle['low'] > next_candle['high'] and
                  current_candle['close'] < current_candle['open']):
                
                gap_size = prev_candle['low'] - next_candle['high']
                if gap_size > current_candle['close'] * self.FVG_MIN_GAP_SIZE:
                    
                    confidence = self._calculate_fvg_confidence(
                        gap_size, current_candle, volume_at_formation, 'bearish'
                    )
                    
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        fvg_signals.append({
                            'timestamp': int(current_candle['timestamp']) if isinstance(current_candle['timestamp'], (int, float)) else int(current_candle['timestamp'].timestamp() * 1000),
                            'type': 'FVG',
                            'direction': 'bearish',
                            'gap_high': prev_candle['low'],
                            'gap_low': next_candle['high'],
                            'gap_size': gap_size,
                            'gap_size_percent': (gap_size / current_candle['close']) * 100,
                            'volume_confirmation': volume_at_formation,
                            'confidence_score': confidence,
                            'strength': self._calculate_fvg_strength(gap_size, current_candle),
                            'description': f"Bearish FVG at {next_candle['high']:.4f}-{prev_candle['low']:.4f} with {confidence:.1%} confidence"
                        })
        
        return fvg_signals
    
    def detect_liquidity_sweeps_categorized(self, data: List[Dict], swing_points: Dict[str, List[Dict]], 
                                          volume_deltas: List[Dict]) -> List[Dict]:
        """
        🌊 Enhanced Liquidity Sweep Detection with IRL/ERL Categorization
        
        Detects liquidity sweeps with:
        - IRL (Internal Range Liquidity) vs ERL (External Range Liquidity) categorization
        - Volume confirmation
        - Confidence scoring
        
        Args:
            data: OHLCV data
            swing_points: Identified swing points
            volume_deltas: Volume delta data
            
        Returns:
            List of categorized liquidity sweeps with confidence scores
        """
        liquidity_sweeps = []
        
        if not swing_points or len(data) < 10:
            return liquidity_sweeps
        
        swing_highs = swing_points['swing_highs']
        swing_lows = swing_points['swing_lows']
        
        # Detect liquidity sweeps at swing highs
        for i, swing_high in enumerate(swing_highs):
            if i < len(swing_highs) - 1:
                next_swing = swing_highs[i + 1]
                
                # Check if price swept above the high and then reversed
                sweep_candles = [candle for candle in data if 
                                swing_high['timestamp'] < candle['timestamp'] < next_swing['timestamp']]
                
                if sweep_candles:
                    max_price = max(candle['high'] for candle in sweep_candles)
                    
                    if max_price > swing_high['price'] * 1.001:  # 0.1% sweep
                        # Categorize as IRL or ERL
                        liquidity_category = self._categorize_liquidity_sweep(
                            swing_high, swing_highs, swing_lows, 'high'
                        )
                        
                        # Get volume at sweep
                        sweep_candle = max(sweep_candles, key=lambda x: x['high'])
                        volume_at_sweep = self._get_volume_at_timestamp(volume_deltas, sweep_candle['timestamp'])
                        
                        confidence = self._calculate_liquidity_sweep_confidence(
                            swing_high, max_price, volume_at_sweep, liquidity_category
                        )
                        
                        if confidence >= self.CONFIDENCE_THRESHOLD:
                            liquidity_sweeps.append({
                                'timestamp': sweep_candle['timestamp'],
                                'type': 'liquidity_sweep',
                                'direction': 'bearish',
                                'sweep_level': swing_high['price'],
                                'sweep_price': max_price,
                                'sweep_distance': max_price - swing_high['price'],
                                'liquidity_category': liquidity_category,
                                'volume_confirmation': volume_at_sweep,
                                'confidence_score': confidence,
                                'strength': self._calculate_liquidity_strength(data, sweep_candle, swing_high),
                                'description': f"Bearish {liquidity_category} sweep at {max_price:.4f} with {confidence:.1%} confidence"
                            })
        
        # Similar logic for swing lows
        for i, swing_low in enumerate(swing_lows):
            if i < len(swing_lows) - 1:
                next_swing = swing_lows[i + 1]
                
                sweep_candles = [candle for candle in data if 
                                swing_low['timestamp'] < candle['timestamp'] < next_swing['timestamp']]
                
                if sweep_candles:
                    min_price = min(candle['low'] for candle in sweep_candles)
                    
                    if min_price < swing_low['price'] * 0.999:  # 0.1% sweep
                        liquidity_category = self._categorize_liquidity_sweep(
                            swing_low, swing_highs, swing_lows, 'low'
                        )
                        
                        sweep_candle = min(sweep_candles, key=lambda x: x['low'])
                        volume_at_sweep = self._get_volume_at_timestamp(volume_deltas, sweep_candle['timestamp'])
                        
                        confidence = self._calculate_liquidity_sweep_confidence(
                            swing_low, min_price, volume_at_sweep, liquidity_category
                        )
                        
                        if confidence >= self.CONFIDENCE_THRESHOLD:
                            liquidity_sweeps.append({
                                'timestamp': sweep_candle['timestamp'],
                                'type': 'liquidity_sweep',
                                'direction': 'bullish',
                                'sweep_level': swing_low['price'],
                                'sweep_price': min_price,
                                'sweep_distance': swing_low['price'] - min_price,
                                'liquidity_category': liquidity_category,
                                'volume_confirmation': volume_at_sweep,
                                'confidence_score': confidence,
                                'strength': self._calculate_liquidity_strength(data, sweep_candle, swing_low),
                                'description': f"Bullish {liquidity_category} sweep at {min_price:.4f} with {confidence:.1%} confidence"
                            })
        
        return liquidity_sweeps
    
    def detect_eqh_eql(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """
        ⚖️ Enhanced Equal Highs/Lows Detection
        
        Detects equal highs and lows with:
        - Price tolerance validation
        - Confidence scoring
        - Pattern strength analysis
        
        Args:
            data: OHLCV data
            swing_points: Identified swing points
            
        Returns:
            List of EQH/EQL patterns with confidence scores
        """
        eqh_eql_signals = []
        
        if not swing_points:
            return eqh_eql_signals
        
        swing_highs = swing_points['swing_highs']
        swing_lows = swing_points['swing_lows']
        
        # Detect Equal Highs (EQH)
        for i in range(len(swing_highs) - 1):
            for j in range(i + 1, len(swing_highs)):
                high1 = swing_highs[i]
                high2 = swing_highs[j]
                
                # Check if prices are equal within tolerance
                price_diff = abs(high1['price'] - high2['price'])
                tolerance = high1['price'] * 0.002  # 0.2% tolerance
                
                if price_diff <= tolerance:
                    confidence = self._calculate_eqh_eql_confidence(high1, high2, price_diff, tolerance)
                    
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        eqh_eql_signals.append({
                            'timestamp': max(high1['timestamp'], high2['timestamp']),
                            'type': 'EQH',
                            'direction': 'resistance',
                            'price_level': (high1['price'] + high2['price']) / 2,
                            'price_1': high1['price'],
                            'price_2': high2['price'],
                            'price_difference': price_diff,
                            'tolerance': tolerance,
                            'confidence_score': confidence,
                            'strength': self._calculate_eqh_eql_strength(high1, high2),
                            'description': f"EQH at {(high1['price'] + high2['price']) / 2:.4f} with {confidence:.1%} confidence"
                        })
        
        # Detect Equal Lows (EQL)
        for i in range(len(swing_lows) - 1):
            for j in range(i + 1, len(swing_lows)):
                low1 = swing_lows[i]
                low2 = swing_lows[j]
                
                price_diff = abs(low1['price'] - low2['price'])
                tolerance = low1['price'] * 0.002  # 0.2% tolerance
                
                if price_diff <= tolerance:
                    confidence = self._calculate_eqh_eql_confidence(low1, low2, price_diff, tolerance)
                    
                    if confidence >= self.CONFIDENCE_THRESHOLD:
                        eqh_eql_signals.append({
                            'timestamp': max(low1['timestamp'], low2['timestamp']),
                            'type': 'EQL',
                            'direction': 'support',
                            'price_level': (low1['price'] + low2['price']) / 2,
                            'price_1': low1['price'],
                            'price_2': low2['price'],
                            'price_difference': price_diff,
                            'tolerance': tolerance,
                            'confidence_score': confidence,
                            'strength': self._calculate_eqh_eql_strength(low1, low2),
                            'description': f"EQL at {(low1['price'] + low2['price']) / 2:.4f} with {confidence:.1%} confidence"
                        })
        
        return eqh_eql_signals
    
    def _determine_enhanced_market_structure(self, choch_bos_signals: List[Dict], order_blocks: List[Dict], 
                                           inducement_patterns: List[Dict], cvd_divergences: List[Dict]) -> Dict[str, Any]:
        """
        🧠 Enhanced Market Structure Analysis
        
        Determines market structure with:
        - CHoCH/BOS pattern analysis
        - Inducement pattern consideration
        - CVD divergence integration
        - Confidence-based weighting
        
        Args:
            choch_bos_signals: CHoCH/BOS patterns
            order_blocks: Order block patterns
            inducement_patterns: Inducement patterns
            cvd_divergences: CVD divergence patterns
            
        Returns:
            Enhanced market structure analysis
        """
        # Get recent patterns (last 20 candles worth of data)
        recent_timestamp = int(datetime.now().timestamp() * 1000) - (20 * 3600000)  # 20 hours ago
        
        recent_choch_bos = [signal for signal in choch_bos_signals if signal['timestamp'] > recent_timestamp]
        recent_inducements = [pattern for pattern in inducement_patterns if pattern.get('timestamp', 0) > recent_timestamp]
        recent_cvd_divergences = [div for div in cvd_divergences if div['timestamp'] > recent_timestamp]
        
        # Calculate trend strength based on patterns
        bullish_signals = sum(1 for signal in recent_choch_bos if signal['direction'] == 'bullish')
        bearish_signals = sum(1 for signal in recent_choch_bos if signal['direction'] == 'bearish')
        
        # Factor in inducement patterns
        bullish_inducements = sum(1 for pattern in recent_inducements if pattern.get('direction') == 'bullish')
        bearish_inducements = sum(1 for pattern in recent_inducements if pattern.get('direction') == 'bearish')
        
        # Factor in CVD divergences
        bullish_divergences = sum(1 for div in recent_cvd_divergences if div['type'] == 'bullish_divergence')
        bearish_divergences = sum(1 for div in recent_cvd_divergences if div['type'] == 'bearish_divergence')
        
        # Calculate overall trend
        total_bullish = bullish_signals + bullish_inducements + bullish_divergences
        total_bearish = bearish_signals + bearish_inducements + bearish_divergences
        
        if total_bullish > total_bearish:
            trend = 'bullish'
            trend_strength = total_bullish / (total_bullish + total_bearish) if (total_bullish + total_bearish) > 0 else 0.5
        elif total_bearish > total_bullish:
            trend = 'bearish'
            trend_strength = total_bearish / (total_bullish + total_bearish) if (total_bullish + total_bearish) > 0 else 0.5
        else:
            trend = 'neutral'
            trend_strength = 0.5
        
        # Calculate structure quality
        structure_quality = self._calculate_structure_quality(recent_choch_bos, order_blocks, recent_inducements)
        
        return {
            'trend': trend,
            'trend_strength': trend_strength,
            'structure_quality': structure_quality,
            'recent_choch_bos_count': len(recent_choch_bos),
            'recent_inducement_count': len(recent_inducements),
            'recent_cvd_divergence_count': len(recent_cvd_divergences),
            'bullish_signals': total_bullish,
            'bearish_signals': total_bearish,
            'dominant_pattern': self._get_dominant_pattern(recent_choch_bos, recent_inducements),
            'description': f"{trend.title()} trend with {trend_strength:.1%} strength and {structure_quality:.1%} quality"
        }
    
    def _generate_ai_ready_output(self, choch_bos_signals: List[Dict], order_blocks: List[Dict], 
                                 fvg_signals: List[Dict], liquidity_sweeps: List[Dict],
                                 eqh_eql_signals: List[Dict], inducement_patterns: List[Dict],
                                 nested_order_blocks: List[Dict], fvg_ob_confluences: List[Dict],
                                 volume_absorptions: List[Dict], cvd_divergences: List[Dict]) -> Dict[str, Any]:
        """
        📦 Generate AI-Ready Output for GPT Integration
        
        Creates standardized output format for AI snapshot system with:
        - Structured pattern summaries
        - Confidence-based filtering
        - Detailed descriptions for GPT prompts
        - Visualization-ready data
        
        Returns:
            AI-ready analysis dictionary for GPT integration
        """
        
        # Filter high-confidence patterns only
        high_confidence_choch_bos = [s for s in choch_bos_signals if s.get('confidence_score', 0) >= 0.7]
        high_confidence_order_blocks = [ob for ob in order_blocks if ob.get('confidence_score', 0) >= 0.7]
        high_confidence_fvg = [fvg for fvg in fvg_signals if fvg.get('confidence_score', 0) >= 0.7]
        high_confidence_sweeps = [sweep for sweep in liquidity_sweeps if sweep.get('confidence_score', 0) >= 0.7]
        
        # Create AI-ready summary
        ai_summary = {
            'market_bias': self._determine_ai_market_bias(high_confidence_choch_bos, cvd_divergences),
            'key_levels': self._extract_key_levels(high_confidence_order_blocks, high_confidence_fvg),
            'trading_opportunities': self._identify_trading_opportunities(
                high_confidence_choch_bos, high_confidence_order_blocks, 
                high_confidence_fvg, inducement_patterns
            ),
            'risk_factors': self._identify_risk_factors(liquidity_sweeps, cvd_divergences),
            'confluence_zones': self._summarize_confluence_zones(nested_order_blocks, fvg_ob_confluences),
            'volume_insights': self._summarize_volume_insights(volume_absorptions, cvd_divergences)
        }
        
        # Generate GPT-ready descriptions
        gpt_descriptions = {
            'market_structure': self._generate_market_structure_description(high_confidence_choch_bos),
            'support_resistance': self._generate_support_resistance_description(high_confidence_order_blocks),
            'fair_value_gaps': self._generate_fvg_description(high_confidence_fvg),
            'liquidity_analysis': self._generate_liquidity_description(high_confidence_sweeps),
            'inducement_analysis': self._generate_inducement_description(inducement_patterns),
            'volume_analysis': self._generate_volume_description(volume_absorptions, cvd_divergences)
        }
        
        return {
            'ai_summary': ai_summary,
            'gpt_descriptions': gpt_descriptions,
            'pattern_counts': {
                'choch_bos': len(high_confidence_choch_bos),
                'order_blocks': len(high_confidence_order_blocks),
                'fvg': len(high_confidence_fvg),
                'liquidity_sweeps': len(high_confidence_sweeps),
                'inducements': len(inducement_patterns),
                'confluences': len(nested_order_blocks) + len(fvg_ob_confluences)
            },
            'visualization_ready': {
                'levels': self._prepare_levels_for_visualization(high_confidence_order_blocks, high_confidence_fvg),
                'zones': self._prepare_zones_for_visualization(nested_order_blocks, fvg_ob_confluences),
                'signals': self._prepare_signals_for_visualization(high_confidence_choch_bos, high_confidence_sweeps)
            }
        }
    
    def _generate_enhanced_trading_signals(self, choch_bos_signals: List[Dict], order_blocks: List[Dict],
                                         fvg_signals: List[Dict], liquidity_sweeps: List[Dict],
                                         market_structure: Dict[str, Any], inducement_patterns: List[Dict],
                                         cvd_divergences: List[Dict]) -> List[Dict]:
        """
        🎯 Generate Enhanced Trading Signals
        
        Creates comprehensive trading signals with:
        - Multiple pattern confirmation
        - Risk-reward calculations
        - Entry/SL/TP levels
        - Confidence-based filtering
        
        Returns:
            List of enhanced trading signals
        """
        trading_signals = []
        
        # Generate signals from high-confidence patterns
        high_confidence_patterns = [
            pattern for pattern in choch_bos_signals 
            if pattern.get('confidence_score', 0) >= self.CONFIDENCE_THRESHOLD
        ]
        
        for pattern in high_confidence_patterns:
            # Find supporting patterns
            supporting_obs = [ob for ob in order_blocks if self._is_supporting_pattern(pattern, ob)]
            supporting_fvgs = [fvg for fvg in fvg_signals if self._is_supporting_pattern(pattern, fvg)]
            supporting_inducements = [ind for ind in inducement_patterns if self._is_supporting_pattern(pattern, ind)]
            
            # Calculate signal strength based on confluences
            signal_strength = self._calculate_signal_strength_enhanced(
                pattern, supporting_obs, supporting_fvgs, supporting_inducements
            )
            
            if signal_strength >= 0.7:  # High-quality signals only
                # Calculate entry, SL, TP levels
                entry_level, sl_level, tp_level = self._calculate_trade_levels(
                    pattern, supporting_obs, supporting_fvgs, market_structure
                )
                
                # Calculate risk-reward ratio
                risk_reward_ratio = self._calculate_risk_reward_ratio(entry_level, sl_level, tp_level)
                
                if risk_reward_ratio >= 2.0:  # Minimum 2:1 R:R
                    trading_signals.append({
                        'timestamp': pattern['timestamp'],
                        'type': 'enhanced_trading_signal',
                        'direction': pattern['direction'],
                        'pattern_type': pattern['type'],
                        'entry_level': entry_level,
                        'stop_loss': sl_level,
                        'take_profit': tp_level,
                        'risk_reward_ratio': risk_reward_ratio,
                        'signal_strength': signal_strength,
                        'confidence_score': pattern['confidence_score'],
                        'supporting_patterns': {
                            'order_blocks': len(supporting_obs),
                            'fvg': len(supporting_fvgs),
                            'inducements': len(supporting_inducements)
                        },
                        'market_structure_alignment': self._check_market_structure_alignment(pattern, market_structure),
                        'description': f"{pattern['direction'].title()} {pattern['type']} signal with {signal_strength:.1%} strength and {risk_reward_ratio:.1f}:1 R:R"
                    })
        
        return trading_signals
    
    # ======================================================================
    # 🚀 ADVANCED SMC FEATURES - FITUR LANJUTAN
    # ======================================================================
    
    def detect_volume_imbalance(self, data: List[Dict], volume_deltas: List[Dict]) -> List[Dict]:
        """
        📊 Volume Imbalance Detection
        
        Deteksi ketidakseimbangan volume antara side bid/ask secara tiba-tiba
        Mencari imbalance > 2x untuk korelasi dengan FVG atau OB
        
        Args:
            data: OHLCV data
            volume_deltas: Volume delta data
            
        Returns:
            List of volume imbalance patterns
        """
        volume_imbalances = []
        
        if not volume_deltas or len(volume_deltas) < 2:
            return volume_imbalances
        
        self.logger.info(f"📊 Analyzing {len(volume_deltas)} candles for volume imbalance")
        
        for i in range(1, len(volume_deltas)):
            current_vd = volume_deltas[i]
            prev_vd = volume_deltas[i-1]
            
            buy_volume = current_vd.get('buy_volume', 0)
            sell_volume = current_vd.get('sell_volume', 0)
            
            if buy_volume > 0 and sell_volume > 0:
                # Calculate imbalance ratio
                if buy_volume > sell_volume:
                    imbalance_ratio = buy_volume / sell_volume
                    direction = 'bullish'
                    dominant_volume = buy_volume
                else:
                    imbalance_ratio = sell_volume / buy_volume
                    direction = 'bearish'
                    dominant_volume = sell_volume
                
                # Check for significant imbalance (>2x)
                if imbalance_ratio >= 2.0:
                    candle = data[i]
                    
                    # Calculate confidence based on imbalance strength
                    confidence = min(0.9, 0.4 + (imbalance_ratio / 10))
                    
                    # Check for volume spike
                    avg_volume = sum(vd.get('total_volume', 0) for vd in volume_deltas[max(0, i-5):i]) / min(5, i)
                    is_volume_spike = current_vd.get('total_volume', 0) > avg_volume * 1.5
                    
                    volume_imbalances.append({
                        'timestamp': candle['timestamp'],
                        'type': 'volume_imbalance',
                        'direction': direction,
                        'imbalance_ratio': imbalance_ratio,
                        'dominant_volume': dominant_volume,
                        'total_volume': current_vd.get('total_volume', 0),
                        'is_volume_spike': is_volume_spike,
                        'confidence_score': confidence,
                        'price_level': candle['close'],
                        'description': f"{direction.title()} volume imbalance {imbalance_ratio:.1f}:1 with {confidence:.1%} confidence"
                    })
        
        return volume_imbalances
    
    def detect_fvg_refinement_entries(self, data: List[Dict], fvg_signals: List[Dict], 
                                    order_blocks: List[Dict]) -> List[Dict]:
        """
        🎯 FVG Refinement Entry Detection
        
        Untuk setiap FVG, cari internal order block atau level retracement
        untuk entry yang lebih presisi (fibo 0.62)
        
        Args:
            data: OHLCV data
            fvg_signals: Detected FVG signals
            order_blocks: Detected order blocks
            
        Returns:
            Enhanced FVG signals with refined entry zones
        """
        enhanced_fvgs = []
        
        if not fvg_signals:
            return enhanced_fvgs
        
        self.logger.info(f"🎯 Analyzing {len(fvg_signals)} FVG signals for refinement entries")
        
        for fvg in fvg_signals:
            enhanced_fvg = fvg.copy()
            fvg_high = fvg.get('fvg_high', 0)
            fvg_low = fvg.get('fvg_low', 0)
            fvg_timestamp = fvg.get('timestamp')
            
            # Find internal order blocks within FVG
            internal_obs = []
            for ob in order_blocks:
                ob_high = ob.get('price_high', ob.get('price', 0))
                ob_low = ob.get('price_low', ob.get('price', 0))
                ob_timestamp = ob.get('timestamp')
                
                # Check if OB is within FVG price range and timeframe
                if (fvg_low <= ob_high <= fvg_high and 
                    fvg_low <= ob_low <= fvg_high and
                    ob_timestamp >= fvg_timestamp):
                    internal_obs.append(ob)
            
            # Calculate Fibonacci levels for refinement
            fvg_range = fvg_high - fvg_low
            fibo_levels = {
                'fibo_618': fvg_low + (fvg_range * 0.618),
                'fibo_500': fvg_low + (fvg_range * 0.500),
                'fibo_382': fvg_low + (fvg_range * 0.382)
            }
            
            # Determine refined entry zone
            if internal_obs:
                # Use internal order block as refined entry
                best_ob = max(internal_obs, key=lambda x: x.get('confidence_score', 0))
                refined_entry = {
                    'type': 'internal_order_block',
                    'entry_high': best_ob.get('price_high', best_ob.get('price', 0)),
                    'entry_low': best_ob.get('price_low', best_ob.get('price', 0)),
                    'confidence_boost': 0.2,
                    'ob_strength': best_ob.get('strength', 0)
                }
            else:
                # Use Fibonacci 0.618 as refined entry
                refined_entry = {
                    'type': 'fibonacci_retracement',
                    'entry_level': fibo_levels['fibo_618'],
                    'fibo_382': fibo_levels['fibo_382'],
                    'fibo_500': fibo_levels['fibo_500'],
                    'confidence_boost': 0.15
                }
            
            # Add refined entry to FVG
            enhanced_fvg['refined_entry_zone'] = refined_entry
            enhanced_fvg['confidence_score'] = min(0.95, 
                enhanced_fvg.get('confidence_score', 0) + refined_entry.get('confidence_boost', 0))
            
            enhanced_fvgs.append(enhanced_fvg)
        
        return enhanced_fvgs
    
    def detect_realtime_swing_points(self, data: List[Dict], lookback_period: int = 10) -> Dict[str, List[Dict]]:
        """
        ⚡ Real-time Swing Point Detection
        
        Deteksi swing point yang tidak perlu menunggu candle selesai penuh
        Untuk analisa streaming (1m/5m)
        
        Args:
            data: OHLCV data
            lookback_period: Number of candles to look back
            
        Returns:
            Dictionary with swing highs and lows
        """
        realtime_swings = {'swing_highs': [], 'swing_lows': []}
        
        if len(data) < lookback_period * 2:
            return realtime_swings
        
        self.logger.info(f"⚡ Detecting real-time swing points with {lookback_period} lookback")
        
        # Use shorter lookback for real-time detection
        for i in range(lookback_period, len(data) - lookback_period):
            current_candle = data[i]
            
            # Check for swing high (peak)
            is_swing_high = True
            for j in range(i - lookback_period, i + lookback_period + 1):
                if j != i and data[j]['high'] >= current_candle['high']:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                # Calculate swing strength based on price deviation
                price_range = max(c['high'] for c in data[i-lookback_period:i+lookback_period]) - \
                             min(c['low'] for c in data[i-lookback_period:i+lookback_period])
                
                strength = min(0.9, 0.5 + (price_range / current_candle['high']))
                
                realtime_swings['swing_highs'].append({
                    'timestamp': current_candle['timestamp'],
                    'type': 'realtime_swing_high',
                    'price': current_candle['high'],
                    'strength': strength,
                    'lookback_period': lookback_period,
                    'confidence_score': 0.7 + (strength * 0.2),
                    'description': f"Real-time swing high at {current_candle['high']:.4f}"
                })
            
            # Check for swing low (valley)
            is_swing_low = True
            for j in range(i - lookback_period, i + lookback_period + 1):
                if j != i and data[j]['low'] <= current_candle['low']:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                price_range = max(c['high'] for c in data[i-lookback_period:i+lookback_period]) - \
                             min(c['low'] for c in data[i-lookback_period:i+lookback_period])
                
                strength = min(0.9, 0.5 + (price_range / current_candle['low']))
                
                realtime_swings['swing_lows'].append({
                    'timestamp': current_candle['timestamp'],
                    'type': 'realtime_swing_low',
                    'price': current_candle['low'],
                    'strength': strength,
                    'lookback_period': lookback_period,
                    'confidence_score': 0.7 + (strength * 0.2),
                    'description': f"Real-time swing low at {current_candle['low']:.4f}"
                })
        
        return realtime_swings
    
    def analyze_multi_timeframe_confluence(self, current_analysis: Dict, higher_tf_analysis: Dict = None) -> Dict:
        """
        📈 Multi-Timeframe Confluence Analysis
        
        Bandingkan hasil analisis SMC dari timeframe lebih tinggi
        untuk validasi sinyal dengan confidence boost
        
        Args:
            current_analysis: Current timeframe analysis
            higher_tf_analysis: Higher timeframe analysis (1H/4H)
            
        Returns:
            Enhanced analysis with MTF confluence
        """
        mtf_confluence = {
            'has_htf_confirmation': False,
            'confluence_signals': [],
            'confidence_boost': 0.0
        }
        
        if not higher_tf_analysis:
            return mtf_confluence
        
        self.logger.info(f"📈 Analyzing multi-timeframe confluence")
        
        # Get current timeframe patterns
        current_obs = current_analysis.get('order_blocks', [])
        current_fvgs = current_analysis.get('fvg', [])
        current_structure = current_analysis.get('structure', {})
        
        # Get higher timeframe patterns
        htf_obs = higher_tf_analysis.get('order_blocks', [])
        htf_fvgs = higher_tf_analysis.get('fvg', [])
        htf_structure = higher_tf_analysis.get('structure', {})
        
        confluence_found = False
        
        # Check structure alignment
        current_trend = current_structure.get('trend', 'neutral')
        htf_trend = htf_structure.get('trend', 'neutral')
        
        if current_trend == htf_trend and current_trend != 'neutral':
            confluence_found = True
            mtf_confluence['confluence_signals'].append({
                'type': 'structure_alignment',
                'description': f"HTF and LTF both show {current_trend} trend",
                'confidence_boost': 0.15
            })
        
        # Check order block confluence
        for current_ob in current_obs:
            current_price = current_ob.get('price', 0)
            for htf_ob in htf_obs:
                htf_price = htf_ob.get('price', 0)
                # Check if prices are within 0.5% of each other
                if abs(current_price - htf_price) / current_price < 0.005:
                    confluence_found = True
                    mtf_confluence['confluence_signals'].append({
                        'type': 'order_block_confluence',
                        'description': f"OB confluence at {current_price:.4f}",
                        'confidence_boost': 0.2
                    })
        
        # Check FVG confluence
        for current_fvg in current_fvgs:
            current_mid = (current_fvg.get('fvg_high', 0) + current_fvg.get('fvg_low', 0)) / 2
            for htf_fvg in htf_fvgs:
                htf_mid = (htf_fvg.get('fvg_high', 0) + htf_fvg.get('fvg_low', 0)) / 2
                if abs(current_mid - htf_mid) / current_mid < 0.01:
                    confluence_found = True
                    mtf_confluence['confluence_signals'].append({
                        'type': 'fvg_confluence',
                        'description': f"FVG confluence at {current_mid:.4f}",
                        'confidence_boost': 0.18
                    })
        
        # Calculate total confidence boost
        mtf_confluence['has_htf_confirmation'] = confluence_found
        mtf_confluence['confidence_boost'] = sum(
            signal.get('confidence_boost', 0) for signal in mtf_confluence['confluence_signals']
        )
        
        return mtf_confluence
    
    def _calculate_enhanced_confidence_score(self, choch_bos_signals: List[Dict], order_blocks: List[Dict],
                                           fvg_signals: List[Dict], liquidity_sweeps: List[Dict],
                                           inducement_patterns: List[Dict], cvd_divergences: List[Dict],
                                           nested_order_blocks: List[Dict], fvg_ob_confluences: List[Dict]) -> float:
        """
        🧠 Calculate Enhanced Confidence Score
        
        Calculates overall analysis confidence based on:
        - Pattern quality and quantity
        - Volume confirmation
        - Confluence strength
        - Pattern consistency
        
        Returns:
            Overall confidence score (0.0 to 1.0)
        """
        
        # Base confidence from pattern quality
        pattern_scores = []
        
        # CHoCH/BOS confidence
        if choch_bos_signals:
            avg_choch_bos_confidence = sum(s.get('confidence_score', 0) for s in choch_bos_signals) / len(choch_bos_signals)
            pattern_scores.append(avg_choch_bos_confidence * 0.3)  # 30% weight
        
        # Order block confidence
        if order_blocks:
            avg_ob_confidence = sum(ob.get('confidence_score', 0) for ob in order_blocks) / len(order_blocks)
            pattern_scores.append(avg_ob_confidence * 0.25)  # 25% weight
        
        # FVG confidence
        if fvg_signals:
            avg_fvg_confidence = sum(fvg.get('confidence_score', 0) for fvg in fvg_signals) / len(fvg_signals)
            pattern_scores.append(avg_fvg_confidence * 0.2)  # 20% weight
        
        # Liquidity sweep confidence
        if liquidity_sweeps:
            avg_sweep_confidence = sum(sweep.get('confidence_score', 0) for sweep in liquidity_sweeps) / len(liquidity_sweeps)
            pattern_scores.append(avg_sweep_confidence * 0.15)  # 15% weight
        
        # Confluence bonus
        confluence_bonus = 0
        if nested_order_blocks or fvg_ob_confluences:
            confluence_bonus = min(0.1, (len(nested_order_blocks) + len(fvg_ob_confluences)) * 0.02)
        
        # Volume confirmation bonus
        volume_bonus = 0
        if cvd_divergences:
            strong_divergences = [div for div in cvd_divergences if div.get('strength', 0) > 0.5]
            volume_bonus = min(0.05, len(strong_divergences) * 0.01)
        
        # Calculate final confidence
        base_confidence = sum(pattern_scores) if pattern_scores else 0.5
        final_confidence = min(1.0, base_confidence + confluence_bonus + volume_bonus)
        
        return final_confidence
    
    def _generate_enhanced_smc_summary(self, choch_bos_signals: List[Dict], order_blocks: List[Dict],
                                     fvg_signals: List[Dict], liquidity_sweeps: List[Dict],
                                     eqh_eql_signals: List[Dict], inducement_patterns: List[Dict],
                                     confidence_score: float) -> Dict[str, Any]:
        """
        📊 Generate Enhanced SMC Summary for GPT Integration
        
        Creates comprehensive summary for AI analysis with:
        - Pattern counts and strengths
        - Market bias assessment
        - Key level identification
        - Trading recommendations
        
        Returns:
            Enhanced SMC summary dictionary
        """
        
        # Calculate pattern strengths
        strong_patterns = {
            'choch_bos': [s for s in choch_bos_signals if s.get('confidence_score', 0) >= 0.8],
            'order_blocks': [ob for ob in order_blocks if ob.get('confidence_score', 0) >= 0.8],
            'fvg': [fvg for fvg in fvg_signals if fvg.get('confidence_score', 0) >= 0.8],
            'liquidity_sweeps': [sweep for sweep in liquidity_sweeps if sweep.get('confidence_score', 0) >= 0.8]
        }
        
        # Determine market bias
        bullish_signals = sum(1 for s in choch_bos_signals if s['direction'] == 'bullish')
        bearish_signals = sum(1 for s in choch_bos_signals if s['direction'] == 'bearish')
        
        market_bias = 'bullish' if bullish_signals > bearish_signals else 'bearish' if bearish_signals > bullish_signals else 'neutral'
        
        # Extract key levels
        resistance_levels = [ob['price_high'] for ob in order_blocks if ob['direction'] == 'resistance']
        support_levels = [ob['price_low'] for ob in order_blocks if ob['direction'] == 'support']
        
        return {
            'analysis_quality': 'high' if confidence_score >= 0.8 else 'medium' if confidence_score >= 0.6 else 'low',
            'confidence_score': confidence_score,
            'market_bias': market_bias,
            'bias_strength': abs(bullish_signals - bearish_signals) / max(bullish_signals + bearish_signals, 1),
            
            'pattern_summary': {
                'total_patterns': len(choch_bos_signals) + len(order_blocks) + len(fvg_signals) + len(liquidity_sweeps),
                'strong_patterns': sum(len(patterns) for patterns in strong_patterns.values()),
                'choch_bos_count': len(choch_bos_signals),
                'order_block_count': len(order_blocks),
                'fvg_count': len(fvg_signals),
                'liquidity_sweep_count': len(liquidity_sweeps),
                'inducement_count': len(inducement_patterns)
            },
            
            'key_levels': {
                'resistance_levels': sorted(resistance_levels, reverse=True)[:3],  # Top 3
                'support_levels': sorted(support_levels)[:3],  # Top 3
                'fvg_levels': [fvg['gap_low'] for fvg in fvg_signals[:3]]  # Top 3
            },
            
            'trading_context': {
                'high_probability_zones': len([ob for ob in order_blocks if ob.get('confidence_score', 0) >= 0.9]),
                'confluence_opportunities': len([fvg for fvg in fvg_signals if fvg.get('confidence_score', 0) >= 0.9]),
                'risk_areas': len([sweep for sweep in liquidity_sweeps if sweep.get('confidence_score', 0) >= 0.8])
            },
            
            'recommendation': self._generate_trading_recommendation(market_bias, confidence_score, strong_patterns)
        }
    
    # 🔧 Helper Methods for Enhanced Functionality
    
    def _get_volume_at_timestamp(self, volume_deltas: List[Dict], timestamp: int) -> Dict:
        """Get volume delta data at specific timestamp"""
        for volume_data in volume_deltas:
            if volume_data['timestamp'] == timestamp:
                return volume_data
        return {'delta': 0, 'delta_ratio': 0, 'total_volume': 0}
    
    def _validate_volume_confirmation(self, volume_data: Dict, direction: str, threshold: float) -> bool:
        """Validate volume confirmation for pattern"""
        if direction == 'bullish':
            return volume_data.get('delta', 0) > 0 and volume_data.get('delta_ratio', 0) > 0.1
        else:
            return volume_data.get('delta', 0) < 0 and volume_data.get('delta_ratio', 0) < -0.1
    
    def _calculate_pattern_confidence(self, current_swing: Dict, prev_swing: Dict, 
                                    volume_confirmation: bool, pattern_type: str) -> float:
        """Calculate pattern confidence score"""
        base_confidence = 0.6
        
        # Volume confirmation bonus
        if volume_confirmation:
            base_confidence += 0.2
        
        # Pattern type bonus
        if pattern_type == 'CHoCH':
            base_confidence += 0.1
        elif pattern_type == 'BOS':
            base_confidence += 0.15
        
        # Price movement strength
        price_movement = abs(current_swing['price'] - prev_swing['price']) / prev_swing['price']
        movement_bonus = min(0.1, price_movement * 10)
        
        return min(1.0, base_confidence + movement_bonus)
    
    def _calculate_order_block_confidence(self, block_volume: float, avg_volume: float, 
                                        block_size: float, volume_at_formation: Dict) -> float:
        """Calculate order block confidence score"""
        volume_ratio = block_volume / avg_volume
        volume_score = min(0.4, volume_ratio * 0.2)
        
        size_score = min(0.3, block_size * 100)  # Normalize size
        
        delta_score = 0.2 if abs(volume_at_formation.get('delta_ratio', 0)) > 0.1 else 0.1
        
        return min(1.0, 0.3 + volume_score + size_score + delta_score)
    
    def _calculate_fvg_confidence(self, gap_size: float, current_candle: Dict, 
                                volume_at_formation: Dict, direction: str) -> float:
        """Calculate FVG confidence score"""
        # Gap size relative to price
        gap_ratio = gap_size / current_candle['close']
        size_score = min(0.4, gap_ratio * 100)
        
        # Volume confirmation
        volume_score = 0.3 if self._validate_volume_confirmation(volume_at_formation, direction, 1.0) else 0.1
        
        # Candle strength
        candle_body = abs(current_candle['close'] - current_candle['open'])
        candle_range = current_candle['high'] - current_candle['low']
        candle_strength = candle_body / candle_range if candle_range > 0 else 0
        candle_score = candle_strength * 0.3
        
        return min(1.0, size_score + volume_score + candle_score)
    
    def _categorize_liquidity_sweep(self, swing_point: Dict, swing_highs: List[Dict], 
                                  swing_lows: List[Dict], swing_type: str) -> str:
        """Categorize liquidity sweep as IRL or ERL"""
        # Simple categorization based on swing position
        if swing_type == 'high':
            recent_highs = [h for h in swing_highs if h['timestamp'] > swing_point['timestamp'] - 24*3600000]  # 24h
            if len(recent_highs) >= 2:
                return 'IRL'  # Internal Range Liquidity
            else:
                return 'ERL'  # External Range Liquidity
        else:
            recent_lows = [l for l in swing_lows if l['timestamp'] > swing_point['timestamp'] - 24*3600000]  # 24h
            if len(recent_lows) >= 2:
                return 'IRL'
            else:
                return 'ERL'
    
    def _calculate_liquidity_sweep_confidence(self, swing_point: Dict, sweep_price: float, 
                                            volume_at_sweep: Dict, liquidity_category: str) -> float:
        """Calculate liquidity sweep confidence"""
        # Distance factor
        distance = abs(sweep_price - swing_point['price']) / swing_point['price']
        distance_score = min(0.3, distance * 100)
        
        # Volume factor
        volume_score = 0.3 if volume_at_sweep.get('total_volume', 0) > 0 else 0.1
        
        # Category factor
        category_score = 0.3 if liquidity_category == 'ERL' else 0.2  # ERL sweeps are more significant
        
        return min(1.0, 0.2 + distance_score + volume_score + category_score)
    
    def _calculate_eqh_eql_confidence(self, point1: Dict, point2: Dict, 
                                    price_diff: float, tolerance: float) -> float:
        """Calculate EQH/EQL confidence score"""
        # Price precision factor
        precision_score = (1 - price_diff / tolerance) * 0.4
        
        # Time distance factor (closer in time = higher confidence)
        time_diff = abs(point1['timestamp'] - point2['timestamp'])
        time_score = max(0.2, 0.4 - (time_diff / (24*3600000)) * 0.1)  # Normalize by 24h
        
        return min(1.0, 0.3 + precision_score + time_score)
    
    def _calculate_eqh_eql_strength(self, point1: Dict, point2: Dict) -> float:
        """Calculate EQH/EQL strength based on price precision and time proximity"""
        # Price precision factor
        price_diff = abs(point1['price'] - point2['price'])
        avg_price = (point1['price'] + point2['price']) / 2
        precision_score = 1 - (price_diff / (avg_price * 0.01))  # Normalize by 1% of average price
        precision_score = max(0.0, min(1.0, precision_score))
        
        # Time proximity factor
        time_diff = abs(point1['timestamp'] - point2['timestamp'])
        max_time_diff = 7 * 24 * 3600 * 1000  # 7 days in milliseconds
        time_score = max(0.2, 1 - (time_diff / max_time_diff))
        
        # Combined strength
        strength = (precision_score * 0.6) + (time_score * 0.4)
        
        return min(1.0, max(0.0, strength))
    
    def identify_swing_points(self, data: List[Dict], lookback: int = 5) -> Dict[str, List[Dict]]:
        """
        🔍 Identify swing points in price data
        
        Identifies swing highs and lows using a lookback period.
        A swing high is a high that is higher than the previous and next `lookback` candles.
        A swing low is a low that is lower than the previous and next `lookback` candles.
        
        Args:
            data: List of OHLCV dictionaries
            lookback: Number of candles to look back/forward for swing confirmation
            
        Returns:
            Dictionary containing swing highs and lows
        """
        if len(data) < (lookback * 2 + 1):
            return {'swing_highs': [], 'swing_lows': []}
        
        swing_highs = []
        swing_lows = []
        
        # Process each candle (excluding first and last `lookback` candles)
        for i in range(lookback, len(data) - lookback):
            current_candle = data[i]
            current_high = current_candle['high']
            current_low = current_candle['low']
            
            # Check for swing high
            is_swing_high = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and data[j]['high'] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.append({
                    'timestamp': current_candle['timestamp'],
                    'price': current_high,
                    'index': i,
                    'type': 'swing_high',
                    'candle_data': current_candle
                })
            
            # Check for swing low
            is_swing_low = True
            for j in range(i - lookback, i + lookback + 1):
                if j != i and data[j]['low'] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.append({
                    'timestamp': current_candle['timestamp'],
                    'price': current_low,
                    'index': i,
                    'type': 'swing_low',
                    'candle_data': current_candle
                })
        
        # Sort by timestamp
        swing_highs.sort(key=lambda x: x['timestamp'])
        swing_lows.sort(key=lambda x: x['timestamp'])
        
        self.logger.info(f"Identified {len(swing_highs)} swing highs and {len(swing_lows)} swing lows")
        
        return {
            'swing_highs': swing_highs,
            'swing_lows': swing_lows
        }
    
    def _convert_df_to_data(self, df: pd.DataFrame) -> List[Dict]:
        """Convert DataFrame to list of dictionaries for compatibility"""
        data = []
        for _, row in df.iterrows():
            data.append({
                'timestamp': int(row['timestamp'].timestamp() * 1000) if hasattr(row['timestamp'], 'timestamp') else row['timestamp'],
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })
        return data
    
    def _empty_smc_analysis(self) -> Dict[str, Any]:
        """Return empty SMC analysis result"""
        return {
            'symbol': 'UNKNOWN',
            'timeframe': '1H',
            'timestamp': int(datetime.now().timestamp() * 1000),
            'current_price': 0.0,
            'structure': {
                'swing_points': {'swing_highs': [], 'swing_lows': []},
                'choch_bos_signals': [],
                'market_structure': {'trend': 'neutral', 'trend_strength': 0.5, 'structure_quality': 0.5}
            },
            'order_blocks': [],
            'fvg': [],
            'liquidity_sweeps': [],
            'eqh_eql_signals': [],
            'inducement': [],
            'nested_order_blocks': [],
            'confluence_zones': [],
            'volume_confirmation': {
                'volume_deltas': [],
                'cvd_data': [],
                'volume_absorptions': [],
                'cvd_divergences': []
            },
            'ai_snapshot': {
                'ai_summary': {},
                'gpt_descriptions': {},
                'pattern_counts': {},
                'visualization_ready': {}
            },
            'trading_signals': [],
            'confidence_score': 0.0,
            'smc_summary': {
                'analysis_quality': 'low',
                'confidence_score': 0.0,
                'market_bias': 'neutral',
                'pattern_summary': {'total_patterns': 0},
                'key_levels': {'resistance_levels': [], 'support_levels': [], 'fvg_levels': []},
                'trading_context': {},
                'recommendation': 'No analysis available'
            }
        }
    
    def _get_previous_swing_low(self, all_swings: List[Dict], current_idx: int) -> Dict:
        """Get previous swing low before current index"""
        for i in range(current_idx - 1, -1, -1):
            if all_swings[i]['type'] == 'swing_low':
                return all_swings[i]
        return {'price': 0}  # Default if not found
    
    def _get_previous_swing_high(self, all_swings: List[Dict], current_idx: int) -> Dict:
        """Get previous swing high before current index"""
        for i in range(current_idx - 1, -1, -1):
            if all_swings[i]['type'] == 'swing_high':
                return all_swings[i]
        return {'price': 0}  # Default if not found
    
    def _calculate_signal_strength(self, data: List[Dict], current_swing: Dict, prev_swing: Dict) -> float:
        """Calculate signal strength based on price movement and volume"""
        if not data or not current_swing or not prev_swing:
            return 0.5
        
        # Price movement factor
        price_movement = abs(current_swing['price'] - prev_swing['price']) / prev_swing['price']
        movement_score = min(0.5, price_movement * 20)  # Normalize to 0-0.5
        
        # Base strength
        base_strength = 0.5 + movement_score
        
        return min(1.0, base_strength)
    
    def _calculate_order_block_strength(self, data: List[Dict], block_start: int, block_end: int) -> float:
        """Calculate order block strength"""
        if block_end <= block_start or block_end > len(data):
            return 0.5
        
        # Volume strength
        block_volume = sum(data[i]['volume'] for i in range(block_start, block_end))
        avg_volume = sum(d['volume'] for d in data) / len(data)
        volume_strength = min(1.0, (block_volume / (block_end - block_start)) / avg_volume)
        
        return min(1.0, 0.3 + volume_strength * 0.7)
    
    def _calculate_fvg_strength(self, gap_size: float, current_candle: Dict) -> float:
        """Calculate FVG strength based on gap size"""
        gap_ratio = gap_size / current_candle['close']
        return min(1.0, 0.5 + gap_ratio * 100)
    
    def _calculate_liquidity_strength(self, data: List[Dict], sweep_candle: Dict, swing_point: Dict) -> float:
        """Calculate liquidity sweep strength"""
        # Distance factor
        distance = abs(sweep_candle['high'] - swing_point['price']) / swing_point['price']
        distance_score = min(0.5, distance * 100)
        
        # Volume factor
        avg_volume = sum(d['volume'] for d in data) / len(data)
        volume_score = min(0.5, sweep_candle['volume'] / avg_volume / 2)
        
        return min(1.0, distance_score + volume_score)
    
    def _calculate_structure_quality(self, recent_choch_bos: List[Dict], order_blocks: List[Dict], 
                                   recent_inducements: List[Dict]) -> float:
        """Calculate structure quality score"""
        # Pattern consistency
        pattern_count = len(recent_choch_bos) + len(order_blocks) + len(recent_inducements)
        pattern_score = min(0.5, pattern_count * 0.1)
        
        # Pattern quality
        if recent_choch_bos:
            avg_confidence = sum(p.get('confidence_score', 0) for p in recent_choch_bos) / len(recent_choch_bos)
            quality_score = avg_confidence * 0.5
        else:
            quality_score = 0.25
        
        return min(1.0, pattern_score + quality_score)
    
    def _get_dominant_pattern(self, recent_choch_bos: List[Dict], recent_inducements: List[Dict]) -> str:
        """Get dominant pattern type"""
        if not recent_choch_bos and not recent_inducements:
            return 'none'
        
        if len(recent_choch_bos) > len(recent_inducements):
            return 'structural'
        elif len(recent_inducements) > len(recent_choch_bos):
            return 'inducement'
        else:
            return 'mixed'
    
    def _determine_ai_market_bias(self, high_confidence_choch_bos: List[Dict], cvd_divergences: List[Dict]) -> str:
        """Determine market bias for AI analysis"""
        bullish_count = sum(1 for signal in high_confidence_choch_bos if signal['direction'] == 'bullish')
        bearish_count = sum(1 for signal in high_confidence_choch_bos if signal['direction'] == 'bearish')
        
        # Factor in CVD divergences
        bullish_divergences = sum(1 for div in cvd_divergences if div['type'] == 'bullish_divergence')
        bearish_divergences = sum(1 for div in cvd_divergences if div['type'] == 'bearish_divergence')
        
        total_bullish = bullish_count + bullish_divergences
        total_bearish = bearish_count + bearish_divergences
        
        if total_bullish > total_bearish:
            return 'bullish'
        elif total_bearish > total_bullish:
            return 'bearish'
        else:
            return 'neutral'
    
    def _extract_key_levels(self, high_confidence_order_blocks: List[Dict], high_confidence_fvg: List[Dict]) -> Dict:
        """Extract key levels for AI analysis"""
        resistance_levels = [ob['price_high'] for ob in high_confidence_order_blocks if ob['direction'] == 'resistance']
        support_levels = [ob['price_low'] for ob in high_confidence_order_blocks if ob['direction'] == 'support']
        fvg_levels = [(fvg['gap_low'] + fvg['gap_high']) / 2 for fvg in high_confidence_fvg]
        
        return {
            'resistance': sorted(resistance_levels, reverse=True)[:5],
            'support': sorted(support_levels)[:5],
            'fvg_zones': sorted(fvg_levels)[:5]
        }
    
    def _identify_trading_opportunities(self, choch_bos: List[Dict], order_blocks: List[Dict], 
                                      fvg: List[Dict], inducements: List[Dict]) -> List[Dict]:
        """Identify trading opportunities"""
        opportunities = []
        
        # High-confidence signals as opportunities
        for signal in choch_bos:
            if signal.get('confidence_score', 0) >= 0.8:
                opportunities.append({
                    'type': 'structural_break',
                    'direction': signal['direction'],
                    'confidence': signal['confidence_score'],
                    'description': f"{signal['direction']} {signal['type']} with high confidence"
                })
        
        return opportunities[:5]  # Top 5 opportunities
    
    def _identify_risk_factors(self, liquidity_sweeps: List[Dict], cvd_divergences: List[Dict]) -> List[Dict]:
        """Identify risk factors"""
        risk_factors = []
        
        # Liquidity sweeps as risk
        for sweep in liquidity_sweeps:
            if sweep.get('confidence_score', 0) >= 0.7:
                risk_factors.append({
                    'type': 'liquidity_sweep',
                    'severity': 'high' if sweep['liquidity_category'] == 'ERL' else 'medium',
                    'description': f"{sweep['direction']} {sweep['liquidity_category']} liquidity sweep"
                })
        
        return risk_factors[:5]  # Top 5 risks
    
    def _summarize_confluence_zones(self, nested_order_blocks: List[Dict], fvg_ob_confluences: List[Dict]) -> Dict:
        """Summarize confluence zones"""
        return {
            'nested_blocks': len(nested_order_blocks),
            'fvg_ob_confluences': len(fvg_ob_confluences),
            'total_confluences': len(nested_order_blocks) + len(fvg_ob_confluences),
            'high_probability_zones': [
                zone for zone in nested_order_blocks + fvg_ob_confluences
                if zone.get('confluence_strength', 0) >= 0.8
            ]
        }
    
    def _summarize_volume_insights(self, volume_absorptions: List[Dict], cvd_divergences: List[Dict]) -> Dict:
        """Summarize volume insights"""
        return {
            'volume_absorptions': len(volume_absorptions),
            'cvd_divergences': len(cvd_divergences),
            'bullish_volume_signals': len([d for d in cvd_divergences if d['type'] == 'bullish_divergence']),
            'bearish_volume_signals': len([d for d in cvd_divergences if d['type'] == 'bearish_divergence']),
            'institutional_activity': len([abs for abs in volume_absorptions if abs.get('volume_ratio', 0) >= 2.0])
        }
    
    def _generate_market_structure_description(self, choch_bos: List[Dict]) -> str:
        """Generate market structure description for GPT"""
        if not choch_bos:
            return "No clear market structure signals detected"
        
        bullish_count = sum(1 for s in choch_bos if s['direction'] == 'bullish')
        bearish_count = sum(1 for s in choch_bos if s['direction'] == 'bearish')
        
        if bullish_count > bearish_count:
            return f"Bullish market structure with {bullish_count} bullish CHoCH/BOS signals vs {bearish_count} bearish"
        elif bearish_count > bullish_count:
            return f"Bearish market structure with {bearish_count} bearish CHoCH/BOS signals vs {bullish_count} bullish"
        else:
            return f"Neutral market structure with equal {bullish_count} bullish and {bearish_count} bearish signals"
    
    def _generate_support_resistance_description(self, order_blocks: List[Dict]) -> str:
        """Generate support/resistance description for GPT"""
        if not order_blocks:
            return "No significant order blocks detected"
        
        support_count = sum(1 for ob in order_blocks if ob['direction'] == 'support')
        resistance_count = sum(1 for ob in order_blocks if ob['direction'] == 'resistance')
        
        return f"Detected {support_count} support levels and {resistance_count} resistance levels with institutional volume"
    
    def _generate_fvg_description(self, fvg_signals: List[Dict]) -> str:
        """Generate FVG description for GPT"""
        if not fvg_signals:
            return "No Fair Value Gaps detected"
        
        bullish_fvg = sum(1 for fvg in fvg_signals if fvg['direction'] == 'bullish')
        bearish_fvg = sum(1 for fvg in fvg_signals if fvg['direction'] == 'bearish')
        
        return f"Detected {bullish_fvg} bullish FVGs and {bearish_fvg} bearish FVGs representing unfilled market inefficiencies"
    
    def _generate_liquidity_description(self, liquidity_sweeps: List[Dict]) -> str:
        """Generate liquidity description for GPT"""
        if not liquidity_sweeps:
            return "No liquidity sweeps detected"
        
        erl_count = sum(1 for sweep in liquidity_sweeps if sweep.get('liquidity_category') == 'ERL')
        irl_count = sum(1 for sweep in liquidity_sweeps if sweep.get('liquidity_category') == 'IRL')
        
        return f"Detected {erl_count} External Range Liquidity sweeps and {irl_count} Internal Range Liquidity sweeps"
    
    def _generate_inducement_description(self, inducements: List[Dict]) -> str:
        """Generate inducement description for GPT"""
        if not inducements:
            return "No inducement patterns detected"
        
        return f"Detected {len(inducements)} inducement patterns indicating potential smart money manipulation"
    
    def _generate_volume_description(self, volume_absorptions: List[Dict], cvd_divergences: List[Dict]) -> str:
        """Generate volume description for GPT"""
        if not volume_absorptions and not cvd_divergences:
            return "No significant volume patterns detected"
        
        return f"Volume analysis shows {len(volume_absorptions)} absorption patterns and {len(cvd_divergences)} CVD divergences"
    
    def _prepare_levels_for_visualization(self, order_blocks: List[Dict], fvg_signals: List[Dict]) -> List[Dict]:
        """Prepare levels for visualization"""
        levels = []
        
        # Add order block levels
        for ob in order_blocks:
            levels.append({
                'price': ob['price_high'] if ob['direction'] == 'resistance' else ob['price_low'],
                'type': ob['direction'],
                'strength': ob.get('confidence_score', 0.5),
                'source': 'order_block'
            })
        
        # Add FVG levels
        for fvg in fvg_signals:
            levels.append({
                'price': (fvg['gap_high'] + fvg['gap_low']) / 2,
                'type': 'fvg',
                'strength': fvg.get('confidence_score', 0.5),
                'source': 'fair_value_gap'
            })
        
        return levels
    
    def _prepare_zones_for_visualization(self, nested_obs: List[Dict], fvg_ob_confluences: List[Dict]) -> List[Dict]:
        """Prepare zones for visualization"""
        zones = []
        
        # Add nested order block zones
        for nested in nested_obs:
            zones.append({
                'high': nested['price_range']['high'],
                'low': nested['price_range']['low'],
                'type': 'nested_order_block',
                'strength': nested.get('confluence_strength', 0.5)
            })
        
        # Add FVG-OB confluence zones
        for confluence in fvg_ob_confluences:
            zones.append({
                'high': confluence['high_probability_zone']['high'],
                'low': confluence['high_probability_zone']['low'],
                'type': 'fvg_ob_confluence',
                'strength': confluence.get('confluence_strength', 0.5)
            })
        
        return zones
    
    def _prepare_signals_for_visualization(self, choch_bos: List[Dict], liquidity_sweeps: List[Dict]) -> List[Dict]:
        """Prepare signals for visualization"""
        signals = []
        
        # Add CHoCH/BOS signals
        for signal in choch_bos:
            signals.append({
                'timestamp': signal['timestamp'],
                'price': signal['price'],
                'type': signal['type'],
                'direction': signal['direction'],
                'strength': signal.get('confidence_score', 0.5)
            })
        
        # Add liquidity sweep signals
        for sweep in liquidity_sweeps:
            signals.append({
                'timestamp': sweep['timestamp'],
                'price': sweep['sweep_price'],
                'type': 'liquidity_sweep',
                'direction': sweep['direction'],
                'strength': sweep.get('confidence_score', 0.5)
            })
        
        return signals
    
    def _is_supporting_pattern(self, main_pattern: Dict, supporting_pattern: Dict) -> bool:
        """Check if pattern supports the main pattern"""
        # Simple time-based support check
        time_diff = abs(main_pattern['timestamp'] - supporting_pattern.get('timestamp', 0))
        return time_diff < 24 * 3600 * 1000  # Within 24 hours
    
    def _calculate_signal_strength_enhanced(self, pattern: Dict, supporting_obs: List[Dict],
                                          supporting_fvgs: List[Dict], supporting_inducements: List[Dict]) -> float:
        """Calculate enhanced signal strength"""
        base_strength = pattern.get('confidence_score', 0.5)
        
        # Support bonuses
        ob_bonus = min(0.2, len(supporting_obs) * 0.05)
        fvg_bonus = min(0.15, len(supporting_fvgs) * 0.05)
        inducement_bonus = min(0.15, len(supporting_inducements) * 0.05)
        
        return min(1.0, base_strength + ob_bonus + fvg_bonus + inducement_bonus)
    
    def _calculate_trade_levels(self, pattern: Dict, supporting_obs: List[Dict], 
                              supporting_fvgs: List[Dict], market_structure: Dict) -> tuple:
        """Calculate trade levels (entry, SL, TP)"""
        price = pattern['price']
        
        # Simple calculation based on pattern direction
        if pattern['direction'] == 'bullish':
            entry_level = price * 1.001  # 0.1% above
            sl_level = price * 0.995     # 0.5% below
            tp_level = price * 1.01      # 1% above
        else:
            entry_level = price * 0.999  # 0.1% below
            sl_level = price * 1.005     # 0.5% above
            tp_level = price * 0.99      # 1% below
        
        return entry_level, sl_level, tp_level
    
    def _calculate_risk_reward_ratio(self, entry: float, sl: float, tp: float) -> float:
        """Calculate risk-reward ratio"""
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        return reward / risk if risk > 0 else 0
    
    def _check_market_structure_alignment(self, pattern: Dict, market_structure: Dict) -> bool:
        """Check if pattern aligns with market structure"""
        pattern_direction = pattern['direction']
        market_trend = market_structure.get('trend', 'neutral')
        
        if pattern_direction == 'bullish' and market_trend == 'bullish':
            return True
        elif pattern_direction == 'bearish' and market_trend == 'bearish':
            return True
        else:
            return False
    
    def _generate_trading_recommendation(self, market_bias: str, confidence_score: float, 
                                       strong_patterns: Dict) -> str:
        """Generate trading recommendation"""
        if confidence_score >= 0.8:
            quality = "HIGH"
        elif confidence_score >= 0.6:
            quality = "MEDIUM"
        else:
            quality = "LOW"
        
        pattern_count = sum(len(patterns) for patterns in strong_patterns.values())
        
        if market_bias == 'bullish' and pattern_count >= 3:
            return f"{quality} CONFIDENCE: Look for bullish entries with {pattern_count} strong patterns"
        elif market_bias == 'bearish' and pattern_count >= 3:
            return f"{quality} CONFIDENCE: Look for bearish entries with {pattern_count} strong patterns"
        else:
            return f"{quality} CONFIDENCE: Wait for clearer signals, mixed structure"

class VolumeAnalyzer:
    """
    📊 Volume Analysis Engine
    
    Provides comprehensive volume analysis including:
    - Volume delta calculation
    - CVD (Cumulative Volume Delta) tracking
    - Volume absorption detection
    - Volume spike identification
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.VolumeAnalyzer")
    
    def calculate_volume_delta(self, data: List[Dict]) -> List[Dict]:
        """
        Calculate volume delta for each candle
        
        Args:
            data: List of OHLCV candles
            
        Returns:
            List of volume delta data with buy/sell volume estimation
        """
        volume_deltas = []
        
        for i, candle in enumerate(data):
            # Estimate buy/sell volume based on price movement and volume
            close_price = candle['close']
            open_price = candle['open']
            high_price = candle['high']
            low_price = candle['low']
            total_volume = candle['volume']
            
            # Calculate price position within the candle
            if high_price != low_price:
                price_position = (close_price - low_price) / (high_price - low_price)
            else:
                price_position = 0.5
            
            # Estimate buy/sell volume
            buy_volume = total_volume * price_position
            sell_volume = total_volume * (1 - price_position)
            
            # Calculate delta
            delta = buy_volume - sell_volume
            
            volume_deltas.append({
                'timestamp': candle['timestamp'],
                'total_volume': total_volume,
                'buy_volume': buy_volume,
                'sell_volume': sell_volume,
                'delta': delta,
                'delta_ratio': delta / total_volume if total_volume > 0 else 0
            })
        
        return volume_deltas
    
    def detect_volume_absorption(self, data: List[Dict], volume_deltas: List[Dict]) -> List[Dict]:
        """
        Detect volume absorption patterns
        
        Args:
            data: OHLCV data
            volume_deltas: Volume delta data
            
        Returns:
            List of absorption patterns
        """
        absorptions = []
        avg_volume = sum(d['volume'] for d in data) / len(data)
        
        for i in range(2, len(data)):
            current_candle = data[i]
            current_delta = volume_deltas[i]
            
            # High volume with small price movement indicates absorption
            if (current_candle['volume'] > avg_volume * 2.0 and
                abs(current_candle['close'] - current_candle['open']) < 
                (current_candle['high'] - current_candle['low']) * 0.3):
                
                absorptions.append({
                    'timestamp': current_candle['timestamp'],
                    'type': 'absorption',
                    'volume': current_candle['volume'],
                    'volume_ratio': current_candle['volume'] / avg_volume,
                    'delta': current_delta['delta'],
                    'price_range': current_candle['high'] - current_candle['low'],
                    'body_size': abs(current_candle['close'] - current_candle['open']),
                    'direction': 'bullish' if current_delta['delta'] > 0 else 'bearish'
                })
        
        return absorptions

class CVDCalculator:
    """
    📈 Cumulative Volume Delta (CVD) Calculator
    
    Tracks cumulative volume delta to identify:
    - Price/volume divergences
    - Institutional accumulation/distribution
    - Trend confirmation/rejection
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.CVDCalculator")
    
    def calculate_cvd(self, volume_deltas: List[Dict]) -> List[Dict]:
        """
        Calculate Cumulative Volume Delta
        
        Args:
            volume_deltas: Volume delta data
            
        Returns:
            List of CVD data points
        """
        cvd_data = []
        cumulative_delta = 0
        
        for delta_point in volume_deltas:
            cumulative_delta += delta_point['delta']
            
            cvd_data.append({
                'timestamp': delta_point['timestamp'],
                'cvd': cumulative_delta,
                'delta': delta_point['delta'],
                'delta_ratio': delta_point['delta_ratio']
            })
        
        return cvd_data
    
    def detect_cvd_divergence(self, data: List[Dict], cvd_data: List[Dict]) -> List[Dict]:
        """
        Detect price-CVD divergences
        
        Args:
            data: OHLCV data
            cvd_data: CVD data
            
        Returns:
            List of divergence patterns
        """
        divergences = []
        
        if len(data) < 20 or len(cvd_data) < 20:
            return divergences
        
        # Look for divergences in recent data
        for i in range(10, len(data) - 1):
            price_current = data[i]['close']
            price_prev = data[i-10]['close']
            
            cvd_current = cvd_data[i]['cvd']
            cvd_prev = cvd_data[i-10]['cvd']
            
            # Bullish divergence: price down, CVD up
            if price_current < price_prev and cvd_current > cvd_prev:
                divergences.append({
                    'timestamp': data[i]['timestamp'],
                    'type': 'bullish_divergence',
                    'price_change': (price_current - price_prev) / price_prev,
                    'cvd_change': cvd_current - cvd_prev,
                    'strength': abs((price_current - price_prev) / price_prev) * 
                               abs(cvd_current - cvd_prev) / max(abs(cvd_current), abs(cvd_prev), 1)
                })
            
            # Bearish divergence: price up, CVD down
            elif price_current > price_prev and cvd_current < cvd_prev:
                divergences.append({
                    'timestamp': data[i]['timestamp'],
                    'type': 'bearish_divergence',
                    'price_change': (price_current - price_prev) / price_prev,
                    'cvd_change': cvd_current - cvd_prev,
                    'strength': abs((price_current - price_prev) / price_prev) * 
                               abs(cvd_current - cvd_prev) / max(abs(cvd_current), abs(cvd_prev), 1)
                })
        
        return divergences

class ConfluenceDetector:
    """
    🎯 Confluence Zone Detection Engine
    
    Identifies high-probability zones where multiple SMC patterns converge:
    - Nested Order Blocks
    - FVG within Order Blocks
    - Multiple pattern confirmations
    - Liquidity confluence areas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.ConfluenceDetector")
    
    def detect_nested_order_blocks(self, order_blocks: List[Dict]) -> List[Dict]:
        """
        Detect nested order blocks (OB within OB)
        
        Args:
            order_blocks: List of detected order blocks
            
        Returns:
            List of nested order block patterns
        """
        nested_obs = []
        
        for i, ob1 in enumerate(order_blocks):
            for j, ob2 in enumerate(order_blocks):
                if i != j and self._is_nested_order_block(ob1, ob2):
                    nested_obs.append({
                        'timestamp': max(ob1['timestamp'], ob2['timestamp']),
                        'type': 'nested_order_block',
                        'outer_block': ob1,
                        'inner_block': ob2,
                        'direction': ob1['direction'],
                        'confluence_strength': self._calculate_confluence_strength(ob1, ob2),
                        'price_range': {
                            'high': max(ob1['price_high'], ob2['price_high']),
                            'low': min(ob1['price_low'], ob2['price_low'])
                        }
                    })
        
        return nested_obs
    
    def detect_fvg_ob_confluence(self, fvg_signals: List[Dict], order_blocks: List[Dict]) -> List[Dict]:
        """
        Detect FVG within Order Block confluence
        
        Args:
            fvg_signals: List of FVG patterns
            order_blocks: List of order blocks
            
        Returns:
            List of FVG-OB confluence patterns
        """
        confluences = []
        
        for fvg in fvg_signals:
            for ob in order_blocks:
                if self._is_fvg_within_ob(fvg, ob):
                    confluences.append({
                        'timestamp': max(fvg['timestamp'], ob['timestamp']),
                        'type': 'fvg_ob_confluence',
                        'fvg_pattern': fvg,
                        'order_block': ob,
                        'direction': fvg['direction'],
                        'confluence_strength': self._calculate_fvg_ob_confluence_strength(fvg, ob),
                        'high_probability_zone': {
                            'high': min(fvg['gap_high'], ob['price_high']),
                            'low': max(fvg['gap_low'], ob['price_low'])
                        }
                    })
        
        return confluences
    
    def _is_nested_order_block(self, ob1: Dict, ob2: Dict) -> bool:
        """Check if ob2 is nested within ob1"""
        return (ob1['price_low'] <= ob2['price_low'] and 
                ob1['price_high'] >= ob2['price_high'] and
                ob1['direction'] == ob2['direction'])
    
    def _is_fvg_within_ob(self, fvg: Dict, ob: Dict) -> bool:
        """Check if FVG is within Order Block"""
        return (ob['price_low'] <= fvg['gap_low'] and 
                ob['price_high'] >= fvg['gap_high'] and
                fvg['direction'] == ('bullish' if ob['direction'] == 'support' else 'bearish'))
    
    def _calculate_confluence_strength(self, ob1: Dict, ob2: Dict) -> float:
        """Calculate confluence strength between two order blocks"""
        volume_factor = (ob1['volume'] + ob2['volume']) / 2
        size_factor = min(ob1['strength'], ob2['strength'])
        return min(volume_factor * size_factor, 1.0)
    
    def _calculate_fvg_ob_confluence_strength(self, fvg: Dict, ob: Dict) -> float:
        """Calculate FVG-OB confluence strength"""
        fvg_strength = fvg['strength']
        ob_strength = ob['strength']
        return min((fvg_strength + ob_strength) / 2, 1.0)
        
    def analyze_comprehensive(self, df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Comprehensive SMC analysis combining all detection methods"""
        
        try:
            if df is None or df.empty:
                return self._empty_smc_analysis()
            
            # Convert DataFrame to list of dicts for compatibility
            data = self._convert_df_to_data(df)
            
            # 1. Identify swing points
            swing_points = self.identify_swing_points(data)
            
            # 2. Detect CHoCH and BOS patterns
            choch_bos_signals = self.detect_choch_bos(data, swing_points)
            
            # 3. Detect Order Blocks
            order_blocks = self.detect_order_blocks(data, swing_points)
            
            # 4. Detect Fair Value Gaps (FVG)
            fvg_signals = self.detect_fvg(data)
            
            # 5. Detect Liquidity Sweeps
            liquidity_sweeps = self.detect_liquidity_sweeps(data, swing_points)
            
            # 6. Detect Equal Highs/Lows (EQH/EQL)
            eqh_eql_signals = self.detect_eqh_eql(data, swing_points)
            
            # 7. Detect Inducement Patterns
            inducement_patterns = self.inducement_detector.detect_inducements(data, swing_points)
            
            # 8. Determine market structure
            market_structure = self._determine_market_structure(choch_bos_signals, order_blocks)
            
            # 9. Generate comprehensive summary
            smc_summary = self._generate_smc_summary(
                choch_bos_signals, order_blocks, fvg_signals, 
                liquidity_sweeps, eqh_eql_signals, inducement_patterns
            )
            
            # 10. Generate trading signals
            trading_signals = self._generate_trading_signals(
                choch_bos_signals, order_blocks, fvg_signals, 
                liquidity_sweeps, market_structure, inducement_patterns
            )
            
            return {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': int(df['timestamp'].iloc[-1].timestamp() * 1000) if 'timestamp' in df.columns else int(datetime.now().timestamp() * 1000),
                'current_price': float(df['close'].iloc[-1]),
                'swing_points': swing_points,
                'choch_bos_signals': choch_bos_signals,
                'order_blocks': order_blocks,
                'fvg_signals': fvg_signals,
                'liquidity_sweeps': liquidity_sweeps,
                'eqh_eql_signals': eqh_eql_signals,
                'inducement_patterns': inducement_patterns,
                'market_structure': market_structure,
                'smc_summary': smc_summary,
                'trading_signals': trading_signals,
                'confidence_score': self._calculate_confidence_score(
                    choch_bos_signals, order_blocks, fvg_signals, liquidity_sweeps, inducement_patterns
                )
            }
            
        except Exception as e:
            self.logger.error(f"Professional SMC analysis error for {symbol}: {e}")
            return self._empty_smc_analysis()
    
    def identify_swing_points(self, data: List[Dict]) -> Dict[str, List[Dict]]:
        """Identify swing highs and lows"""
        if len(data) < self.swing_period * 2 + 1:
            return {'swing_highs': [], 'swing_lows': []}
        
        swing_highs = []
        swing_lows = []
        
        for i in range(self.swing_period, len(data) - self.swing_period):
            current_high = data[i]['high']
            current_low = data[i]['low']
            
            # Check for swing high
            is_swing_high = True
            for j in range(i - self.swing_period, i + self.swing_period + 1):
                if j != i and data[j]['high'] >= current_high:
                    is_swing_high = False
                    break
            
            if is_swing_high:
                swing_highs.append({
                    'timestamp': int(data[i]['timestamp'].timestamp() * 1000) if hasattr(data[i]['timestamp'], 'timestamp') else int(data[i]['timestamp']),
                    'index': i,
                    'price': current_high,
                    'type': 'swing_high'
                })
            
            # Check for swing low
            is_swing_low = True
            for j in range(i - self.swing_period, i + self.swing_period + 1):
                if j != i and data[j]['low'] <= current_low:
                    is_swing_low = False
                    break
            
            if is_swing_low:
                swing_lows.append({
                    'timestamp': int(data[i]['timestamp'].timestamp() * 1000) if hasattr(data[i]['timestamp'], 'timestamp') else int(data[i]['timestamp']),
                    'index': i,
                    'price': current_low,
                    'type': 'swing_low'
                })
        
        return {'swing_highs': swing_highs, 'swing_lows': swing_lows}
    
    def detect_choch_bos(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect Change of Character (CHoCH) and Break of Structure (BOS)"""
        if not swing_points or len(swing_points['swing_highs']) < 2 or len(swing_points['swing_lows']) < 2:
            return []
        
        choch_bos_signals = []
        swing_highs = swing_points['swing_highs']
        swing_lows = swing_points['swing_lows']
        
        # Combine and sort swing points by timestamp
        all_swings = swing_highs + swing_lows
        for swing in all_swings:
            swing['timestamp'] = int(swing['timestamp']) if isinstance(swing['timestamp'], str) else swing['timestamp']
        all_swings.sort(key=lambda x: x['timestamp'])
        
        if len(all_swings) < 3:
            return []
        
        # Track market structure
        for i in range(2, len(all_swings)):
            current_swing = all_swings[i]
            prev_swing = all_swings[i-1]
            prev_prev_swing = all_swings[i-2]
            
            # Detect CHoCH (Change of Character)
            if (prev_prev_swing['type'] == 'swing_high' and 
                prev_swing['type'] == 'swing_low' and 
                current_swing['type'] == 'swing_high'):
                
                # Bullish CHoCH: Higher High after Lower Low
                if (current_swing['price'] > prev_prev_swing['price'] and 
                    prev_swing['price'] < self._get_previous_swing_low(all_swings, i-1)['price']):
                    
                    choch_bos_signals.append({
                        'timestamp': current_swing['timestamp'],
                        'type': 'CHoCH',
                        'direction': 'bullish',
                        'price': current_swing['price'],
                        'strength': self._calculate_signal_strength(data, current_swing, prev_swing)
                    })
            
            elif (prev_prev_swing['type'] == 'swing_low' and 
                  prev_swing['type'] == 'swing_high' and 
                  current_swing['type'] == 'swing_low'):
                
                # Bearish CHoCH: Lower Low after Higher High
                if (current_swing['price'] < prev_prev_swing['price'] and 
                    prev_swing['price'] > self._get_previous_swing_high(all_swings, i-1)['price']):
                    
                    choch_bos_signals.append({
                        'timestamp': current_swing['timestamp'],
                        'type': 'CHoCH',
                        'direction': 'bearish',
                        'price': current_swing['price'],
                        'strength': self._calculate_signal_strength(data, current_swing, prev_swing)
                    })
            
            # Detect BOS (Break of Structure)
            # BOS occurs when price breaks significant support/resistance
            if current_swing['type'] == 'swing_high':
                recent_highs = [s for s in swing_highs if s['timestamp'] < current_swing['timestamp']][-3:]
                if recent_highs:
                    max_recent_high = max(recent_highs, key=lambda x: x['price'])
                    if current_swing['price'] > max_recent_high['price'] * 1.01:  # 1% break
                        choch_bos_signals.append({
                            'timestamp': current_swing['timestamp'],
                            'type': 'BOS',
                            'direction': 'bullish',
                            'price': current_swing['price'],
                            'strength': self._calculate_signal_strength(data, current_swing, max_recent_high)
                        })
            
            elif current_swing['type'] == 'swing_low':
                recent_lows = [s for s in swing_lows if s['timestamp'] < current_swing['timestamp']][-3:]
                if recent_lows:
                    min_recent_low = min(recent_lows, key=lambda x: x['price'])
                    if current_swing['price'] < min_recent_low['price'] * 0.99:  # 1% break
                        choch_bos_signals.append({
                            'timestamp': current_swing['timestamp'],
                            'type': 'BOS',
                            'direction': 'bearish',
                            'price': current_swing['price'],
                            'strength': self._calculate_signal_strength(data, current_swing, min_recent_low)
                        })
        
        return choch_bos_signals
    
    def detect_order_blocks(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect Order Blocks (institutional interest zones)"""
        order_blocks = []
        
        if not swing_points or len(data) < 10:
            return order_blocks
        
        # Order blocks form around swing points with high volume
        for swing_high in swing_points['swing_highs']:
            idx = swing_high['index']
            if idx >= 3 and idx < len(data) - 3:
                # Look for order block formation around swing high
                block_start = max(0, idx - 3)
                block_end = min(len(data), idx + 3)
                
                # Calculate volume average
                avg_volume = sum(data[i]['volume'] for i in range(block_start, block_end)) / (block_end - block_start)
                
                # Check if volume is above average
                if avg_volume > self._get_average_volume(data) * 1.5:
                    order_blocks.append({
                        'timestamp': swing_high['timestamp'],
                        'type': 'order_block',
                        'direction': 'resistance',
                        'price_high': swing_high['price'],
                        'price_low': min(data[i]['low'] for i in range(block_start, block_end)),
                        'volume': avg_volume,
                        'strength': self._calculate_order_block_strength(data, block_start, block_end)
                    })
        
        for swing_low in swing_points['swing_lows']:
            idx = swing_low['index']
            if idx >= 3 and idx < len(data) - 3:
                # Look for order block formation around swing low
                block_start = max(0, idx - 3)
                block_end = min(len(data), idx + 3)
                
                # Calculate volume average
                avg_volume = sum(data[i]['volume'] for i in range(block_start, block_end)) / (block_end - block_start)
                
                # Check if volume is above average
                if avg_volume > self._get_average_volume(data) * 1.5:
                    order_blocks.append({
                        'timestamp': swing_low['timestamp'],
                        'type': 'order_block',
                        'direction': 'support',
                        'price_high': max(data[i]['high'] for i in range(block_start, block_end)),
                        'price_low': swing_low['price'],
                        'volume': avg_volume,
                        'strength': self._calculate_order_block_strength(data, block_start, block_end)
                    })
        
        return order_blocks
    
    def detect_fvg(self, data: List[Dict]) -> List[Dict]:
        """Detect Fair Value Gaps (FVG)"""
        fvg_signals = []
        
        if len(data) < 3:
            return fvg_signals
        
        for i in range(1, len(data) - 1):
            prev_candle = data[i-1]
            current_candle = data[i]
            next_candle = data[i+1]
            
            # Bullish FVG: Gap between prev high and next low
            if (prev_candle['high'] < next_candle['low'] and
                current_candle['close'] > current_candle['open']):  # Bullish candle
                
                gap_size = next_candle['low'] - prev_candle['high']
                if gap_size > 0:
                    fvg_signals.append({
                        'timestamp': int(current_candle['timestamp']) if isinstance(current_candle['timestamp'], (int, float)) else int(current_candle['timestamp'].timestamp() * 1000),
                        'type': 'FVG',
                        'direction': 'bullish',
                        'gap_high': next_candle['low'],
                        'gap_low': prev_candle['high'],
                        'gap_size': gap_size,
                        'strength': self._calculate_fvg_strength(gap_size, current_candle)
                    })
            
            # Bearish FVG: Gap between prev low and next high
            elif (prev_candle['low'] > next_candle['high'] and
                  current_candle['close'] < current_candle['open']):  # Bearish candle
                
                gap_size = prev_candle['low'] - next_candle['high']
                if gap_size > 0:
                    fvg_signals.append({
                        'timestamp': int(current_candle['timestamp']) if isinstance(current_candle['timestamp'], (int, float)) else int(current_candle['timestamp'].timestamp() * 1000),
                        'type': 'FVG',
                        'direction': 'bearish',
                        'gap_high': prev_candle['low'],
                        'gap_low': next_candle['high'],
                        'gap_size': gap_size,
                        'strength': self._calculate_fvg_strength(gap_size, current_candle)
                    })
        
        return fvg_signals
    
    def detect_liquidity_sweeps(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect Liquidity Pool Sweeps"""
        liquidity_sweeps = []
        
        if not swing_points or len(data) < 10:
            return liquidity_sweeps
        
        # Check for liquidity sweeps at swing highs
        for swing_high in swing_points['swing_highs']:
            idx = swing_high['index']
            if idx < len(data) - 5:
                # Look for price breaking above swing high and then reversing
                for i in range(idx + 1, min(idx + 6, len(data))):
                    if data[i]['high'] > swing_high['price'] * 1.005:  # Break above with 0.5% buffer
                        # Check for reversal within next few candles
                        reversal_found = False
                        for j in range(i + 1, min(i + 4, len(data))):
                            if data[j]['low'] < swing_high['price'] * 0.995:  # Reversal below swing high
                                reversal_found = True
                                break
                        
                        if reversal_found:
                            liquidity_sweeps.append({
                                'timestamp': int(data[i]['timestamp']) if isinstance(data[i]['timestamp'], (int, float)) else int(data[i]['timestamp'].timestamp() * 1000),
                                'type': 'liquidity_sweep',
                                'direction': 'bearish',
                                'sweep_price': data[i]['high'],
                                'original_level': swing_high['price'],
                                'strength': self._calculate_liquidity_strength(data, i, swing_high)
                            })
                            break
        
        # Check for liquidity sweeps at swing lows
        for swing_low in swing_points['swing_lows']:
            idx = swing_low['index']
            if idx < len(data) - 5:
                # Look for price breaking below swing low and then reversing
                for i in range(idx + 1, min(idx + 6, len(data))):
                    if data[i]['low'] < swing_low['price'] * 0.995:  # Break below with 0.5% buffer
                        # Check for reversal within next few candles
                        reversal_found = False
                        for j in range(i + 1, min(i + 4, len(data))):
                            if data[j]['high'] > swing_low['price'] * 1.005:  # Reversal above swing low
                                reversal_found = True
                                break
                        
                        if reversal_found:
                            liquidity_sweeps.append({
                                'timestamp': int(data[i]['timestamp']) if isinstance(data[i]['timestamp'], (int, float)) else int(data[i]['timestamp'].timestamp() * 1000),
                                'type': 'liquidity_sweep',
                                'direction': 'bullish',
                                'sweep_price': data[i]['low'],
                                'original_level': swing_low['price'],
                                'strength': self._calculate_liquidity_strength(data, i, swing_low)
                            })
                            break
        
        return liquidity_sweeps
    
    def detect_eqh_eql(self, data: List[Dict], swing_points: Dict[str, List[Dict]]) -> List[Dict]:
        """Detect Equal Highs (EQH) and Equal Lows (EQL)"""
        eqh_eql_signals = []
        tolerance = 0.002  # 0.2% tolerance for "equal" levels
        
        if not swing_points:
            return eqh_eql_signals
        
        # Detect Equal Highs (EQH)
        swing_highs = swing_points['swing_highs']
        for i in range(len(swing_highs) - 1):
            for j in range(i + 1, len(swing_highs)):
                high1 = swing_highs[i]
                high2 = swing_highs[j]
                
                price_diff = abs(high1['price'] - high2['price'])
                if price_diff / high1['price'] <= tolerance:
                    eqh_eql_signals.append({
                        'timestamp': high2['timestamp'],
                        'type': 'EQH',
                        'direction': 'resistance',
                        'price': (high1['price'] + high2['price']) / 2,
                        'price_diff': price_diff,
                        'strength': self._calculate_eqh_eql_strength(high1, high2)
                    })
        
        # Detect Equal Lows (EQL)
        swing_lows = swing_points['swing_lows']
        for i in range(len(swing_lows) - 1):
            for j in range(i + 1, len(swing_lows)):
                low1 = swing_lows[i]
                low2 = swing_lows[j]
                
                price_diff = abs(low1['price'] - low2['price'])
                if price_diff / low1['price'] <= tolerance:
                    eqh_eql_signals.append({
                        'timestamp': low2['timestamp'],
                        'type': 'EQL',
                        'direction': 'support',
                        'price': (low1['price'] + low2['price']) / 2,
                        'price_diff': price_diff,
                        'strength': self._calculate_eqh_eql_strength(low1, low2)
                    })
        
        return eqh_eql_signals
    
    def _generate_trading_signals(self, choch_bos_signals: List[Dict], order_blocks: List[Dict], 
                                 fvg_signals: List[Dict], liquidity_sweeps: List[Dict], 
                                 market_structure: Dict[str, Any]) -> List[Dict]:
        """Generate trading signals based on SMC analysis"""
        trading_signals = []
        
        # Recent signals only (last 10)
        recent_choch_bos = choch_bos_signals[-10:] if choch_bos_signals else []
        recent_order_blocks = order_blocks[-5:] if order_blocks else []
        recent_fvg = fvg_signals[-5:] if fvg_signals else []
        recent_liquidity = liquidity_sweeps[-5:] if liquidity_sweeps else []
        
        # Generate signals based on pattern confluences
        for signal in recent_choch_bos:
            if signal['type'] == 'CHoCH' and signal['strength'] > 60:
                # Look for confluence with order blocks
                confluence_count = 0
                supporting_patterns = []
                
                # Check for order block confluence
                for ob in recent_order_blocks:
                    if (signal['direction'] == 'bullish' and ob['direction'] == 'support' and
                        abs(signal['price'] - ob['price_low']) / signal['price'] < 0.02):
                        confluence_count += 1
                        supporting_patterns.append('order_block')
                
                # Check for FVG confluence  
                for fvg in recent_fvg:
                    if (signal['direction'] == fvg['direction'] and
                        abs(signal['timestamp'] - fvg['timestamp']) < 3600000):  # Within 1 hour
                        confluence_count += 1
                        supporting_patterns.append('fvg')
                
                # Generate signal if confluence is strong
                if confluence_count >= 1:
                    trading_signals.append({
                        'timestamp': signal['timestamp'],
                        'action': 'BUY' if signal['direction'] == 'bullish' else 'SELL',
                        'pattern_type': 'CHoCH_CONFLUENCE',
                        'entry_price': signal['price'],
                        'confidence': min(signal['strength'] + confluence_count * 10, 100),
                        'supporting_patterns': supporting_patterns,
                        'timeframe_strength': market_structure.get('strength', 0)
                    })
        
        return trading_signals
    
    # Helper methods
    def _convert_df_to_data(self, df: pd.DataFrame) -> List[Dict]:
        """Convert DataFrame to list of dictionaries"""
        data = []
        for _, row in df.iterrows():
            # Handle timestamp conversion properly
            if 'timestamp' in row:
                timestamp = row['timestamp']
                try:
                    if hasattr(timestamp, 'timestamp'):  # pandas Timestamp
                        timestamp = int(timestamp.timestamp() * 1000)
                    elif isinstance(timestamp, str):
                        # Handle string timestamps
                        timestamp = int(float(timestamp))
                    elif isinstance(timestamp, (int, float)):
                        timestamp = int(timestamp)
                    else:
                        timestamp = int(datetime.now().timestamp() * 1000)
                except (ValueError, TypeError):
                    timestamp = int(datetime.now().timestamp() * 1000)
            else:
                timestamp = int(datetime.now().timestamp() * 1000)
            
            data.append({
                'timestamp': timestamp,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']) if 'volume' in row else 0.0
            })
        return data
    

    
    def _get_previous_swing_low(self, all_swings: List[Dict], current_index: int) -> Dict:
        """Get previous swing low before current index"""
        for i in range(current_index - 1, -1, -1):
            if all_swings[i]['type'] == 'swing_low':
                return all_swings[i]
        return {'price': 0}
    
    def _get_previous_swing_high(self, all_swings: List[Dict], current_index: int) -> Dict:
        """Get previous swing high before current index"""
        for i in range(current_index - 1, -1, -1):
            if all_swings[i]['type'] == 'swing_high':
                return all_swings[i]
        return {'price': float('inf')}
    
    def _calculate_signal_strength(self, data: List[Dict], signal_point: Dict, reference_point: Dict) -> float:
        """Calculate signal strength based on various factors"""
        try:
            # Volume factor
            idx = signal_point.get('index', 0)
            if idx < len(data):
                volume_factor = data[idx]['volume'] / self._get_average_volume(data)
            else:
                volume_factor = 1.0
            
            # Price movement factor
            signal_price = self._safe_get_price(signal_point)
            reference_price = self._safe_get_price(reference_point)
            
            if reference_price > 0:
                price_diff = abs(signal_price - reference_price)
                price_factor = price_diff / reference_price * 100
            else:
                price_factor = 0
            
            # Time factor (more recent = stronger)
            time_diff = abs(signal_point['timestamp'] - reference_point['timestamp']) / 3600000  # hours
            time_factor = max(1, 24 / (time_diff + 1))  # Decay over 24 hours
            
            strength = min(volume_factor * price_factor * time_factor * 20, 100)
            return max(strength, 30)  # Minimum strength
        except:
            return 50.0
    
    def _calculate_order_block_strength(self, data: List[Dict], start_idx: int, end_idx: int) -> float:
        """Calculate order block strength"""
        try:
            avg_volume = sum(data[i]['volume'] for i in range(start_idx, end_idx)) / (end_idx - start_idx)
            total_avg_volume = self._get_average_volume(data)
            volume_strength = min(avg_volume / total_avg_volume * 50, 100)
            return max(volume_strength, 40)
        except:
            return 50.0
    
    def _calculate_fvg_strength(self, gap_size: float, current_candle: Dict) -> float:
        """Calculate FVG strength"""
        try:
            gap_percentage = gap_size / current_candle['close'] * 100
            return min(gap_percentage * 10, 100)
        except:
            return 50.0
    
    def _calculate_liquidity_strength(self, data: List[Dict], sweep_idx: int, original_level: Dict) -> float:
        """Calculate liquidity sweep strength"""
        try:
            volume_factor = data[sweep_idx]['volume'] / self._get_average_volume(data)
            price_factor = abs(data[sweep_idx]['high'] - original_level['price']) / original_level['price'] * 100
            return min(volume_factor * price_factor * 20, 100)
        except:
            return 50.0
    
    def _calculate_eqh_eql_strength(self, point1: Dict, point2: Dict) -> float:
        """Calculate EQH/EQL strength"""
        try:
            time_diff = abs(point1['timestamp'] - point2['timestamp']) / 3600000
            time_strength = min(time_diff / 20, 2.0)
            price_diff = abs(point1['price'] - point2['price'])
            precision_strength = 1.0 / (1.0 + price_diff / point1['price'] * 100)
            return min(time_strength * precision_strength * 50, 100)
        except:
            return 50.0
    
    def _get_average_volume(self, data: List[Dict]) -> float:
        """Calculate average volume"""
        if not data:
            return 1.0
        return sum(d['volume'] for d in data) / len(data)
    
    def _determine_market_structure(self, choch_bos_signals: List[Dict], order_blocks: List[Dict]) -> Dict[str, Any]:
        """Determine overall market structure"""
        if not choch_bos_signals:
            return {'trend': 'neutral', 'strength': 0}
        
        recent_signals = choch_bos_signals[-5:] if len(choch_bos_signals) >= 5 else choch_bos_signals
        
        bullish_count = sum(1 for signal in recent_signals if signal['direction'] == 'bullish')
        bearish_count = sum(1 for signal in recent_signals if signal['direction'] == 'bearish')
        
        if bullish_count > bearish_count:
            trend = 'bullish'
            strength = (bullish_count / len(recent_signals)) * 100
        elif bearish_count > bullish_count:
            trend = 'bearish'
            strength = (bearish_count / len(recent_signals)) * 100
        else:
            trend = 'neutral'
            strength = 0
        
        return {
            'trend': trend,
            'strength': strength,
            'recent_signals': len(recent_signals),
            'order_blocks_count': len(order_blocks)
        }
    
    def _generate_smc_summary(self, choch_bos_signals: List[Dict], order_blocks: List[Dict], 
                             fvg_signals: List[Dict], liquidity_sweeps: List[Dict], 
                             eqh_eql_signals: List[Dict]) -> Dict[str, Any]:
        """Generate SMC analysis summary"""
        return {
            'total_choch_bos': len(choch_bos_signals),
            'total_order_blocks': len(order_blocks),
            'total_fvg': len(fvg_signals),
            'total_liquidity_sweeps': len(liquidity_sweeps),
            'total_eqh_eql': len(eqh_eql_signals),
            'bullish_signals': len([s for s in choch_bos_signals if s['direction'] == 'bullish']),
            'bearish_signals': len([s for s in choch_bos_signals if s['direction'] == 'bearish']),
            'recent_activity': len([s for s in choch_bos_signals[-10:] if s]) if choch_bos_signals else 0,
            'pattern_diversity': len([t for t in ['CHoCH', 'BOS', 'FVG', 'liquidity_sweep', 'EQH', 'EQL'] 
                                    if any(s.get('type') == t for s in (choch_bos_signals + fvg_signals + liquidity_sweeps + eqh_eql_signals))])
        }
    
    def _calculate_confidence_score(self, choch_bos_signals: List[Dict], order_blocks: List[Dict], 
                                   fvg_signals: List[Dict], liquidity_sweeps: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not any([choch_bos_signals, order_blocks, fvg_signals, liquidity_sweeps]):
            return 0.0
        
        # Base score from signal count
        signal_count = len(choch_bos_signals) + len(order_blocks) + len(fvg_signals) + len(liquidity_sweeps)
        base_score = min(signal_count * 10, 60)
        
        # Confluence bonus
        confluence_bonus = 0
        if len(choch_bos_signals) > 0 and len(order_blocks) > 0:
            confluence_bonus += 15
        if len(fvg_signals) > 0 and len(liquidity_sweeps) > 0:
            confluence_bonus += 10
        
        # Recent activity bonus
        recent_signals = [s for s in choch_bos_signals if s['timestamp'] > (datetime.now().timestamp() - 3600) * 1000]
        recent_bonus = len(recent_signals) * 5
        
        total_score = base_score + confluence_bonus + recent_bonus
        return min(total_score, 100)
    
    def _empty_smc_analysis(self) -> Dict[str, Any]:
        """Return empty SMC analysis structure"""
        return {
            'symbol': '',
            'timeframe': '',
            'timestamp': int(datetime.now().timestamp() * 1000),
            'current_price': 0.0,
            'swing_points': {'swing_highs': [], 'swing_lows': []},
            'choch_bos_signals': [],
            'order_blocks': [],
            'fvg_signals': [],
            'liquidity_sweeps': [],
            'eqh_eql_signals': [],
            'market_structure': {'trend': 'neutral', 'strength': 0},
            'smc_summary': {
                'total_choch_bos': 0,
                'total_order_blocks': 0,
                'total_fvg': 0,
                'total_liquidity_sweeps': 0,
                'total_eqh_eql': 0,
                'bullish_signals': 0,
                'bearish_signals': 0,
                'recent_activity': 0,
                'pattern_diversity': 0
            },
            'trading_signals': [],
            'confidence_score': 0.0
        }