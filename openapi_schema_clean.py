#!/usr/bin/env python3
"""
Clean OpenAPI Schema Endpoint - Minimal working version
Focuses on providing 200 OK responses for documentation endpoints
"""

from flask import Blueprint, jsonify

openapi_bp = Blueprint('openapi', __name__)

@openapi_bp.route('/', methods=['GET'])
def schema_root():
    """Main schema endpoint - Basic stub"""
    return jsonify({
        "status": "ok",
        "message": "Base OpenAPI schema endpoint",
        "service": "crypto-trading-api",
        "version": "1.0.0",
        "endpoints": {
            "openapi.json": "Full OpenAPI specification",
            "api-docs": "Human-readable documentation",
            ".well-known/openapi.json": "OpenAPI discovery endpoint"
        }
    })

@openapi_bp.route('/openapi.json', methods=['GET'])
def openapi_spec():
    """Minimal OpenAPI specification"""
    return jsonify({
        "openapi": "3.1.0",
        "info": {
            "title": "Cryptocurrency Trading Signals API",
            "description": "AI-powered cryptocurrency trading signals with Smart Money Concept analysis",
            "version": "1.0.0"
        },
        "servers": [
            {
                "url": "https://32bb5b7b-cddc-40fa-a719-935c5c911eeb-00-1837nkastd9rq.kirk.replit.dev",
                "description": "Production Server"
            }
        ],
        "paths": {
            "/api/gpts/sinyal/tajam": {
                "post": {
                    "operationId": "getTradingSignal",
                    "summary": "Get AI-powered trading signals",
                    "description": "Generate cryptocurrency trading signals using Smart Money Concept analysis",
                    "parameters": [],
                    "responses": {
                        "200": {
                            "description": "Trading signal generated successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "signal": {"type": "string"},
                                            "confidence": {"type": "number"},
                                            "reasoning": {"type": "string"}
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
                    "summary": "Get API status",
                    "responses": {
                        "200": {
                            "description": "API status information"
                        }
                    }
                }
            }
        }
    })

@openapi_bp.route('/api-docs', methods=['GET'])
def api_docs():
    """Human-readable API documentation"""
    return jsonify({
        "title": "Cryptocurrency Trading Signals API",
        "description": "API untuk mendapatkan sinyal trading cryptocurrency dengan analisis Smart Money Concept",
        "version": "1.0.0",
        "endpoints": {
            "GET /api/gpts/status": "Status kesehatan API",
            "POST /api/gpts/sinyal/tajam": "Analisis mendalam dengan AI",
            "GET /api/institutional/status": "Status institutional endpoints",
            "GET /api/enhanced/status": "Status enhanced signals",
            "GET /api/smc/status": "Status SMC analysis"
        },
        "openapi_spec": "/api/schema/openapi.json"
    })

@openapi_bp.route('/.well-known/openapi.json', methods=['GET'])
def openapi_wellknown():
    """OpenAPI discovery endpoint"""
    return openapi_spec()