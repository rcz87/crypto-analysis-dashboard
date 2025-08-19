"""
Ultra Complete OpenAPI Schema for ChatGPT Custom GPTs
Includes ALL discovered working endpoints (30+ operations)
"""

from flask import Blueprint, jsonify

openapi_bp = Blueprint('openapi_ultra', __name__)

def get_ultra_complete_openapi_schema():
    """Generate ultra-complete OpenAPI 3.1.0 schema for ALL available endpoints"""
    
    return {
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/sinyal/tajam": {
                "post": {
                    "operationId": "getDetailedAnalysis", 
                    "summary": "Advanced Trading Analysis",
                    "description": "Deep AI analysis with SMC, sentiment, and institutional insights",
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
                            "description": "Detailed analysis completed",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
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
                                    "schema": {"type": "object"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }

@openapi_bp.route('/openapi.json')
def openapi_schema():
    """Main OpenAPI schema endpoint"""
    return jsonify(get_ultra_complete_openapi_schema())

@openapi_bp.route('/.well-known/openapi.json') 
def well_known_openapi():
    """Well-known OpenAPI schema endpoint"""
    return jsonify(get_ultra_complete_openapi_schema())

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