"""
SMC Structure Memory System
Menyimpan dan mengelola riwayat struktur Smart Money Concept untuk konteks analisis
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SMCMemory:
    """
    Memory system untuk menyimpan riwayat struktur SMC terbaru
    Digunakan untuk konteks analisis dan keputusan GPT
    """
    
    def __init__(self):
        self.last_bos = None
        self.last_choch = None
        self.last_bullish_ob = []
        self.last_bearish_ob = []
        self.last_fvg = []
        self.last_liquidity = None
        self.history = []  # Full history for advanced analysis
        self.max_history = 100  # Keep last 100 analyses
        
        logger.info("🧠 SMC Memory System initialized")
    
    def update(self, smc_data: dict, symbol: str = "BTCUSDT", timeframe: str = "1H"):
        """Update SMC memory with new analysis data"""
        try:
            timestamp = datetime.now().isoformat()
            
            # 🚨 Check for significant events before updating
            try:
                from .smc_alert_system import smc_alert_system
                smc_alert_system.check_and_alert(smc_data, symbol, timeframe)
            except ImportError:
                pass  # Alert system not available
            
            # Update latest structures
            if smc_data.get("break_of_structure"):
                bos_data = smc_data["break_of_structure"]
                if isinstance(bos_data, list) and bos_data:
                    # Take the latest/most significant BOS
                    bos_data = bos_data[-1] if bos_data else {}
                elif not isinstance(bos_data, dict):
                    bos_data = {}
                
                self.last_bos = {
                    **bos_data,
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "timeframe": timeframe
                }
                
            if smc_data.get("change_of_character"):
                choch_data = smc_data["change_of_character"]
                if isinstance(choch_data, list) and choch_data:
                    # Take the latest/most significant CHoCH
                    choch_data = choch_data[-1] if choch_data else {}
                elif not isinstance(choch_data, dict):
                    choch_data = {}
                
                self.last_choch = {
                    **choch_data,
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "timeframe": timeframe
                }
                
            if smc_data.get("order_blocks", {}).get("bullish"):
                self.last_bullish_ob = [
                    {**ob, "timestamp": timestamp, "symbol": symbol, "timeframe": timeframe, 
                     "mitigation_status": ob.get("mitigation_status", "untested")}
                    for ob in smc_data["order_blocks"]["bullish"]
                ]
                
            if smc_data.get("order_blocks", {}).get("bearish"):
                self.last_bearish_ob = [
                    {**ob, "timestamp": timestamp, "symbol": symbol, "timeframe": timeframe,
                     "mitigation_status": ob.get("mitigation_status", "untested")}
                    for ob in smc_data["order_blocks"]["bearish"]
                ]
                
            if smc_data.get("fair_value_gaps"):
                self.last_fvg = [
                    {**fvg, "timestamp": timestamp, "symbol": symbol, "timeframe": timeframe,
                     "fill_status": fvg.get("fill_status", "unfilled")}
                    for fvg in smc_data["fair_value_gaps"]
                ]
                
            if smc_data.get("liquidity_sweep"):
                liquidity_data = smc_data["liquidity_sweep"]
                if isinstance(liquidity_data, list) and liquidity_data:
                    # Take the latest/most significant liquidity sweep
                    liquidity_data = liquidity_data[-1] if liquidity_data else {}
                elif not isinstance(liquidity_data, dict):
                    liquidity_data = {}
                
                self.last_liquidity = {
                    **liquidity_data,
                    "timestamp": timestamp,
                    "symbol": symbol,
                    "timeframe": timeframe
                }
            
            # Add to full history
            history_entry = {
                "timestamp": timestamp,
                "symbol": symbol,
                "timeframe": timeframe,
                "smc_data": smc_data
            }
            
            self.history.append(history_entry)
            
            # Keep only recent history
            if len(self.history) > self.max_history:
                self.history = self.history[-self.max_history:]
            
            logger.info(f"🧠 SMC Memory updated for {symbol} {timeframe}")
            
        except Exception as e:
            logger.error(f"Failed to update SMC memory: {e}")
    
    def get_context(self) -> Dict[str, Any]:
        """Get current SMC context for GPT analysis"""
        return {
            "last_bos": self.last_bos,
            "last_choch": self.last_choch,
            "last_bullish_ob": self.last_bullish_ob,
            "last_bearish_ob": self.last_bearish_ob,
            "last_fvg": self.last_fvg,
            "last_liquidity": self.last_liquidity,
            "memory_stats": {
                "total_entries": len(self.history),
                "last_updated": self.history[-1]["timestamp"] if self.history else None,
                "symbols_tracked": list(set(entry["symbol"] for entry in self.history)),
                "timeframes_tracked": list(set(entry["timeframe"] for entry in self.history))
            }
        }
    
    def get_recent_history(self, hours: int = 24, symbol: str = None, timeframe: str = None) -> List[Dict]:
        """Get recent SMC history with optional filtering"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        filtered_history = []
        for entry in self.history:
            try:
                entry_time = datetime.fromisoformat(entry["timestamp"])
                if entry_time >= cutoff_time:
                    # Apply filters if specified
                    if symbol and entry["symbol"] != symbol:
                        continue
                    if timeframe and entry["timeframe"] != timeframe:
                        continue
                    filtered_history.append(entry)
            except ValueError:
                continue
        
        return filtered_history
    
    def get_structure_summary(self) -> Dict[str, Any]:
        """Get summary of current SMC structures for quick analysis"""
        summary = {
            "active_structures": {
                "has_bos": self.last_bos is not None,
                "has_choch": self.last_choch is not None,
                "bullish_ob_count": len(self.last_bullish_ob),
                "bearish_ob_count": len(self.last_bearish_ob),
                "fvg_count": len(self.last_fvg),
                "has_liquidity_sweep": self.last_liquidity is not None
            },
            "market_bias": self._analyze_market_bias(),
            "key_levels": self._extract_key_levels(),
            "last_significant_event": self._get_last_significant_event()
        }
        
        return summary
    
    def _analyze_market_bias(self) -> str:
        """Analyze current market bias based on SMC structures"""
        bullish_signals = 0
        bearish_signals = 0
        
        # BOS analysis
        if self.last_bos:
            if self.last_bos.get("direction") == "bullish":
                bullish_signals += 2
            elif self.last_bos.get("direction") == "bearish":
                bearish_signals += 2
        
        # CHoCH analysis  
        if self.last_choch:
            if self.last_choch.get("direction") == "bullish":
                bullish_signals += 1
            elif self.last_choch.get("direction") == "bearish":
                bearish_signals += 1
        
        # Order blocks analysis
        if len(self.last_bullish_ob) > len(self.last_bearish_ob):
            bullish_signals += 1
        elif len(self.last_bearish_ob) > len(self.last_bullish_ob):
            bearish_signals += 1
        
        # Liquidity sweep analysis
        if self.last_liquidity:
            if self.last_liquidity.get("direction") == "bullish":
                bullish_signals += 1
            elif self.last_liquidity.get("direction") == "bearish":
                bearish_signals += 1
        
        if bullish_signals > bearish_signals:
            return "BULLISH"
        elif bearish_signals > bullish_signals:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _extract_key_levels(self) -> Dict[str, List[float]]:
        """Extract key price levels from SMC structures"""
        key_levels = {
            "support_levels": [],
            "resistance_levels": [],
            "fvg_levels": []
        }
        
        # Extract from Order Blocks
        for ob in self.last_bullish_ob:
            if ob.get("price_level"):
                key_levels["support_levels"].append(ob["price_level"])
        
        for ob in self.last_bearish_ob:
            if ob.get("price_level"):
                key_levels["resistance_levels"].append(ob["price_level"])
        
        # Extract from FVG
        for fvg in self.last_fvg:
            if fvg.get("upper_level") and fvg.get("lower_level"):
                key_levels["fvg_levels"].extend([fvg["upper_level"], fvg["lower_level"]])
        
        return key_levels
    
    def _get_last_significant_event(self) -> Optional[Dict]:
        """Get the most recent significant SMC event"""
        events = []
        
        if self.last_bos:
            events.append(("BOS", self.last_bos))
        if self.last_choch:
            events.append(("CHoCH", self.last_choch))
        if self.last_liquidity:
            events.append(("Liquidity Sweep", self.last_liquidity))
        
        if not events:
            return None
        
        # Find most recent based on timestamp
        most_recent = None
        latest_time = None
        
        for event_type, event_data in events:
            try:
                event_time = datetime.fromisoformat(event_data["timestamp"])
                if latest_time is None or event_time > latest_time:
                    latest_time = event_time
                    most_recent = {"type": event_type, "data": event_data}
            except (KeyError, ValueError):
                continue
        
        return most_recent
    
    def clear_old_data(self, hours: int = 48):
        """Clear data older than specified hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Clear history
        self.history = [
            entry for entry in self.history
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
        ]
        
        # Clear individual structures if too old
        def is_recent(structure):
            if not structure or "timestamp" not in structure:
                return False
            try:
                return datetime.fromisoformat(structure["timestamp"]) >= cutoff_time
            except ValueError:
                return False
        
        if not is_recent(self.last_bos):
            self.last_bos = None
        if not is_recent(self.last_choch):
            self.last_choch = None
        if not is_recent(self.last_liquidity):
            self.last_liquidity = None
        
        # Filter lists
        self.last_bullish_ob = [ob for ob in self.last_bullish_ob if is_recent(ob)]
        self.last_bearish_ob = [ob for ob in self.last_bearish_ob if is_recent(ob)]
        self.last_fvg = [fvg for fvg in self.last_fvg if is_recent(fvg)]
        
        logger.info(f"🧹 Cleared SMC data older than {hours} hours")

# Global instance
smc_memory = SMCMemory()