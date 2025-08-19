#!/usr/bin/env python3
"""
ChatGPT Custom GPTs OpenAPI Schema - COMPLETE VERSION
Includes ALL available endpoints for maximum functionality
"""

import os
from flask import Blueprint, jsonify

# Create blueprint for OpenAPI schema
openapi_bp = Blueprint('openapi_complete', __name__)

def get_base_url():
    """Get the correct base URL for the API"""
    replit_url = os.environ.get('REPL_SLUG', 'crypto-analysis-dashboard')
    replit_owner = os.environ.get('REPL_OWNER', 'ricoz87')
    return f"https://{replit_url}.{replit_owner}.replit.dev"

@openapi_bp.route('/openapi.json')
def openapi_schema():
    """Complete OpenAPI 3.1.0 schema with ALL endpoints"""
    
    base_url = get_base_url()
    
    schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Cryptocurrency Trading Analysis API - Complete",
            "description": "Complete API for cryptocurrency trading analysis with Smart Money Concept, real-time OKX data, AI analysis, and comprehensive market intelligence",
            "version": "2.0.0"
        },
        "servers": [{"url": base_url, "description": "Production API Server"}],
        "paths": {
            # Core system endpoints
            "/health": {
                "get": {
                    "operationId": "getHealthCheck",
                    "summary": "Basic health check",
                    "description": "Check if API is responding and database is connected",
                    "responses": {"200": {"description": "Health status", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            "/api/gpts/status": {
                "get": {
                    "operationId": "getSystemStatus",
                    "summary": "Get detailed system status",
                    "description": "Complete system health with all components status",
                    "responses": {"200": {"description": "System status", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            # Quick trading signals
            "/api/gpts/signal": {
                "get": {
                    "operationId": "getTradingSignal",
                    "summary": "Get quick trading signal",
                    "description": "Fast trading signal with basic analysis",
                    "parameters": [
                        {"name": "symbol", "in": "query", "required": True, "schema": {"type": "string", "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]}},
                        {"name": "timeframe", "in": "query", "required": False, "schema": {"type": "string", "enum": ["15m", "1H", "4H", "1D"], "default": "1H"}}
                    ],
                    "responses": {"200": {"description": "Trading signal", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            # Advanced trading analysis
            "/api/gpts/sinyal/tajam": {
                "post": {
                    "operationId": "getDetailedAnalysis",
                    "summary": "Get detailed AI trading analysis",
                    "description": "Comprehensive SMC analysis with AI narrative in Indonesian",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["symbol", "timeframe"],
                                    "properties": {
                                        "symbol": {"type": "string", "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]},
                                        "timeframe": {"type": "string", "enum": ["15m", "1H", "4H", "1D"]}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {"200": {"description": "Detailed analysis", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            # Market data endpoints
            "/api/gpts/market-data": {
                "get": {
                    "operationId": "getMarketData",
                    "summary": "Get real-time market data",
                    "description": "Authentic OHLCV candles from OKX Exchange",
                    "parameters": [
                        {"name": "symbol", "in": "query", "required": True, "schema": {"type": "string", "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]}},
                        {"name": "timeframe", "in": "query", "required": False, "schema": {"type": "string", "enum": ["1H", "4H", "1D"], "default": "1H"}},
                        {"name": "limit", "in": "query", "required": False, "schema": {"type": "integer", "minimum": 1, "maximum": 300, "default": 100}}
                    ],
                    "responses": {"200": {"description": "Market data", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            "/api/gpts/ticker/{symbol}": {
                "get": {
                    "operationId": "getTicker",
                    "summary": "Get real-time ticker",
                    "description": "Current price and 24h statistics",
                    "parameters": [
                        {"name": "symbol", "in": "path", "required": True, "schema": {"type": "string", "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]}}
                    ],
                    "responses": {"200": {"description": "Ticker data", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            "/api/gpts/orderbook/{symbol}": {
                "get": {
                    "operationId": "getOrderbook",
                    "summary": "Get real-time orderbook",
                    "description": "Live order book depth from OKX (bids/asks)",
                    "parameters": [
                        {"name": "symbol", "in": "path", "required": True, "schema": {"type": "string", "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]}}
                    ],
                    "responses": {"200": {"description": "Orderbook data", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            # SMC Analysis endpoints
            "/api/gpts/smc-analysis": {
                "get": {
                    "operationId": "getSmcAnalysis",
                    "summary": "Get Smart Money Concept analysis",
                    "description": "Detailed SMC analysis with order blocks, FVG, liquidity sweeps",
                    "parameters": [
                        {"name": "symbol", "in": "query", "required": True, "schema": {"type": "string", "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]}},
                        {"name": "timeframe", "in": "query", "required": False, "schema": {"type": "string", "enum": ["15m", "1H", "4H", "1D"], "default": "1H"}}
                    ],
                    "responses": {"200": {"description": "SMC analysis", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            "/api/gpts/smc-zones/{symbol}": {
                "get": {
                    "operationId": "getSmcZonesBySymbol",
                    "summary": "Get SMC zones for specific symbol",
                    "description": "SMC zones data for chart visualization",
                    "parameters": [
                        {"name": "symbol", "in": "path", "required": True, "schema": {"type": "string", "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]}},
                        {"name": "timeframe", "in": "query", "required": False, "schema": {"type": "string", "enum": ["15m", "1H", "4H", "1D"], "default": "1H"}}
                    ],
                    "responses": {"200": {"description": "SMC zones", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            "/api/smc/zones": {
                "get": {
                    "operationId": "getSmcZones",
                    "summary": "Get SMC zones with filters",
                    "description": "SMC zones with filtering and proximity alerts",
                    "parameters": [
                        {"name": "symbol", "in": "query", "required": False, "schema": {"type": "string", "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]}},
                        {"name": "tf", "in": "query", "required": False, "schema": {"type": "string", "enum": ["15m", "1H", "4H", "1D"], "default": "1H"}}
                    ],
                    "responses": {"200": {"description": "Filtered SMC zones", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            # Additional services
            "/api/promptbook/": {
                "get": {
                    "operationId": "getPromptbook",
                    "summary": "Get AI prompt templates",
                    "description": "Collection of AI prompts for trading analysis",
                    "responses": {"200": {"description": "Prompt templates", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            "/api/performance/stats": {
                "get": {
                    "operationId": "getPerformanceStats",
                    "summary": "Get performance statistics",
                    "description": "Trading performance metrics and statistics",
                    "responses": {"200": {"description": "Performance stats", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            },
            
            "/api/news/status": {
                "get": {
                    "operationId": "getNewsStatus",
                    "summary": "Get crypto news analysis status",
                    "description": "Status of crypto news sentiment analysis system",
                    "responses": {"200": {"description": "News analysis status", "content": {"application/json": {"schema": {"type": "object"}}}}}
                }
            }
        }
    }
    
    return jsonify(schema)

@openapi_bp.route('/.well-known/openapi.json')
def well_known_openapi():
    return openapi_schema()

@openapi_bp.route('/api/docs')
def api_docs():
    return jsonify({
        "title": "Complete Cryptocurrency Trading API",
        "description": "Full-featured API with 12+ endpoints for comprehensive crypto analysis",
        "total_endpoints": 12,
        "openapi_schema": f"{get_base_url()}/openapi.json",
        "chatgpt_setup": {
            "import_url": f"{get_base_url()}/openapi.json",
            "description": "Complete schema with all available endpoints"
        },
        "categories": {
            "system": ["/health", "/api/gpts/status"],
            "trading_signals": ["/api/gpts/signal", "/api/gpts/sinyal/tajam"], 
            "market_data": ["/api/gpts/market-data", "/api/gpts/ticker/{symbol}", "/api/gpts/orderbook/{symbol}"],
            "smc_analysis": ["/api/gpts/smc-analysis", "/api/gpts/smc-zones/{symbol}", "/api/smc/zones"],
            "additional": ["/api/promptbook/", "/api/performance/stats", "/api/news/status"]
        }
    })