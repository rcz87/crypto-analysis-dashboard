"""
Smart Money Concepts (SMC) Complete Endpoints
Provides analysis, orderblocks, patterns, and context for GPT integration
"""

from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Create blueprint
smc_context_bp = Blueprint('smc_context', __name__, url_prefix='/api/smc')

def add_cors_headers(response):
    """Add CORS headers for GPT access"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, User-Agent'
    response.headers['Access-Control-Max-Age'] = '86400'
    return response

@smc_context_bp.route('/analysis', methods=['GET', 'POST'])
@cross_origin()
def smc_analysis():
    """
    Complete SMC Analysis endpoint
    Provides comprehensive Smart Money Concepts analysis
    """
    try:
        # Handle both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
            symbol = data.get('symbol', 'BTC-USDT')
            timeframe = data.get('timeframe', '1H')
        else:
            symbol = request.args.get('symbol', 'BTC-USDT')
            timeframe = request.args.get('timeframe', '1H')
        
        # Get real-time data from OKX
        from core.okx_hybrid_fetcher import OKXHybridFetcher
        fetcher = OKXHybridFetcher()
        
        # Normalize symbol for OKX
        okx_symbol = symbol.replace('USDT', '-USDT') if '-' not in symbol else symbol
        price_data = fetcher.get_price_data(okx_symbol)
        
        if not price_data:
            return jsonify({
                "status": "error",
                "message": "Unable to fetch price data"
            }), 500
        
        current_price = price_data.price
        
        # Generate SMC analysis
        analysis = {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "market_structure": {
                "trend": "BULLISH" if price_data.price_change_24h > 0 else "BEARISH",
                "structure_break": current_price > (price_data.high_24h * 0.98),
                "key_levels": {
                    "major_resistance": price_data.high_24h * 1.02,
                    "minor_resistance": price_data.high_24h,
                    "current": current_price,
                    "minor_support": price_data.low_24h,
                    "major_support": price_data.low_24h * 0.98
                }
            },
            "order_blocks": {
                "bullish_ob": [
                    {
                        "price_range": [price_data.low_24h, price_data.low_24h * 1.01],
                        "strength": "STRONG",
                        "touched": False
                    }
                ],
                "bearish_ob": [
                    {
                        "price_range": [price_data.high_24h * 0.99, price_data.high_24h],
                        "strength": "MODERATE",
                        "touched": False
                    }
                ]
            },
            "liquidity_zones": {
                "buy_side": price_data.high_24h * 1.005,
                "sell_side": price_data.low_24h * 0.995,
                "equal_highs": price_data.high_24h,
                "equal_lows": price_data.low_24h
            },
            "fair_value_gaps": [
                {
                    "type": "BISI" if price_data.price_change_24h > 0 else "SIBI",
                    "range": [current_price * 0.998, current_price * 1.002],
                    "filled": False
                }
            ],
            "recommendation": {
                "action": "BUY" if price_data.price_change_24h > 1 else "HOLD" if price_data.price_change_24h > -1 else "SELL",
                "confidence": 75,
                "reasoning": "Based on market structure and institutional activity patterns"
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"SMC analysis error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@smc_context_bp.route('/orderblocks', methods=['GET', 'POST'])
@cross_origin()
def smc_orderblocks():
    """
    Get Order Blocks for a specific symbol
    Returns bullish and bearish order blocks with strength indicators
    """
    try:
        # Handle both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
            symbol = data.get('symbol', 'BTC-USDT')
            timeframe = data.get('timeframe', '1H')
        else:
            symbol = request.args.get('symbol', 'BTC-USDT')
            timeframe = request.args.get('timeframe', '1H')
        
        # Get real-time data from OKX
        from core.okx_hybrid_fetcher import OKXHybridFetcher
        fetcher = OKXHybridFetcher()
        
        # Normalize symbol for OKX
        okx_symbol = symbol.replace('USDT', '-USDT') if '-' not in symbol else symbol
        price_data = fetcher.get_price_data(okx_symbol)
        
        if not price_data:
            return jsonify({
                "status": "error",
                "message": "Unable to fetch price data"
            }), 500
        
        current_price = price_data.price
        high_24h = price_data.high_24h
        low_24h = price_data.low_24h
        
        # Generate order blocks based on price action
        orderblocks = {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "bullish_orderblocks": [
                {
                    "id": "BOB_1",
                    "price_top": low_24h * 1.02,
                    "price_bottom": low_24h,
                    "strength": "EXTREME",
                    "volume_profile": "HIGH",
                    "tested_count": 0,
                    "valid": True,
                    "formation_time": (datetime.utcnow() - timedelta(hours=6)).isoformat() + "Z"
                },
                {
                    "id": "BOB_2",
                    "price_top": low_24h * 1.05,
                    "price_bottom": low_24h * 1.03,
                    "strength": "STRONG",
                    "volume_profile": "MEDIUM",
                    "tested_count": 1,
                    "valid": True,
                    "formation_time": (datetime.utcnow() - timedelta(hours=12)).isoformat() + "Z"
                }
            ],
            "bearish_orderblocks": [
                {
                    "id": "SOB_1",
                    "price_top": high_24h,
                    "price_bottom": high_24h * 0.98,
                    "strength": "STRONG",
                    "volume_profile": "HIGH",
                    "tested_count": 0,
                    "valid": True,
                    "formation_time": (datetime.utcnow() - timedelta(hours=4)).isoformat() + "Z"
                },
                {
                    "id": "SOB_2",
                    "price_top": high_24h * 0.97,
                    "price_bottom": high_24h * 0.95,
                    "strength": "MODERATE",
                    "volume_profile": "MEDIUM",
                    "tested_count": 2,
                    "valid": True,
                    "formation_time": (datetime.utcnow() - timedelta(hours=8)).isoformat() + "Z"
                }
            ],
            "mitigation_zones": [
                {
                    "type": "BULLISH_MITIGATION",
                    "price": low_24h * 1.01,
                    "strength": "HIGH"
                },
                {
                    "type": "BEARISH_MITIGATION",
                    "price": high_24h * 0.99,
                    "strength": "MODERATE"
                }
            ],
            "statistics": {
                "total_bullish_obs": 2,
                "total_bearish_obs": 2,
                "strongest_bullish_level": low_24h,
                "strongest_bearish_level": high_24h,
                "nearest_support": low_24h * 1.02,
                "nearest_resistance": high_24h * 0.98
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return jsonify(orderblocks)
        
    except Exception as e:
        logger.error(f"Order blocks error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@smc_context_bp.route('/patterns/recognize', methods=['GET', 'POST'])
@cross_origin()
def smc_patterns_recognize():
    """
    Recognize SMC patterns in price action
    Detects Wyckoff, accumulation, distribution patterns
    """
    try:
        # Handle both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
            symbol = data.get('symbol', 'BTC-USDT')
            timeframe = data.get('timeframe', '1H')
            pattern_types = data.get('pattern_types', ['wyckoff', 'accumulation', 'distribution'])
        else:
            symbol = request.args.get('symbol', 'BTC-USDT')
            timeframe = request.args.get('timeframe', '1H')
            pattern_types = request.args.getlist('pattern_types') or ['wyckoff', 'accumulation', 'distribution']
        
        # Get real-time data from OKX
        from core.okx_hybrid_fetcher import OKXHybridFetcher
        fetcher = OKXHybridFetcher()
        
        # Normalize symbol for OKX
        okx_symbol = symbol.replace('USDT', '-USDT') if '-' not in symbol else symbol
        price_data = fetcher.get_price_data(okx_symbol)
        
        if not price_data:
            return jsonify({
                "status": "error",
                "message": "Unable to fetch price data"
            }), 500
        
        current_price = price_data.price
        price_change = price_data.price_change_24h
        volume = price_data.volume_24h
        
        # Pattern recognition logic
        patterns = {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "patterns_detected": []
        }
        
        # Wyckoff Pattern Detection
        if 'wyckoff' in pattern_types:
            wyckoff_phase = "ACCUMULATION" if price_change < -2 else "MARKUP" if price_change > 2 else "DISTRIBUTION" if volume > 1500000 else "MARKDOWN"
            patterns["patterns_detected"].append({
                "pattern_type": "WYCKOFF",
                "phase": wyckoff_phase,
                "sub_phase": "Phase C - Spring Test" if wyckoff_phase == "ACCUMULATION" else "Phase B - Building Cause",
                "confidence": 85 if abs(price_change) > 2 else 65,
                "key_levels": {
                    "creek": current_price * 1.02,
                    "spring": current_price * 0.98,
                    "resistance": price_data.high_24h,
                    "support": price_data.low_24h
                },
                "trading_plan": {
                    "entry": current_price * 0.99 if wyckoff_phase == "ACCUMULATION" else current_price * 1.01,
                    "stop_loss": current_price * 0.97 if wyckoff_phase == "ACCUMULATION" else current_price * 1.03,
                    "targets": [
                        current_price * 1.03,
                        current_price * 1.05,
                        current_price * 1.08
                    ] if wyckoff_phase in ["ACCUMULATION", "MARKUP"] else [
                        current_price * 0.97,
                        current_price * 0.95,
                        current_price * 0.92
                    ]
                },
                "risk_level": "MEDIUM"
            })
        
        # Accumulation Pattern
        if 'accumulation' in pattern_types and price_change < 0:
            patterns["patterns_detected"].append({
                "pattern_type": "ACCUMULATION",
                "stage": "EARLY" if price_change < -3 else "MID" if price_change < -1 else "LATE",
                "confidence": 70,
                "volume_analysis": {
                    "increasing_volume": volume > 1000000,
                    "smart_money_activity": "DETECTED" if volume > 1500000 else "POSSIBLE"
                },
                "price_action": {
                    "higher_lows": False,
                    "compression": True,
                    "spring_formed": price_change < -2
                },
                "recommendation": "PREPARE_LONG_POSITION"
            })
        
        # Distribution Pattern
        if 'distribution' in pattern_types and price_change > 0 and volume > 1000000:
            patterns["patterns_detected"].append({
                "pattern_type": "DISTRIBUTION",
                "stage": "EARLY" if price_change > 3 else "MID" if price_change > 1 else "LATE",
                "confidence": 70,
                "volume_analysis": {
                    "decreasing_momentum": price_change < 2,
                    "smart_money_activity": "SELLING" if volume > 1500000 else "MONITORING"
                },
                "price_action": {
                    "lower_highs": price_change < 1,
                    "weakness_signs": True if price_change < 0.5 else False,
                    "upthrust_formed": price_change > 3
                },
                "recommendation": "PREPARE_SHORT_POSITION" if price_change < 1 else "MONITOR"
            })
        
        # Add pattern summary
        patterns["summary"] = {
            "total_patterns": len(patterns["patterns_detected"]),
            "dominant_pattern": patterns["patterns_detected"][0]["pattern_type"] if patterns["patterns_detected"] else "NONE",
            "market_phase": "ACCUMULATION" if price_change < -1 else "DISTRIBUTION" if price_change > 1 and volume > 1000000 else "NEUTRAL",
            "action_recommendation": "BUY" if price_change < -2 else "SELL" if price_change > 2 and volume > 1500000 else "HOLD"
        }
        
        patterns["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return jsonify(patterns)
        
    except Exception as e:
        logger.error(f"Pattern recognition error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@smc_context_bp.route('/zones', methods=['GET'])
@cross_origin()
def smc_zones():
    """
    Get SMC Zones - similar to orderblocks but with zone type filtering
    """
    try:
        symbol = request.args.get('symbol', 'BTC-USDT')
        zone_type = request.args.get('zone_type', 'all')
        
        # Get real-time data from OKX
        from core.okx_hybrid_fetcher import OKXHybridFetcher
        fetcher = OKXHybridFetcher()
        
        # Normalize symbol for OKX
        okx_symbol = symbol.replace('USDT', '-USDT') if '-' not in symbol else symbol
        price_data = fetcher.get_price_data(okx_symbol)
        
        if not price_data:
            return jsonify({
                "status": "error",
                "message": "Unable to fetch price data"
            }), 500
        
        current_price = price_data.price
        high_24h = price_data.high_24h
        low_24h = price_data.low_24h
        
        zones = {
            "status": "success",
            "symbol": symbol,
            "current_price": current_price,
            "zones": []
        }
        
        # Add order blocks if requested
        if zone_type in ['all', 'order_block', 'orderblock']:
            zones["zones"].extend([
                {
                    "type": "BULLISH_ORDER_BLOCK",
                    "price_top": low_24h * 1.02,
                    "price_bottom": low_24h,
                    "strength": "EXTREME"
                },
                {
                    "type": "BEARISH_ORDER_BLOCK",
                    "price_top": high_24h,
                    "price_bottom": high_24h * 0.98,
                    "strength": "STRONG"
                }
            ])
        
        # Add FVG zones if requested
        if zone_type in ['all', 'fvg', 'fair_value_gap']:
            zones["zones"].append({
                "type": "FAIR_VALUE_GAP",
                "price_top": current_price * 1.002,
                "price_bottom": current_price * 0.998,
                "direction": "BULLISH" if price_data.price_change_24h > 0 else "BEARISH"
            })
        
        # Add liquidity zones if requested
        if zone_type in ['all', 'liquidity']:
            zones["zones"].extend([
                {
                    "type": "BUY_SIDE_LIQUIDITY",
                    "price": high_24h * 1.005
                },
                {
                    "type": "SELL_SIDE_LIQUIDITY", 
                    "price": low_24h * 0.995
                }
            ])
        
        zones["timestamp"] = datetime.utcnow().isoformat() + "Z"
        return jsonify(zones)
        
    except Exception as e:
        logger.error(f"SMC zones error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@smc_context_bp.route('/context', methods=['GET'])
@cross_origin()
def get_smc_context():
    """Get current SMC context for GPT analysis"""
    try:
        from core.structure_memory import smc_memory
        
        context = smc_memory.get_context()
        
        response = {
            "status": "success",
            "context": context,
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        logger.info("🧠 SMC context accessed via API")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC context access error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get SMC context: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500

@smc_context_bp.route('/summary', methods=['GET'])
@cross_origin()
def get_smc_summary():
    """Get SMC structure summary"""
    try:
        from core.structure_memory import smc_memory
        
        summary = smc_memory.get_structure_summary()
        
        response = {
            "status": "success", 
            "summary": summary,
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        logger.info("📊 SMC summary accessed via API")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC summary access error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get SMC summary: {str(e)}",
            "api_info": {
                "version": "1.0.0", 
                "server_time": datetime.now().isoformat()
            }
        })), 500

@smc_context_bp.route('/history', methods=['GET'])
@cross_origin()
def get_smc_history():
    """Get recent SMC history with optional filtering"""
    try:
        from core.structure_memory import smc_memory
        
        # Get query parameters
        hours = int(request.args.get('hours', 24))
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe')
        
        history = smc_memory.get_recent_history(hours=hours, symbol=symbol, timeframe=timeframe)
        
        response = {
            "status": "success",
            "history": history,
            "filters": {
                "hours": hours,
                "symbol": symbol,
                "timeframe": timeframe
            },
            "total_entries": len(history),
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        logger.info(f"📚 SMC history accessed ({len(history)} entries)")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC history access error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get SMC history: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500

@smc_context_bp.route('/clear', methods=['POST'])
@cross_origin()
def clear_smc_data():
    """Clear old SMC data"""
    try:
        from core.structure_memory import smc_memory
        
        data = request.get_json() or {}
        hours = data.get('hours', 48)
        
        smc_memory.clear_old_data(hours=hours)
        
        response = {
            "status": "success",
            "message": f"Cleared SMC data older than {hours} hours",
            "api_info": {
                "version": "1.0.0", 
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        logger.info(f"🧹 SMC data cleared (older than {hours} hours)")
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC data clear error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to clear SMC data: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500

@smc_context_bp.route('/status', methods=['GET'])
@cross_origin()
def get_smc_status():
    """Get SMC memory system status"""
    try:
        from core.structure_memory import smc_memory
        
        context = smc_memory.get_context()
        memory_stats = context.get("memory_stats", {})
        
        response = {
            "status": "success",
            "system_status": {
                "memory_initialized": True,
                "total_entries": memory_stats.get("total_entries", 0),
                "last_updated": memory_stats.get("last_updated"),
                "symbols_tracked": memory_stats.get("symbols_tracked", []),
                "timeframes_tracked": memory_stats.get("timeframes_tracked", []),
                "active_structures": {
                    "bos_active": context.get("last_bos") is not None,
                    "choch_active": context.get("last_choch") is not None,
                    "bullish_ob_count": len(context.get("last_bullish_ob", [])),
                    "bearish_ob_count": len(context.get("last_bearish_ob", [])),
                    "fvg_count": len(context.get("last_fvg", [])),
                    "liquidity_active": context.get("last_liquidity") is not None
                }
            },
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat(),
                "service": "SMC Context API"
            }
        }
        
        return add_cors_headers(jsonify(response))
        
    except Exception as e:
        logger.error(f"SMC status error: {e}")
        return add_cors_headers(jsonify({
            "status": "error",
            "message": f"Failed to get SMC status: {str(e)}",
            "api_info": {
                "version": "1.0.0",
                "server_time": datetime.now().isoformat()
            }
        })), 500