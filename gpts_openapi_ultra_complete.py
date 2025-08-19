"""
Ultra Complete OpenAPI Schema for ChatGPT Custom GPTs
Includes ALL discovered working endpoints (30+ operations)
"""

from flask import Blueprint, jsonify

openapi_bp = Blueprint('openapi_ultra', __name__)

# --- OpenAPI relaxer: tambahkan additionalProperties untuk semua response object yang kosong ---
def _relax_all_responses(schema: dict) -> dict:
    for path_item in schema.get("paths", {}).values():
        for mname, method in list(path_item.items()):
            if mname.lower() not in ("get", "post", "put", "delete", "patch", "options", "head"):
                continue
            for resp in method.get("responses", {}).values():
                cj = resp.setdefault("content", {}).setdefault("application/json", {})
                sch = cj.setdefault("schema", {"type": "object"})
                if isinstance(sch, dict) and sch.get("type") == "object" and not any(
                    k in sch for k in ("properties","additionalProperties","$ref","oneOf","anyOf","allOf")
                ):
                    sch["additionalProperties"] = True
    return schema

def _relax_responses(schema: dict) -> dict:
    """Add additionalProperties: True to bare object schemas - Legacy function"""
    return _relax_all_responses(schema)

def get_ultra_complete_openapi_schema():
    """Generate ultra-complete OpenAPI 3.1.0 schema for ALL available endpoints"""
    
    schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Cryptocurrency Trading Analysis API - Ultra Complete",
            "description": "Advanced institutional-grade cryptocurrency trading analysis with AI, SMC patterns, real-time data, and comprehensive market insights. Features 30+ endpoints for complete trading workflow automation.",
            "version": "3.0.0",
            "contact": {
                "name": "GPTs Trading API",
                "url": "https://gpts.guardiansofthetoken.id/openapi.json"
            }
        },
        "servers": [
            {
                "url": "https://gpts.guardiansofthetoken.id",
                "description": "Production API Server"
            }
        ],
        "paths": {
            # Core System Endpoints
            "/health": {
                "get": {
                    "operationId": "getHealthCheck",
                    "summary": "System Health Check", 
                    "description": "Basic system health and database connectivity check",
                    "responses": {
                        "200": {
                            "description": "System is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "healthy"},
                                            "database": {"type": "string", "example": "connected"},
                                            "version": {"type": "string", "example": "2.0.0"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/health": {
                "get": {
                    "operationId": "getHealth",
                    "summary": "System Health Check (alias)",
                    "description": "Alias for /health - System health and database connectivity check for GPTs",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/status": {
                "get": {
                    "operationId": "getSystemStatus",
                    "summary": "Complete System Status",
                    "description": "Detailed system status including all components and services",
                    "responses": {
                        "200": {
                            "description": "Complete system status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "system": {"type": "object", "additionalProperties": True},
                                            "components": {"type": "object", "additionalProperties": True},
                                            "health": {"type": "string", "example": "healthy"},
                                            "timestamp": {"type": "string", "example": "2025-08-19T10:30:00Z"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },
            
            # Trading Signal Endpoints
            "/api/gpts/signal": {
                "get": {
                    "operationId": "getTradingSignal",
                    "summary": "Get Trading Signal",
                    "description": "Generate AI-powered trading signals with SMC analysis",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query", 
                            "description": "Trading pair (e.g., BTC-USDT)",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "description": "Timeframe for analysis", 
                            "schema": {"type": "string", "default": "1H"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Trading signal generated",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "signal": {"type": "object", "additionalProperties": True},
                                            "status": {"type": "string", "example": "success"},
                                            "confidence": {"type": "number", "example": 75.5},
                                            "symbol": {"type": "string", "example": "BTC-USDT"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/sinyal/tajam": {
                "get": {
                    "operationId": "getSharpTradingSignal",
                    "summary": "Sharp Trading Signal",
                    "description": "Deep AI analysis with SMC, sentiment, and institutional insights",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "schema": {"type": "string", "default": "BTCUSDT"}
                        },
                        {
                            "name": "tf",
                            "in": "query",
                            "schema": {"type": "string", "default": "1h"}
                        },
                        {
                            "name": "format",
                            "in": "query",
                            "schema": {"type": "string", "enum": ["json", "narrative"], "default": "json"}
                        },
                        {
                            "name": "min_confidence",
                            "in": "query",
                            "schema": {"type": "number", "default": 70}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                },
                "post": {
                    "operationId": "getDetailedAnalysis", 
                    "summary": "Advanced Trading Analysis (POST)",
                    "description": "Deep AI analysis with SMC, sentiment, and institutional insights via POST method",
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "symbol": {"type": "string", "default": "BTC-USDT"},
                                        "timeframe": {"type": "string", "default": "1H"},
                                        "format": {"type": "string", "default": "json"},
                                        "min_confidence": {"type": "number", "default": 70}
                                    },
                                    "additionalProperties": True
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Detailed analysis completed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "analysis": {"type": "object", "additionalProperties": True},
                                            "confidence": {"type": "number", "example": 85.2},
                                            "signals": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
                                            "status": {"type": "string", "example": "success"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/signal/top": {
                "get": {
                    "operationId": "getTopSignals",
                    "summary": "Top Trading Signals",
                    "description": "Get highest confidence trading signals across multiple pairs",
                    "responses": {
                        "200": {
                            "description": "Top signals retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"signals": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "status": {"type": "string", "example": "success"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            
            # Market Data Endpoints
            "/api/gpts/market-data": {
                "get": {
                    "operationId": "getMarketData",
                    "summary": "OHLCV Market Data",
                    "description": "Real-time OHLCV candlestick data from OKX exchange",
                    "parameters": [
                        {
                            "name": "symbol", 
                            "in": "query",
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        },
                        {
                            "name": "timeframe",
                            "in": "query", 
                            "description": "Chart timeframe",
                            "schema": {"type": "string", "default": "1H"}
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "description": "Number of candles",
                            "schema": {"type": "integer", "default": 300}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Market data retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"data": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "symbol": {"type": "string"}, "timeframe": {"type": "string"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/ticker/{symbol}": {
                "get": {
                    "operationId": "getTicker",
                    "summary": "Real-time Price Ticker",
                    "description": "Current price and 24h statistics",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "path",
                            "required": True,
                            "description": "Trading pair symbol",
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Ticker data retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"ticker": {"type": "object", "additionalProperties": True}, "symbol": {"type": "string"}, "price": {"type": "number"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/orderbook/{symbol}": {
                "get": {
                    "operationId": "getOrderbook",
                    "summary": "Order Book Depth",
                    "description": "Real-time order book with bid/ask levels",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "path",
                            "required": True,
                            "description": "Trading pair symbol", 
                            "schema": {"type": "string"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Order book retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"orderbook": {"type": "object", "additionalProperties": True}, "symbol": {"type": "string"}, "depth": {"type": "integer"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            
            # SMC Analysis Endpoints
            "/api/gpts/smc-analysis": {
                "get": {
                    "operationId": "getSmcAnalysis",
                    "summary": "Smart Money Concept Analysis",
                    "description": "Professional SMC pattern analysis with CHoCH, BOS, Order Blocks",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        },
                        {
                            "name": "timeframe", 
                            "in": "query",
                            "description": "Analysis timeframe",
                            "schema": {"type": "string", "default": "1H"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "SMC analysis completed",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"smc_analysis": {"type": "object", "additionalProperties": True}, "patterns": {"type": "array", "items": {"type": "object", "additionalProperties": True}}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/smc-zones/{symbol}": {
                "get": {
                    "operationId": "getSmcZonesBySymbol", 
                    "summary": "SMC Zones by Symbol",
                    "description": "SMC zones and levels for specific trading pair",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "path",
                            "required": True,
                            "description": "Trading pair symbol",
                            "schema": {"type": "string"}
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "description": "Analysis timeframe",
                            "schema": {"type": "string", "default": "1H"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "SMC zones retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"zones": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "symbol": {"type": "string"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/smc/zones": {
                "get": {
                    "operationId": "getSmcZones",
                    "summary": "SMC Zones with Filters",
                    "description": "SMC zones with advanced filtering options",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        },
                        {
                            "name": "tf",
                            "in": "query", 
                            "description": "Timeframe",
                            "schema": {"type": "string", "default": "1H"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Filtered SMC zones",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"smc_zones": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "analysis": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/smc/orderblocks": {
                "get": {
                    "operationId": "getSmcOrderBlocks",
                    "summary": "SMC Order Blocks",
                    "description": "Smart Money Concept order block analysis",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Order blocks retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"orderblocks": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "timeframe": {"type": "string"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/smc/patterns/recognize": {
                "post": {
                    "operationId": "recognizeSmcPatterns",
                    "summary": "SMC Pattern Recognition",
                    "description": "AI-powered SMC pattern recognition and analysis",
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "symbol": {"type": "string", "default": "BTC-USDT"},
                                        "timeframe": {"type": "string", "default": "1H"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Pattern recognition completed",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"patterns": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "recognition_result": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            
            # Enhanced Analysis Endpoints
            "/api/gpts/analysis/deep": {
                "get": {
                    "operationId": "getDeepAnalysis",
                    "summary": "Deep Market Analysis",
                    "description": "Comprehensive multi-factor market analysis",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Deep analysis completed",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"analysis": {"type": "object", "additionalProperties": True}, "insights": {"type": "array", "items": {"type": "object", "additionalProperties": True}}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/sinyal/enhanced": {
                "post": {
                    "operationId": "getEnhancedSignal",
                    "summary": "Enhanced Trading Signal",
                    "description": "Advanced signal generation with enhanced AI analysis",
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "symbol": {"type": "string", "default": "BTC-USDT"},
                                        "timeframe": {"type": "string", "default": "1H"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Enhanced signal generated",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"signal": {"type": "object", "additionalProperties": True}, "enhanced_analysis": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/context/live": {
                "get": {
                    "operationId": "getLiveContext",
                    "summary": "Live Market Context",
                    "description": "Real-time market context and conditions",
                    "responses": {
                        "200": {
                            "description": "Live context retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"context": {"type": "object", "additionalProperties": True}, "live_data": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/alerts/status": {
                "get": {
                    "operationId": "getAlertsStatus",
                    "summary": "Alert System Status",
                    "description": "Current status of trading alert system",
                    "responses": {
                        "200": {
                            "description": "Alerts status retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"alerts": {"type": "object", "additionalProperties": True}, "status": {"type": "string", "example": "active"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            
            # Backtest Endpoints
            "/api/backtest": {
                "get": {
                    "operationId": "getBacktestResults",
                    "summary": "Backtest Results",
                    "description": "Historical strategy backtest results",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        },
                        {
                            "name": "strategy",
                            "in": "query",
                            "description": "Strategy name",
                            "schema": {"type": "string", "default": "RSI_MACD"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Backtest results retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"backtest_results": {"type": "object", "additionalProperties": True}, "performance": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                },
                "post": {
                    "operationId": "runBacktest",
                    "summary": "Run Backtest",
                    "description": "Execute strategy backtest on historical data",
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "symbol": {"type": "string", "default": "BTC-USDT"},
                                        "strategy": {"type": "string", "default": "RSI_MACD"},
                                        "timeframe": {"type": "string", "default": "1H"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Backtest completed",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/backtest/strategies": {
                "get": {
                    "operationId": "getBacktestStrategies",
                    "summary": "Available Strategies",
                    "description": "List all available backtest strategies",
                    "responses": {
                        "200": {
                            "description": "Strategies retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"strategies": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "count": {"type": "integer"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/backtest/quick": {
                "get": {
                    "operationId": "getQuickBacktest",
                    "summary": "Quick Backtest",
                    "description": "Fast backtest with default parameters",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query", 
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Quick backtest completed",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"quick_results": {"type": "object", "additionalProperties": True}, "summary": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            
            # Chart & Dashboard Endpoints
            "/widget": {
                "get": {
                    "operationId": "getTradingWidget",
                    "summary": "Trading Widget",
                    "description": "Interactive trading widget display",
                    "responses": {
                        "200": {
                            "description": "Widget displayed",
                            "content": {
                                "text/html": {
                                    "schema": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "/dashboard": {
                "get": {
                    "operationId": "getTradingDashboard",
                    "summary": "Trading Dashboard", 
                    "description": "Complete trading dashboard interface",
                    "responses": {
                        "200": {
                            "description": "Dashboard displayed",
                            "content": {
                                "text/html": {
                                    "schema": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            },
            "/data": {
                "get": {
                    "operationId": "getChartData",
                    "summary": "Chart Data",
                    "description": "Chart data for visualization",
                    "responses": {
                        "200": {
                            "description": "Chart data retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"widget_data": {"type": "object", "additionalProperties": True}, "config": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            
            # Additional Service Endpoints
            "/api/promptbook/": {
                "get": {
                    "operationId": "getPromptbook",
                    "summary": "AI Prompt Templates",
                    "description": "Collection of AI prompt templates for trading analysis",
                    "responses": {
                        "200": {
                            "description": "Prompt templates retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"prompts": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "templates": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/performance/stats": {
                "get": {
                    "operationId": "getPerformanceStats",
                    "summary": "Performance Statistics",
                    "description": "Trading performance metrics and statistics",
                    "responses": {
                        "200": {
                            "description": "Performance stats retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"performance": {"type": "object", "additionalProperties": True}, "stats": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/news/status": {
                "get": {
                    "operationId": "getNewsStatus",
                    "summary": "News Analysis Status",
                    "description": "Status of crypto news sentiment analysis",
                    "responses": {
                        "200": {
                            "description": "News status retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"news_service": {"type": "object", "additionalProperties": True}, "status": {"type": "string", "example": "operational"}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/signals/history": {
                "get": {
                    "operationId": "getSignalsHistory",
                    "summary": "Signals History",
                    "description": "Historical trading signals and outcomes",
                    "responses": {
                        "200": {
                            "description": "Signals history retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"history": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "pagination": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/telegram/status": {
                "get": {
                    "operationId": "getTelegramStatus",
                    "summary": "Telegram Integration Status",
                    "description": "Check Telegram bot integration status and connectivity",
                    "responses": {
                        "200": {
                            "description": "Telegram status retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/sharp-scoring/test": {
                "get": {
                    "operationId": "testSharpScoring",
                    "summary": "Sharp Scoring Test",
                    "description": "Test sharp scoring algorithm functionality",
                    "responses": {
                        "200": {
                            "description": "Sharp scoring test completed",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/webhooks/tradingview/test": {
                "post": {
                    "operationId": "postTradingViewTest",
                    "summary": "TradingView Webhook Test",
                    "description": "Test TradingView webhook integration",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "additionalProperties": True
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Webhook test completed",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    
    # Schema akan di-relax oleh handler endpoint, tidak perlu di sini
    return schema

@openapi_bp.route('/openapi.json')
def openapi_schema():
    """Main OpenAPI schema endpoint"""
    schema = get_ultra_complete_openapi_schema()
    schema = _relax_all_responses(schema)
    return jsonify(schema)

@openapi_bp.route('/.well-known/openapi.json') 
def well_known_openapi():
    """Well-known OpenAPI schema endpoint"""
    schema = get_ultra_complete_openapi_schema()
    schema = _relax_all_responses(schema)
    return jsonify(schema)

@openapi_bp.route('/api/docs')
def api_docs():
    """API documentation summary"""
    schema = get_ultra_complete_openapi_schema()
    operations = []
    for path, methods in schema['paths'].items():
        for method, details in methods.items():
            operations.append({
                "method": method.upper(),
                "path": path,
                "operationId": details['operationId'],
                "summary": details['summary']
            })
    
    # Categorize operations
    system_ops = [op for op in operations if "health" in op["operationId"].lower() or "status" in op["operationId"].lower()]
    signal_ops = [op for op in operations if "signal" in op["operationId"].lower() or "analysis" in op["operationId"].lower()]
    market_ops = [op for op in operations if "market" in op["operationId"].lower() or "ticker" in op["operationId"].lower() or "orderbook" in op["operationId"].lower()]
    smc_ops = [op for op in operations if "smc" in op["operationId"].lower()]
    backtest_ops = [op for op in operations if "backtest" in op["operationId"].lower()]
    chart_ops = [op for op in operations if "chart" in op["operationId"].lower() or "widget" in op["operationId"].lower() or "dashboard" in op["operationId"].lower()]
    
    categorized_ops = system_ops + signal_ops + market_ops + smc_ops + backtest_ops + chart_ops
    additional_ops = [op for op in operations if op not in categorized_ops]
    
    categories = {
        "system": system_ops,
        "trading_signals": signal_ops,
        "market_data": market_ops,
        "smc_analysis": smc_ops,
        "backtest": backtest_ops,
        "chart": chart_ops,
        "additional": additional_ops
    }
    
    return jsonify({
        "title": schema['info']['title'],
        "version": schema['info']['version'],
        "total_operations": len(operations),
        "categories": {k: [f"{op['method']} {op['path']}" for op in v] for k, v in categories.items()},
        "chatgpt_setup": {
            "schema_url": "https://gpts.guardiansofthetoken.id/openapi.json",
            "instructions": "Import this schema to ChatGPT Custom GPT Actions for complete trading analysis capabilities"
        }
    })