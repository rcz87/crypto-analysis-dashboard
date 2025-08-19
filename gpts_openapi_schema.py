#!/usr/bin/env python3
"""
ChatGPT Custom GPTs OpenAPI Schema Generator
Generates complete OpenAPI 3.1.0 schema for ChatGPT Actions integration
"""

import os
from flask import Blueprint, jsonify

# Create blueprint for OpenAPI schema
openapi_bp = Blueprint('openapi', __name__)

def get_base_url():
    """Get the correct base URL for the API"""
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
            "description": "Advanced cryptocurrency trading signals with Smart Money Concept (SMC) analysis, AI-powered insights, and real-time market data from OKX Exchange. Perfect for professional trading analysis and decision making.",
            "version": "2.0.0",
            "contact": {
                "name": "Crypto Trading API Support",
                "url": f"{base_url}/health"
            }
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
                    "description": "Check the health and status of all API services including database, OKX data, and AI analysis engines.",
                    "responses": {
                        "200": {
                            "description": "System status information",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "description": "Overall system status"},
                                            "components": {
                                                "type": "object",
                                                "description": "Status of individual components"
                                            },
                                            "timestamp": {"type": "integer", "description": "Unix timestamp"}
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
                    "description": "Get a fast trading signal for a cryptocurrency pair with basic analysis and recommendations.",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": true,
                            "schema": {
                                "type": "string",
                                "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT", "ADA-USDT", "DOT-USDT", "MATIC-USDT"],
                                "description": "Trading pair symbol"
                            },
                            "example": "BTC-USDT"
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "required": false,
                            "schema": {
                                "type": "string",
                                "enum": ["15m", "1H", "4H", "1D"],
                                "default": "1H"
                            },
                            "example": "1H"
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
                                                    "signal": {"type": "string", "enum": ["BUY", "SELL", "HOLD", "neutral"]},
                                                    "confidence": {"type": "number", "description": "Confidence level 0-100"},
                                                    "current_price": {"type": "number"},
                                                    "target_price": {"type": "number"},
                                                    "stop_loss": {"type": "number"},
                                                    "reasoning": {"type": "string", "description": "AI analysis reasoning"}
                                                }
                                            },
                                            "status": {"type": "string"},
                                            "timestamp": {"type": "integer"}
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
                    "operationId": "getDetailedTradingAnalysis",
                    "summary": "Get detailed AI trading analysis",
                    "description": "Get comprehensive trading analysis with Smart Money Concept (SMC) indicators, AI narrative, and detailed market structure analysis in Indonesian language.",
                    "requestBody": {
                        "required": true,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["symbol", "timeframe"],
                                    "properties": {
                                        "symbol": {
                                            "type": "string",
                                            "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT", "ADA-USDT", "DOT-USDT", "MATIC-USDT"],
                                            "description": "Trading pair symbol"
                                        },
                                        "timeframe": {
                                            "type": "string",
                                            "enum": ["15m", "1H", "4H", "1D"],
                                            "description": "Analysis timeframe"
                                        },
                                        "format": {
                                            "type": "string",
                                            "enum": ["json", "narrative", "both"],
                                            "default": "both",
                                            "description": "Response format type"
                                        }
                                    }
                                },
                                "example": {
                                    "symbol": "BTC-USDT",
                                    "timeframe": "1H",
                                    "format": "both"
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Detailed trading analysis with SMC and AI insights",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "signal": {
                                                "type": "object",
                                                "properties": {
                                                    "direction": {"type": "string"},
                                                    "confidence": {"type": "number"},
                                                    "entry_price": {"type": "number"},
                                                    "take_profit": {"type": "number"},
                                                    "stop_loss": {"type": "number"},
                                                    "reasoning": {"type": "string"}
                                                }
                                            },
                                            "analysis": {
                                                "type": "object",
                                                "properties": {
                                                    "smc": {"type": "object", "description": "Smart Money Concept analysis"},
                                                    "technical": {"type": "string", "description": "Technical analysis summary"},
                                                    "risk_reward": {"type": "number", "description": "Risk-reward ratio"}
                                                }
                                            },
                                            "market_data": {
                                                "type": "object",
                                                "description": "Current market data and candle analysis"
                                            },
                                            "narrative": {
                                                "type": "string",
                                                "description": "AI-generated trading narrative in Indonesian"
                                            }
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
                    "description": "Get authentic real-time market data including OHLCV candles from OKX Exchange.",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": true,
                            "schema": {
                                "type": "string",
                                "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT", "ADA-USDT", "DOT-USDT", "MATIC-USDT"]
                            }
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "required": false,
                            "schema": {
                                "type": "string",
                                "enum": ["1m", "5m", "15m", "30m", "1H", "4H", "1D"],
                                "default": "1H"
                            }
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": false,
                            "schema": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 1440,
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
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "candles": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "timestamp": {"type": "integer"},
                                                                "open": {"type": "number"},
                                                                "high": {"type": "number"},
                                                                "low": {"type": "number"},
                                                                "close": {"type": "number"},
                                                                "volume": {"type": "number"}
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
                    }
                }
            },
            "/api/gpts/smc-analysis": {
                "get": {
                    "operationId": "getSmcAnalysis",
                    "summary": "Get Smart Money Concept analysis",
                    "description": "Get detailed Smart Money Concept (SMC) analysis including order blocks, fair value gaps, liquidity sweeps, and market structure.",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": true,
                            "schema": {
                                "type": "string",
                                "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT", "ADA-USDT", "DOT-USDT", "MATIC-USDT"]
                            }
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "required": false,
                            "schema": {
                                "type": "string",
                                "enum": ["15m", "1H", "4H", "1D"],
                                "default": "1H"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "SMC analysis with structure and patterns",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "smc_analysis": {
                                                "type": "object",
                                                "properties": {
                                                    "market_bias": {"type": "string"},
                                                    "structure_analysis": {"type": "object"},
                                                    "order_blocks": {"type": "array"},
                                                    "fair_value_gaps": {"type": "array"},
                                                    "liquidity_analysis": {"type": "object"}
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
            "/api/gpts/ticker/{symbol}": {
                "get": {
                    "operationId": "getTicker",
                    "summary": "Get real-time ticker data",
                    "description": "Get real-time ticker information including current price, 24h volume, and price changes.",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "path",
                            "required": true,
                            "schema": {
                                "type": "string",
                                "enum": ["BTC-USDT", "ETH-USDT", "SOL-USDT", "AVAX-USDT", "BNB-USDT", "ADA-USDT", "DOT-USDT", "MATIC-USDT"]
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
                                            "ticker": {
                                                "type": "object",
                                                "properties": {
                                                    "symbol": {"type": "string"},
                                                    "last_price": {"type": "number"},
                                                    "bid_price": {"type": "number"},
                                                    "ask_price": {"type": "number"},
                                                    "volume_24h": {"type": "number"},
                                                    "change_24h": {"type": "number"},
                                                    "high_24h": {"type": "number"},
                                                    "low_24h": {"type": "number"}
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
        },
        "components": {
            "schemas": {
                "TradingSignal": {
                    "type": "object",
                    "properties": {
                        "signal": {"type": "string", "enum": ["BUY", "SELL", "HOLD", "neutral"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                        "reasoning": {"type": "string"}
                    }
                },
                "MarketData": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "current_price": {"type": "number"},
                        "volume": {"type": "number"},
                        "timestamp": {"type": "integer"}
                    }
                }
            }
        }
    }
    
    return jsonify(schema)

@openapi_bp.route('/.well-known/openapi.json')
def well_known_openapi():
    """Well-known OpenAPI endpoint for auto-discovery"""
    return openapi_schema()

@openapi_bp.route('/api/docs')
def api_docs():
    """API documentation endpoint"""
    return jsonify({
        "title": "Cryptocurrency Trading API Documentation",
        "description": "Complete API documentation for cryptocurrency trading analysis",
        "openapi_schema": f"{get_base_url()}/openapi.json",
        "endpoints": {
            "system_status": "/api/gpts/status",
            "quick_signal": "/api/gpts/signal",
            "detailed_analysis": "/api/gpts/sinyal/tajam",
            "market_data": "/api/gpts/market-data",
            "smc_analysis": "/api/gpts/smc-analysis",
            "ticker_data": "/api/gpts/ticker/{symbol}"
        },
        "chatgpt_setup": {
            "schema_url": f"{get_base_url()}/openapi.json",
            "description": "Import this OpenAPI schema into ChatGPT Custom GPT Actions"
        }
    })