#!/usr/bin/env python3
"""
OpenAPI Schema for ChatGPT Custom GPT Integration
Creates proper API specification that GPT can understand
"""

from flask import Blueprint, jsonify

openapi_bp = Blueprint('openapi', __name__)

def get_openapi_schema():
    """Generate OpenAPI 3.0 schema for ChatGPT Custom GPT"""
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Cryptocurrency Trading Signals API",
            "description": "API untuk analisis trading cryptocurrency dengan Smart Money Concept (SMC), technical analysis, dan AI-powered insights dalam bahasa Indonesia",
            "version": "1.0.0",
            "contact": {
                "name": "Crypto Trading API Support"
            }
        },
        "servers": [
            {
                "url": "https://32bb5b7b-cddc-40fa-a719-935c5c911eeb-00-1837nkastd9rq.kirk.replit.dev",
                "description": "Replit Production Server for ChatGPT Custom GPT"
            }
        ],
        "paths": {
            "/api/gpts/signal": {
                "get": {
                    "operationId": "getTradingSignal",
                    "summary": "Dapatkan sinyal trading cryptocurrency", 
                    "description": "Menganalisis pasar cryptocurrency menggunakan Smart Money Concept (SMC) dan memberikan rekomendasi BUY/SELL/NEUTRAL dengan confidence level",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string", "example": "BTC/USDT"},
                            "description": "Pasangan trading (BTC/USDT, ETH/USDT, SOL/USDT, dll)"
                        },
                        {
                            "name": "tf",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "enum": ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"], "default": "1h"},
                            "description": "Timeframe analisis (1m=1 menit, 5m=5 menit, 1h=1 jam, 1d=1 hari, dll)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Sinyal trading berhasil dibuat",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "signal": {"type": "string", "enum": ["BUY", "SELL", "STRONG_BUY", "STRONG_SELL", "NEUTRAL"]},
                                                    "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                                                    "current_price": {"type": "number"},
                                                    "entry_price": {"type": "number"},
                                                    "stop_loss": {"type": "number"},
                                                    "take_profit": {"type": "array", "items": {"type": "number"}},
                                                    "risk_reward_ratio": {"type": "string"},
                                                    "human_readable": {"type": "string"},
                                                    "timestamp": {"type": "string", "format": "date-time"},
                                                    "symbol": {"type": "string"},
                                                    "api_version": {"type": "string"},
                                                    "server_time": {"type": "string", "format": "date-time"},
                                                    "service": {"type": "string"}
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
                "get": {
                    "operationId": "getDeepAnalysis", 
                    "summary": "Analisis trading mendalam dengan naratif AI",
                    "description": "Memberikan analisis trading lengkap dengan penjelasan AI dalam bahasa Indonesia, termasuk SMC analysis, technical indicators, dan reasoning",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string", "example": "BTCUSDT"},
                            "description": "Pasangan trading (BTCUSDT, ETHUSDT, SOLUSDT, dll)"
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "enum": ["1M", "3M", "5M", "15M", "30M", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1Mo"], "default": "1H"},
                            "description": "Timeframe analisis (1M=1 menit, 5M=5 menit, 1H=1 jam, 1D=1 hari, dll)"
                        },
                        {
                            "name": "format",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "enum": ["json", "narrative", "both"], "default": "both"},
                            "description": "Format response"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Analisis trading berhasil dibuat",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "signal": {"type": "string"},
                                                    "confidence": {"type": "number"},
                                                    "current_price": {"type": "number"},
                                                    "analysis": {"type": "object"},
                                                    "narrative": {"type": "string"},
                                                    "reasoning": {"type": "string"},
                                                    "risk_management": {"type": "object"},
                                                    "smc_analysis": {"type": "object"},
                                                    "technical_indicators": {"type": "object"}
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
            "/api/gpts/orderbook": {
                "get": {
                    "operationId": "getOrderbook",
                    "summary": "Data orderbook real-time",
                    "description": "Mengambil data orderbook (bid/ask) dari OKX exchange dengan analisis market depth",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "BTC-USDT", "example": "BTC-USDT"},
                            "description": "Symbol trading (BTC-USDT, ETH-USDT, SOL-USDT, dll)"
                        },
                        {
                            "name": "depth",
                            "in": "query", 
                            "required": False,
                            "schema": {"type": "integer", "default": 20, "minimum": 5, "maximum": 50},
                            "description": "Jumlah level orderbook (5-50)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Data orderbook berhasil diambil",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "symbol": {"type": "string"},
                                                    "timestamp": {"type": "integer"},
                                                    "orderbook": {
                                                        "type": "object",
                                                        "properties": {
                                                            "bids": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}},
                                                            "asks": {"type": "array", "items": {"type": "array", "items": {"type": "number"}}}
                                                        }
                                                    },
                                                    "market_depth": {
                                                        "type": "object",
                                                        "properties": {
                                                            "best_bid": {"type": "number"},
                                                            "best_ask": {"type": "number"},
                                                            "spread": {"type": "number"},
                                                            "spread_percentage": {"type": "number"},
                                                            "total_bid_volume": {"type": "number"},
                                                            "total_ask_volume": {"type": "number"},
                                                            "bid_ask_ratio": {"type": "number"}
                                                        }
                                                    },
                                                    "significant_levels": {
                                                        "type": "object",
                                                        "properties": {
                                                            "support_levels": {"type": "array"},
                                                            "resistance_levels": {"type": "array"}
                                                        }
                                                    },
                                                    "analysis": {
                                                        "type": "object",
                                                        "properties": {
                                                            "market_sentiment": {"type": "string", "enum": ["bullish", "bearish"]},
                                                            "liquidity_quality": {"type": "string", "enum": ["good", "limited"]},
                                                            "spread_quality": {"type": "string", "enum": ["tight", "normal", "wide"]}
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
            "/api/gpts/market-depth": {
                "get": {
                    "operationId": "getMarketDepth",
                    "summary": "Analisis kedalaman market",
                    "description": "Analisis mendalam tentang market depth, pressure analysis, dan liquidity untuk trading decisions",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "BTC-USDT", "example": "BTC-USDT"},
                            "description": "Symbol trading"
                        },
                        {
                            "name": "levels",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 10, "minimum": 5, "maximum": 20},
                            "description": "Jumlah level depth analysis"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Analisis market depth berhasil",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "symbol": {"type": "string"},
                                                    "depth_levels": {"type": "integer"},
                                                    "market_depth_analysis": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "object",
                                                            "properties": {
                                                                "level": {"type": "integer"},
                                                                "bid_price": {"type": "number"},
                                                                "bid_volume": {"type": "number"},
                                                                "cumulative_bid_volume": {"type": "number"},
                                                                "ask_price": {"type": "number"},
                                                                "ask_volume": {"type": "number"},
                                                                "cumulative_ask_volume": {"type": "number"},
                                                                "imbalance": {"type": "number"}
                                                            }
                                                        }
                                                    },
                                                    "pressure_analysis": {
                                                        "type": "object",
                                                        "properties": {
                                                            "total_bid_pressure": {"type": "number"},
                                                            "total_ask_pressure": {"type": "number"},
                                                            "pressure_ratio": {"type": "number"},
                                                            "market_bias": {"type": "string", "enum": ["buying_pressure", "selling_pressure", "balanced"]}
                                                        }
                                                    },
                                                    "liquidity_analysis": {
                                                        "type": "object",
                                                        "properties": {
                                                            "avg_bid_size": {"type": "number"},
                                                            "avg_ask_size": {"type": "number"},
                                                            "depth_quality": {"type": "string", "enum": ["deep", "shallow"]},
                                                            "market_impact_1pct": {"type": "number"}
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
            "/api/gpts/indicators": {
                "get": {
                    "operationId": "getTechnicalIndicators",
                    "summary": "Indikator teknis lengkap (MACD, RSI, Stochastic, CCI, dll)",
                    "description": "Mengambil semua indikator teknis utama termasuk MACD/DIF/Signal, RSI, Stochastic, CCI, Bollinger Bands, EMA, Volume Delta, ATR, Williams %R, MFI untuk analisis trading comprehensive",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "BTC-USDT", "example": "BTC-USDT"},
                            "description": "Symbol trading (BTC-USDT, ETH-USDT, SOL-USDT, dll)"
                        },
                        {
                            "name": "timeframe",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "enum": ["1M", "3M", "5M", "15M", "30M", "1H", "2H", "4H", "6H", "8H", "12H", "1D", "3D", "1W", "1Mo"], "default": "1H"},
                            "description": "Timeframe untuk analisis indikator (1M=1 menit, 5M=5 menit, 1H=1 jam, 1D=1 hari, dll)"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Indikator teknis berhasil dihitung",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "symbol": {"type": "string"},
                                                    "timeframe": {"type": "string"},
                                                    "current_price": {"type": "number"},
                                                    "technical_indicators": {
                                                        "type": "object",
                                                        "properties": {
                                                            "rsi": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "value": {"type": "number"},
                                                                    "overbought": {"type": "boolean"},
                                                                    "oversold": {"type": "boolean"},
                                                                    "signal": {"type": "string", "enum": ["BUY", "SELL", "NEUTRAL"]}
                                                                }
                                                            },
                                                            "macd": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "macd": {"type": "number"},
                                                                    "signal": {"type": "number"},
                                                                    "histogram": {"type": "number"},
                                                                    "bullish": {"type": "boolean"},
                                                                    "trend": {"type": "string", "enum": ["BULLISH", "BEARISH"]}
                                                                }
                                                            },
                                                            "stochastic": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "k": {"type": "number"},
                                                                    "d": {"type": "number"},
                                                                    "signal": {"type": "string", "enum": ["BUY", "SELL", "NEUTRAL"]}
                                                                }
                                                            },
                                                            "cci": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "value": {"type": "number"},
                                                                    "signal": {"type": "string", "enum": ["BUY", "SELL", "NEUTRAL"]}
                                                                }
                                                            },
                                                            "volume_analysis": {
                                                                "type": "object",
                                                                "properties": {
                                                                    "current_volume": {"type": "number"},
                                                                    "volume_delta": {"type": "number"},
                                                                    "volume_spike": {"type": "boolean"},
                                                                    "volume_trend": {"type": "string", "enum": ["HIGH", "NORMAL", "LOW"]}
                                                                }
                                                            }
                                                        }
                                                    },
                                                    "market_summary": {
                                                        "type": "object",
                                                        "properties": {
                                                            "overall_trend": {"type": "string", "enum": ["BULLISH", "BEARISH"]},
                                                            "momentum": {"type": "string", "enum": ["STRONG", "WEAK"]},
                                                            "volatility": {"type": "string", "enum": ["HIGH", "NORMAL", "LOW"]}
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
            "/api/gpts/funding-rate": {
                "get": {
                    "operationId": "getFundingRate",
                    "summary": "Funding Rate dan Open Interest data",
                    "description": "Mengambil data funding rate, Open Interest (OI), dan analisis sentiment trader dari futures market",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "BTC-USDT", "example": "BTC-USDT"},
                            "description": "Symbol futures trading"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Data funding rate berhasil diambil",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "symbol": {"type": "string"},
                                                    "funding_rate": {
                                                        "type": "object",
                                                        "properties": {
                                                            "current_rate": {"type": "number"},
                                                            "rate_percent": {"type": "number"},
                                                            "next_funding_time": {"type": "string"},
                                                            "sentiment": {"type": "string", "enum": ["VERY_BULLISH", "BULLISH", "NEUTRAL", "BEARISH", "VERY_BEARISH"]},
                                                            "description": {"type": "string"},
                                                            "strength": {"type": "number"}
                                                        }
                                                    },
                                                    "open_interest": {
                                                        "type": "object",
                                                        "properties": {
                                                            "oi_contracts": {"type": "number"},
                                                            "oi_value_usd": {"type": "number"},
                                                            "oi_trend": {"type": "string", "enum": ["INCREASING", "DECREASING", "UNKNOWN"]}
                                                        }
                                                    },
                                                    "market_analysis": {
                                                        "type": "object",
                                                        "properties": {
                                                            "long_short_ratio": {"type": "string", "enum": ["LONGS_PAYING", "SHORTS_PAYING", "BALANCED"]},
                                                            "market_structure": {"type": "string", "enum": ["CONTANGO", "BACKWARDATION", "BALANCED"]},
                                                            "trader_sentiment": {"type": "string"},
                                                            "risk_assessment": {"type": "string", "enum": ["HIGH", "MEDIUM", "LOW"]}
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
            "/api/gpts/context/init": {
                "get": {
                    "operationId": "initializeGPTContext",
                    "summary": "Inisialisasi konteks GPT dengan Prompt Book",
                    "description": "Mengambil Prompt Book dan instruksi lengkap untuk menginisialisasi sesi GPT baru dengan preferensi analisis yang tepat",
                    "responses": {
                        "200": {
                            "description": "Konteks GPT berhasil diinisialisasi",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "data": {
                                                "type": "object",
                                                "properties": {
                                                    "context_prompt": {"type": "string", "description": "Prompt lengkap untuk GPT"},
                                                    "system_status": {"type": "object"},
                                                    "initialization_time": {"type": "string"},
                                                    "instructions": {"type": "string"}
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
            "/api/gpts/context/prompt-book": {
                "get": {
                    "operationId": "getPromptBook", 
                    "summary": "Ambil konfigurasi Prompt Book",
                    "description": "Mengambil konfigurasi Prompt Book lengkap untuk review atau debugging",
                    "responses": {
                        "200": {
                            "description": "Prompt Book configuration",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "data": {"type": "object"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/promptbook/": {
                "get": {
                    "operationId": "getPromptBookMinimal",
                    "summary": "Ambil Prompt Book dalam format minimal",
                    "description": "Mengambil konfigurasi Prompt Book dalam format JSON yang clean dan minimal untuk GPT integration",
                    "responses": {
                        "200": {
                            "description": "Minimal Prompt Book response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "promptbook": {
                                                "type": "object",
                                                "properties": {
                                                    "purpose": {"type": "string"},
                                                    "language": {"type": "string"},
                                                    "style": {"type": "string"},
                                                    "version": {"type": "string"},
                                                    "timeframes": {
                                                        "type": "object",
                                                        "properties": {
                                                            "supported": {"type": "array", "items": {"type": "string"}},
                                                            "active": {"type": "array", "items": {"type": "string"}},
                                                            "total_count": {"type": "integer"}
                                                        }
                                                    },
                                                    "features": {"type": "object"},
                                                    "endpoints": {"type": "object"}
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
            "/api/promptbook/init": {
                "get": {
                    "operationId": "initPromptBookContext",
                    "summary": "Inisialisasi konteks GPT dengan prompt lengkap",
                    "description": "Mengambil prompt lengkap untuk inisialisasi konteks GPT baru dengan semua preferensi dan konfigurasi",
                    "responses": {
                        "200": {
                            "description": "GPT context initialized successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "context": {
                                                "type": "object",
                                                "properties": {
                                                    "full_prompt": {"type": "string"},
                                                    "prompt_length": {"type": "integer"},
                                                    "system_status": {"type": "object"},
                                                    "initialization_time": {"type": "string"},
                                                    "instructions": {"type": "string"}
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
            "/api/promptbook/status": {
                "get": {
                    "operationId": "getPromptBookStatus",
                    "summary": "Status kesehatan Prompt Book system",
                    "description": "Mengecek status dan kesehatan sistem Prompt Book untuk monitoring",
                    "responses": {
                        "200": {
                            "description": "Prompt Book system status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "system_health": {
                                                "type": "object",
                                                "properties": {
                                                    "promptbook_loaded": {"type": "boolean"},
                                                    "version": {"type": "string"},
                                                    "supported_timeframes": {"type": "integer"},
                                                    "total_endpoints": {"type": "integer"},
                                                    "language": {"type": "string"},
                                                    "features_enabled": {"type": "object"}
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
            "/api/smc/context": {
                "get": {
                    "operationId": "getSMCContext",
                    "summary": "Ambil konteks SMC structures untuk analisis",
                    "description": "Mengambil riwayat struktur Smart Money Concept terbaru untuk konteks analisis GPT",
                    "responses": {
                        "200": {
                            "description": "SMC context data with historical structures",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "context": {
                                                "type": "object",
                                                "properties": {
                                                    "last_bos": {"type": "object"},
                                                    "last_choch": {"type": "object"},
                                                    "last_bullish_ob": {"type": "array", "items": {"type": "object"}},
                                                    "last_bearish_ob": {"type": "array", "items": {"type": "object"}},
                                                    "last_fvg": {"type": "array", "items": {"type": "object"}},
                                                    "last_liquidity": {"type": "object"},
                                                    "memory_stats": {"type": "object"}
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
            "/api/smc/summary": {
                "get": {
                    "operationId": "getSMCSummary",
                    "summary": "Ringkasan struktur SMC aktif",
                    "description": "Mendapatkan ringkasan struktur Smart Money Concept yang aktif dan bias pasar",
                    "responses": {
                        "200": {
                            "description": "SMC structures summary with market bias",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "summary": {
                                                "type": "object",
                                                "properties": {
                                                    "active_structures": {"type": "object"},
                                                    "market_bias": {"type": "string", "enum": ["BULLISH", "BEARISH", "NEUTRAL"]},
                                                    "key_levels": {"type": "object"},
                                                    "last_significant_event": {"type": "object"}
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
            "/api/smc/status": {
                "get": {
                    "operationId": "getSMCStatus", 
                    "summary": "Status SMC Memory System",
                    "description": "Mengecek status dan kesehatan SMC Memory System untuk monitoring",
                    "responses": {
                        "200": {
                            "description": "SMC Memory system status",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string", "example": "success"},
                                            "system_status": {
                                                "type": "object",
                                                "properties": {
                                                    "memory_initialized": {"type": "boolean"},
                                                    "total_entries": {"type": "integer"},
                                                    "last_updated": {"type": "string"},
                                                    "symbols_tracked": {"type": "array", "items": {"type": "string"}},
                                                    "timeframes_tracked": {"type": "array", "items": {"type": "string"}},
                                                    "active_structures": {"type": "object"}
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
            "/api/gpts/status": {
                "get": {
                    "operationId": "getAPIStatus",
                    "summary": "Status kesehatan API",
                    "description": "Mengecek status dan kesehatan sistem API",
                    "responses": {
                        "200": {
                            "description": "Status API",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "api_version": {"type": "string"},
                                            "server_time": {"type": "string"},
                                            "core_features": {"type": "array", "items": {"type": "string"}}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/news/latest": {
                "get": {
                    "operationId": "getLatestNews",
                    "summary": "Berita crypto terbaru",
                    "description": "Mengambil berita cryptocurrency terbaru dari berbagai sumber untuk analisis sentiment dan konteks market",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10},
                            "description": "Jumlah berita yang diambil"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Berita crypto terbaru",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "data": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "title": {"type": "string"},
                                                        "url": {"type": "string"},
                                                        "published": {"type": "string"},
                                                        "source": {"type": "string"}
                                                    }
                                                }
                                            },
                                            "count": {"type": "integer"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/news/sentiment": {
                "get": {
                    "operationId": "getNewsSentiment",
                    "summary": "Analisis sentiment berita crypto",
                    "description": "Menganalisis sentiment berita cryptocurrency menggunakan AI untuk memahami dampak terhadap market",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10},
                            "description": "Jumlah berita untuk analisis"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Analisis sentiment berita",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "overall_sentiment": {"type": "string", "enum": ["BULLISH", "BEARISH", "NEUTRAL"]},
                                            "sentiment_score": {"type": "number"},
                                            "news_analysis": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "title": {"type": "string"},
                                                        "sentiment": {"type": "string"},
                                                        "confidence": {"type": "number"},
                                                        "market_impact": {"type": "string"}
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
            "/api/performance/stats": {
                "get": {
                    "operationId": "getPerformanceStats",
                    "summary": "Statistik performa trading",
                    "description": "Mengambil statistik performa trading termasuk win rate, Sharpe ratio, dan drawdown untuk evaluasi strategi",
                    "parameters": [
                        {
                            "name": "strategy",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "main", "enum": ["main", "smc", "ai_signals"]},
                            "description": "Strategi trading yang ingin dievaluasi"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Statistik performa trading",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "strategy": {"type": "string"},
                                            "win_rate": {"type": "number"},
                                            "sharpe_ratio": {"type": "number"},
                                            "max_drawdown": {"type": "number"},
                                            "total_trades": {"type": "integer"},
                                            "profit_factor": {"type": "number"},
                                            "calmar_ratio": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/gpts/state/signal-history": {
                "get": {
                    "operationId": "getSignalHistory",
                    "summary": "Riwayat sinyal trading",
                    "description": "Mengambil riwayat sinyal trading yang telah dihasilkan untuk analisis performa dan learning",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50},
                            "description": "Jumlah sinyal dalam riwayat"
                        },
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string"},
                            "description": "Filter berdasarkan symbol trading"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Riwayat sinyal trading",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "signals": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "signal_id": {"type": "string"},
                                                        "symbol": {"type": "string"},
                                                        "signal": {"type": "string"},
                                                        "confidence": {"type": "number"},
                                                        "timestamp": {"type": "string"},
                                                        "outcome": {"type": "string"}
                                                    }
                                                }
                                            },
                                            "total_count": {"type": "integer"},
                                            "performance_summary": {
                                                "type": "object",
                                                "properties": {
                                                    "accuracy": {"type": "number"},
                                                    "avg_confidence": {"type": "number"}
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
            "/api/performance/detailed-report": {
                "get": {
                    "operationId": "getDetailedPerformanceReport",
                    "summary": "Laporan performa trading detail",
                    "description": "Menghasilkan laporan performa trading lengkap dengan metrics Sharpe ratio, Sortino ratio, dan analisis drawdown",
                    "parameters": [
                        {
                            "name": "strategy",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "main", "enum": ["main", "smc", "ai_signals"]},
                            "description": "Strategi trading untuk analisis"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Laporan performa detail",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "sharpe_ratio": {"type": "number"},
                                            "sortino_ratio": {"type": "number"},
                                            "max_drawdown": {"type": "number"},
                                            "calmar_ratio": {"type": "number"},
                                            "profit_factor": {"type": "number"},
                                            "win_rate": {"type": "number"},
                                            "total_trades": {"type": "integer"},
                                            "strategy": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/performance/equity-curve": {
                "get": {
                    "operationId": "getEquityCurve",
                    "summary": "Data equity curve untuk visualisasi",
                    "description": "Mengambil data equity curve dan daily returns untuk analisis performa visual trading strategy",
                    "parameters": [
                        {
                            "name": "strategy",
                            "in": "query", 
                            "required": False,
                            "schema": {"type": "string", "default": "main"},
                            "description": "Strategi trading"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Data equity curve",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "equity_curve": {"type": "array", "items": {"type": "number"}},
                                            "daily_returns": {"type": "array", "items": {"type": "number"}},
                                            "timestamps": {"type": "array", "items": {"type": "string"}},
                                            "strategy": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/api/performance/backtest": {
                "get": {
                    "operationId": "getBacktestResults",
                    "summary": "Hasil backtesting strategy",
                    "description": "Menjalankan backtest trading strategy dengan data historis untuk validasi performa",
                    "parameters": [
                        {
                            "name": "strategy",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "main"},
                            "description": "Strategy untuk backtest"
                        },
                        {
                            "name": "symbol",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "string", "default": "BTCUSDT"},
                            "description": "Symbol untuk backtest"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Hasil backtest",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "total_return": {"type": "number"},
                                            "sharpe_ratio": {"type": "number"},
                                            "max_drawdown": {"type": "number"},
                                            "win_rate": {"type": "number"},
                                            "total_trades": {"type": "integer"},
                                            "backtest_period": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/api/performance/": {
            "get": {
                "operationId": "getPerformanceMetrics",
                "summary": "Dapatkan metrik performa trading lengkap",
                "description": "Mengambil metrik performa trading komprehensif dari database PostgreSQL termasuk Sharpe ratio, win rate, max drawdown, profit factor, dan statistik trading lainnya",
                "parameters": [
                    {
                        "name": "symbol",
                        "in": "query",
                        "description": "Filter berdasarkan symbol tertentu (contoh: BTCUSDT)",
                        "required": False,
                        "schema": {"type": "string"}
                    },
                    {
                        "name": "days",
                        "in": "query", 
                        "description": "Jumlah hari untuk analisis (default: 30)",
                        "required": False,
                        "schema": {"type": "integer", "minimum": 1, "maximum": 365}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Metrik performa berhasil diambil",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "success"},
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "total_signals": {"type": "integer", "description": "Total sinyal yang dieksekusi"},
                                                "win_rate": {"type": "number", "description": "Persentase win rate"},
                                                "sharpe_ratio": {"type": "number", "description": "Sharpe ratio untuk mengukur return vs risk"},
                                                "max_drawdown": {"type": "number", "description": "Maximum drawdown dalam persen"},
                                                "profit_factor": {"type": "number", "description": "Profit factor (total win / total loss)"},
                                                "total_pnl": {"type": "number", "description": "Total profit/loss dalam persen"},
                                                "average_pnl": {"type": "number", "description": "Rata-rata PnL per trade"},
                                                "best_trade": {"type": "number", "description": "Trade terbaik dalam persen"},
                                                "worst_trade": {"type": "number", "description": "Trade terburuk dalam persen"},
                                                "wins": {"type": "integer", "description": "Jumlah trade yang profit"},
                                                "losses": {"type": "integer", "description": "Jumlah trade yang loss"}
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
        "/api/performance/summary": {
            "get": {
                "operationId": "getPerformanceSummary",
                "summary": "Dapatkan ringkasan performa trading",
                "description": "Mengambil ringkasan performa trading yang disederhanakan untuk overview cepat",
                "responses": {
                    "200": {
                        "description": "Ringkasan performa berhasil diambil",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "success"},
                                        "data": {
                                            "type": "object",
                                            "properties": {
                                                "win_rate": {"type": "number", "description": "Win rate dalam persen"},
                                                "total_signals": {"type": "integer", "description": "Total sinyal"},
                                                "sharpe_ratio": {"type": "number", "description": "Sharpe ratio"},
                                                "total_pnl": {"type": "number", "description": "Total PnL persen"},
                                                "status": {"type": "string", "description": "Status profitabilitas"},
                                                "performance_grade": {"type": "string", "description": "Grade performa (A/B/C)"}
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
                        "signal": {"type": "string", "enum": ["BUY", "SELL", "STRONG_BUY", "STRONG_SELL", "NEUTRAL"]},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 100},
                        "current_price": {"type": "number"},
                        "reasoning": {"type": "string"}
                    }
                }
            }
        }
    }

@openapi_bp.route('/openapi.json', methods=['GET'])
def openapi_spec():
    """Serve OpenAPI specification for ChatGPT Custom GPT"""
    return jsonify(get_openapi_schema())

@openapi_bp.route('/.well-known/openapi.json', methods=['GET'])
def openapi_wellknown():
    """Alternative OpenAPI endpoint for GPT discovery"""
    return jsonify(get_openapi_schema())

@openapi_bp.route('/api-docs', methods=['GET'])
def api_docs():
    """Human-readable API documentation"""
    return jsonify({
        "title": "Cryptocurrency Trading Signals API",
        "description": "API untuk mendapatkan sinyal trading cryptocurrency dengan analisis Smart Money Concept",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/gpts/signal": "Dapatkan sinyal trading untuk symbol tertentu",
            "POST /api/gpts/sinyal/tajam": "Analisis mendalam dengan naratif AI", 
            "GET /api/gpts/status": "Status kesehatan API"
        },
        "openapi_spec": "/openapi.json"
    })