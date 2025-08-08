"""
🔍 SMC Zones Endpoint - Untuk visualisasi chart dan zona kritis
Menyediakan data Bullish OB, Bearish OB, dan FVG untuk TradingView overlay
"""

from flask import Blueprint, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime
from typing import Dict, List, Any

# Blueprint initialization
smc_zones_bp = Blueprint("smc_zones", __name__)
logger = logging.getLogger(__name__)

@smc_zones_bp.route("/api/smc/zones", methods=["GET"])
@cross_origin()
def get_smc_zones():
    """
    🔍 Get SMC Zones - Bullish OB, Bearish OB, Fair Value Gaps
    
    Query Parameters:
    - symbol: Filter by symbol (e.g., ETHUSDT, BTCUSDT)
    - tf: Filter by timeframe (e.g., 1H, 4H, 1D)
    
    Example: GET /api/smc/zones?symbol=ETHUSDT&tf=1H
    
    Response:
    {
        "status": "success",
        "symbol": "ETHUSDT",
        "timeframe": "1H", 
        "zones": {
            "bullish_ob": [...],
            "bearish_ob": [...],
            "fvg": [...]
        },
        "server_time": "2025-08-05T04:00:00"
    }
    
    Use cases:
    🔍 TradingView chart overlay
    📊 GPTs logic untuk proximity checks
    🔔 Critical zone notifications
    """
    try:
        from core.structure_memory import smc_memory
        from flask import request
        
        # Get query parameters
        filter_symbol = request.args.get('symbol', '').upper()
        filter_timeframe = request.args.get('tf', '')
        
        # Get current SMC context
        context = smc_memory.get_context()
        
        # Filter zones based on query parameters
        filtered_zones = _filter_zones_by_symbol_tf(context, filter_symbol, filter_timeframe)
        
        # Extract symbol and timeframe for response
        response_symbol = filter_symbol if filter_symbol else _get_primary_symbol(context)
        response_timeframe = filter_timeframe if filter_timeframe else _get_primary_timeframe(context)
        
        # Build zones response
        zones_data = {
            "status": "success",
            "symbol": response_symbol,
            "timeframe": response_timeframe,
            "filters_applied": {
                "symbol_filter": filter_symbol if filter_symbol else "none",
                "timeframe_filter": filter_timeframe if filter_timeframe else "none"
            },
            "zones": {
                "bullish_ob": filtered_zones.get("bullish_ob", []),
                "bearish_ob": filtered_zones.get("bearish_ob", []),
                "fvg": filtered_zones.get("fvg", [])
            },
            "zone_counts": {
                "bullish_ob_count": len(filtered_zones.get("bullish_ob", [])),
                "bearish_ob_count": len(filtered_zones.get("bearish_ob", [])),
                "fvg_count": len(filtered_zones.get("fvg", []))
            },
            "zone_analysis": {
                "total_zones": (
                    len(filtered_zones.get("bullish_ob", [])) + 
                    len(filtered_zones.get("bearish_ob", [])) + 
                    len(filtered_zones.get("fvg", []))
                ),
                "active_zones": _count_active_zones_filtered(filtered_zones),
                "untested_zones": _count_untested_zones_filtered(filtered_zones),
                "proximity_alerts": _generate_proximity_alerts_filtered(filtered_zones)
            },
            "server_time": datetime.now().isoformat(),
            "api_info": {
                "version": "2.0.0",
                "service": "SMC Zones API",
                "last_updated": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ SMC Zones data retrieved for {response_symbol} ({response_timeframe}) - Filters: symbol={filter_symbol}, tf={filter_timeframe}")
        return jsonify(zones_data)
        
    except Exception as e:
        logger.error(f"SMC Zones endpoint error: {e}")
        return jsonify({
            'error': 'Failed to retrieve SMC zones',
            'details': str(e),
            'api_version': '2.0.0',
            'server_time': datetime.now().isoformat()
        }), 500

@smc_zones_bp.route("/api/smc/zones/proximity/<symbol>/<float:current_price>", methods=["GET"])
@cross_origin()
def check_zone_proximity(symbol: str, current_price: float):
    """
    🎯 Check proximity to SMC zones for given price
    
    Usage: /api/smc/zones/proximity/BTCUSDT/43250.0
    
    Response:
    {
        "status": "success",
        "current_price": 43250.0,
        "proximity_analysis": {
            "nearest_zone": {...},
            "distance": 50.0,
            "zone_type": "bullish_ob",
            "alert_level": "warning"
        }
    }
    """
    try:
        from core.structure_memory import smc_memory
        
        context = smc_memory.get_context()
        
        # Find nearest zones
        nearest_zones = _find_nearest_zones(context, current_price)
        proximity_analysis = _analyze_proximity(nearest_zones, current_price)
        
        response = {
            "status": "success",
            "symbol": symbol.upper(),
            "current_price": current_price,
            "proximity_analysis": proximity_analysis,
            "nearby_zones": nearest_zones,
            "trading_alerts": _generate_trading_alerts(proximity_analysis, current_price),
            "api_info": {
                "version": "2.0.0",
                "service": "SMC Zone Proximity API",
                "server_time": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ Proximity analysis for {symbol} at {current_price}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Zone proximity check error: {e}")
        return jsonify({
            'error': 'Failed to check zone proximity',
            'details': str(e)
        }), 500

@smc_zones_bp.route("/api/smc/zones/critical", methods=["GET"])
@cross_origin()
def get_critical_zones():
    """
    🔔 Get critical zones yang perlu diperhatikan
    
    Response mencakup:
    - Untested zones dengan strength tinggi
    - Zones dengan proximity tinggi ke current price
    - High-volume zones
    """
    try:
        from core.structure_memory import smc_memory
        
        context = smc_memory.get_context()
        
        # Filter critical zones
        critical_bullish = _filter_critical_zones(context.get("last_bullish_ob", []))
        critical_bearish = _filter_critical_zones(context.get("last_bearish_ob", []))
        critical_fvg = _filter_critical_fvg(context.get("last_fvg", []))
        
        critical_analysis = {
            "status": "success",
            "critical_zones": {
                "bullish_ob": critical_bullish,
                "bearish_ob": critical_bearish,
                "fvg": critical_fvg
            },
            "criticality_metrics": {
                "high_strength_zones": len([z for z in critical_bullish + critical_bearish if z.get('strength', 0) > 0.8]),
                "untested_zones": len([z for z in critical_bullish + critical_bearish if z.get('mitigation_status') == 'untested']),
                "unfilled_fvgs": len([z for z in critical_fvg if z.get('fill_status') == 'unfilled'])
            },
            "alert_priorities": _generate_zone_priorities(critical_bullish, critical_bearish, critical_fvg),
            "api_info": {
                "version": "2.0.0",
                "service": "Critical SMC Zones API",
                "server_time": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ Critical zones analysis completed")
        return jsonify(critical_analysis)
        
    except Exception as e:
        logger.error(f"Critical zones error: {e}")
        return jsonify({
            'error': 'Failed to get critical zones',
            'details': str(e)
        }), 500

def _count_active_zones(context: dict) -> int:
    """Count zones dengan status active"""
    try:
        active_count = 0
        
        # Count active bullish OBs
        for ob in context.get("last_bullish_ob", []):
            if ob.get("mitigation_status") == "active":
                active_count += 1
        
        # Count active bearish OBs
        for ob in context.get("last_bearish_ob", []):
            if ob.get("mitigation_status") == "active":
                active_count += 1
        
        # Count unfilled FVGs (considered active)
        for fvg in context.get("last_fvg", []):
            if fvg.get("fill_status") == "unfilled":
                active_count += 1
        
        return active_count
        
    except Exception as e:
        logger.error(f"Active zones count error: {e}")
        return 0

def _count_untested_zones(context: dict) -> int:
    """Count zones dengan status untested"""
    try:
        untested_count = 0
        
        # Count untested OBs
        for ob in context.get("last_bullish_ob", []) + context.get("last_bearish_ob", []):
            if ob.get("mitigation_status") == "untested":
                untested_count += 1
        
        return untested_count
        
    except Exception as e:
        logger.error(f"Untested zones count error: {e}")
        return 0

def _generate_proximity_alerts(context: dict) -> list:
    """Generate proximity-based alerts"""
    try:
        alerts = []
        
        # Check for high-strength untested zones
        for ob in context.get("last_bullish_ob", []):
            if ob.get("strength", 0) > 0.8 and ob.get("mitigation_status") == "untested":
                alerts.append(f"🎯 High-strength bullish OB at {ob.get('price_level', 'N/A')} (untested)")
        
        for ob in context.get("last_bearish_ob", []):
            if ob.get("strength", 0) > 0.8 and ob.get("mitigation_status") == "untested":
                alerts.append(f"🎯 High-strength bearish OB at {ob.get('price_level', 'N/A')} (untested)")
        
        # Check for unfilled FVGs
        for fvg in context.get("last_fvg", []):
            if fvg.get("fill_status") == "unfilled" and fvg.get("strength", 0) > 0.6:
                alerts.append(f"📊 Unfilled FVG: {fvg.get('gap_low', 'N/A')}-{fvg.get('gap_high', 'N/A')}")
        
        return alerts[:5]  # Limit to top 5 alerts
        
    except Exception as e:
        logger.error(f"Proximity alerts error: {e}")
        return []

def _find_nearest_zones(context: dict, current_price: float) -> list:
    """Find zones nearest to current price"""
    try:
        all_zones = []
        
        # Add bullish OBs
        for ob in context.get("last_bullish_ob", []):
            price_level = ob.get("price_level", 0)
            if price_level > 0:
                distance = abs(current_price - price_level)
                all_zones.append({
                    **ob,
                    "zone_type": "bullish_ob",
                    "distance": distance
                })
        
        # Add bearish OBs
        for ob in context.get("last_bearish_ob", []):
            price_level = ob.get("price_level", 0)
            if price_level > 0:
                distance = abs(current_price - price_level)
                all_zones.append({
                    **ob,
                    "zone_type": "bearish_ob",
                    "distance": distance
                })
        
        # Add FVGs (use midpoint)
        for fvg in context.get("last_fvg", []):
            gap_high = fvg.get("gap_high", 0)
            gap_low = fvg.get("gap_low", 0)
            if gap_high > 0 and gap_low > 0:
                midpoint = (gap_high + gap_low) / 2
                distance = abs(current_price - midpoint)
                all_zones.append({
                    **fvg,
                    "zone_type": "fvg",
                    "distance": distance,
                    "midpoint": midpoint
                })
        
        # Sort by distance and return top 3
        return sorted(all_zones, key=lambda x: x.get("distance", float('inf')))[:3]
        
    except Exception as e:
        logger.error(f"Find nearest zones error: {e}")
        return []

def _analyze_proximity(nearest_zones: list, current_price: float) -> dict:
    """Analyze proximity to nearest zone"""
    try:
        if not nearest_zones:
            return {
                "nearest_zone": None,
                "distance": None,
                "zone_type": None,
                "alert_level": "none"
            }
        
        nearest = nearest_zones[0]
        distance = nearest.get("distance", 0)
        
        # Determine alert level based on distance
        if distance < 50:  # Very close
            alert_level = "critical"
        elif distance < 100:  # Close
            alert_level = "warning"
        elif distance < 200:  # Moderate
            alert_level = "info"
        else:
            alert_level = "none"
        
        return {
            "nearest_zone": {
                "zone_type": nearest.get("zone_type"),
                "price_level": nearest.get("price_level") or nearest.get("midpoint"),
                "strength": nearest.get("strength", 0),
                "status": nearest.get("mitigation_status") or nearest.get("fill_status")
            },
            "distance": distance,
            "zone_type": nearest.get("zone_type"),
            "alert_level": alert_level,
            "proximity_percentage": (distance / current_price) * 100 if current_price > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Proximity analysis error: {e}")
        return {"alert_level": "error"}

def _generate_trading_alerts(proximity_analysis: dict, current_price: float) -> list:
    """Generate trading alerts based on proximity"""
    try:
        alerts = []
        alert_level = proximity_analysis.get("alert_level", "none")
        nearest_zone = proximity_analysis.get("nearest_zone", {})
        
        if alert_level == "critical":
            zone_type = nearest_zone.get("zone_type", "unknown")
            price_level = nearest_zone.get("price_level", "N/A")
            alerts.append(f"🚨 CRITICAL: Very close to {zone_type} at {price_level}")
            
            if zone_type == "bullish_ob":
                alerts.append("📈 Potential bounce opportunity if price holds")
            elif zone_type == "bearish_ob":
                alerts.append("📉 Potential rejection opportunity at resistance")
            elif zone_type == "fvg":
                alerts.append("📊 FVG fill opportunity - watch for reversal")
        
        elif alert_level == "warning":
            alerts.append(f"⚠️ Approaching {nearest_zone.get('zone_type')} zone")
            alerts.append("🎯 Prepare for potential reaction")
        
        return alerts
        
    except Exception as e:
        logger.error(f"Trading alerts error: {e}")
        return []

def _filter_critical_zones(zones: list) -> list:
    """Filter zones yang critical (high strength, untested)"""
    try:
        critical = []
        
        for zone in zones:
            strength = zone.get("strength", 0)
            status = zone.get("mitigation_status", "unknown")
            
            # Critical criteria
            if strength > 0.75 and status == "untested":
                critical.append({
                    **zone,
                    "criticality_score": strength + 0.2,  # Bonus for untested
                    "criticality_reason": "High strength + untested"
                })
            elif strength > 0.85:
                critical.append({
                    **zone,
                    "criticality_score": strength,
                    "criticality_reason": "Very high strength"
                })
        
        return sorted(critical, key=lambda x: x.get("criticality_score", 0), reverse=True)
        
    except Exception as e:
        logger.error(f"Filter critical zones error: {e}")
        return []

def _filter_critical_fvg(fvgs: list) -> list:
    """Filter critical FVGs"""
    try:
        critical = []
        
        for fvg in fvgs:
            strength = fvg.get("strength", 0)
            fill_status = fvg.get("fill_status", "unknown")
            
            if strength > 0.6 and fill_status == "unfilled":
                gap_size = fvg.get("gap_high", 0) - fvg.get("gap_low", 0)
                critical.append({
                    **fvg,
                    "criticality_score": strength + (gap_size / 1000),  # Bonus for larger gaps
                    "criticality_reason": "Strong unfilled gap"
                })
        
        return sorted(critical, key=lambda x: x.get("criticality_score", 0), reverse=True)
        
    except Exception as e:
        logger.error(f"Filter critical FVG error: {e}")
        return []

def _generate_zone_priorities(bullish_obs: list, bearish_obs: list, fvgs: list) -> list:
    """Generate priority alerts for zones"""
    try:
        priorities = []
        
        # High priority untested zones
        untested_count = len([z for z in bullish_obs + bearish_obs if z.get("mitigation_status") == "untested"])
        if untested_count > 0:
            priorities.append(f"🎯 {untested_count} untested zones require monitoring")
        
        # High strength zones
        high_strength = len([z for z in bullish_obs + bearish_obs if z.get("strength", 0) > 0.8])
        if high_strength > 0:
            priorities.append(f"💪 {high_strength} high-strength zones identified")
        
        # Unfilled FVGs
        unfilled_fvg = len([z for z in fvgs if z.get("fill_status") == "unfilled"])
        if unfilled_fvg > 0:
            priorities.append(f"📊 {unfilled_fvg} unfilled FVGs pending")
        
        return priorities
        
    except Exception as e:
        logger.error(f"Zone priorities error: {e}")
        return []

def _filter_zones_by_symbol_tf(context: dict, symbol_filter: str, tf_filter: str) -> dict:
    """Filter zones berdasarkan symbol dan timeframe"""
    try:
        filtered_zones = {
            "bullish_ob": [],
            "bearish_ob": [],
            "fvg": []
        }
        
        # Filter bullish OBs
        for ob in context.get("last_bullish_ob", []):
            if _matches_filters(ob, symbol_filter, tf_filter):
                filtered_zones["bullish_ob"].append(ob)
        
        # Filter bearish OBs
        for ob in context.get("last_bearish_ob", []):
            if _matches_filters(ob, symbol_filter, tf_filter):
                filtered_zones["bearish_ob"].append(ob)
        
        # Filter FVGs
        for fvg in context.get("last_fvg", []):
            if _matches_filters(fvg, symbol_filter, tf_filter):
                filtered_zones["fvg"].append(fvg)
        
        return filtered_zones
        
    except Exception as e:
        logger.error(f"Zone filtering error: {e}")
        return {"bullish_ob": [], "bearish_ob": [], "fvg": []}

def _matches_filters(zone: dict, symbol_filter: str, tf_filter: str) -> bool:
    """Check if zone matches the filters"""
    try:
        # Check symbol filter
        if symbol_filter:
            zone_symbol = zone.get("symbol", "").upper()
            if zone_symbol != symbol_filter:
                return False
        
        # Check timeframe filter
        if tf_filter:
            zone_tf = zone.get("timeframe", "")
            if zone_tf != tf_filter:
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"Filter matching error: {e}")
        return False

def _get_primary_symbol(context: dict) -> str:
    """Get primary symbol from context"""
    try:
        # Try BOS first
        last_bos = context.get("last_bos", {})
        symbol = last_bos.get("symbol", "")
        if symbol:
            return symbol
        
        # Try from OBs
        bullish_obs = context.get("last_bullish_ob", [])
        if bullish_obs:
            return bullish_obs[0].get("symbol", "UNKNOWN")
        
        bearish_obs = context.get("last_bearish_ob", [])
        if bearish_obs:
            return bearish_obs[0].get("symbol", "UNKNOWN")
        
        # Try from FVGs
        fvgs = context.get("last_fvg", [])
        if fvgs:
            return fvgs[0].get("symbol", "UNKNOWN")
        
        return "UNKNOWN"
        
    except Exception as e:
        logger.error(f"Primary symbol error: {e}")
        return "UNKNOWN"

def _get_primary_timeframe(context: dict) -> str:
    """Get primary timeframe from context"""
    try:
        # Try BOS first
        last_bos = context.get("last_bos", {})
        timeframe = last_bos.get("timeframe", "")
        if timeframe:
            return timeframe
        
        # Try from OBs
        bullish_obs = context.get("last_bullish_ob", [])
        if bullish_obs:
            return bullish_obs[0].get("timeframe", "UNKNOWN")
        
        bearish_obs = context.get("last_bearish_ob", [])
        if bearish_obs:
            return bearish_obs[0].get("timeframe", "UNKNOWN")
        
        # Try from FVGs
        fvgs = context.get("last_fvg", [])
        if fvgs:
            return fvgs[0].get("timeframe", "UNKNOWN")
        
        return "UNKNOWN"
        
    except Exception as e:
        logger.error(f"Primary timeframe error: {e}")
        return "UNKNOWN"

def _count_active_zones_filtered(filtered_zones: dict) -> int:
    """Count active zones dari filtered data"""
    try:
        active_count = 0
        
        # Count active bullish OBs
        for ob in filtered_zones.get("bullish_ob", []):
            if ob.get("mitigation_status") == "active":
                active_count += 1
        
        # Count active bearish OBs
        for ob in filtered_zones.get("bearish_ob", []):
            if ob.get("mitigation_status") == "active":
                active_count += 1
        
        # Count unfilled FVGs (considered active)
        for fvg in filtered_zones.get("fvg", []):
            if fvg.get("fill_status") == "unfilled":
                active_count += 1
        
        return active_count
        
    except Exception as e:
        logger.error(f"Active zones filtered count error: {e}")
        return 0

def _count_untested_zones_filtered(filtered_zones: dict) -> int:
    """Count untested zones dari filtered data"""
    try:
        untested_count = 0
        
        # Count untested OBs
        for ob in filtered_zones.get("bullish_ob", []) + filtered_zones.get("bearish_ob", []):
            if ob.get("mitigation_status") == "untested":
                untested_count += 1
        
        return untested_count
        
    except Exception as e:
        logger.error(f"Untested zones filtered count error: {e}")
        return 0

def _generate_proximity_alerts_filtered(filtered_zones: dict) -> list:
    """Generate proximity alerts dari filtered data"""
    try:
        alerts = []
        
        # Check for high-strength untested zones
        for ob in filtered_zones.get("bullish_ob", []):
            if ob.get("strength", 0) > 0.8 and ob.get("mitigation_status") == "untested":
                alerts.append(f"🎯 High-strength bullish OB at {ob.get('price_level', 'N/A')} (untested)")
        
        for ob in filtered_zones.get("bearish_ob", []):
            if ob.get("strength", 0) > 0.8 and ob.get("mitigation_status") == "untested":
                alerts.append(f"🎯 High-strength bearish OB at {ob.get('price_level', 'N/A')} (untested)")
        
        # Check for unfilled FVGs
        for fvg in filtered_zones.get("fvg", []):
            if fvg.get("fill_status") == "unfilled" and fvg.get("strength", 0) > 0.6:
                alerts.append(f"📊 Unfilled FVG: {fvg.get('gap_low', 'N/A')}-{fvg.get('gap_high', 'N/A')}")
        
        return alerts[:5]  # Limit to top 5 alerts
        
    except Exception as e:
        logger.error(f"Proximity alerts filtered error: {e}")
        return []

logger.info("🔍 SMC Zones Endpoints initialized")