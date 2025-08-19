#!/usr/bin/env python3
"""
ChatGPT Custom GPTs OpenAPI Schema - Simple and Working Version
"""

import os
from flask import Blueprint, jsonify

# Create blueprint for OpenAPI schema
openapi_bp = Blueprint('openapi_simple', __name__)

def get_base_url():
    """Get the correct base URL for the API"""
    # Try to get Replit URL from environment
    replit_url = os.environ.get('REPL_SLUG', 'crypto-analysis-dashboard')
    replit_owner = os.environ.get('REPL_OWNER', 'ricoz87')
    return f"https://{replit_url}.{replit_owner}.replit.dev"

@openapi_bp.route('/openapi.json')
def openapi_schema():
    """Complete OpenAPI 3.1.0 schema for ChatGPT Custom GPTs"""
    
    base_url = get_base_url()
    
    schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Cryptocurrency Trading Analysis API",
            "description": "Advanced cryptocurrency trading signals with Smart Money Concept analysis and real-time OKX data",
            "version": "2.0.0"
        },
        "servers": [
            {
                "url": base_url,
                "description": "Production API Server"
            }
        ],
        "paths": {
            "/api/gpts/status": {
                "get": {
                    "operationId": "getSystemStatus",
                    "summary": "Get API system status",
                    "description": "Check health and status of all API services",
                    "responses": {
                        "200": {
                            "description": "System status information",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "components": {"type": "object"},
                                            "timestamp": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/signal": {
                "get": {
                    "operationId": "getTradingSignal", 
                    "summary": "Get quick trading signal",
                    "description": "Get fast trading signal with basic analysis",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]
                            }
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["15m", "1H", "4H", "1D"],
                                "default": "1H"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Trading signal with analysis",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "signal": {
                                                "type": "object",
                                                "properties": {
                                                    "signal": {"type": "string"},
                                                    "confidence": {"type": "number"},
                                                    "current_price": {"type": "number"},
                                                    "reasoning": {"type": "string"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/sinyal/tajam": {
                "post": {
                    "operationId": "getDetailedAnalysis",
                    "summary": "Get detailed trading analysis",
                    "description": "Get comprehensive SMC analysis with AI narrative in Indonesian",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["symbol", "timeframe"],
                                    "properties": {
                                        "symbol": {
                                            "type": "string",
                                            "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]
                                        },
                                        "timeframe": {
                                            "type": "string",
                                            "enum": ["15m", "1H", "4H", "1D"]
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Detailed trading analysis",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "signal": {"type": "object"},
                                            "analysis": {"type": "object"},
                                            "narrative": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/market-data": {
                "get": {
                    "operationId": "getMarketData",
                    "summary": "Get real-time market data",
                    "description": "Get authentic OHLCV data from OKX Exchange",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]
                            }
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "string",
                                "enum": ["1H", "4H", "1D"],
                                "default": "1H"
                            }
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 300,
                                "default": 100
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Market data with OHLCV candles",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "data": {"type": "object"},
                                            "status": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/ticker/{symbol}": {
                "get": {
                    "operationId": "getTicker",
                    "summary": "Get real-time ticker data",
                    "description": "Get current price and 24h stats",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string",
                                "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT"]
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Real-time ticker data",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "ticker": {"type": "object"},
                                            "status": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    return jsonify(schema)

@openapi_bp.route('/.well-known/openapi.json')
def well_known_openapi():
    """Well-known OpenAPI endpoint"""
    return openapi_schema()

@openapi_bp.route('/api/docs')
def api_docs():
    """API documentation"""
    return jsonify({
        "title": "Cryptocurrency Trading API",
        "description": "Complete API for crypto trading analysis",
        "openapi_schema": f"{get_base_url()}/openapi.json",
        "chatgpt_setup": {
            "import_url": f"{get_base_url()}/openapi.json",
            "description": "Use this URL in ChatGPT Custom GPT Actions"
        }
    })