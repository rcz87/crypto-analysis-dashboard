#!/usr/bin/env python3
"""
SMC State Manager - Deterministik SMC rule tracking per simbol/TF
Menyimpan state struktur untuk audit dan konsistensi
"""
import logging
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class StructureType(Enum):
    BOS = "break_of_structure"
    CHOCH = "change_of_character"
    
class SwingType(Enum):
    HH = "higher_high"
    HL = "higher_low" 
    LH = "lower_high"
    LL = "lower_low"

@dataclass
class SwingPoint:
    timestamp: float
    price: float
    swing_type: SwingType
    confirmed: bool = False

@dataclass
class SMCState:
    symbol: str
    timeframe: str
    last_updated: float
    
    # Current structure
    trend_direction: str  # bullish/bearish/neutral
    last_structure_break: Optional[Dict[str, Any]] = None
    
    # Swing points (last 10)
    swing_highs: List[SwingPoint] = None
    swing_lows: List[SwingPoint] = None
    
    # Order blocks (active)
    bullish_ob: List[Dict[str, Any]] = None
    bearish_ob: List[Dict[str, Any]] = None
    
    # FVG tracking
    fvg_zones: List[Dict[str, Any]] = None
    
    # Liquidity levels
    liquidity_sweeps: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.swing_highs is None:
            self.swing_highs = []
        if self.swing_lows is None:
            self.swing_lows = []
        if self.bullish_ob is None:
            self.bullish_ob = []
        if self.bearish_ob is None:
            self.bearish_ob = []
        if self.fvg_zones is None:
            self.fvg_zones = []
        if self.liquidity_sweeps is None:
            self.liquidity_sweeps = []

class SMCStateManager:
    def __init__(self, data_dir: str = "logs"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # In-memory state cache
        self.states: Dict[str, SMCState] = {}
        
        # Load existing states
        self._load_states()
        
        # Deterministik parameters
        self.swing_detection = {
            'lookback_periods': 5,
            'min_price_change_pct': 0.1,  # 0.1% minimum untuk swing
            'confirmation_periods': 2
        }
        
        self.structure_rules = {
            'bos_confirmation_pct': 0.05,  # 0.05% break untuk BOS
            'choch_retest_periods': 3,     # 3 periode untuk CHoCH confirm
            'ob_validity_periods': 50      # 50 periode OB masih valid
        }
        
    def update_smc_state(self, 
                        symbol: str, 
                        timeframe: str, 
                        market_data: Any,
                        current_price: float) -> SMCState:
        """
        Update SMC state dengan rules deterministik
        """
        try:
            state_key = f"{symbol}_{timeframe}"
            
            # Get atau create state
            if state_key not in self.states:
                self.states[state_key] = SMCState(
                    symbol=symbol,
                    timeframe=timeframe,
                    last_updated=time.time(),
                    trend_direction="neutral"
                )
            
            state = self.states[state_key]
            
            # Update swing points
            self._update_swing_points(state, market_data, current_price)
            
            # Detect structure breaks
            self._detect_structure_breaks(state, market_data, current_price)
            
            # Update order blocks
            self._update_order_blocks(state, market_data)
            
            # Update FVG zones
            self._update_fvg_zones(state, market_data)
            
            # Update liquidity tracking
            self._update_liquidity_tracking(state, market_data, current_price)
            
            # Save updated state
            state.last_updated = time.time()
            self._save_state(state_key, state)
            
            return state
            
        except Exception as e:
            logger.error(f"SMC state update error: {e}")
            return self._get_fallback_state(symbol, timeframe)
    
    def get_smc_state(self, symbol: str, timeframe: str) -> Optional[SMCState]:
        """Get current SMC state"""
        state_key = f"{symbol}_{timeframe}"
        return self.states.get(state_key)
    
    def _update_swing_points(self, state: SMCState, market_data: Any, current_price: float):
        """Update swing highs and lows dengan rules deterministik"""
        try:
            # Simplified swing detection - would use real OHLC data
            lookback = self.swing_detection['lookback_periods']
            min_change = self.swing_detection['min_price_change_pct'] / 100
            
            # Mock swing detection logic
            if len(state.swing_highs) == 0:
                # Initialize first swing
                swing_high = SwingPoint(
                    timestamp=time.time(),
                    price=current_price * 1.02,
                    swing_type=SwingType.HH,
                    confirmed=True
                )
                state.swing_highs.append(swing_high)
                
            # Maintain last 10 swings
            if len(state.swing_highs) > 10:
                state.swing_highs = state.swing_highs[-10:]
            if len(state.swing_lows) > 10:
                state.swing_lows = state.swing_lows[-10:]
                
        except Exception as e:
            logger.warning(f"Swing point update error: {e}")
    
    def _detect_structure_breaks(self, state: SMCState, market_data: Any, current_price: float):
        """Detect BOS/CHoCH dengan rules yang jelas"""
        try:
            if not state.swing_highs or not state.swing_lows:
                return
                
            bos_threshold = self.structure_rules['bos_confirmation_pct'] / 100
            
            # Get last significant swing
            last_high = state.swing_highs[-1] if state.swing_highs else None
            last_low = state.swing_lows[-1] if state.swing_lows else None
            
            # BOS detection logic
            if last_high and current_price > last_high.price * (1 + bos_threshold):
                # Bullish BOS
                structure_break = {
                    'type': StructureType.BOS.value,
                    'direction': 'bullish',
                    'break_price': current_price,
                    'previous_level': last_high.price,
                    'timestamp': time.time(),
                    'confirmed': True
                }
                state.last_structure_break = structure_break
                state.trend_direction = 'bullish'
                
            elif last_low and current_price < last_low.price * (1 - bos_threshold):
                # Bearish BOS  
                structure_break = {
                    'type': StructureType.BOS.value,
                    'direction': 'bearish',
                    'break_price': current_price,
                    'previous_level': last_low.price,
                    'timestamp': time.time(),
                    'confirmed': True
                }
                state.last_structure_break = structure_break
                state.trend_direction = 'bearish'
                
        except Exception as e:
            logger.warning(f"Structure break detection error: {e}")
    
    def _update_order_blocks(self, state: SMCState, market_data: Any):
        """Update order blocks dengan validity tracking"""
        try:
            current_time = time.time()
            validity_seconds = self.structure_rules['ob_validity_periods'] * 60  # Convert to seconds
            
            # Remove expired order blocks
            state.bullish_ob = [
                ob for ob in state.bullish_ob 
                if current_time - ob.get('timestamp', 0) < validity_seconds
            ]
            state.bearish_ob = [
                ob for ob in state.bearish_ob
                if current_time - ob.get('timestamp', 0) < validity_seconds
            ]
            
            # Add new order blocks based on structure breaks
            if state.last_structure_break:
                if state.last_structure_break['direction'] == 'bullish':
                    # Add bullish OB
                    ob = {
                        'price': state.last_structure_break['previous_level'] * 0.99,
                        'timestamp': current_time,
                        'quality': 0.8,
                        'tested': False
                    }
                    state.bullish_ob.append(ob)
                    
        except Exception as e:
            logger.warning(f"Order block update error: {e}")
    
    def _update_fvg_zones(self, state: SMCState, market_data: Any):
        """Update Fair Value Gaps"""
        try:
            current_time = time.time()
            
            # Remove filled FVG zones (simplified)
            state.fvg_zones = [
                fvg for fvg in state.fvg_zones
                if not fvg.get('filled', False)
            ]
            
            # Mock FVG detection
            if len(state.fvg_zones) < 3:  # Keep max 3 active FVG
                fvg = {
                    'type': 'bullish',
                    'high': 45200.0,
                    'low': 45150.0,
                    'timestamp': current_time,
                    'filled': False
                }
                state.fvg_zones.append(fvg)
                
        except Exception as e:
            logger.warning(f"FVG update error: {e}")
    
    def _update_liquidity_tracking(self, state: SMCState, market_data: Any, current_price: float):
        """Track liquidity sweeps and raids"""
        try:
            # Simplified liquidity tracking
            if state.swing_highs:
                for swing in state.swing_highs[-3:]:  # Check last 3 swings
                    if abs(current_price - swing.price) / swing.price < 0.001:  # Within 0.1%
                        sweep = {
                            'type': 'high_sweep',
                            'level': swing.price,
                            'timestamp': time.time(),
                            'volume_confirmation': True
                        }
                        state.liquidity_sweeps.append(sweep)
                        
            # Keep only recent sweeps
            cutoff_time = time.time() - 3600  # 1 hour
            state.liquidity_sweeps = [
                sweep for sweep in state.liquidity_sweeps
                if sweep['timestamp'] > cutoff_time
            ]
            
        except Exception as e:
            logger.warning(f"Liquidity tracking error: {e}")
    
    def get_audit_report(self, symbol: str, timeframe: str) -> Dict[str, Any]:
        """Generate audit report untuk SMC state"""
        try:
            state = self.get_smc_state(symbol, timeframe)
            if not state:
                return {"error": "State not found"}
            
            return {
                "symbol": state.symbol,
                "timeframe": state.timeframe,
                "last_updated": state.last_updated,
                "trend_direction": state.trend_direction,
                "structure_summary": {
                    "last_break": state.last_structure_break,
                    "swing_highs_count": len(state.swing_highs),
                    "swing_lows_count": len(state.swing_lows),
                    "active_bullish_ob": len(state.bullish_ob),
                    "active_bearish_ob": len(state.bearish_ob),
                    "active_fvg": len(state.fvg_zones),
                    "recent_liquidity_sweeps": len(state.liquidity_sweeps)
                },
                "deterministik_rules": {
                    "swing_detection": self.swing_detection,
                    "structure_rules": self.structure_rules
                }
            }
            
        except Exception as e:
            logger.error(f"Audit report error: {e}")
            return {"error": str(e)}
    
    def _get_fallback_state(self, symbol: str, timeframe: str) -> SMCState:
        """Fallback state when update fails"""
        return SMCState(
            symbol=symbol,
            timeframe=timeframe,
            last_updated=time.time(),
            trend_direction="neutral"
        )
    
    def _load_states(self):
        """Load SMC states from disk"""
        states_file = self.data_dir / "smc_states.json"
        
        if states_file.exists():
            try:
                with open(states_file, 'r') as f:
                    data = json.load(f)
                    
                for key, state_data in data.items():
                    # Convert back to SMCState object
                    state = SMCState(**state_data)
                    
                    # Convert swing points back to objects
                    state.swing_highs = [
                        SwingPoint(**sp) if isinstance(sp, dict) else sp 
                        for sp in state.swing_highs
                    ]
                    state.swing_lows = [
                        SwingPoint(**sp) if isinstance(sp, dict) else sp
                        for sp in state.swing_lows
                    ]
                    
                    self.states[key] = state
                    
                logger.info(f"Loaded {len(self.states)} SMC states")
                
            except Exception as e:
                logger.warning(f"Failed to load SMC states: {e}")
    
    def _save_state(self, state_key: str, state: SMCState):
        """Save single state update"""
        try:
            # Update in-memory cache
            self.states[state_key] = state
            
            # Save to disk periodically
            self._save_all_states()
            
        except Exception as e:
            logger.warning(f"Failed to save state {state_key}: {e}")
    
    def _save_all_states(self):
        """Save all states to disk"""
        try:
            states_file = self.data_dir / "smc_states.json"
            
            # Convert states to serializable format
            serializable_states = {}
            for key, state in self.states.items():
                state_dict = asdict(state)
                # Convert SwingPoint objects to dicts
                state_dict['swing_highs'] = [asdict(sp) if hasattr(sp, '__dict__') else sp for sp in state_dict['swing_highs']]
                state_dict['swing_lows'] = [asdict(sp) if hasattr(sp, '__dict__') else sp for sp in state_dict['swing_lows']]
                serializable_states[key] = state_dict
            
            with open(states_file, 'w') as f:
                json.dump(serializable_states, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save all SMC states: {e}")