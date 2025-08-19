#!/usr/bin/env python3
"""
Data Quality Enhancement API Endpoints
Real-time data quality monitoring, anomaly detection, dan multi-source management
"""

from flask import Blueprint, jsonify, request
import logging
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

# Import our new data quality components
from core.market_anomaly_detector import get_market_anomaly_detector
from core.multi_source_data_manager import get_multi_source_data_manager, DataSource
from core.historical_data_completeness_checker import get_historical_data_checker
from core.okx_fetcher import OKXFetcher
from core.enhanced_okx_fetcher import EnhancedOKXFetcher

logger = logging.getLogger(__name__)

# Create blueprint
data_quality_bp = Blueprint('data_quality', __name__, url_prefix='/api/data-quality')

# Initialize components
anomaly_detector = get_market_anomaly_detector()
multi_source_manager = get_multi_source_data_manager()
data_completeness_checker = get_historical_data_checker()
okx_fetcher = OKXFetcher()

@data_quality_bp.route('/status', methods=['GET'])
def get_data_quality_status():
    """
    Status overview semua komponen data quality
    """
    try:
        # Test semua data sources
        source_status = multi_source_manager.get_all_sources_status()
        
        # Get recent anomalies summary
        anomaly_summary = anomaly_detector.get_anomaly_summary(hours=1)
        
        # Get completeness summary
        completeness_summary = data_completeness_checker.get_completeness_summary(days=1)
        
        # Overall health score
        total_sources = len(source_status)
        available_sources = sum(1 for status in source_status.values() if status.is_available)
        source_availability = (available_sources / total_sources * 100) if total_sources > 0 else 0
        
        # Calculate overall score
        overall_score = (
            source_availability * 0.4 +  # 40% source availability
            (100 - min(20, anomaly_summary.get('total_anomalies', 0))) * 0.3 +  # 30% anomaly score
            completeness_summary.get('overall_stats', {}).get('avg_quality', 100) * 0.3  # 30% completeness
        )
        
        return jsonify({
            "status": "active",
            "timestamp": time.time(),
            "overall_score": round(overall_score, 1),
            "components": {
                "anomaly_detector": "operational",
                "multi_source_manager": "operational", 
                "completeness_checker": "operational"
            },
            "data_sources": {
                source.lower(): {
                    "available": status.is_available,
                    "latency_ms": round(status.latency_ms, 1),
                    "quality_score": round(status.quality_score, 1),
                    "error_rate": round(status.error_rate * 100, 1)
                } for source, status in source_status.items()
            },
            "anomaly_summary": {
                "total_recent": anomaly_summary.get('total_anomalies', 0),
                "by_severity": anomaly_summary.get('by_severity', {}),
                "most_recent": anomaly_summary.get('most_recent')
            },
            "data_completeness": {
                "avg_completeness": round(completeness_summary.get('overall_stats', {}).get('avg_completeness', 0), 1),
                "avg_quality": round(completeness_summary.get('overall_stats', {}).get('avg_quality', 0), 1),
                "total_reports": completeness_summary.get('overall_stats', {}).get('total_reports', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting data quality status: {e}")
        return jsonify({"error": str(e)}), 500

@data_quality_bp.route('/anomalies/detect', methods=['POST'])
def detect_real_time_anomalies():
    """
    Real-time anomaly detection untuk market data
    """
    try:
        data = request.get_json()
        symbol = data.get('symbol', 'BTC-USDT')
        
        # Normalize symbol
        if not symbol.endswith('-USDT'):
            symbol = f"{symbol.replace('USDT', '')}-USDT"
        
        # Get fresh market data dari multiple sources
        market_data_response = multi_source_manager.get_market_data(symbol, 'ticker')
        
        if not market_data_response:
            return jsonify({
                "error": "Unable to fetch market data from any source",
                "symbol": symbol
            }), 400
        
        # Get additional data untuk comprehensive analysis
        enhanced_data = {}
        try:
            # Get OHLCV data
            kline_response = multi_source_manager.get_market_data(symbol, 'kline')
            if kline_response:
                enhanced_data['ohlcv'] = kline_response.data.get('candles', [])
            
            # Get orderbook data
            orderbook_response = multi_source_manager.get_market_data(symbol, 'orderbook')
            if orderbook_response:
                enhanced_data['orderbook'] = orderbook_response.data
            
            # Get liquidation data if available (from enhanced OKX fetcher)
            try:
                enhanced_okx = EnhancedOKXFetcher()
                if hasattr(enhanced_okx, 'get_liquidation_orders'):
                    liquidations = enhanced_okx.get_liquidation_orders()
                    if liquidations:
                        enhanced_data['liquidations'] = liquidations
            except:
                pass  # Liquidation data is optional
            
        except Exception as e:
            logger.warning(f"Could not fetch enhanced data: {e}")
        
        # Combine all market data
        combined_data = market_data_response.data.copy()
        combined_data.update(enhanced_data)
        
        # Detect anomalies
        anomaly_alerts = anomaly_detector.detect_real_time_anomalies(combined_data, symbol)
        
        # Get market health score
        health_score = anomaly_detector.get_market_health_score(symbol)
        
        return jsonify({
            "symbol": symbol,
            "timestamp": time.time(),
            "data_source": market_data_response.source.value,
            "data_quality_score": market_data_response.quality_score,
            "market_health": health_score,
            "anomalies_detected": len(anomaly_alerts),
            "anomalies": [
                {
                    "type": alert.anomaly_type.value,
                    "severity": alert.severity,
                    "confidence": alert.confidence,
                    "description": alert.description,
                    "metrics": alert.metrics,
                    "recommended_action": alert.recommended_action,
                    "timestamp": alert.timestamp
                } for alert in anomaly_alerts
            ],
            "market_data": {
                "price": combined_data.get('price', 0),
                "volume": combined_data.get('volume', 0),
                "change_24h_percentage": combined_data.get('change_24h_percentage', 0)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in real-time anomaly detection: {e}")
        return jsonify({"error": str(e)}), 500

@data_quality_bp.route('/sources/status', methods=['GET'])
def get_sources_status():
    """
    Status detail semua data sources
    """
    try:
        # Get current status
        sources_status = multi_source_manager.get_all_sources_status()
        
        # Test dengan sample symbol
        test_symbol = request.args.get('test_symbol', 'BTC-USDT')
        test_results = multi_source_manager.test_all_sources(test_symbol)
        
        return jsonify({
            "timestamp": time.time(),
            "test_symbol": test_symbol,
            "sources": {
                source: {
                    "status": status.is_available,
                    "latency_ms": round(status.latency_ms, 1),
                    "error_rate_percentage": round(status.error_rate * 100, 1),
                    "quality_score": round(status.quality_score, 1),
                    "last_successful_call": status.last_successful_call,
                    "test_result": test_results.get(source, {})
                } for source, status in sources_status.items()
            },
            "recommendations": [
                f"Primary source: {multi_source_manager.primary_source.value}",
                "Backup sources available" if len([s for s in sources_status.values() if s.is_available]) > 1 else "⚠️ Limited backup sources",
                "All sources operational" if all(s.is_available for s in sources_status.values()) else "Some sources experiencing issues"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting sources status: {e}")
        return jsonify({"error": str(e)}), 500

@data_quality_bp.route('/sources/test', methods=['POST'])
def test_data_sources():
    """
    Test semua data sources dengan symbol spesifik
    """
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTC-USDT')
        data_type = data.get('data_type', 'ticker')  # ticker, kline, orderbook
        
        # Test individual sources
        test_results = {}
        
        for source in DataSource:
            try:
                start_time = time.time()
                result = multi_source_manager.get_market_data(symbol, data_type, force_source=source)
                end_time = time.time()
                
                if result:
                    test_results[source.value] = {
                        "status": "success",
                        "latency_ms": round((end_time - start_time) * 1000, 1),
                        "data_quality_score": result.quality_score,
                        "data_available": bool(result.data),
                        "sample_data": {
                            "price": result.data.get('price'),
                            "volume": result.data.get('volume'),
                            "timestamp": result.data.get('timestamp')
                        }
                    }
                else:
                    test_results[source.value] = {
                        "status": "failed",
                        "latency_ms": round((end_time - start_time) * 1000, 1),
                        "error": "No data returned"
                    }
                    
            except Exception as e:
                test_results[source.value] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Summary
        successful_sources = [source for source, result in test_results.items() 
                            if result.get('status') == 'success']
        
        return jsonify({
            "test_symbol": symbol,
            "data_type": data_type,
            "timestamp": time.time(),
            "summary": {
                "total_sources": len(test_results),
                "successful_sources": len(successful_sources),
                "success_rate_percentage": round(len(successful_sources) / len(test_results) * 100, 1),
                "available_sources": successful_sources
            },
            "detailed_results": test_results,
            "recommendations": [
                "✅ Multiple sources available" if len(successful_sources) > 1 else "⚠️ Limited source availability",
                f"Primary source ({multi_source_manager.primary_source.value}) " + 
                ("operational" if multi_source_manager.primary_source.value in successful_sources else "experiencing issues"),
                "Backup sources available" if len(successful_sources) > 1 else "Consider implementing additional backup sources"
            ]
        })
        
    except Exception as e:
        logger.error(f"Error testing data sources: {e}")
        return jsonify({"error": str(e)}), 500

@data_quality_bp.route('/completeness/check', methods=['POST'])
def check_data_completeness():
    """
    Check historical data completeness untuk symbol tertentu
    """
    try:
        data = request.get_json() or {}
        symbol = data.get('symbol', 'BTC-USDT')
        timeframe = data.get('timeframe', '1h')
        days_back = data.get('days_back', 7)
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Check completeness
        report = data_completeness_checker.check_data_completeness(
            symbol, timeframe, start_date, end_date
        )
        
        return jsonify({
            "symbol": report.symbol,
            "timeframe": report.timeframe,
            "period": {
                "start_date": report.start_date.isoformat(),
                "end_date": report.end_date.isoformat(),
                "days": days_back
            },
            "completeness": {
                "percentage": round(report.completeness_percentage, 2),
                "expected_candles": report.total_expected_candles,
                "available_candles": report.available_candles,
                "missing_candles": report.missing_candles
            },
            "quality_score": round(report.quality_score, 1),
            "gaps": [
                {
                    "start_time": gap.start_time.isoformat(),
                    "end_time": gap.end_time.isoformat(),
                    "duration_minutes": gap.duration_minutes,
                    "severity": gap.severity.value,
                    "type": gap.gap_type
                } for gap in report.gaps
            ],
            "recommendations": report.recommendations,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error checking data completeness: {e}")
        return jsonify({"error": str(e)}), 500

@data_quality_bp.route('/completeness/summary', methods=['GET'])
def get_completeness_summary():
    """
    Get summary completeness untuk multiple symbols/timeframes
    """
    try:
        # Get query parameters
        symbol = request.args.get('symbol')
        timeframe = request.args.get('timeframe')
        days = int(request.args.get('days', 30))
        
        # Get summary (handle None values)
        summary = data_completeness_checker.get_completeness_summary(
            symbol=symbol if symbol else None, 
            timeframe=timeframe if timeframe else None, 
            days=days
        )
        
        return jsonify({
            "period_days": summary.get('period_days', days),
            "filters": {
                "symbol": symbol,
                "timeframe": timeframe
            },
            "overall_stats": summary.get('overall_stats', {}),
            "reports": summary.get('reports', []),
            "gap_summary": summary.get('gap_summary', {}),
            "recommendations": summary.get('recommendations', []),
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error getting completeness summary: {e}")
        return jsonify({"error": str(e)}), 500

@data_quality_bp.route('/enhanced-data/<symbol>', methods=['GET'])
def get_enhanced_market_data(symbol):
    """
    Get enhanced market data dengan quality validation
    """
    try:
        symbol = symbol.upper()
        
        # Normalize symbol format
        if not symbol.endswith('-USDT'):
            symbol = f"{symbol.replace('USDT', '')}-USDT"
        
        # Get data dari multiple sources
        ticker_data = multi_source_manager.get_market_data(symbol, 'ticker')
        kline_data = multi_source_manager.get_market_data(symbol, 'kline')
        orderbook_data = multi_source_manager.get_market_data(symbol, 'orderbook')
        
        if not ticker_data:
            return jsonify({
                "error": "Unable to fetch ticker data from any source",
                "symbol": symbol
            }), 400
        
        # Prepare response
        response_data = {
            "symbol": symbol,
            "timestamp": time.time(),
            "primary_source": ticker_data.source.value,
            "data_quality_score": ticker_data.quality_score,
            "ticker": ticker_data.data
        }
        
        # Add kline data jika available
        if kline_data:
            response_data["kline"] = {
                "source": kline_data.source.value,
                "quality_score": kline_data.quality_score,
                "data": kline_data.data
            }
        
        # Add orderbook data jika available
        if orderbook_data:
            response_data["orderbook"] = {
                "source": orderbook_data.source.value,
                "quality_score": orderbook_data.quality_score,
                "data": orderbook_data.data
            }
        
        # Detect anomalies in real-time
        combined_data = ticker_data.data.copy()
        if kline_data:
            combined_data.update(kline_data.data)
        
        anomalies = anomaly_detector.detect_real_time_anomalies(combined_data, symbol)
        
        if anomalies:
            response_data["anomalies"] = [
                {
                    "type": alert.anomaly_type.value,
                    "severity": alert.severity,
                    "description": alert.description
                } for alert in anomalies
            ]
        
        # Get market health score
        health_score = anomaly_detector.get_market_health_score(symbol)
        response_data["market_health"] = health_score
        
        return jsonify(response_data)
        
    except Exception as e:
        symbol_safe = symbol if 'symbol' in locals() else 'unknown'
        logger.error(f"Error getting enhanced market data for {symbol_safe}: {e}")
        return jsonify({"error": str(e)}), 500

@data_quality_bp.route('/monitor/dashboard', methods=['GET'])
def get_monitoring_dashboard():
    """
    Dashboard data untuk real-time monitoring
    """
    try:
        # Get popular symbols untuk monitoring
        symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'ADA-USDT']
        
        dashboard_data = {
            "timestamp": time.time(),
            "system_health": {},
            "data_sources": {},
            "anomalies": {},
            "quality_metrics": {}
        }
        
        # System health overview
        source_status = multi_source_manager.get_all_sources_status()
        available_sources = sum(1 for status in source_status.values() if status.is_available)
        total_sources = len(source_status)
        
        dashboard_data["system_health"] = {
            "overall_status": "healthy" if available_sources >= 2 else "degraded",
            "available_sources": available_sources,
            "total_sources": total_sources,
            "source_availability_percentage": round(available_sources / total_sources * 100, 1)
        }
        
        # Data sources performance
        dashboard_data["data_sources"] = {
            source: {
                "status": "online" if status.is_available else "offline",
                "latency_ms": round(status.latency_ms, 1),
                "quality_score": round(status.quality_score, 1)
            } for source, status in source_status.items()
        }
        
        # Recent anomalies across symbols
        recent_anomalies = []
        for symbol in symbols:
            try:
                # Get market data
                market_data = multi_source_manager.get_market_data(symbol, 'ticker')
                if market_data:
                    # Quick anomaly check
                    alerts = anomaly_detector.detect_real_time_anomalies(market_data.data, symbol)
                    for alert in alerts[-3:]:  # Last 3 alerts per symbol
                        recent_anomalies.append({
                            "symbol": symbol,
                            "type": alert.anomaly_type.value,
                            "severity": alert.severity,
                            "timestamp": alert.timestamp
                        })
            except:
                continue
        
        dashboard_data["anomalies"] = {
            "recent_count": len(recent_anomalies),
            "recent_alerts": recent_anomalies[-10:],  # Last 10 alerts
            "summary": anomaly_detector.get_anomaly_summary(hours=1)
        }
        
        # Quality metrics
        completeness_summary = data_completeness_checker.get_completeness_summary(days=1)
        dashboard_data["quality_metrics"] = {
            "avg_completeness": round(completeness_summary.get('overall_stats', {}).get('avg_completeness', 0), 1),
            "avg_quality_score": round(completeness_summary.get('overall_stats', {}).get('avg_quality', 0), 1),
            "total_gaps": sum(completeness_summary.get('gap_summary', {}).values())
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error generating monitoring dashboard: {e}")
        return jsonify({"error": str(e)}), 500

@data_quality_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check untuk data quality system
    """
    try:
        # Test core components
        tests = {
            "anomaly_detector": False,
            "multi_source_manager": False,
            "completeness_checker": False,
            "primary_data_source": False
        }
        
        # Test anomaly detector
        try:
            test_data = {"price": 50000, "volume": 1000, "timestamp": time.time()}
            anomaly_detector.detect_real_time_anomalies(test_data, "TEST-USDT")
            tests["anomaly_detector"] = True
        except:
            pass
        
        # Test multi-source manager
        try:
            status = multi_source_manager.get_all_sources_status()
            tests["multi_source_manager"] = len(status) > 0
        except:
            pass
        
        # Test completeness checker
        try:
            summary = data_completeness_checker.get_completeness_summary(days=1)
            tests["completeness_checker"] = 'overall_stats' in summary
        except:
            pass
        
        # Test primary data source
        try:
            result = multi_source_manager.get_market_data("BTC-USDT", "ticker")
            tests["primary_data_source"] = result is not None
        except:
            pass
        
        # Calculate health score
        passed_tests = sum(tests.values())
        total_tests = len(tests)
        health_score = (passed_tests / total_tests) * 100
        
        status = "healthy" if health_score >= 75 else "degraded" if health_score >= 50 else "critical"
        
        return jsonify({
            "status": status,
            "health_score": round(health_score, 1),
            "tests_passed": passed_tests,
            "total_tests": total_tests,
            "component_tests": tests,
            "timestamp": time.time()
        })
        
    except Exception as e:
        logger.error(f"Error in data quality health check: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }), 500

# Register blueprint (akan dilakukan di routes.py)
logger.info("🔍 Data Quality Enhancement API endpoints initialized")