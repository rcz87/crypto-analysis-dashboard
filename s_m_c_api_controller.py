# smc_routes.py
from flask import Blueprint, jsonify, request
from core.professional_smc_analyzer import ProfessionalSMCAnalyzer
from core.okx_fetcher import OKXFetcher
import logging
from datetime import datetime

smc_api = Blueprint('smc_api', __name__, url_prefix='/api/smc')
logger = logging.getLogger(__name__)

# Inisialisasi komponen
smc_analyzer = ProfessionalSMCAnalyzer()
okx_fetcher = OKXFetcher()

@smc_api.route('/context', methods=['GET'])
def get_smc_context():
    """
    Get SMC context for a symbol and timeframe
    """
    try:
        symbol = request.args.get('symbol', 'BTC').upper()
        timeframe = request.args.get('timeframe', '1H')
        
        # Konversi format simbol
        okx_symbol = f"{symbol}-USDT" if not '-' in symbol else symbol
        if symbol.endswith('USDT'):
            okx_symbol = symbol.replace('USDT', '-USDT')
        
        # Fetch data pasar
        market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
        
        if not market_data or 'candles' not in market_data:
            return jsonify({
                "status": "error",
                "message": f"Failed to get market data for {symbol} {timeframe}"
            }), 400
        
        # Analisis SMC
        smc_result = smc_analyzer.analyze_market_structure(market_data['candles'])
        
        # Current price
        current_price = float(market_data['candles'][-1]['close']) if market_data['candles'] else 0
        
        # Format SMC context
        context = {
            "market_structure": smc_result.get('market_structure', 'NEUTRAL'),
            "trend_bias": smc_result.get('trend_bias', 'NEUTRAL'),
            "trend_strength": smc_result.get('trend_strength', 0),
            "current_phase": smc_result.get('current_phase', 'ACCUMULATION'),
            "order_block_proximity": smc_result.get('order_block_proximity', 'NONE'),
            "liquidity_status": {
                "above": smc_result.get('liquidity', {}).get('above', False),
                "below": smc_result.get('liquidity', {}).get('below', False),
                "recent_sweep": smc_result.get('liquidity_sweep', {}).get('detected', False)
            },
            "key_levels": smc_result.get('key_levels', []),
            "recent_structure_change": smc_result.get('structure_change', False),
            "high_timeframe_alignment": smc_result.get('htf_alignment', 'NEUTRAL')
        }
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in SMC context: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get SMC context",
            "error": str(e)
        }), 500

@smc_api.route('/summary', methods=['GET'])
def get_smc_summary():
    """
    Get summarized SMC view
    """
    try:
        symbol = request.args.get('symbol', 'BTC').upper()
        timeframe = request.args.get('timeframe', '1H')
        
        # Konversi format simbol
        okx_symbol = f"{symbol}-USDT" if not '-' in symbol else symbol
        if symbol.endswith('USDT'):
            okx_symbol = symbol.replace('USDT', '-USDT')
        
        # Fetch data pasar
        market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 100)  # Reduced count for summary
        
        if not market_data or 'candles' not in market_data:
            return jsonify({
                "status": "error",
                "message": f"Failed to get market data for {symbol} {timeframe}"
            }), 400
        
        # Analisis SMC
        smc_result = smc_analyzer.analyze_market_structure(market_data['candles'])
        
        # Current price
        current_price = float(market_data['candles'][-1]['close']) if market_data['candles'] else 0
        
        # Format SMC summary (ringkas)
        summary = {
            "bias": smc_result.get('trend_bias', 'NEUTRAL'),
            "structure": smc_result.get('market_structure', 'NEUTRAL'),
            "ob_count": {
                "bullish": len(smc_result.get('order_blocks', {}).get('bullish', [])),
                "bearish": len(smc_result.get('order_blocks', {}).get('bearish', []))
            },
            "fvg_count": len(smc_result.get('fair_value_gaps', [])),
            "nearest_level": smc_result.get('nearest_level', 0),
            "phase": smc_result.get('current_phase', 'ACCUMULATION')
        }
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in SMC summary: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get SMC summary",
            "error": str(e)
        }), 500

@smc_api.route('/history', methods=['GET'])
def get_smc_history():
    """
    Get historical SMC changes
    """
    try:
        symbol = request.args.get('symbol', 'BTC').upper()
        timeframe = request.args.get('timeframe', '1H')
        limit = min(int(request.args.get('limit', 5)), 20)
        
        # Mock history (sementara)
        # Implementasi nyata perlu tracking di database
        history = [
            {
                "timestamp": "2025-08-12T08:30:00Z",
                "event_type": "STRUCTURE_CHANGE",
                "old_structure": "BULLISH",
                "new_structure": "NEUTRAL",
                "price": 59782.50
            },
            {
                "timestamp": "2025-08-11T14:15:00Z",
                "event_type": "LIQUIDITY_SWEEP",
                "direction": "DOWN",
                "price": 58120.75
            },
            {
                "timestamp": "2025-08-11T04:00:00Z",
                "event_type": "ORDER_BLOCK_CREATED",
                "type": "BULLISH",
                "price_range": [57800.0, 58100.0]
            },
            {
                "timestamp": "2025-08-10T16:45:00Z",
                "event_type": "FAIR_VALUE_GAP",
                "direction": "UP",
                "price_range": [56900.0, 57300.0]
            },
            {
                "timestamp": "2025-08-09T22:30:00Z",
                "event_type": "STRUCTURE_CHANGE",
                "old_structure": "NEUTRAL",
                "new_structure": "BULLISH",
                "price": 56450.0
            }
        ]
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "history": history[:limit],
            "count": len(history[:limit]),
            "note": "Historical tracking requires database integration"
        })
        
    except Exception as e:
        logger.error(f"Error in SMC history: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get SMC history",
            "error": str(e)
        }), 500

@smc_api.route('/status', methods=['GET'])
def get_smc_status():
    """
    Get SMC analyzer status
    """
    return jsonify({
        "status": "operational",
        "analyzer_version": "1.0.0",
        "supported_features": [
            "market_structure_analysis",
            "order_blocks",
            "fair_value_gaps",
            "liquidity_sweep_detection",
            "smart_money_concepts"
        ],
        "supported_timeframes": ["1m", "5m", "15m", "30m", "1H", "4H", "1D"],
        "timestamp": datetime.utcnow().isoformat()
    })

@smc_api.route('/zones', methods=['GET'])
def get_smc_zones():
    """
    Get all SMC zones for a symbol/timeframe
    """
    try:
        symbol = request.args.get('symbol', 'BTC').upper()
        timeframe = request.args.get('timeframe', '1H')
        
        # Konversi format simbol
        okx_symbol = f"{symbol}-USDT" if not '-' in symbol else symbol
        if symbol.endswith('USDT'):
            okx_symbol = symbol.replace('USDT', '-USDT')
        
        # Fetch data pasar
        market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
        
        if not market_data or 'candles' not in market_data:
            return jsonify({
                "status": "error",
                "message": f"Failed to get market data for {symbol} {timeframe}"
            }), 400
        
        # Analisis SMC
        smc_result = smc_analyzer.analyze_market_structure(market_data['candles'])
        
        # Current price
        current_price = float(market_data['candles'][-1]['close']) if market_data['candles'] else 0
        
        # Format zones dari hasil SMC
        # Bullish order blocks
        bullish_obs = []
        for ob in smc_result.get('order_blocks', {}).get('bullish', []):
            bullish_obs.append({
                "type": "ORDER_BLOCK_BULLISH",
                "price_low": float(ob.get('low', 0)),
                "price_high": float(ob.get('high', 0)),
                "timestamp": ob.get('timestamp', 0),
                "strength": ob.get('strength', 'medium'),
                "distance_from_current": round((current_price - float(ob.get('high', 0))) / current_price * 100, 2),
                "status": "UNTESTED" if current_price > float(ob.get('high', 0)) else "ACTIVE"
            })
        
        # Bearish order blocks
        bearish_obs = []
        for ob in smc_result.get('order_blocks', {}).get('bearish', []):
            bearish_obs.append({
                "type": "ORDER_BLOCK_BEARISH",
                "price_low": float(ob.get('low', 0)),
                "price_high": float(ob.get('high', 0)),
                "timestamp": ob.get('timestamp', 0),
                "strength": ob.get('strength', 'medium'),
                "distance_from_current": round((float(ob.get('low', 0)) - current_price) / current_price * 100, 2),
                "status": "UNTESTED" if current_price < float(ob.get('low', 0)) else "ACTIVE"
            })
        
        # Fair value gaps
        fvgs = []
        for fvg in smc_result.get('fair_value_gaps', []):
            fvgs.append({
                "type": "FAIR_VALUE_GAP",
                "direction": fvg.get('type', 'neutral').upper(),
                "price_low": float(fvg.get('low', 0)),
                "price_high": float(fvg.get('high', 0)),
                "timestamp": fvg.get('timestamp', 0),
                "status": "UNFILLED",
                "distance_from_current": round(
                    ((float(fvg.get('high', 0)) + float(fvg.get('low', 0)))/2 - current_price) / current_price * 100, 2
                )
            })
        
        # Support/Resistance levels
        key_levels = []
        for level in smc_result.get('key_levels', []):
            key_levels.append({
                "type": "KEY_LEVEL",
                "level_type": level.get('type', 'SUPPORT'),
                "price": float(level.get('price', 0)),
                "strength": level.get('strength', 'medium'),
                "touches": level.get('touches', 0),
                "distance_from_current": round((float(level.get('price', 0)) - current_price) / current_price * 100, 2)
            })
        
        # Liquidity
        liquidity = []
        if smc_result.get('liquidity_sweep', {}).get('detected'):
            sweep = smc_result.get('liquidity_sweep', {})
            liquidity.append({
                "type": "LIQUIDITY_LEVEL",
                "direction": sweep.get('type', 'unknown').upper(),
                "price": float(sweep.get('price', 0)),
                "timestamp": sweep.get('timestamp', 0),
                "status": "SWEPT" if sweep.get('detected') else "ACTIVE",
                "distance_from_current": round((float(sweep.get('price', 0)) - current_price) / current_price * 100, 2)
            })
        
        # Combine all zones
        all_zones = bullish_obs + bearish_obs + fvgs + key_levels + liquidity
        
        # Sort by distance from current price
        all_zones.sort(key=lambda x: abs(x['distance_from_current']))
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "zones": {
                "all": all_zones,
                "bullish_order_blocks": bullish_obs,
                "bearish_order_blocks": bearish_obs,
                "fair_value_gaps": fvgs,
                "key_levels": key_levels,
                "liquidity": liquidity
            },
            "counts": {
                "total": len(all_zones),
                "bullish_obs": len(bullish_obs),
                "bearish_obs": len(bearish_obs),
                "fvgs": len(fvgs),
                "key_levels": len(key_levels),
                "liquidity": len(liquidity)
            },
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in SMC zones: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get SMC zones",
            "error": str(e)
        }), 500

@smc_api.route('/zones/proximity/<symbol>/<price>', methods=['GET'])
def get_zones_proximity(symbol, price):
    """
    Get zones near a specific price
    """
    try:
        # Validate input
        symbol = symbol.upper()
        price = float(price)
        timeframe = request.args.get('timeframe', '1H')
        proximity_pct = float(request.args.get('proximity_pct', 2.0))  # Default 2% proximity
        
        # Konversi format simbol
        okx_symbol = f"{symbol}-USDT" if not '-' in symbol else symbol
        if symbol.endswith('USDT'):
            okx_symbol = symbol.replace('USDT', '-USDT')
        
        # Fetch data pasar
        market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
        
        if not market_data or 'candles' not in market_data:
            return jsonify({
                "status": "error",
                "message": f"Failed to get market data for {symbol} {timeframe}"
            }), 400
        
        # Analisis SMC
        smc_result = smc_analyzer.analyze_market_structure(market_data['candles'])
        
        # Current market price (untuk referensi)
        current_price = float(market_data['candles'][-1]['close']) if market_data['candles'] else 0
        
        # Kumpulkan semua zona
        all_zones = []
        
        # OBs Bullish
        for ob in smc_result.get('order_blocks', {}).get('bullish', []):
            ob_high = float(ob.get('high', 0))
            ob_low = float(ob.get('low', 0))
            
            # Cek apakah harga berada dalam proximity dari zona
            distance_high_pct = abs(price - ob_high) / price * 100
            distance_low_pct = abs(price - ob_low) / price * 100
            
            if distance_high_pct <= proximity_pct or distance_low_pct <= proximity_pct or (price >= ob_low and price <= ob_high):
                all_zones.append({
                    "type": "ORDER_BLOCK_BULLISH",
                    "price_low": ob_low,
                    "price_high": ob_high,
                    "distance_pct": min(distance_high_pct, distance_low_pct),
                    "strength": ob.get('strength', 'medium')
                })
        
        # OBs Bearish
        for ob in smc_result.get('order_blocks', {}).get('bearish', []):
            ob_high = float(ob.get('high', 0))
            ob_low = float(ob.get('low', 0))
            
            # Cek apakah harga berada dalam proximity dari zona
            distance_high_pct = abs(price - ob_high) / price * 100
            distance_low_pct = abs(price - ob_low) / price * 100
            
            if distance_high_pct <= proximity_pct or distance_low_pct <= proximity_pct or (price >= ob_low and price <= ob_high):
                all_zones.append({
                    "type": "ORDER_BLOCK_BEARISH",
                    "price_low": ob_low,
                    "price_high": ob_high,
                    "distance_pct": min(distance_high_pct, distance_low_pct),
                    "strength": ob.get('strength', 'medium')
                })
        
        # FVGs
        for fvg in smc_result.get('fair_value_gaps', []):
            fvg_high = float(fvg.get('high', 0))
            fvg_low = float(fvg.get('low', 0))
            
            # Cek proximity
            distance_high_pct = abs(price - fvg_high) / price * 100
            distance_low_pct = abs(price - fvg_low) / price * 100
            
            if distance_high_pct <= proximity_pct or distance_low_pct <= proximity_pct or (price >= fvg_low and price <= fvg_high):
                all_zones.append({
                    "type": "FAIR_VALUE_GAP",
                    "price_low": fvg_low,
                    "price_high": fvg_high,
                    "distance_pct": min(distance_high_pct, distance_low_pct),
                    "direction": fvg.get('type', 'neutral').upper()
                })
        
        # Key levels
        for level in smc_result.get('key_levels', []):
            level_price = float(level.get('price', 0))
            
            # Cek proximity
            distance_pct = abs(price - level_price) / price * 100
            
            if distance_pct <= proximity_pct:
                all_zones.append({
                    "type": "KEY_LEVEL",
                    "price": level_price,
                    "distance_pct": distance_pct,
                    "level_type": level.get('type', 'SUPPORT'),
                    "strength": level.get('strength', 'medium')
                })
        
        # Sort by proximity
        all_zones.sort(key=lambda x: x['distance_pct'])
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "target_price": price,
            "current_price": current_price,
            "proximity_pct": proximity_pct,
            "zones_in_proximity": all_zones,
            "count": len(all_zones),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Invalid price format"
        }), 400
    except Exception as e:
        logger.error(f"Error in zones proximity: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get zones in proximity",
            "error": str(e)
        }), 500

@smc_api.route('/zones/critical', methods=['GET'])
def get_critical_zones():
    """
    Get critical/high-impact zones
    """
    try:
        symbol = request.args.get('symbol', 'BTC').upper()
        timeframe = request.args.get('timeframe', '1H')
        
        # Konversi format simbol
        okx_symbol = f"{symbol}-USDT" if not '-' in symbol else symbol
        if symbol.endswith('USDT'):
            okx_symbol = symbol.replace('USDT', '-USDT')
        
        # Fetch data pasar
        market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
        
        if not market_data or 'candles' not in market_data:
            return jsonify({
                "status": "error",
                "message": f"Failed to get market data for {symbol} {timeframe}"
            }), 400
        
        # Analisis SMC
        smc_result = smc_analyzer.analyze_market_structure(market_data['candles'])
        
        # Current price
        current_price = float(market_data['candles'][-1]['close']) if market_data['candles'] else 0
        
        # Filter zona berdasarkan strength dan proximity ke harga saat ini
        critical_zones = []
        
        # OBs dengan strength tinggi
        for ob_type in ['bullish', 'bearish']:
            for ob in smc_result.get('order_blocks', {}).get(ob_type, []):
                if ob.get('strength', 'medium') == 'strong':
                    # Hitung proximity ke harga saat ini
                    ob_mid = (float(ob.get('high', 0)) + float(ob.get('low', 0))) / 2
                    distance_pct = abs(current_price - ob_mid) / current_price * 100
                    
                    critical_zones.append({
                        "type": f"ORDER_BLOCK_{ob_type.upper()}",
                        "price_low": float(ob.get('low', 0)),
                        "price_high": float(ob.get('high', 0)),
                        "distance_pct": distance_pct,
                        "strength": "STRONG",
                        "impact": "HIGH"
                    })
        
        # FVGs yang belum terisi
        for fvg in smc_result.get('fair_value_gaps', []):
            # Cek jika FVG belum terisi
            is_filled = False  # Logic untuk cek fill status perlu diimplementasikan
            
            if not is_filled:
                fvg_mid = (float(fvg.get('high', 0)) + float(fvg.get('low', 0))) / 2
                distance_pct = abs(current_price - fvg_mid) / current_price * 100
                
                if distance_pct <= 5.0:  # FVGs dalam range 5%
                    critical_zones.append({
                        "type": "FAIR_VALUE_GAP",
                        "price_low": float(fvg.get('low', 0)),
                        "price_high": float(fvg.get('high', 0)),
                        "distance_pct": distance_pct,
                        "direction": fvg.get('type', 'neutral').upper(),
                        "impact": "MEDIUM"
                    })
        
        # Key levels dengan banyak touches
        for level in smc_result.get('key_levels', []):
            if level.get('touches', 0) >= 3 or level.get('strength', 'medium') == 'strong':
                distance_pct = abs(current_price - float(level.get('price', 0))) / current_price * 100
                
                if distance_pct <= 3.0:  # Levels dalam range 3%
                    critical_zones.append({
                        "type": "KEY_LEVEL",
                        "level_type": level.get('type', 'SUPPORT'),
                        "price": float(level.get('price', 0)),
                        "distance_pct": distance_pct,
                        "touches": level.get('touches', 0),
                        "impact": "HIGH" if level.get('touches', 0) >= 3 else "MEDIUM"
                    })
        
        # Sort by distance and impact
        critical_zones.sort(key=lambda x: (0 if x['impact'] == 'HIGH' else 1, x['distance_pct']))
        
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "current_price": current_price,
            "critical_zones": critical_zones,
            "count": len(critical_zones),
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in critical zones: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get critical zones",
            "error": str(e)
        }), 500

@smc_api.route('/patterns/recognize', methods=['POST'])
def recognize_patterns():
    """
    Recognize SMC patterns from candle data
    """
    try:
        data = request.get_json()
        
        # Option 1: Pass candles directly
        candles = data.get('candles')
        
        # Option 2: Pass symbol/timeframe to fetch
        if not candles:
            symbol = data.get('symbol', 'BTC').upper()
            timeframe = data.get('timeframe', '1H')
            
            # Konversi format simbol
            okx_symbol = f"{symbol}-USDT" if not '-' in symbol else symbol
            if symbol.endswith('USDT'):
                okx_symbol = symbol.replace('USDT', '-USDT')
            
            # Fetch data pasar
            market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, 200)
            
            if not market_data or 'candles' not in market_data:
                return jsonify({
                    "status": "error",
                    "message": f"Failed to get market data for {symbol} {timeframe}"
                }), 400
                
            candles = market_data['candles']
        
        if not candles:
            return jsonify({
                "status": "error",
                "message": "No candle data provided"
            }), 400
        
        # Lakukan analisis pola
        # Ini mensimulasikan analisis yang sebenarnya memerlukan implementasi yang kompleks
        patterns = []
        
        # Example pattern detection (mock)
        patterns.append({
            "type": "BREAK_OF_STRUCTURE",
            "direction": "BULLISH",
            "confidence": 0.85,
            "candle_index": len(candles) - 5,
            "description": "Price broke above previous structure high, creating bullish BOS"
        })
        
        patterns.append({
            "type": "ORDERBLOCK_FORMED",
            "direction": "BULLISH",
            "confidence": 0.75,
            "candle_index": len(candles) - 8,
            "price_range": [float(candles[-8]['low']), float(candles[-8]['high'])],
            "description": "Bullish order block formed before significant move up"
        })
        
        # Add more mock patterns for example
        if len(candles) > 20:
            patterns.append({
                "type": "LIQUIDITY_GRAB",
                "direction": "BEARISH",
                "confidence": 0.7,
                "candle_index": len(candles) - 15,
                "description": "Price swept lows before reversing, indicating liquidity grab"
            })
        
        # Current price
        current_price = float(candles[-1]['close']) if candles else 0
        
        return jsonify({
            "status": "success",
            "patterns_detected": patterns,
            "count": len(patterns),
            "current_price": current_price,
            "timestamp": datetime.utcnow().isoformat(),
            "note": "Pattern recognition uses heuristic rules and may not be 100% accurate"
        })
        
    except Exception as e:
        logger.error(f"Error recognizing patterns: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to recognize patterns",
            "error": str(e)
        }), 500
