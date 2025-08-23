#!/usr/bin/env python3
"""
Enhanced Ultra-Complete OpenAPI Schema for ChatGPT Custom GPTs
Comprehensive documentation for all 29+ endpoints with enhanced descriptions
and ChatGPT-optimized schema definitions.
"""

from flask import Blueprint, jsonify, current_app
import inspect
import re
import logging

logger = logging.getLogger(__name__)

# Create blueprint for OpenAPI schema endpoint
openapi_enhanced_bp = Blueprint('openapi_enhanced', __name__)

@openapi_enhanced_bp.route('/', methods=['GET'])
def enhanced_schema_root():
    """Enhanced schema endpoint - Basic stub"""
    return jsonify({
        "status": "ok",
        "message": "Enhanced OpenAPI schema endpoint",
        "endpoints": {
            "openapi-enhanced.json": "Enhanced OpenAPI specification",
            "openapi-chatgpt.json": "ChatGPT-optimized schema"
        }
    })

@openapi_enhanced_bp.route('/openapi', methods=['GET'])
def get_enhanced_openapi():
    """Main endpoint to serve the enhanced OpenAPI schema for ChatGPT"""
    try:
        schema = get_enhanced_ultra_complete_openapi_schema()
        return jsonify(schema)
    except Exception as e:
        logger.error(f"Error generating enhanced OpenAPI schema: {e}")
        return jsonify({"error": "Failed to generate OpenAPI schema"}), 500

def get_enhanced_ultra_complete_openapi_schema():
    """
    Generate an OpenAPI 3.1.0 schema for ChatGPT Custom GPT integration by
    introspecting all registered Flask routes. This dynamic approach ensures
    every endpoint in the application is documented without manual
    enumeration.
    """

    # Base OpenAPI structure
    schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Cryptocurrency Trading Analysis API - Ultra Complete Enhanced",
            "description": "Automatically generated OpenAPI schema for all endpoints in the trading analysis platform.",
            "version": "3.1.0",
            "contact": {
                "name": "Enhanced GPTs Trading API",
                "url": "https://gpts.guardiansofthetoken.id"
            },
            "license": {
                "name": "API License",
                "url": "https://gpts.guardiansofthetoken.id/license"
            }
        },
        "servers": [
            {
                "url": "https://76ec735d-0891-462f-b480-6be1343dbeca-00-31zfb82614q0g.kirk.replit.dev",
                "description": "Cryptocurrency Trading Analysis API Server"
            }
        ],
        "paths": {}
    }

    # Obtain the Flask application instance for route introspection
    try:
        app_obj = current_app._get_current_object()
    except Exception:
        # Fall back to importing app directly when outside of a request context
        from app import app as app_obj

    # Loop through all URL rules to build the paths dynamically
    for rule in app_obj.url_map.iter_rules():
        # Skip static files and OpenAPI endpoints to avoid self-references
        if rule.endpoint.startswith("static") or rule.rule.startswith("/openapi"):
            continue
        path = rule.rule
        # Convert Flask-style <param> to OpenAPI-style {param}
        path_formatted = re.sub(r"<([^>]+)>", r"{\1}", path)
        if path_formatted not in schema["paths"]:
            schema["paths"][path_formatted] = {}
        # Prepare parameter definitions for path parameters
        parameters = []
        for arg in rule.arguments:
            parameters.append({
                "name": arg,
                "in": "path",
                "required": True,
                "description": f"Path parameter {arg}",
                "schema": {"type": "string"}
            })
        # Build operation objects for each HTTP method
        for method in sorted(rule.methods - {"HEAD", "OPTIONS"}):
            operation = method.lower()
            # Skip if already defined (could happen if multiple decorators used)
            if operation in schema["paths"][path_formatted]:
                continue
            view_fn = app_obj.view_functions.get(rule.endpoint)
            doc = inspect.getdoc(view_fn) if view_fn else None
            if doc:
                lines = doc.strip().split("\n")
                summary = lines[0]
                description = doc
            else:
                summary = f"{method.title()} {path_formatted}"
                description = f"Auto‑generated description for {method} {path_formatted}."
            # Assign tag based on URL path segments (after leading slash)
            segments = [seg for seg in path_formatted.split('/') if seg]
            tag = segments[0] if segments else "General"
            method_obj = {
                "operationId": f"{operation}{rule.endpoint.title().replace('_', '')}",
                "summary": summary,
                "description": description,
                "tags": [tag],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "additionalProperties": True
                                }
                            }
                        }
                    }
                }
            }
            if parameters:
                method_obj["parameters"] = parameters
            if method in {"POST", "PUT", "PATCH"}:
                method_obj["requestBody"] = {
                    "required": False,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "additionalProperties": True
                            }
                        }
                    }
                }
            schema["paths"][path_formatted][operation] = method_obj

    return schema

    """  # The following legacy static OpenAPI definitions are retained for reference
    but are ignored by the dynamic schema generator above. They remain within a
    triple‑quoted string so that they do not execute or interfere with the
    runtime behavior of this module.

            
            "/api/status": {
                "get": {
                    "operationId": "getAPIStatus", 
                    "summary": "Detailed API Status",
                    "description": "Detailed API status including endpoint availability, rate limits, and service metrics",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "API status retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "api_version": {"type": "string", "example": "3.1.0"},
                                            "endpoints_active": {"type": "number", "example": 29},
                                            "requests_today": {"type": "number", "example": 1500},
                                            "average_response_time": {"type": "number", "example": 120},
                                            "rate_limit": {
                                                "type": "object",
                                                "properties": {
                                                    "requests_per_minute": {"type": "number", "example": 60},
                                                    "requests_per_hour": {"type": "number", "example": 1000}
                                                }
                                            }
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            # =================================================================
            # CORE TRADING SIGNAL ENDPOINTS  
            # =================================================================
            "/api/signal": {
                "get": {
                    "operationId": "getTradingSignal",
                    "summary": "AI-Powered Trading Signal Generation",
                    "description": "Generate comprehensive AI-powered trading signals with confidence scoring, entry/exit levels, and detailed market analysis using advanced machine learning algorithms",
                    "tags": ["Trading Signals"],
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
                            "description": "Trading pair symbol (e.g., BTC-USDT, ETH-USDT)",
                            "schema": {"type": "string", "default": "BTC-USDT", "example": "BTC-USDT"}
                        },
                        {
                            "name": "timeframe", 
                            "in": "query",
                            "required": False,
                            "description": "Analysis timeframe (1m, 5m, 15m, 1H, 4H, 1D)",
                            "schema": {"type": "string", "default": "1H", "enum": ["1m", "5m", "15m", "30m", "1H", "4H", "6H", "12H", "1D"]}
                        },
                        {
                            "name": "confidence_threshold",
                            "in": "query", 
                            "required": False,
                            "description": "Minimum confidence threshold for signal generation (0-100)",
                            "schema": {"type": "number", "minimum": 0, "maximum": 100, "default": 60}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Trading signal generated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "signal": {
                                                "type": "object",
                                                "properties": {
                                                    "action": {"type": "string", "enum": ["BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL"]},
                                                    "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                                                    "entry_price": {"type": "number"},
                                                    "stop_loss": {"type": "number"},
                                                    "take_profit": {"type": "number"},
                                                    "risk_reward_ratio": {"type": "number"}
                                                }
                                            },
                                            "market_analysis": {
                                                "type": "object",
                                                "properties": {
                                                    "trend": {"type": "string"},
                                                    "volatility": {"type": "string"},
                                                    "volume_analysis": {"type": "string"}
                                                }
                                            },
                                            "technical_indicators": {"type": "object", "additionalProperties": True},
                                            "reasoning": {"type": "string"},
                                            "timestamp": {"type": "string", "format": "date-time"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            "/api/signal/sharp": {
                "post": {
                    "operationId": "getSharpTradingSignal",
                    "summary": "Sharp Trading Signal (Enhanced)",
                    "description": "Generate high-precision 'Sharp' trading signals with enhanced accuracy using multi-model ensemble approach and institutional-grade analysis",
                    "tags": ["Trading Signals"],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "symbol": {"type": "string", "default": "BTC-USDT", "example": "BTC-USDT"},
                                        "timeframe": {"type": "string", "default": "1H", "enum": ["1m", "5m", "15m", "1H", "4H", "1D"]},
                                        "sharp_mode": {"type": "boolean", "default": True, "description": "Enable enhanced sharp signal mode"},
                                        "risk_level": {"type": "string", "enum": ["conservative", "moderate", "aggressive"], "default": "moderate"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Sharp trading signal generated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "sharp_signal": {
                                                "type": "object", 
                                                "properties": {
                                                    "action": {"type": "string"},
                                                    "confidence": {"type": "number"},
                                                    "sharpness_score": {"type": "number", "description": "Signal precision score"},
                                                    "entry_zone": {"type": "object"},
                                                    "targets": {"type": "array", "items": {"type": "number"}},
                                                    "stop_loss": {"type": "number"}
                                                }
                                            },
                                            "market_context": {"type": "object", "additionalProperties": True},
                                            "risk_assessment": {"type": "object", "additionalProperties": True},
                                            "telegram_message": {"type": "string", "description": "Formatted message for Telegram"},
                                            "natural_language": {"type": "string", "description": "Human-readable analysis"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                },
                "get": {
                    "operationId": "getSharpSignalQuick",
                    "summary": "Quick Sharp Signal",
                    "description": "Quick access to sharp trading signals via GET request",
                    "tags": ["Trading Signals"],
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": False,
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Quick sharp signal retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "signal": {"type": "object", "additionalProperties": True},
                                            "timestamp": {"type": "string"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            # =================================================================
            # SMART MONEY CONCEPT (SMC) ENDPOINTS
            # =================================================================
            "/api/smc/analysis": {
                "get": {
                    "operationId": "getSmcAnalysis",
                    "summary": "Smart Money Concept Analysis",
                    "description": "Comprehensive Smart Money Concept (SMC) analysis including market structure, order blocks, fair value gaps, and institutional trading patterns",
                    "tags": ["SMC Analysis"],
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
                            "description": "Trading pair for SMC analysis",
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
                            "description": "SMC analysis completed successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "market_structure": {
                                                "type": "object",
                                                "properties": {
                                                    "trend": {"type": "string"},
                                                    "bias": {"type": "string"},
                                                    "structure_points": {"type": "array", "items": {"type": "object"}}
                                                }
                                            },
                                            "order_blocks": {"type": "array", "items": {"type": "object"}},
                                            "fair_value_gaps": {"type": "array", "items": {"type": "object"}},
                                            "liquidity_zones": {"type": "array", "items": {"type": "object"}},
                                            "trading_plan": {"type": "object", "additionalProperties": True}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            "/api/smc/zones": {
                "get": {
                    "operationId": "getSmcZones",
                    "summary": "SMC Zones with Advanced Filtering",
                    "description": "Get Smart Money Concept zones with advanced filtering options for order blocks, fair value gaps, and liquidity zones",
                    "tags": ["SMC Analysis"],
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
                            "description": "Trading pair symbol",
                            "schema": {"type": "string", "default": "BTC-USDT"}
                        },
                        {
                            "name": "zone_type",
                            "in": "query",
                            "description": "Type of SMC zone to filter",
                            "schema": {"type": "string", "enum": ["order_block", "fair_value_gap", "liquidity_zone", "all"], "default": "all"}
                        },
                        {
                            "name": "strength_filter",
                            "in": "query",
                            "description": "Minimum zone strength (0-100)",
                            "schema": {"type": "number", "minimum": 0, "maximum": 100, "default": 50}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "SMC zones retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "zones": {"type": "array", "items": {"type": "object"}},
                                            "zone_summary": {"type": "object"},
                                            "active_zones_count": {"type": "number"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            # =================================================================
            # MARKET DATA & CHART ENDPOINTS
            # =================================================================
            "/api/chart": {
                "get": {
                    "operationId": "getChartData",
                    "summary": "Enhanced Chart Data with Indicators",
                    "description": "Get comprehensive chart data with technical indicators, volume analysis, and market structure overlay for advanced charting applications",
                    "tags": ["Market Data"],
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
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
                            "name": "bars",
                            "in": "query",
                            "description": "Number of bars to retrieve",
                            "schema": {"type": "number", "minimum": 10, "maximum": 500, "default": 100}
                        },
                        {
                            "name": "indicators",
                            "in": "query",
                            "description": "Include technical indicators",
                            "schema": {"type": "boolean", "default": True}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Chart data retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "ohlcv_data": {"type": "array", "items": {"type": "object"}},
                                            "technical_indicators": {"type": "object", "additionalProperties": True},
                                            "volume_profile": {"type": "object"},
                                            "market_structure": {"type": "object"},
                                            "metadata": {"type": "object"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            # =================================================================
            # TELEGRAM INTEGRATION ENDPOINTS
            # =================================================================
            "/api/telegram/status": {
                "get": {
                    "operationId": "getTelegramStatus",
                    "summary": "Telegram Bot Status",
                    "description": "Check Telegram bot connectivity and configuration status",
                    "tags": ["Telegram"],
                    "responses": {
                        "200": {
                            "description": "Telegram status retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "bot_status": {"type": "string", "enum": ["active", "inactive", "error"]},
                                            "connected_chats": {"type": "number"},
                                            "messages_sent_today": {"type": "number"},
                                            "last_message_time": {"type": "string", "format": "date-time"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            "/api/telegram/send": {
                "post": {
                    "operationId": "sendTelegramSignal",
                    "summary": "Send Trading Signal to Telegram",
                    "description": "Send formatted trading signal to configured Telegram channels",
                    "tags": ["Telegram"],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "signal_data": {"type": "object", "description": "Trading signal data to send"},
                                        "message_type": {"type": "string", "enum": ["signal", "alert", "analysis"], "default": "signal"},
                                        "format_style": {"type": "string", "enum": ["standard", "enhanced", "minimal"], "default": "enhanced"}
                                    },
                                    "required": ["signal_data"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Message sent successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "sent": {"type": "boolean"},
                                            "message_id": {"type": "string"},
                                            "recipients": {"type": "number"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            # =================================================================
            # ENHANCED GPTS ENDPOINTS
            # =================================================================
            "/api/gpts/enhanced/analysis": {
                "post": {
                    "operationId": "getEnhancedGptsAnalysis",
                    "summary": "Enhanced GPTs Market Analysis",
                    "description": "Advanced market analysis specifically optimized for ChatGPT consumption with structured responses",
                    "tags": ["Enhanced GPTs"],
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "symbol": {"type": "string", "default": "BTC-USDT"},
                                        "analysis_type": {"type": "string", "enum": ["comprehensive", "technical", "fundamental", "sentiment"], "default": "comprehensive"},
                                        "output_format": {"type": "string", "enum": ["structured", "narrative", "bullets"], "default": "structured"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Enhanced analysis completed",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "analysis": {"type": "object", "additionalProperties": True},
                                            "market_data": {"type": "object", "additionalProperties": True},
                                            "timestamp": {"type": "string"}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            },

            # ==================================================================
            # ENTERPRISE MANAGEMENT ENDPOINTS  
            # ==================================================================
            "/api/enterprise/dashboard": {
                "get": {
                    "operationId": "getEnterpriseDashboard",
                    "summary": "Enterprise Dashboard",
                    "description": "Comprehensive dashboard for 50+ endpoints with real-time analytics",
                    "tags": ["Enterprise"],
                    "responses": {
                        "200": {
                            "description": "Enterprise dashboard data",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/enterprise/auto-discover": {
                "post": {
                    "operationId": "autoDiscoverEndpoints",
                    "summary": "Auto-Discover Endpoints",
                    "description": "Automatically discover and register all Flask endpoints",
                    "tags": ["Enterprise"],
                    "responses": {
                        "200": {
                            "description": "Endpoints discovered successfully",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/enterprise/performance/real-time": {
                "get": {
                    "operationId": "getRealTimePerformance",
                    "summary": "Real-Time Performance Monitoring",
                    "description": "Get real-time performance metrics and anomalies",
                    "tags": ["Enterprise"],
                    "parameters": [
                        {
                            "name": "minutes",
                            "in": "query",
                            "description": "Time range in minutes (max 240)",
                            "schema": {"type": "integer", "default": 30}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Real-time performance data",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/enterprise/scaling/recommendations": {
                "get": {
                    "operationId": "getScalingRecommendations",
                    "summary": "Intelligent Scaling Recommendations",
                    "description": "AI-powered scaling recommendations based on load patterns",
                    "tags": ["Enterprise"],
                    "responses": {
                        "200": {
                            "description": "Scaling recommendations",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/enterprise/analytics/advanced": {
                "get": {
                    "operationId": "getAdvancedAnalytics",
                    "summary": "Advanced Analytics & Predictive Insights",
                    "description": "Advanced analytics with predictive load forecasting and anomaly detection",
                    "tags": ["Enterprise"],
                    "responses": {
                        "200": {
                            "description": "Advanced analytics data",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            "/api/performance/cache-stats": {
                "get": {
                    "operationId": "getCacheStats",
                    "summary": "Universal Cache Statistics",
                    "description": "Comprehensive cache statistics from Universal Cache System",
                    "tags": ["Performance"],
                    "responses": {
                        "200": {
                            "description": "Cache statistics",
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "additionalProperties": True}
                                }
                            }
                        }
                    }
                }
            },
            
            # =================================================================
            # OPENAPI SCHEMA ENDPOINT
            # =================================================================
            "/openapi.json": {
                "get": {
                    "operationId": "getOpenApiSchema",
                    "summary": "Get OpenAPI Schema",
                    "description": "Retrieve the complete OpenAPI 3.1.0 schema for this API",
                    "tags": ["Documentation"],
                    "responses": {
                        "200": {
                            "description": "OpenAPI schema retrieved",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "openapi": {"type": "string", "example": "3.1.0"},
                                            "info": {"type": "object", "additionalProperties": True},
                                            "paths": {"type": "object", "additionalProperties": True},
                                            "components": {"type": "object", "additionalProperties": True}
                                        },
                                        "additionalProperties": True
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        
        # =================================================================
        # ENHANCED COMPONENTS DEFINITIONS
        # =================================================================
        "components": {
            "schemas": {
                "TradingSignal": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "enum": ["BUY", "SELL", "HOLD", "STRONG_BUY", "STRONG_SELL"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                        "entry_price": {"type": "number"},
                        "stop_loss": {"type": "number"},
                        "take_profit": {"type": "number"},
                        "risk_reward_ratio": {"type": "number"},
                        "reasoning": {"type": "string"}
                    },
                    "required": ["action", "confidence"]
                },
                "MarketData": {
                    "type": "object",
                    "properties": {
                        "symbol": {"type": "string"},
                        "price": {"type": "number"},
                        "volume": {"type": "number"},
                        "timestamp": {"type": "string", "format": "date-time"}
                    }
                },
                "SmcZone": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["order_block", "fair_value_gap", "liquidity_zone"]},
                        "price_level": {"type": "number"},
                        "strength": {"type": "number", "minimum": 0, "maximum": 100},
                        "direction": {"type": "string", "enum": ["bullish", "bearish"]},
                        "active": {"type": "boolean"}
                    }
                }
            },
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-KEY"
                }
            }
        },
        
        "tags": [
            {"name": "System", "description": "System health and status endpoints"},
            {"name": "Trading Signals", "description": "AI-powered trading signal generation"},
            {"name": "SMC Analysis", "description": "Smart Money Concept analysis and zones"},
            {"name": "Market Data", "description": "Real-time market data and charts"},
            {"name": "Telegram", "description": "Telegram bot integration"},
            {"name": "Enhanced GPTs", "description": "ChatGPT-optimized endpoints"},
            {"name": "Documentation", "description": "API documentation and schemas"}
        ]
    }
    
    # ---------------------------------------------------------------------
    # Append definitions for missing endpoints.  These are generic stubs
    # meant to provide full coverage of all known routes exposed by the
    # underlying service.  Each entry follows the same structure as the
    # existing endpoints above: a GET method with a simple summary,
    # description and a permissive response schema so that clients like
    # ChatGPT can consume the API without strict typing.  Feel free to
    # extend these definitions with more detailed parameters and responses
    # as your API evolves.
    missing_endpoints = {
        "/api/v2/signal/enhanced": {
            "get": {
                "operationId": "getV2SignalEnhanced",
                "summary": "Enhanced v2 trading signal",
                "description": "Generate enhanced AI‑powered trading signal using the v2 engine.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {
                        "description": "Enhanced trading signal generated successfully",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "additionalProperties": True}
                            }
                        }
                    }
                }
            }
        },
        "/api/v2/smc/analyze": {
            "get": {
                "operationId": "getV2SmcAnalyze",
                "summary": "Advanced SMC analysis (v2)",
                "description": "Run Smart Money Concept analysis using the v2 analysis engine.",
                "tags": ["SMC Analysis"],
                "responses": {
                    "200": {
                        "description": "SMC v2 analysis completed successfully",
                        "content": {
                            "application/json": {"schema": {"type": "object", "additionalProperties": True}}
                        }
                    }
                }
            }
        },
        "/api/v2/risk-management/profile": {
            "get": {
                "operationId": "getV2RiskManagementProfile",
                "summary": "Risk management profile (v2)",
                "description": "Retrieve or calculate a risk management profile for the current portfolio using the v2 API.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {
                        "description": "Risk profile returned successfully",
                        "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}
                    }
                }
            }
        },
        "/api/v2/technical/indicators": {
            "get": {
                "operationId": "getV2TechnicalIndicators",
                "summary": "Technical indicators (v2)",
                "description": "Fetch a list of supported technical indicators available in the v2 API.",
                "tags": ["Market Data"],
                "responses": {
                    "200": {
                        "description": "List of technical indicators returned successfully",
                        "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}
                    }
                }
            }
        },
        "/api/v2/market-data/candles": {
            "get": {
                "operationId": "getV2MarketDataCandles",
                "summary": "Market candles (v2)",
                "description": "Retrieve candlestick data using the v2 API. Supports multiple timeframes and symbols.",
                "tags": ["Market Data"],
                "responses": {
                    "200": {
                        "description": "Candlestick data retrieved successfully",
                        "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}
                    }
                }
            }
        },
        "/api/v2/version": {
            "get": {
                "operationId": "getV2Version",
                "summary": "API v2 version",
                "description": "Return the current API v2 version and build information.",
                "tags": ["System"],
                "responses": {
                    "200": {"description": "API version returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/v2/endpoints": {
            "get": {
                "operationId": "listV2Endpoints",
                "summary": "List of v2 endpoints",
                "description": "Get a list of all available v2 API endpoints for discovery and documentation.",
                "tags": ["Documentation"],
                "responses": {
                    "200": {
                        "description": "Endpoint list returned successfully",
                        "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}
                    }
                }
            }
        },
        "/api/tradinglite/connect": {
            "get": {
                "operationId": "getTradingLiteConnect",
                "summary": "TradingLite connection status",
                "description": "Check the connection status or establish a connection with the TradingLite service.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {"description": "Connection status returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/tradinglite/liquidity-analysis": {
            "get": {
                "operationId": "getTradingLiteLiquidityAnalysis",
                "summary": "Liquidity analysis via TradingLite",
                "description": "Perform liquidity analysis using TradingLite data sources.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {"description": "Liquidity analysis result returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/tradinglite/order-flow-analysis": {
            "get": {
                "operationId": "getTradingLiteOrderFlowAnalysis",
                "summary": "Order flow analysis via TradingLite",
                "description": "Retrieve order flow analytics from TradingLite.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {"description": "Order flow analysis returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/tradinglite/combined-signal": {
            "get": {
                "operationId": "getTradingLiteCombinedSignal",
                "summary": "Combined signal via TradingLite",
                "description": "Generate a combined trading signal using both internal analysis and TradingLite data.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {"description": "Combined signal generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/tradinglite/litscript/generate": {
            "post": {
                "operationId": "postTradingLiteLitScriptGenerate",
                "summary": "Generate TradingLite script",
                "description": "Generate or compile a LitScript for TradingLite based on provided parameters.",
                "tags": ["Trading Signals"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "additionalProperties": True}
                        }
                    }
                },
                "responses": {
                    "200": {"description": "LitScript generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/tradinglite/status": {
            "get": {
                "operationId": "getTradingLiteStatus",
                "summary": "TradingLite service status",
                "description": "Retrieve the operational status of the TradingLite integration.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {"description": "Status returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/tradinglite/telegram/send": {
            "post": {
                "operationId": "postTradingLiteTelegramSend",
                "summary": "Send TradingLite update to Telegram",
                "description": "Send a notification or update from TradingLite to a configured Telegram channel.",
                "tags": ["Telegram"],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"type": "object", "additionalProperties": True}
                        }
                    }
                },
                "responses": {
                    "200": {"description": "Notification sent", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/docs/": {
            "get": {
                "operationId": "getDocumentationHome",
                "summary": "API documentation home",
                "description": "Return an overview of available documentation pages and links.",
                "tags": ["Documentation"],
                "responses": {
                    "200": {"description": "Documentation index returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/docs/sdk/{language}": {
            "get": {
                "operationId": "getDocumentationSdkLanguage",
                "summary": "SDK documentation",
                "description": "Retrieve SDK usage documentation for the specified programming language.",
                "tags": ["Documentation"],
                "parameters": [
                    {
                        "name": "language",
                        "in": "path",
                        "required": True,
                        "description": "Programming language for the SDK documentation",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "SDK documentation returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/docs/endpoint": {
            "get": {
                "operationId": "getDocumentationEndpoint",
                "summary": "Specific endpoint documentation",
                "description": "Return documentation for a specific endpoint; accepts query parameter 'path' to specify the endpoint.",
                "tags": ["Documentation"],
                "parameters": [
                    {
                        "name": "path",
                        "in": "query",
                        "required": True,
                        "description": "API path to document",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {"description": "Endpoint documentation returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/docs/openapi": {
            "get": {
                "operationId": "getDocumentationOpenapi",
                "summary": "Raw OpenAPI schema",
                "description": "Return the raw OpenAPI specification for the API.",
                "tags": ["Documentation"],
                "responses": {
                    "200": {"description": "OpenAPI specification returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/monitoring/system": {
            "get": {
                "operationId": "getMonitoringSystem",
                "summary": "System monitoring data",
                "description": "Retrieve system‑level monitoring metrics such as CPU, memory, and disk usage.",
                "tags": ["System"],
                "responses": {
                    "200": {"description": "Monitoring data returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/monitoring/health": {
            "get": {
                "operationId": "getMonitoringHealth",
                "summary": "Service health metrics",
                "description": "Retrieve health metrics for all services and dependencies.",
                "tags": ["System"],
                "responses": {
                    "200": {"description": "Health metrics returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/monitoring/performance": {
            "get": {
                "operationId": "getMonitoringPerformance",
                "summary": "Performance metrics",
                "description": "Return performance and response time metrics for API endpoints.",
                "tags": ["System"],
                "responses": {
                    "200": {"description": "Performance metrics returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/websocket/status": {
            "get": {
                "operationId": "getWebsocketStatus",
                "summary": "WebSocket connection status",
                "description": "Check the status of the WebSocket streaming service.",
                "tags": ["System"],
                "responses": {
                    "200": {"description": "WebSocket status returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/websocket/start": {
            "post": {
                "operationId": "postWebsocketStart",
                "summary": "Start WebSocket stream",
                "description": "Initiate a WebSocket stream for live data feeds.",
                "tags": ["System"],
                "responses": {
                    "200": {"description": "WebSocket stream started", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/websocket/stop": {
            "post": {
                "operationId": "postWebsocketStop",
                "summary": "Stop WebSocket stream",
                "description": "Terminate an active WebSocket stream.",
                "tags": ["System"],
                "responses": {
                    "200": {"description": "WebSocket stream stopped", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/signal/generate": {
            "get": {
                "operationId": "getSignalGenerate",
                "summary": "Generate basic trading signal",
                "description": "Generate a basic trading signal using core indicators and analysis.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {"description": "Trading signal generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/signal/advanced": {
            "get": {
                "operationId": "getSignalAdvanced",
                "summary": "Generate advanced trading signal",
                "description": "Generate an advanced trading signal that combines multiple analysis modules.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {"description": "Advanced trading signal generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/indicators/all": {
            "get": {
                "operationId": "getIndicatorsAll",
                "summary": "List all indicators",
                "description": "Return a list of all available technical and statistical indicators.",
                "tags": ["Market Data"],
                "responses": {
                    "200": {"description": "Indicators list returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/market/candles": {
            "get": {
                "operationId": "getMarketCandles",
                "summary": "Candlestick data",
                "description": "Retrieve candlestick price data for a given symbol and timeframe.",
                "tags": ["Market Data"],
                "responses": {
                    "200": {"description": "Candlestick data returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        },
        "/api/risk/portfolio": {
            "get": {
                "operationId": "getRiskPortfolio",
                "summary": "Portfolio risk analysis",
                "description": "Generate a risk analysis for the current trading portfolio, including drawdown and VaR estimates.",
                "tags": ["Trading Signals"],
                "responses": {
                    "200": {"description": "Portfolio risk analysis returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}
                }
            }
        }
    }
    # ---------------------------------------------------------------------
    # Extended endpoint definitions
    # These endpoints fill out additional categories such as News & Sentiment
    # analysis, optimized AI engines, extended signal/SMC/risk APIs, v2
    # endpoints, and backtest/cache management.  They are provided with
    # generic request/response schemas to ensure the OpenAPI document covers
    # all server routes.  Adjust method types, parameters and response
    # structures as your implementation evolves.
    extended_endpoints = {
        # News & Sentiment Analysis
        "/api/news/analyze": {
            "get": {
                "operationId": "getNewsAnalyze",
                "summary": "Analyze news headlines",
                "description": "Perform sentiment or relevance analysis on recent news articles related to the trading pairs.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "News analysis returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/news/fetch": {
            "get": {
                "operationId": "getNewsFetch",
                "summary": "Fetch news articles",
                "description": "Retrieve a list of recent news articles for supported trading pairs and markets.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "News articles returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/news/sentiment": {
            "get": {
                "operationId": "getNewsSentiment",
                "summary": "News sentiment analysis",
                "description": "Retrieve aggregated sentiment scores for recent news.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "Sentiment scores returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/news/trending": {
            "get": {
                "operationId": "getNewsTrending",
                "summary": "Trending news topics",
                "description": "Return trending topics or keywords from current crypto news.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "Trending topics returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/news/search": {
            "get": {
                "operationId": "getNewsSearch",
                "summary": "Search news",
                "description": "Search for news articles containing a specific keyword or phrase.",
                "tags": ["Market Data"],
                "parameters": [
                    {"name": "query", "in": "query", "required": True, "description": "Search keyword", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Search results returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/news/latest": {
            "get": {
                "operationId": "getNewsLatest",
                "summary": "Latest news",
                "description": "Return the most recent news articles.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "Latest news returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/news/topic": {
            "get": {
                "operationId": "getNewsTopic",
                "summary": "News by topic",
                "description": "Return news articles for a specific topic or category.",
                "tags": ["Market Data"],
                "parameters": [
                    {"name": "topic", "in": "query", "required": True, "description": "Topic or category", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Topic news returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # Optimized AI Endpoints
        "/api/optimized/batch-analysis": {
            "post": {
                "operationId": "postOptimizedBatchAnalysis",
                "summary": "Batch AI analysis",
                "description": "Run AI analysis on a batch of symbols and timeframes for faster throughput.",
                "tags": ["Trading Signals"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Batch analysis completed", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/optimized/ensemble-prediction": {
            "post": {
                "operationId": "postOptimizedEnsemblePrediction",
                "summary": "Ensemble prediction",
                "description": "Generate predictions using an ensemble of models or analyses.",
                "tags": ["Trading Signals"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Ensemble prediction generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/optimized/fast-analysis": {
            "get": {
                "operationId": "getOptimizedFastAnalysis",
                "summary": "Fast AI analysis",
                "description": "Run a fast, less resource‑intensive AI analysis for quick insights.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Fast analysis completed", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/optimized/performance-metrics": {
            "get": {
                "operationId": "getOptimizedPerformanceMetrics",
                "summary": "Optimized performance metrics",
                "description": "Return performance metrics for optimized AI models.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Performance metrics returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/optimized/summary": {
            "get": {
                "operationId": "getOptimizedSummary",
                "summary": "Optimized analysis summary",
                "description": "Return a summary of recent optimized analyses and their performance.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Summary returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/optimized/compare": {
            "post": {
                "operationId": "postOptimizedCompare",
                "summary": "Compare optimized models",
                "description": "Compare the outputs of different optimized AI models.",
                "tags": ["Trading Signals"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Comparison completed", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # Extended Signal Endpoints
        "/api/signal/fast": {
            "get": {
                "operationId": "getSignalFast",
                "summary": "Fast signal generation",
                "description": "Generate a quick trading signal using a simplified analysis pipeline.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Fast signal generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/signal/top": {
            "get": {
                "operationId": "getSignalTop",
                "summary": "Top signals",
                "description": "Return the top performing trading signals for the current period.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Top signals returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/signal/top/telegram": {
            "post": {
                "operationId": "postSignalTopTelegram",
                "summary": "Send top signals to Telegram",
                "description": "Send the top signals to a configured Telegram channel.",
                "tags": ["Telegram"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Top signals sent", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/signals/history": {
            "get": {
                "operationId": "getSignalsHistory",
                "summary": "Signals history",
                "description": "Return historical signals and their outcomes.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Signals history returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/signal/sharp/status": {
            "get": {
                "operationId": "getSignalSharpStatus",
                "summary": "Sharp signal status",
                "description": "Check the status of sharp (high confidence) signals.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Sharp signal status returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/signal/sharp": {
            "get": {
                "operationId": "getSignalSharp",
                "summary": "Sharp signals",
                "description": "Return high confidence trading signals.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Sharp signals returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/signal/best": {
            "get": {
                "operationId": "getSignalBest",
                "summary": "Best performing signals",
                "description": "Return the best performing signals over a longer period.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Best signals returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/signal/best/telegram": {
            "post": {
                "operationId": "postSignalBestTelegram",
                "summary": "Send best signals to Telegram",
                "description": "Send the best performing signals to a configured Telegram channel.",
                "tags": ["Telegram"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Best signals sent", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # Extended SMC Endpoints
        "/api/smc/clear": {
            "post": {
                "operationId": "postSmcClear",
                "summary": "Clear SMC data",
                "description": "Clear or reset current Smart Money Concept analysis data.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "SMC data cleared", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/context": {
            "get": {
                "operationId": "getSmcContext",
                "summary": "SMC context",
                "description": "Return contextual information used in Smart Money Concept analysis.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "SMC context returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/history": {
            "get": {
                "operationId": "getSmcHistory",
                "summary": "SMC history",
                "description": "Return historical Smart Money Concept analyses.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "SMC history returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/orderblocks": {
            "get": {
                "operationId": "getSmcOrderblocks",
                "summary": "SMC order blocks",
                "description": "Return detected order blocks from Smart Money Concept analysis.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "Order blocks returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/patterns/recognize": {
            "post": {
                "operationId": "postSmcPatternsRecognize",
                "summary": "Recognize SMC patterns",
                "description": "Recognize Smart Money Concept patterns in provided data.",
                "tags": ["SMC Analysis"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Patterns recognized", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/summary": {
            "get": {
                "operationId": "getSmcSummary",
                "summary": "SMC summary",
                "description": "Return a summary of the current Smart Money Concept analysis, including confidence scores and key levels.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "SMC summary returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/reset": {
            "post": {
                "operationId": "postSmcReset",
                "summary": "Reset SMC analysis",
                "description": "Completely reset all Smart Money Concept calculations and derived data.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "SMC reset performed", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/config": {
            "get": {
                "operationId": "getSmcConfig",
                "summary": "SMC configuration",
                "description": "Return configuration settings for the SMC analysis engine.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "Configuration returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/probabilities": {
            "get": {
                "operationId": "getSmcProbabilities",
                "summary": "SMC pattern probabilities",
                "description": "Return probability distributions for various SMC patterns.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "Probabilities returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/signals": {
            "get": {
                "operationId": "getSmcSignals",
                "summary": "SMC signals",
                "description": "Return trading signals derived solely from Smart Money Concept analysis.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "SMC signals returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/stats": {
            "get": {
                "operationId": "getSmcStats",
                "summary": "SMC statistics",
                "description": "Return statistical metrics derived from SMC analysis runs.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "Statistics returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/smc/zones/advanced": {
            "get": {
                "operationId": "getSmcZonesAdvanced",
                "summary": "Advanced SMC zones",
                "description": "Return advanced zone calculations for Smart Money Concept including nested order blocks and liquidity pools.",
                "tags": ["SMC Analysis"],
                "responses": {"200": {"description": "Advanced zones returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # Extended API v2
        "/api/v2/auth/token": {
            "post": {
                "operationId": "postV2AuthToken",
                "summary": "Authenticate and obtain token",
                "description": "Authenticate the client and return an access token for v2 API requests.",
                "tags": ["System"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Token issued", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/health": {
            "get": {
                "operationId": "getV2Health",
                "summary": "API v2 health",
                "description": "Return health information for the v2 services.",
                "tags": ["System"],
                "responses": {"200": {"description": "Health status returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/risk/assessment": {
            "get": {
                "operationId": "getV2RiskAssessment",
                "summary": "Risk assessment (v2)",
                "description": "Return an in‑depth risk assessment using v2 algorithms.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Risk assessment returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/signals/generate": {
            "get": {
                "operationId": "getV2SignalsGenerate",
                "summary": "Generate signals (v2)",
                "description": "Generate trading signals using the version 2 API.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Signals generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/trend/analysis": {
            "get": {
                "operationId": "getV2TrendAnalysis",
                "summary": "Trend analysis (v2)",
                "description": "Return trend analysis using v2 market data algorithms.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "Trend analysis returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # Backtest & Cache Management
        "/api/backtest/run": {
            "post": {
                "operationId": "postBacktestRun",
                "summary": "Run backtest",
                "description": "Initiate a backtest of a trading strategy over historical data.",
                "tags": ["Trading Signals"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Backtest completed", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/backtest/history": {
            "get": {
                "operationId": "getBacktestHistory",
                "summary": "Backtest history",
                "description": "Return a history of completed backtests.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Backtest history returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/cache/clear": {
            "post": {
                "operationId": "postCacheClear",
                "summary": "Clear cache",
                "description": "Clear cached data used for market data, analysis, or API responses.",
                "tags": ["System"],
                "responses": {"200": {"description": "Cache cleared", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/cache/status": {
            "get": {
                "operationId": "getCacheStatus",
                "summary": "Cache status",
                "description": "Return information about cached entries and their expiration.",
                "tags": ["System"],
                "responses": {"200": {"description": "Cache status returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/performance/metrics": {
            "get": {
                "operationId": "getPerformanceMetrics",
                "summary": "Performance metrics",
                "description": "Return performance metrics for the backtest and live trading systems.",
                "tags": ["System"],
                "responses": {"200": {"description": "Performance metrics returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/performance/reset": {
            "post": {
                "operationId": "postPerformanceReset",
                "summary": "Reset performance metrics",
                "description": "Reset or clear recorded performance metrics.",
                "tags": ["System"],
                "responses": {"200": {"description": "Performance metrics reset", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # -----------------------------------------------------------------
        # API v2 Additional Endpoints
        # These endpoints extend the version 2 API with advanced signal,
        # SMC analysis, risk management profiles, technical indicators, and
        # market data. Each endpoint returns generic JSON until
        # implementation details are available.
        "/api/v2/signal/enhanced": {
            "get": {
                "operationId": "getV2SignalEnhanced",
                "summary": "Enhanced trading signal (v2)",
                "description": "Return enhanced AI‑powered trading signals using the v2 API.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Enhanced signal returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/smc/analyze": {
            "post": {
                "operationId": "postV2SmcAnalyze",
                "summary": "Analyze SMC patterns (v2)",
                "description": "Perform Smart Money Concept analysis using the v2 engine.",
                "tags": ["SMC Analysis"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "SMC analysis completed", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/risk-management/profile": {
            "get": {
                "operationId": "getV2RiskManagementProfile",
                "summary": "Risk management profile (v2)",
                "description": "Retrieve the current risk management profile using v2 algorithms.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Risk management profile returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/technical/indicators": {
            "get": {
                "operationId": "getV2TechnicalIndicators",
                "summary": "Technical indicators (v2)",
                "description": "Return technical indicator calculations via the v2 API.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Technical indicators returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/market-data/candles": {
            "get": {
                "operationId": "getV2MarketDataCandles",
                "summary": "Market candlestick data (v2)",
                "description": "Return candlestick (OHLCV) market data using the v2 API.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "Candlestick data returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/version": {
            "get": {
                "operationId": "getV2Version",
                "summary": "API v2 version information",
                "description": "Return the current version and metadata for the v2 API.",
                "tags": ["System"],
                "responses": {"200": {"description": "Version info returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/v2/endpoints": {
            "get": {
                "operationId": "getV2Endpoints",
                "summary": "List available endpoints (v2)",
                "description": "Return a list of all available v2 endpoints for discovery purposes.",
                "tags": ["System"],
                "responses": {"200": {"description": "Endpoint list returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # -----------------------------------------------------------------
        # TradingLite Integration Endpoints
        # These endpoints provide integration with the TradingLite platform for
        # advanced liquidity and order‑flow analysis and automated signal
        # generation. Generic responses are used as placeholders.
        "/api/tradinglite/connect": {
            "post": {
                "operationId": "postTradingliteConnect",
                "summary": "Connect to TradingLite",
                "description": "Establish a connection to the TradingLite service and authenticate if necessary.",
                "tags": ["TradingLite"],
                "requestBody": {"required": False, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Connection established", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/tradinglite/liquidity-analysis": {
            "get": {
                "operationId": "getTradingliteLiquidityAnalysis",
                "summary": "TradingLite liquidity analysis",
                "description": "Perform a liquidity analysis using TradingLite data.",
                "tags": ["TradingLite"],
                "responses": {"200": {"description": "Liquidity analysis returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/tradinglite/order-flow-analysis": {
            "get": {
                "operationId": "getTradingliteOrderFlowAnalysis",
                "summary": "TradingLite order flow analysis",
                "description": "Return order flow analysis derived from TradingLite order book data.",
                "tags": ["TradingLite"],
                "responses": {"200": {"description": "Order flow analysis returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/tradinglite/combined-signal": {
            "get": {
                "operationId": "getTradingliteCombinedSignal",
                "summary": "TradingLite combined signal",
                "description": "Return a combined trading signal generated using TradingLite liquidity and order flow data.",
                "tags": ["TradingLite"],
                "responses": {"200": {"description": "Combined signal returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/tradinglite/litscript/generate": {
            "post": {
                "operationId": "postTradingliteLitscriptGenerate",
                "summary": "Generate TradingLite script",
                "description": "Generate a custom TradingLite script (Litscript) based on input parameters.",
                "tags": ["TradingLite"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Script generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/tradinglite/status": {
            "get": {
                "operationId": "getTradingliteStatus",
                "summary": "TradingLite connection status",
                "description": "Return the current connection and service status of TradingLite integration.",
                "tags": ["TradingLite"],
                "responses": {"200": {"description": "Status returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/tradinglite/telegram/send": {
            "post": {
                "operationId": "postTradingliteTelegramSend",
                "summary": "Send TradingLite signal to Telegram",
                "description": "Send a generated TradingLite signal to a configured Telegram channel.",
                "tags": ["Telegram"],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}},
                "responses": {"200": {"description": "Signal sent", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # -----------------------------------------------------------------
        # Documentation Endpoints
        # Provide programmatic access to API documentation in multiple forms.
        "/api/docs/": {
            "get": {
                "operationId": "getDocsIndex",
                "summary": "API documentation index",
                "description": "Return an index of available API documentation resources.",
                "tags": ["Documentation"],
                "responses": {"200": {"description": "Documentation index returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/docs/sdk/{language}": {
            "get": {
                "operationId": "getDocsSdkLanguage",
                "summary": "SDK documentation by language",
                "description": "Return SDK documentation or code examples for the specified programming language.",
                "tags": ["Documentation"],
                "parameters": [
                    {"name": "language", "in": "path", "required": True, "description": "Programming language for the SDK (e.g., python, javascript)", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "SDK documentation returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/docs/endpoint": {
            "get": {
                "operationId": "getDocsEndpoint",
                "summary": "Endpoint documentation",
                "description": "Return detailed documentation for a specific API endpoint.",
                "tags": ["Documentation"],
                "parameters": [
                    {"name": "path", "in": "query", "required": True, "description": "API endpoint path to document", "schema": {"type": "string"}}
                ],
                "responses": {"200": {"description": "Endpoint documentation returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/docs/openapi": {
            "get": {
                "operationId": "getDocsOpenapi",
                "summary": "OpenAPI specification",
                "description": "Return the full OpenAPI specification for the API.",
                "tags": ["Documentation"],
                "responses": {"200": {"description": "OpenAPI specification returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # -----------------------------------------------------------------
        # Monitoring & WebSocket Endpoints
        # Provide system monitoring and WebSocket management capabilities.
        "/api/monitoring/system": {
            "get": {
                "operationId": "getMonitoringSystem",
                "summary": "System monitoring (extended)",
                "description": "Return comprehensive system metrics including CPU, memory, and API response times.",
                "tags": ["Monitoring"],
                "responses": {"200": {"description": "System metrics returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/monitoring/health": {
            "get": {
                "operationId": "getMonitoringHealth",
                "summary": "Monitoring health",
                "description": "Return the health status of the monitoring subsystem.",
                "tags": ["Monitoring"],
                "responses": {"200": {"description": "Monitoring health returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/monitoring/performance": {
            "get": {
                "operationId": "getMonitoringPerformance",
                "summary": "Performance monitoring",
                "description": "Return API performance metrics such as average response times and error rates.",
                "tags": ["Monitoring"],
                "responses": {"200": {"description": "Performance metrics returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/websocket/status": {
            "get": {
                "operationId": "getWebsocketStatus",
                "summary": "WebSocket status",
                "description": "Return the current status of the WebSocket connection and streaming services.",
                "tags": ["WebSocket"],
                "responses": {"200": {"description": "WebSocket status returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/websocket/start": {
            "post": {
                "operationId": "postWebsocketStart",
                "summary": "Start WebSocket stream",
                "description": "Start or restart the WebSocket stream for real‑time data.",
                "tags": ["WebSocket"],
                "responses": {"200": {"description": "WebSocket stream started", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/websocket/stop": {
            "post": {
                "operationId": "postWebsocketStop",
                "summary": "Stop WebSocket stream",
                "description": "Stop the WebSocket stream and close the connection gracefully.",
                "tags": ["WebSocket"],
                "responses": {"200": {"description": "WebSocket stream stopped", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        # -----------------------------------------------------------------
        # Core Trading Additional Endpoints
        # Additional endpoints for generating and retrieving trading signals and
        # market data. These complement the existing /api/signal and
        # technical analysis endpoints.
        "/api/signal/generate": {
            "get": {
                "operationId": "getSignalGenerate",
                "summary": "Generate trading signal",
                "description": "Generate a trading signal using the default analysis pipeline.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Signal generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/signal/advanced": {
            "get": {
                "operationId": "getSignalAdvanced",
                "summary": "Advanced signal generation",
                "description": "Generate an advanced trading signal using expanded analysis techniques and AI models.",
                "tags": ["Trading Signals"],
                "responses": {"200": {"description": "Advanced signal generated", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/indicators/all": {
            "get": {
                "operationId": "getIndicatorsAll",
                "summary": "All technical indicators",
                "description": "Return a comprehensive set of technical indicators for the specified symbol and timeframe.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "Indicators returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        },
        "/api/market/candles": {
            "get": {
                "operationId": "getMarketCandles",
                "summary": "Market candlestick data",
                "description": "Return candlestick (OHLCV) data for a given trading pair and timeframe.",
                "tags": ["Market Data"],
                "responses": {"200": {"description": "Candlestick data returned", "content": {"application/json": {"schema": {"type": "object", "additionalProperties": True}}}}}
            }
        }
    }
    # End of extended endpoints
    # Merge the extended endpoints and placeholder endpoints with the existing schema
    schema["paths"].update(extended_endpoints)
    schema["paths"].update(missing_endpoints)

    return schema
    """

@openapi_enhanced_bp.route('/openapi-enhanced.json', methods=['GET'])
# Duplicate endpoint removed - already defined above

@openapi_enhanced_bp.route('/openapi-chatgpt.json', methods=['GET'])
def get_chatgpt_optimized_openapi():
    """ChatGPT-optimized OpenAPI schema with simplified responses"""
    try:
        schema = get_enhanced_ultra_complete_openapi_schema()
        
        # Add ChatGPT-specific optimizations
        schema["info"]["description"] += "\n\nOptimized for ChatGPT Custom GPT Actions integration."
        
        # Simplify response schemas for ChatGPT consumption
        for path_data in schema["paths"].values():
            for method_data in path_data.values():
                if "responses" in method_data:
                    for response in method_data["responses"].values():
                        if "content" in response and "application/json" in response["content"]:
                            # Ensure all response schemas have additionalProperties: True
                            schema_def = response["content"]["application/json"]["schema"]
                            if isinstance(schema_def, dict) and schema_def.get("type") == "object":
                                schema_def["additionalProperties"] = True
        
        return jsonify(schema)
    except Exception as e:
        logger.error(f"Error generating ChatGPT-optimized OpenAPI schema: {e}")
        return jsonify({"error": "Failed to generate ChatGPT-optimized schema"}), 500

logger.info("🚀 Enhanced OpenAPI Schema module loaded successfully")