# CryptoSage AI Trading Analysis Platform

## Overview

CryptoSage AI is an institutional-grade cryptocurrency trading analysis platform that provides advanced trading signals using Smart Money Concept (SMC) analysis, machine learning predictions, and real-time market data. The platform features a comprehensive API designed for ChatGPT Custom GPTs integration, Telegram bot notifications, and professional trading analysis with explainable AI reasoning.

The system combines traditional technical analysis with modern SMC patterns (Change of Character, Fair Value Gaps, Order Blocks) and machine learning models to generate high-confidence trading signals. It includes comprehensive backtesting capabilities, risk management systems, and real-time market monitoring across multiple timeframes.

## Recent Changes

### August 24, 2025 - WebSocket OKX Integration Completed ✅
- **Status**: Fully integrated with all signal generation systems
- **WebSocket Infrastructure**: Flask-SocketIO with eventlet for async operations
- **Real-time Data Manager**: Central hub distributing live data to all trading components
- **Signal Enhancement**: Real-time signal enhancer adjusts entry/exit based on live data
- **Optimizations Implemented**:
  - Message batching with configurable intervals (1s for prices, 0.5s for signals)
  - Compression enabled with Flask-SocketIO compress=True
  - MessagePack binary encoding for large data structures
  - Separate worker threads for heavy processing (AI/ML computations)
  - Smart throttling - only sends significant changes (>0.1% price change)
- **Integration Points**:
  - Holly Signal Engine: Receives real-time data for enhanced signal generation
  - SMC Analysis: Updates levels based on live price action
  - AI Reasoning Engine: Analyzes real-time events for intelligent decisions
- **New API Endpoints**:
  - `/api/websocket/enhanced/status` - Full integration status
  - `/api/websocket/enhanced/trigger-analysis` - Manual trigger for analysis
  - `/api/websocket/enhanced/configure` - Configure thresholds and batching
- **Performance Metrics**: Built-in monitoring tracks messages/s, batch sizes, processing time
- **Benefits**: Better entry/exit timing, dynamic stop loss, enhanced confidence scores

### August 25, 2025 - HTTPS Production Deployment COMPLETED ✅
- **Status**: ✅ **HTTPS FULLY OPERATIONAL** - Enterprise-grade security deployment complete
- **Production Domain**: `https://guardiansofthetoken.id` - **LIVE and SECURE**
- **SSL/TLS Security**:
  - ✅ Valid Let's Encrypt certificate until November 23, 2025
  - ✅ TLSv1.3 encryption with AES_256_GCM_SHA384 cipher
  - ✅ Perfect SSL handshake and certificate verification
  - ✅ Subject Alternative Name match - no SSL errors
- **HTTPS Infrastructure**:
  - ✅ Port 80: HTTP → HTTPS redirect (301) working perfectly
  - ✅ Port 443: HTTPS traffic properly handled by nginx
  - ✅ Security headers: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
  - ✅ nginx reverse proxy: Stable SSL termination and backend routing
- **Container Status**: All healthy and operational with correct port mapping
  - crypto_trading_app: Healthy (0.0.0.0:5001->5000/tcp)
  - crypto_nginx: Running (0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp)
  - crypto_postgres: Connected and stable
- **Health Verification**: `curl https://guardiansofthetoken.id/health` returns JSON success
- **Achievement**: 🏆 **Production-ready HTTPS platform with enterprise security standards**

### August 24, 2025 - Telegram Integration Completed ✅
- **Status**: Fully operational and production-ready
- **Telegram Bot Integration**: Complete with professional signal delivery
- **API Endpoints**: `/api/gpts/telegram/status`, `/api/gpts/telegram/test`, `/api/gpts/telegram/send` all active
- **Features Verified**: 
  - Real-time trading signal notifications with confidence scores and AI narratives
  - Rich message formatting with professional styling and Indonesian localization
  - Multi-chat support for subscriber management
  - Automatic failover and error handling
  - Integration with AI reasoning engine for intelligent signal analysis
- **Security**: Bot token and chat credentials secured in environment variables
- **Testing Results**: All core functions tested and confirmed working (Message IDs: 44, 45, 48)

## User Preferences

**Communication:** Simple, everyday language.

**Deployment Workflow:** When fixing issues for VPS deployment:
1. 🔄 **Push fix** dari Replit → GitHub  
2. 🔄 **Pull fix** dari GitHub → VPS
3. 🔄 **Rebuild container** dengan perubahan terbaru

Always follow this sequence to ensure VPS gets the latest fixes.

## System Architecture

### Core Architecture Pattern
The application follows the **Flask Application Factory Pattern** to prevent circular imports and enable modular development. The main app is created through `create_app()` function with environment-aware configuration that automatically falls back from PostgreSQL to SQLite for local development.

### API Structure
- **RESTful API Design**: Primary endpoints under `/api/` prefix with consistent HTTP methods
- **Blueprint-based Modularization**: 25+ registered blueprints for different functional areas
- **Versioned Endpoints**: Support for `/api/v1/` and `/api/v2/` with backward compatibility
- **OpenAPI 3.1.0 Schema**: Complete schema documentation for ChatGPT Custom GPTs integration

### Authentication & Security
- **Optional API Key Protection**: Configurable via `API_KEY_REQUIRED` environment variable
- **Multiple Authentication Methods**: Support for both `X-API-KEY` header and `Authorization: Bearer` token
- **Rate Limiting**: Flask-Limiter integration with configurable limits per endpoint
- **Security Headers**: ProxyFix middleware for proper proxy handling and security headers

### Data Layer Architecture
- **Dual Database Support**: Production PostgreSQL with SQLite fallback for development
- **SQLAlchemy ORM**: With connection pooling, pre-ping health checks, and timeout management
- **Data Validation Pipeline**: Comprehensive validation for OHLCV data, NaN detection, and data quality scoring
- **Caching Strategy**: Multi-level caching with in-memory cache for frequently accessed data

### Trading Engine Components
- **Professional SMC Analyzer**: Advanced Smart Money Concept pattern recognition (CHoCH, FVG, Order Blocks)
- **Multi-Timeframe Analysis**: Synchronized analysis across multiple timeframes for confirmation
- **Machine Learning Engine**: Hybrid LSTM + XGBoost ensemble for price prediction
- **Signal Generation Engine**: Rule-based and AI-driven signal generation with confidence scoring
- **Risk Management System**: ATR-based position sizing and risk-reward optimization

### Real-time Data Integration
- **OKX API Integration**: Professional-grade market data fetching with rate limiting and error handling
- **Enhanced Data Fetcher**: Support for liquidation data, funding rates, and institutional metrics
- **Data Quality Assurance**: Real-time validation and fallback mechanisms for data integrity

### AI & Machine Learning Stack
- **Explainable AI Engine**: Transparent decision-making with detailed reasoning for each signal
- **Self-Learning System**: Continuous improvement based on signal performance tracking
- **Natural Language Generation**: Human-readable explanations and market narratives
- **Sentiment Analysis**: Integration with crypto news sources for market sentiment scoring

### Monitoring & Analytics
- **Performance Tracking**: Comprehensive signal performance monitoring and analytics
- **System Health Monitoring**: Real-time health checks for all system components
- **Audit Logging**: Detailed logging for all critical operations and decisions
- **Error Handling**: Graceful error handling with detailed error responses and fallback strategies

## External Dependencies

### Market Data Providers
- **OKX Exchange API**: Primary source for real-time and historical cryptocurrency market data, order book depth, funding rates, and liquidation data
- **Backup Data Sources**: Configurable fallback data sources for high availability

### Machine Learning & AI
- **TensorFlow/Keras**: LSTM neural networks for time series prediction and pattern recognition
- **XGBoost**: Gradient boosting for ensemble learning and feature importance analysis
- **Pandas/NumPy**: Data manipulation and numerical computing for technical analysis
- **Scikit-learn**: Additional machine learning utilities and preprocessing tools

### Communication & Notifications
- **Telegram Bot API**: Real-time trading signal notifications and bot interactions
- **Flask-CORS**: Cross-origin resource sharing for web frontend integration

### Infrastructure & Deployment
- **PostgreSQL**: Production database for signal tracking, performance analytics, and user data
- **SQLite**: Development and fallback database for local development
- **Gunicorn**: WSGI HTTP server for production deployment with optimized worker configuration
- **Flask-Limiter**: API rate limiting and request throttling
- **Redis** (Optional): Enhanced caching and session management for production scaling

### Development & Testing
- **Pytest**: Comprehensive test suite for all API endpoints and core functionality
- **Requests**: HTTP client library for external API integrations and testing
- **Flask-SQLAlchemy**: Database ORM with migration support and connection management

### Monitoring & Observability
- **Python Logging**: Structured logging with configurable levels and formatters
- **PSUtil**: System resource monitoring and performance metrics
- **Custom Health Checks**: Endpoint availability monitoring and dependency health verification