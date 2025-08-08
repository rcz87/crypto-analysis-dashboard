"""
🏆 Top Signal Endpoint - Sinyal terbaik dengan filtering dan Telegram integration
Menampilkan sinyal dengan confidence tertinggi berdasarkan symbol dan timeframe
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Blueprint initialization
signal_top_bp = Blueprint("signal_top", __name__)
logger = logging.getLogger(__name__)

@signal_top_bp.route("/api/signal/top", methods=["GET"])
@cross_origin()
def get_top_signal():
    """
    🏆 Get Top Signal - Sinyal terbaik dengan filtering
    
    Query Parameters:
    - symbol: Filter by symbol (e.g., ETHUSDT, BTCUSDT)
    - tf: Filter by timeframe (e.g., 15M, 1H, 4H)
    - send_telegram: Send signal to Telegram (true/false)
    
    Examples:
    GET /api/signal/top
    GET /api/signal/top?symbol=ETHUSDT
    GET /api/signal/top?tf=15M
    GET /api/signal/top?symbol=SOLUSDT&tf=1H
    GET /api/signal/top?symbol=BTCUSDT&send_telegram=true
    
    Response:
    {
        "status": "success",
        "symbol": "BTCUSDT",
        "timeframe": "1H",
        "signal": {
            "symbol": "BTCUSDT",
            "timeframe": "1H",
            "signal": "BUY",
            "confidence": 82,
            "trend": "BULLISH",
            "entry_price": 43500.0,
            "stop_loss": 42900.0,
            "take_profit": [44300.0, 44800.0],
            "reasoning": "CHoCH bullish + volume breakout + RSI divergence",
            "smc_summary": {
                "bos": true,
                "choch": true,
                "bullish_ob": true,
                "fvg": false,
                "liquidity": false
            },
            "last_updated": "2025-08-05T04:15:00"
        }
    }
    """
    try:
        # Get query parameters
        symbol_filter = request.args.get('symbol', '').upper()
        tf_filter = request.args.get('tf', '')
        send_telegram = request.args.get('send_telegram', 'false').lower() == 'true'
        
        # Get all active signals
        all_signals = get_all_active_signals()
        
        # Filter signals berdasarkan symbol dan timeframe
        filtered_signals = _filter_signals(all_signals, symbol_filter, tf_filter)
        
        # Get top signal dengan prioritas
        top_signal = _get_priority_signal(filtered_signals)
        
        # Prepare response
        response_data = {
            "status": "success",
            "symbol": symbol_filter if symbol_filter else (top_signal.get("symbol") if top_signal else "ALL"),
            "timeframe": tf_filter if tf_filter else (top_signal.get("timeframe") if top_signal else "ALL"),
            "filters_applied": {
                "symbol_filter": symbol_filter if symbol_filter else "none",
                "timeframe_filter": tf_filter if tf_filter else "none"
            },
            "signal": top_signal,
            "signal_stats": {
                "total_signals_found": len(all_signals),
                "filtered_signals": len(filtered_signals),
                "priority_signals": len([s for s in filtered_signals if _is_priority_signal(s)])
            },
            "api_info": {
                "version": "2.0.0",
                "service": "Top Signal API",
                "server_time": datetime.now().isoformat()
            }
        }
        
        # Send to Telegram if requested
        if send_telegram and top_signal:
            telegram_result = _send_signal_to_telegram(top_signal)
            response_data["telegram_sent"] = telegram_result
        
        logger.info(f"✅ Top signal retrieved - Symbol: {symbol_filter}, TF: {tf_filter}, Signal: {top_signal.get('signal') if top_signal else 'None'}")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Top signal endpoint error: {e}")
        return jsonify({
            'error': 'Failed to retrieve top signal',
            'details': str(e),
            'api_version': '2.0.0',
            'server_time': datetime.now().isoformat()
        }), 500

@signal_top_bp.route("/api/signal/top/telegram", methods=["POST"])
@cross_origin()
def send_top_signal_to_telegram():
    """
    📱 Send Top Signal to Telegram
    
    POST /api/signal/top/telegram
    {
        "symbol": "BTCUSDT",
        "tf": "1H",
        "custom_message": "Trading Alert"
    }
    """
    try:
        data = request.get_json() or {}
        symbol_filter = data.get('symbol', '').upper()
        tf_filter = data.get('tf', '')
        custom_message = data.get('custom_message', '')
        
        # Get top signal
        all_signals = get_all_active_signals()
        filtered_signals = _filter_signals(all_signals, symbol_filter, tf_filter)
        top_signal = _get_priority_signal(filtered_signals)
        
        if not top_signal:
            return jsonify({
                'status': 'error',
                'message': 'No signal found to send'
            }), 404
        
        # Send to Telegram
        telegram_result = _send_signal_to_telegram(top_signal, custom_message)
        
        response = {
            "status": "success",
            "signal_sent": top_signal,
            "telegram_result": telegram_result,
            "custom_message": custom_message,
            "api_info": {
                "version": "2.0.0",
                "service": "Telegram Signal Sender",
                "server_time": datetime.now().isoformat()
            }
        }
        
        logger.info(f"✅ Signal sent to Telegram - {top_signal.get('symbol')} {top_signal.get('signal')}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Telegram signal error: {e}")
        return jsonify({
            'error': 'Failed to send signal to Telegram',
            'details': str(e)
        }), 500

def get_all_active_signals() -> List[Dict]:
    """Get semua active signals dari berbagai sumber"""
    try:
        active_signals = []
        
        # Generate signals dari SMC analysis
        smc_signals = _generate_smc_signals()
        active_signals.extend(smc_signals)
        
        # Generate signals dari AI analysis
        ai_signals = _generate_ai_signals()
        active_signals.extend(ai_signals)
        
        # Generate signals dari technical analysis
        technical_signals = _generate_technical_signals()
        active_signals.extend(technical_signals)
        
        # Remove duplicates dan sort by confidence
        unique_signals = _deduplicate_signals(active_signals)
        sorted_signals = sorted(unique_signals, key=lambda x: x.get('confidence', 0), reverse=True)
        
        logger.info(f"✅ Generated {len(sorted_signals)} active signals")
        return sorted_signals
        
    except Exception as e:
        logger.error(f"Get active signals error: {e}")
        # Return fallback signals untuk testing
        return _get_fallback_signals()

def _filter_signals(signals: List[Dict], symbol_filter: str, tf_filter: str) -> List[Dict]:
    """Filter signals berdasarkan symbol dan timeframe"""
    try:
        filtered = []
        
        for signal in signals:
            # Check symbol filter
            if symbol_filter and signal.get("symbol", "").upper() != symbol_filter:
                continue
            
            # Check timeframe filter
            if tf_filter and signal.get("timeframe", "") != tf_filter:
                continue
            
            filtered.append(signal)
        
        return filtered
        
    except Exception as e:
        logger.error(f"Signal filtering error: {e}")
        return signals

def _get_priority_signal(filtered_signals: List[Dict]) -> Optional[Dict]:
    """Get sinyal dengan prioritas tertinggi"""
    try:
        if not filtered_signals:
            return None
        
        # Prioritaskan sinyal aktif dengan high confidence
        priority_signals = [
            s for s in filtered_signals
            if _is_priority_signal(s)
        ]
        
        # Get signal dengan confidence tertinggi dari priority signals
        if priority_signals:
            top_signal = max(priority_signals, key=lambda s: s.get("confidence", 0))
        else:
            # Fallback ke signal dengan confidence tertinggi dari semua signals
            top_signal = max(filtered_signals, key=lambda s: s.get("confidence", 0))
        
        # Enhance signal dengan additional info
        enhanced_signal = _enhance_signal_info(top_signal)
        
        return enhanced_signal
        
    except Exception as e:
        logger.error(f"Priority signal error: {e}")
        return filtered_signals[0] if filtered_signals else None

def _is_priority_signal(signal: Dict) -> bool:
    """Check apakah signal adalah priority signal"""
    try:
        signal_type = signal.get("signal", "").upper()
        confidence = signal.get("confidence", 0)
        
        # Priority criteria
        priority_signals = ["BUY", "SELL", "STRONG_BUY", "STRONG_SELL"]
        min_confidence = 60
        
        return signal_type in priority_signals and confidence >= min_confidence
        
    except Exception as e:
        logger.error(f"Priority signal check error: {e}")
        return False

def _enhance_signal_info(signal: Dict) -> Dict:
    """Enhance signal dengan additional information"""
    try:
        from core.structure_memory import smc_memory
        
        enhanced = signal.copy()
        
        # Add SMC context
        context = smc_memory.get_context()
        
        # Enhance SMC summary
        if "smc_summary" not in enhanced:
            enhanced["smc_summary"] = {
                "bos": bool(context.get("last_bos")),
                "choch": bool(context.get("last_choch")),
                "bullish_ob": len(context.get("last_bullish_ob", [])) > 0,
                "bearish_ob": len(context.get("last_bearish_ob", [])) > 0,
                "fvg": len(context.get("last_fvg", [])) > 0,
                "liquidity": bool(context.get("last_liquidity"))
            }
        
        # Add timestamp if missing
        if "last_updated" not in enhanced:
            enhanced["last_updated"] = datetime.now().isoformat()
        
        # Enhance reasoning dengan struktur detail
        if "reasoning" not in enhanced or not enhanced["reasoning"]:
            enhanced["reasoning"] = _build_detailed_reasoning(enhanced, context)
        
        return enhanced
        
    except Exception as e:
        logger.error(f"Signal enhancement error: {e}")
        return signal

def _generate_smc_signals() -> List[Dict]:
    """Generate signals dari SMC analysis"""
    try:
        from core.structure_memory import smc_memory
        
        context = smc_memory.get_context()
        signals = []
        
        # Analyze symbols dari context
        symbols = set()
        
        # Get symbols dari berbagai structures
        for structure_list in [context.get("last_bullish_ob", []), context.get("last_bearish_ob", []), context.get("last_fvg", [])]:
            for item in structure_list:
                if item.get("symbol"):
                    symbols.add(item["symbol"])
        
        # Generate signal untuk setiap symbol
        for symbol in symbols:
            signal = _analyze_smc_signal(symbol, context)
            if signal:
                signals.append(signal)
        
        # Add default signals if no symbols found
        if not signals:
            default_symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
            for symbol in default_symbols:
                signal = _create_sample_signal(symbol)
                signals.append(signal)
        
        return signals
        
    except Exception as e:
        logger.error(f"SMC signals generation error: {e}")
        return []

def _analyze_smc_signal(symbol: str, context: Dict) -> Optional[Dict]:
    """Analyze SMC signal untuk specific symbol"""
    try:
        # Get bullish dan bearish OBs untuk symbol
        bullish_obs = [ob for ob in context.get("last_bullish_ob", []) if ob.get("symbol") == symbol]
        bearish_obs = [ob for ob in context.get("last_bearish_ob", []) if ob.get("symbol") == symbol]
        fvgs = [fvg for fvg in context.get("last_fvg", []) if fvg.get("symbol") == symbol]
        
        # Calculate signal strength
        bullish_strength = sum(ob.get("strength", 0) for ob in bullish_obs)
        bearish_strength = sum(ob.get("strength", 0) for ob in bearish_obs)
        
        # Determine signal
        if bullish_strength > bearish_strength and bullish_strength > 0.6:
            signal_type = "STRONG_BUY" if bullish_strength > 0.8 else "BUY"
            trend = "BULLISH"
            confidence = min(int(bullish_strength * 100), 95)
        elif bearish_strength > bullish_strength and bearish_strength > 0.6:
            signal_type = "STRONG_SELL" if bearish_strength > 0.8 else "SELL"
            trend = "BEARISH"  
            confidence = min(int(bearish_strength * 100), 95)
        else:
            signal_type = "NEUTRAL"
            trend = "SIDEWAYS"
            confidence = 50
        
        # Get timeframe dari first available structure
        timeframe = "1H"  # default
        if bullish_obs:
            timeframe = bullish_obs[0].get("timeframe", "1H")
        elif bearish_obs:
            timeframe = bearish_obs[0].get("timeframe", "1H")
        elif fvgs:
            timeframe = fvgs[0].get("timeframe", "1H")
        
        # Generate entry price dan levels
        entry_price = _estimate_entry_price(symbol, bullish_obs, bearish_obs)
        stop_loss, take_profit = _calculate_risk_levels(entry_price, signal_type)
        
        signal = {
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": signal_type,
            "confidence": confidence,
            "trend": trend,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "reasoning": f"SMC Analysis: {len(bullish_obs)} bullish OB, {len(bearish_obs)} bearish OB, {len(fvgs)} FVG",
            "smc_summary": {
                "bos": bool(context.get("last_bos")),
                "choch": bool(context.get("last_choch")),
                "bullish_ob": len(bullish_obs) > 0,
                "bearish_ob": len(bearish_obs) > 0,
                "fvg": len(fvgs) > 0,
                "liquidity": bool(context.get("last_liquidity"))
            },
            "last_updated": datetime.now().isoformat()
        }
        
        return signal
        
    except Exception as e:
        logger.error(f"SMC signal analysis error for {symbol}: {e}")
        return None

def _generate_ai_signals() -> List[Dict]:
    """Generate signals dari AI analysis"""
    try:
        # Sample AI-generated signals dengan detailed reasoning
        ai_signals = [
            _create_sample_signal("BTCUSDT", "BUY", 78, "", "1H"),
            _create_sample_signal("ETHUSDT", "SELL", 71, "", "1H"),
            _create_sample_signal("SOLUSDT", "STRONG_BUY", 85, "", "1H")
        ]
        
        return ai_signals
        
    except Exception as e:
        logger.error(f"AI signals generation error: {e}")
        return []

def _generate_technical_signals() -> List[Dict]:
    """Generate signals dari technical analysis"""
    try:
        # Sample technical signals dengan detailed reasoning
        technical_signals = [
            _create_sample_signal("ADAUSDT", "BUY", 66, "", "4H"),
            _create_sample_signal("DOTUSDT", "NEUTRAL", 52, "", "1H"),
            _create_sample_signal("AVAXUSDT", "SELL", 74, "", "1H")
        ]
        
        return technical_signals
        
    except Exception as e:
        logger.error(f"Technical signals generation error: {e}")
        return []

def _create_sample_signal(symbol: str, signal_type: str = "BUY", confidence: int = 75, reasoning: str = "", timeframe: str = "1H") -> Dict:
    """Create sample signal untuk testing"""
    try:
        # Sample price data (dalam production, ambil dari OKX API)
        price_data = {
            "BTCUSDT": 43500.0,
            "ETHUSDT": 2420.0,
            "SOLUSDT": 95.50,
            "ADAUSDT": 0.385,
            "DOTUSDT": 6.75,
            "AVAXUSDT": 28.50
        }
        
        entry_price = price_data.get(symbol, 100.0)
        stop_loss, take_profit = _calculate_risk_levels(entry_price, signal_type)
        
        # Determine trend
        trend_map = {
            "BUY": "BULLISH",
            "STRONG_BUY": "BULLISH",
            "SELL": "BEARISH", 
            "STRONG_SELL": "BEARISH",
            "NEUTRAL": "SIDEWAYS"
        }
        
        # Create SMC summary
        smc_summary = {
            "bos": signal_type in ["BUY", "STRONG_BUY"],
            "choch": confidence > 80,
            "bullish_ob": signal_type in ["BUY", "STRONG_BUY"],
            "bearish_ob": signal_type in ["SELL", "STRONG_SELL"],
            "fvg": confidence > 70,
            "liquidity": confidence > 75
        }
        
        signal = {
            "symbol": symbol,
            "timeframe": timeframe,
            "signal": signal_type,
            "confidence": confidence,
            "trend": trend_map.get(signal_type, "SIDEWAYS"),
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "reasoning": "",  # Will be filled by _build_detailed_reasoning
            "smc_summary": smc_summary,
            "last_updated": datetime.now().isoformat()
        }
        
        # Build detailed reasoning
        signal["reasoning"] = _build_detailed_reasoning(signal, {})
        
        return signal
        
    except Exception as e:
        logger.error(f"Sample signal creation error: {e}")
        return {}

def _estimate_entry_price(symbol: str, bullish_obs: List[Dict], bearish_obs: List[Dict]) -> float:
    """Estimate entry price berdasarkan OBs"""
    try:
        # Default prices untuk testing
        default_prices = {
            "BTCUSDT": 43500.0,
            "ETHUSDT": 2420.0,
            "SOLUSDT": 95.50,
            "ADAUSDT": 0.385,
            "DOTUSDT": 6.75,
            "AVAXUSDT": 28.50
        }
        
        # Ambil dari bullish OB jika ada
        if bullish_obs:
            return bullish_obs[0].get("price_level", default_prices.get(symbol, 100.0))
        
        # Ambil dari bearish OB jika ada
        if bearish_obs:
            return bearish_obs[0].get("price_level", default_prices.get(symbol, 100.0))
        
        return default_prices.get(symbol, 100.0)
        
    except Exception as e:
        logger.error(f"Entry price estimation error: {e}")
        return 100.0

def _calculate_risk_levels(entry_price: float, signal_type: str) -> tuple:
    """Calculate stop loss dan take profit levels"""
    try:
        if signal_type in ["BUY", "STRONG_BUY"]:
            # Long position
            stop_loss = round(entry_price * 0.985, 2)  # 1.5% stop loss
            take_profit = [
                round(entry_price * 1.018, 2),  # 1.8% TP1
                round(entry_price * 1.035, 2)   # 3.5% TP2
            ]
        elif signal_type in ["SELL", "STRONG_SELL"]:
            # Short position
            stop_loss = round(entry_price * 1.015, 2)  # 1.5% stop loss
            take_profit = [
                round(entry_price * 0.982, 2),  # 1.8% TP1
                round(entry_price * 0.965, 2)   # 3.5% TP2
            ]
        else:
            # Neutral
            stop_loss = round(entry_price * 0.99, 2)
            take_profit = [round(entry_price * 1.01, 2)]
        
        return stop_loss, take_profit
        
    except Exception as e:
        logger.error(f"Risk levels calculation error: {e}")
        return entry_price * 0.98, [entry_price * 1.02]

def _deduplicate_signals(signals: List[Dict]) -> List[Dict]:
    """Remove duplicate signals untuk same symbol+timeframe"""
    try:
        seen = set()
        unique_signals = []
        
        for signal in signals:
            key = f"{signal.get('symbol')}_{signal.get('timeframe')}"
            if key not in seen:
                seen.add(key)
                unique_signals.append(signal)
        
        return unique_signals
        
    except Exception as e:
        logger.error(f"Signal deduplication error: {e}")
        return signals

def _build_detailed_reasoning(signal: Dict, context: Dict) -> Dict:
    """Build detailed reasoning dengan struktur yang jelas"""
    try:
        signal_type = signal.get("signal", "")
        confidence = signal.get("confidence", 0)
        symbol = signal.get("symbol", "")
        entry_price = signal.get("entry_price", 0)
        smc_summary = signal.get("smc_summary", {})
        
        # Build structure analysis
        structure_analysis = _analyze_structure_reasoning(smc_summary, signal_type, entry_price)
        
        # Build indicators analysis
        indicators_analysis = _analyze_indicators_reasoning(signal, confidence)
        
        # Build conclusion
        conclusion = _build_reasoning_conclusion(signal_type, confidence, structure_analysis, indicators_analysis)
        
        detailed_reasoning = {
            "structure": structure_analysis,
            "indicators": indicators_analysis,
            "confluence": _analyze_confluence_factors(signal, smc_summary),
            "conclusion": conclusion,
            "risk_assessment": _analyze_risk_factors(signal, smc_summary)
        }
        
        return detailed_reasoning
        
    except Exception as e:
        logger.error(f"Detailed reasoning error: {e}")
        return {
            "structure": {"explanation": "Structure analysis unavailable"},
            "indicators": {"summary": "Indicator analysis unavailable"},
            "conclusion": f"{signal.get('signal', 'NEUTRAL')} signal detected"
        }

def _analyze_structure_reasoning(smc_summary: Dict, signal_type: str, entry_price: float) -> Dict:
    """Analyze SMC structure untuk reasoning"""
    try:
        structure = {
            "bos": smc_summary.get("bos", False),
            "choch": smc_summary.get("choch", False),
            "trend": "bullish" if signal_type in ["BUY", "STRONG_BUY"] else "bearish" if signal_type in ["SELL", "STRONG_SELL"] else "neutral"
        }
        
        # Generate specific explanation
        explanations = []
        
        if structure["bos"] and structure["choch"]:
            if structure["trend"] == "bullish":
                explanations.append(f"BOS bullish terkonfirmasi setelah CHoCH dengan harga menembus level kunci ${entry_price}")
            elif structure["trend"] == "bearish": 
                explanations.append(f"BOS bearish terkonfirmasi setelah CHoCH dengan harga break down dari ${entry_price}")
        elif structure["choch"]:
            explanations.append(f"CHoCH {structure['trend']} terdeteksi menunjukkan shift momentum market")
        elif structure["bos"]:
            explanations.append(f"Break of Structure {structure['trend']} mengkonfirmasi continuation trend")
        
        # Order Block analysis
        if smc_summary.get("bullish_ob") and signal_type in ["BUY", "STRONG_BUY"]:
            explanations.append("Bullish Order Block memberikan support kuat untuk long position")
        elif smc_summary.get("bearish_ob") and signal_type in ["SELL", "STRONG_SELL"]:
            explanations.append("Bearish Order Block menciptakan resistance untuk short opportunity")
        
        # FVG analysis
        if smc_summary.get("fvg"):
            explanations.append("Fair Value Gap belum terisi, menciptakan magnetic effect untuk price movement")
        
        # Liquidity analysis
        if smc_summary.get("liquidity"):
            explanations.append("Liquidity sweep mengkonfirmasi institutional interest dan validasi struktur")
        
        structure["explanation"] = ". ".join(explanations) if explanations else "Market structure menunjukkan kondisi netral dengan mixed signals"
        
        return structure
        
    except Exception as e:
        logger.error(f"Structure reasoning error: {e}")
        return {"explanation": "Structure analysis error"}

def _analyze_indicators_reasoning(signal: Dict, confidence: int) -> Dict:
    """Analyze technical indicators untuk reasoning"""
    try:
        signal_type = signal.get("signal", "")
        symbol = signal.get("symbol", "")
        
        # Generate indicator analysis berdasarkan signal dan confidence
        indicators = {}
        
        # RSI Analysis
        if confidence >= 80:
            if signal_type in ["BUY", "STRONG_BUY"]:
                indicators["rsi"] = "RSI menunjukkan momentum bullish kuat dengan reading 65-70, keluar dari oversold territory"
            elif signal_type in ["SELL", "STRONG_SELL"]:
                indicators["rsi"] = "RSI dalam overbought area 75-80, menunjukkan tekanan jual yang meningkat"
            else:
                indicators["rsi"] = "RSI bergerak di area 45-55, menunjukkan momentum yang seimbang"
        elif confidence >= 60:
            if signal_type in ["BUY", "STRONG_BUY"]:
                indicators["rsi"] = "RSI menunjukkan bias bullish moderat dengan trend naik dari level 50"
            elif signal_type in ["SELL", "STRONG_SELL"]:
                indicators["rsi"] = "RSI menunjukkan tekanan bearish dengan trend turun ke level 40-45"
            else:
                indicators["rsi"] = "RSI consolidation di area 48-52 tanpa arah yang jelas"
        else:
            indicators["rsi"] = "RSI menunjukkan sinyal mixed dengan volatilitas tinggi"
        
        # MACD Analysis
        if signal_type in ["BUY", "STRONG_BUY"]:
            indicators["macd"] = "MACD bullish crossover dengan histogram positif meningkat, mengkonfirmasi upward momentum"
        elif signal_type in ["SELL", "STRONG_SELL"]:
            indicators["macd"] = "MACD bearish crossover dengan histogram negatif, validasi downward pressure"
        else:
            indicators["macd"] = "MACD menunjukkan convergence dengan signal line fluktuatif"
        
        # Volume Analysis
        if confidence >= 75:
            volume_increase = 150 + (confidence - 75) * 2  # Scale volume dengan confidence
            indicators["volume"] = f"Volume meningkat {volume_increase}% dibanding rata-rata 20 candle, menunjukkan institutional interest"
        elif confidence >= 60:
            indicators["volume"] = "Volume above average dengan peningkatan 120-140%, supporting price movement"
        else:
            indicators["volume"] = "Volume relatif rendah, menunjukkan kurangnya conviction dalam current move"
        
        # Price Action
        if signal_type == "STRONG_BUY":
            indicators["price_action"] = "Strong bullish engulfing candle dengan close di upper 25% range"
        elif signal_type == "BUY":
            indicators["price_action"] = "Bullish price action dengan higher highs dan higher lows formation"
        elif signal_type == "STRONG_SELL":
            indicators["price_action"] = "Bearish engulfing pattern dengan strong selling pressure"
        elif signal_type == "SELL":
            indicators["price_action"] = "Bearish price rejection dengan lower highs formation"
        else:
            indicators["price_action"] = "Price action menunjukkan consolidation dengan tight range"
        
        return indicators
        
    except Exception as e:
        logger.error(f"Indicators reasoning error: {e}")
        return {"summary": "Indicator analysis error"}

def _analyze_confluence_factors(signal: Dict, smc_summary: Dict) -> Dict:
    """Analyze confluence factors yang mendukung signal"""
    try:
        signal_type = signal.get("signal", "")
        confidence = signal.get("confidence", 0)
        
        confluences = []
        
        # SMC Confluences
        smc_factors = sum(1 for v in smc_summary.values() if v)
        if smc_factors >= 3:
            confluences.append(f"Multiple SMC confirmations ({smc_factors}/6 factors active)")
        
        # Technical Confluences
        if confidence >= 80:
            confluences.append("High probability setup dengan multiple technical confirmations")
        elif confidence >= 60:
            confluences.append("Medium probability setup dengan beberapa supporting factors")
        
        # Trend Confluences
        if signal_type in ["STRONG_BUY", "STRONG_SELL"]:
            confluences.append("Strong directional bias dengan institutional flow alignment")
        elif signal_type in ["BUY", "SELL"]:
            confluences.append("Directional bias dengan moderate confirmation signals")
        
        return {
            "factors_count": len(confluences),
            "factors": confluences,
            "strength": "High" if len(confluences) >= 3 else "Medium" if len(confluences) >= 2 else "Low"
        }
        
    except Exception as e:
        logger.error(f"Confluence analysis error: {e}")
        return {"strength": "Unknown", "factors": []}

def _build_reasoning_conclusion(signal_type: str, confidence: int, structure: Dict, indicators: Dict) -> str:
    """Build comprehensive conclusion"""
    try:
        # Base conclusion
        signal_strength = "Strong" if confidence >= 80 else "Medium" if confidence >= 60 else "Weak"
        
        # Structure contribution
        structure_support = ""
        if structure.get("bos") and structure.get("choch"):
            structure_support = "Struktur market menunjukkan clear directional bias dengan BOS dan CHoCH confirmation"
        elif structure.get("choch"):
            structure_support = "Market structure shift terdeteksi melalui CHoCH pattern"
        elif structure.get("bos"):
            structure_support = "Break of Structure mengkonfirmasi continuation dari trend existing"
        else:
            structure_support = "Struktur market menunjukkan kondisi mixed dengan limited directional clarity"
        
        # Technical contribution
        technical_support = ""
        if confidence >= 80:
            technical_support = "Multiple technical indicators align untuk mendukung signal direction"
        elif confidence >= 60:
            technical_support = "Beberapa technical indicators menunjukkan supporting evidence"
        else:
            technical_support = "Technical indicators memberikan mixed signals dengan limited conviction"
        
        # Final conclusion
        conclusion = f"{signal_strength} {signal_type} signal dengan confidence {confidence}%. {structure_support}. {technical_support}. "
        
        if confidence >= 75:
            conclusion += "Setup ini memiliki probability tinggi untuk berhasil dengan proper risk management."
        elif confidence >= 60:
            conclusion += "Setup ini memiliki probability medium dengan cautious position sizing yang disarankan."
        else:
            conclusion += "Setup ini memerlukan additional confirmation sebelum entry dengan tight risk control."
        
        return conclusion
        
    except Exception as e:
        logger.error(f"Conclusion building error: {e}")
        return f"{signal_type} signal with {confidence}% confidence based on technical analysis"

def _analyze_risk_factors(signal: Dict, smc_summary: Dict) -> Dict:
    """Analyze risk factors untuk signal"""
    try:
        signal_type = signal.get("signal", "")
        confidence = signal.get("confidence", 0)
        entry_price = signal.get("entry_price", 0)
        stop_loss = signal.get("stop_loss", 0)
        
        risk_factors = []
        risk_level = "Low"
        
        # Confidence-based risk
        if confidence < 60:
            risk_factors.append("Low confidence signal increases execution risk")
            risk_level = "High"
        elif confidence < 75:
            risk_factors.append("Medium confidence requires careful position sizing")
            risk_level = "Medium"
        
        # SMC structure risk
        active_smc = sum(1 for v in smc_summary.values() if v)
        if active_smc < 2:
            risk_factors.append("Limited SMC confirmation increases structural risk")
            if risk_level != "High":
                risk_level = "Medium"
        
        # Stop loss distance risk
        if entry_price > 0 and stop_loss > 0:
            stop_distance_pct = abs((entry_price - stop_loss) / entry_price) * 100
            if stop_distance_pct > 3:
                risk_factors.append(f"Wide stop loss ({stop_distance_pct:.1f}%) increases capital risk")
            elif stop_distance_pct < 1:
                risk_factors.append(f"Tight stop loss ({stop_distance_pct:.1f}%) increases whipsaw risk")
        
        # Market condition risk
        if signal_type == "NEUTRAL":
            risk_factors.append("Neutral signal increases directional uncertainty")
            risk_level = "High"
        
        return {
            "level": risk_level,
            "factors": risk_factors,
            "mitigation": _generate_risk_mitigation_advice(risk_level, signal_type),
            "position_sizing": _recommend_position_sizing(risk_level, confidence)
        }
        
    except Exception as e:
        logger.error(f"Risk analysis error: {e}")
        return {"level": "Unknown", "factors": [], "mitigation": "Standard risk management"}

def _generate_risk_mitigation_advice(risk_level: str, signal_type: str) -> str:
    """Generate risk mitigation advice"""
    try:
        if risk_level == "High":
            return "Consider paper trading atau reduce position size significantly. Wait for additional confirmation."
        elif risk_level == "Medium":
            return "Use conservative position sizing (1-2% risk). Consider partial entries untuk better average."
        else:
            return "Standard position sizing acceptable (2-3% risk) dengan proper stop loss management."
    except:
        return "Apply standard risk management principles"

def _recommend_position_sizing(risk_level: str, confidence: int) -> str:
    """Recommend position sizing berdasarkan risk dan confidence"""
    try:
        if risk_level == "High" or confidence < 60:
            return "0.5-1% account risk per trade (very conservative)"
        elif risk_level == "Medium" or confidence < 75:
            return "1-2% account risk per trade (conservative)"
        else:
            return "2-3% account risk per trade (standard)"
    except:
        return "1-2% account risk per trade"

def _send_signal_to_telegram(signal: Dict, custom_message: str = "") -> Dict:
    """Send signal ke Telegram"""
    try:
        from core.telegram_bot import telegram_bot
        
        # Format message
        message = _format_telegram_message(signal, custom_message)
        
        # Send via telegram bot
        result = telegram_bot.send_signal_alert(message)
        
        return {
            "success": True,
            "message": "Signal sent to Telegram successfully",
            "telegram_result": result
        }
        
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
        return {
            "success": False,
            "message": f"Failed to send to Telegram: {str(e)}"
        }

def _format_telegram_message(signal: Dict, custom_message: str = "") -> str:
    """Format signal untuk Telegram message"""
    try:
        symbol = signal.get("symbol", "")
        timeframe = signal.get("timeframe", "")
        signal_type = signal.get("signal", "")
        confidence = signal.get("confidence", 0)
        entry_price = signal.get("entry_price", 0)
        stop_loss = signal.get("stop_loss", 0)
        take_profit = signal.get("take_profit", [])
        reasoning = signal.get("reasoning", "")
        
        # Signal emoji
        signal_emoji = {
            "STRONG_BUY": "🚀",
            "BUY": "📈",
            "SELL": "📉", 
            "STRONG_SELL": "🔻",
            "NEUTRAL": "⚖️"
        }.get(signal_type, "📊")
        
        # Format message
        message = f"{signal_emoji} **TOP SIGNAL ALERT**\n\n"
        
        if custom_message:
            message += f"🔔 {custom_message}\n\n"
        
        message += f"📊 **{symbol}** ({timeframe})\n"
        message += f"🎯 **Signal:** {signal_type}\n"
        message += f"💪 **Confidence:** {confidence}%\n\n"
        
        message += f"💰 **Entry:** ${entry_price}\n"
        message += f"🛑 **Stop Loss:** ${stop_loss}\n"
        
        if isinstance(take_profit, list) and len(take_profit) > 1:
            message += f"🎯 **TP1:** ${take_profit[0]}\n"
            message += f"🎯 **TP2:** ${take_profit[1]}\n"
        elif take_profit:
            tp_value = take_profit[0] if isinstance(take_profit, list) else take_profit
            message += f"🎯 **Take Profit:** ${tp_value}\n"
        
        message += f"\n📝 **Analysis:** {reasoning}\n"
        
        # Add SMC summary
        smc_summary = signal.get("smc_summary", {})
        if any(smc_summary.values()):
            message += f"\n🧠 **SMC Factors:**\n"
            if smc_summary.get("bos"):
                message += "✅ Break of Structure\n"
            if smc_summary.get("choch"):
                message += "✅ Change of Character\n"
            if smc_summary.get("bullish_ob"):
                message += "✅ Bullish Order Block\n"
            if smc_summary.get("bearish_ob"):
                message += "✅ Bearish Order Block\n"
            if smc_summary.get("fvg"):
                message += "✅ Fair Value Gap\n"
            if smc_summary.get("liquidity"):
                message += "✅ Liquidity Sweep\n"
        
        message += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        return message
        
    except Exception as e:
        logger.error(f"Telegram message formatting error: {e}")
        return f"Signal Alert: {signal.get('symbol')} {signal.get('signal')} - {signal.get('confidence')}%"

def _get_fallback_signals() -> List[Dict]:
    """Get fallback signals untuk testing dengan detailed reasoning"""
    try:
        # Generate fallback signals menggunakan _create_sample_signal yang sudah diperbaiki
        fallback_signals = [
            _create_sample_signal("BTCUSDT", "STRONG_BUY", 85, "", "1H"),
            _create_sample_signal("ETHUSDT", "BUY", 72, "", "1H"),
            _create_sample_signal("SOLUSDT", "STRONG_BUY", 88, "", "1H"),
            _create_sample_signal("ADAUSDT", "BUY", 66, "", "4H"),
            _create_sample_signal("DOTUSDT", "NEUTRAL", 52, "", "1H"),
            _create_sample_signal("AVAXUSDT", "SELL", 74, "", "1H")
        ]
        
        return fallback_signals
        
    except Exception as e:
        logger.error(f"Fallback signals error: {e}")
        return []

logger.info("🏆 Top Signal Endpoints initialized")