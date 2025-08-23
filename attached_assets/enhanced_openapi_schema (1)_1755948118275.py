#!/usr/bin/env python3
"""
Enhanced Ultra-Complete OpenAPI Schema for ChatGPT Custom GPTs
Comprehensive documentation for all 29+ endpoints with enhanced descriptions
and ChatGPT-optimized schema definitions.
"""

from flask import Blueprint, jsonify
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
    Generate the most comprehensive OpenAPI 3.1.0 schema for ChatGPT Custom GPT integration
    Includes all 29+ discovered endpoints with enhanced descriptions and examples
    """
    
    schema = {
        "openapi": "3.1.0",
        "info": {
            "title": "Cryptocurrency Trading Analysis API - Ultra Complete Enhanced",
            "description": """
Advanced institutional-grade cryptocurrency trading analysis platform with AI-powered insights, 
Smart Money Concept (SMC) analysis, real-time market data, and comprehensive trading intelligence.

This API provides 29+ endpoints for complete trading workflow automation including:
• Real-time market data and technical analysis
• AI-powered trading signals with confidence scoring
• Smart Money Concept (SMC) pattern recognition  
• Risk management and portfolio optimization
• Telegram bot integration for instant notifications
• Performance tracking and analytics
• Multi-timeframe analysis capabilities
• Institutional-grade data validation

Perfect for ChatGPT Custom GPT integration, algorithmic trading, and professional market analysis.
            """.strip(),
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
        "paths": {
            # =================================================================
            # CORE SYSTEM ENDPOINTS
            # =================================================================
            "/health": {
                "get": {
                    "operationId": "getSystemHealth",
                    "summary": "System Health & Status Check",
                    "description": "Comprehensive system health check including database connectivity, API services, and component status monitoring",
                    "tags": ["System"],
                    "responses": {
                        "200": {
                            "description": "System health status retrieved successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "enum": ["healthy", "degraded", "unhealthy"], "example": "healthy"},
                                            "database": {"type": "string", "example": "connected"},
                                            "version": {"type": "string", "example": "3.1.0"},
                                            "uptime": {"type": "number", "example": 3600},
                                            "components": {
                                                "type": "object",
                                                "properties": {
                                                    "okx_api": {"type": "string", "example": "operational"},
                                                    "ai_engine": {"type": "string", "example": "operational"},
                                                    "telegram_bot": {"type": "string", "example": "operational"}
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
    # Merge the placeholder endpoints with the existing schema
    schema["paths"].update(missing_endpoints)

    return schema

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