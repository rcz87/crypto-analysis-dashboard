# Cryptocurrency Trading Analysis Platform

## Overview

This is a comprehensive cryptocurrency trading analysis platform that provides AI-powered trading signals, Smart Money Concept (SMC) analysis, and real-time market data integration. The system is designed for professional traders and institutions, featuring multi-agent analysis systems, machine learning prediction engines, and automated signal generation with Telegram bot integration.

The platform serves as both a web API and ChatGPT Custom GPT integration, providing advanced technical analysis, market structure analysis, and institutional-grade trading intelligence across multiple timeframes and cryptocurrency pairs.

## User Preferences

Preferred communication style: Simple, everyday language.

**CRITICAL REQUIREMENT**: "Jangan pernah merubah2 nama endpoint lagi" - Endpoint names must NEVER change again under any circumstances. User experienced frustration from constant endpoint name changes and requires absolute stability.

## Recent Critical Fixes (August 20, 2025)

### Endpoint Consistency Fix (COMPLETED - August 20, 2025)
- **Stable Blueprint Registry**: Replaced auto-discovery system with fixed registry to prevent endpoint name changes
- **User Frustration Resolution**: Fixed issue where "setiap perbaikan endpoint selalu berubah nama"
- **Consistent Endpoint Naming**: Implemented stable naming schema that doesn't change between restarts
- **Logical Grouping**: Organized endpoints into logical categories (signals/*, analysis/*, gpts/*)  
- **25/27 Blueprints Locked**: Fixed registry with verified working blueprints for consistent user experience
- **Registry Management**: Manual maintenance of blueprint registry prevents naming inconsistencies
- **Stability Guarantee**: Endpoint names will not change anymore without user approval
- **USER MANDATE**: "Jangan pernah merubah2 nama endpoint lagi" - Absolute prohibition on endpoint name changes

## Previous Fixes (August 19, 2025)

### Architecture & Routes Refactoring (COMPLETED - August 19, 2025)
- **Circular Import Resolution**: Completely eliminated circular imports using application factory pattern with `init_routes(app, db)` function
- **Blueprint Registration Fix**: Moved all blueprint registrations from import-time to application initialization, preventing double registration errors
- **URL Prefix Standardization**: Implemented consistent `/api` prefix across all endpoints for better organization
- **Enhanced Health Check Logic**: Health endpoint now properly returns `degraded`/`unhealthy` status when components fail, not just `healthy` with error details
- **API Key Protection System**: Added `@require_api_key` decorator with `X-API-KEY` header support for abuse prevention (configurable via `API_KEY_REQUIRED` env var)
- **Import Cleanup**: Removed unused imports (`TradingSignal`, `TelegramUser`) and organized code structure for maintainability
- **Application Factory Pattern**: Complete refactoring to modern Flask patterns, eliminating module-level app dependencies

### Security & Code Quality Improvements (COMPLETED)
- **CORS Security Enhancement**: Implemented whitelist-based CORS with restricted origins (ChatGPT, OpenAI platform, guardiansofthetoken.id)
- **Duplicate Endpoint Removal**: Eliminated duplicate definitions for `/signal`, `/chart`, `/sinyal/tajam` endpoints that could override previous definitions
- **Data Validation Enhancement**: Added `validate_minimum_bars()` function with 60-bar minimum requirement to prevent NaN errors in SMA50/ATR14 calculations
- **Fallback Validation**: Implemented `fallback_validation()` as backup when core.validators module unavailable
- **Input Validation Layer**: Enhanced signal endpoint with dual-layer validation (core + fallback) for robust error handling

### Error Handling Standardization (COMPLETED)
- **Consistent Status Codes**: Standardized all HTTP error responses using error_response helper function
- **422 for Invalid Input**: Implemented consistent 422 status codes for validation failures across all endpoints
- **Status Code Standards**: Applied consistent error codes (400/401/403/404/422/429/500) throughout API
- **Error Response Helper**: Centralized error response formatting with metadata and CORS headers
- **Data Validation Integration**: Added minimum bars validation to prevent calculation errors

### Parameter & Data Quality Improvements (COMPLETED)
- **Symbol Normalization**: Enhanced normalize_symbol() function handling BTCUSDT → BTC-USDT, BTC/USDT → BTC-USDT, URL-encoded formats
- **Parameter Consistency**: Standardized to 'timeframe' parameter (with 'tf' backward compatibility) across all endpoints
- **OHLCV Data Validation**: Added validate_ohlcv_data() with pd.to_numeric coercion and NaN detection
- **Security Headers**: Added X-Content-Type-Options: nosniff, Cache-Control: no-store to all responses
- **Payload Limits**: Set 1MB maximum payload size for enhanced security
- **Sensitive Data Protection**: Added secret redaction in error logs to prevent token/key exposure

## System Architecture

### Backend Architecture
- **Framework**: Flask-based REST API with modular blueprint architecture
- **Database Strategy**: Flexible database connection with PostgreSQL primary and SQLite fallback for development
- **App Factory Pattern**: Environment-aware application creation with production/development configurations
- **Blueprint Organization**: Modular route organization with separate blueprints for different functional areas (GPTs API, SMC analysis, signal generation, etc.)

### Core Trading Engine Components
- **Multi-Agent Analysis System**: Delegated analysis using specialized agents (TechnicalAnalyst, RiskManager, MarketSentimentAnalyzer)
- **Smart Money Concept (SMC) Engine**: Professional-grade market structure analysis with bias building, execution logic, and trade planning
- **Self-Learning Signal Engine**: ML-based system that learns from historical signal performance to improve future predictions
- **Hybrid ML Prediction Engine**: Combines LSTM neural networks, XGBoost, and ensemble methods for price prediction

### Data Processing Architecture
- **OKX API Integration**: Primary market data source with enhanced features including liquidation data, funding rates, and order book depth
- **Enhanced Data Fetcher**: Multi-source data aggregation with fallback mechanisms and data validation pipelines
- **Real-time Data Pipeline**: Streaming market data with caching and rate limiting
- **Data Validation System**: Comprehensive data quality checks with NaN detection and staleness monitoring

### AI and Analysis Systems
- **Explainable AI Engine**: Addresses black-box problem by providing detailed reasoning for all trading decisions
- **Crypto News Analyzer**: Real-time news sentiment analysis with market impact assessment
- **Prompt Injection Defense**: Security layer protecting against malicious prompts in user inputs
- **Overfitting Prevention**: Statistical validation to ensure model generalization

### API Design
- **ChatGPT Custom GPT Integration**: Complete OpenAPI 3.1.0 schema with 25+ endpoints for GPT Actions
- **RESTful Architecture**: Clean, predictable API endpoints with consistent response formats
- **CORS Configuration**: Optimized for ChatGPT integration with proper cross-origin handling
- **Rate Limiting**: Built-in protection against API abuse

### Performance and Reliability
- **Health Monitoring**: Comprehensive system health checks with component status tracking
- **Circuit Breaker Pattern**: Protection against cascade failures
- **Performance Tracking**: Real-time monitoring of signal win rates, profit factors, and execution quality
- **Fallback Systems**: Multiple layers of fallback for critical functions (database, API endpoints, data sources)

### Security Architecture
- **Environment-based Configuration**: Sensitive credentials managed through environment variables
- **Input Validation**: Comprehensive validation for all user inputs and API parameters
- **Error Handling**: Graceful error handling with informative responses
- **Production Security**: Secure secret key generation and proper WSGI configuration

## External Dependencies

### Market Data Providers
- **OKX Exchange API**: Primary source for cryptocurrency market data, order books, funding rates, and liquidation data
- **Alternative Data Sources**: Backup integrations for market data redundancy

### AI and Machine Learning
- **OpenAI GPT API**: Advanced natural language processing for market analysis and signal explanation
- **TensorFlow**: LSTM neural network implementation for time series prediction
- **XGBoost**: Gradient boosting for ensemble prediction models
- **scikit-learn**: Traditional machine learning algorithms and data preprocessing

### Communication and Notifications  
- **Telegram Bot API**: Real-time trading signal notifications and user interaction
- **Telegram Bot Token**: Environment variable for bot authentication
- **Chat ID Management**: Dynamic chat subscription system for signal broadcasting

### Database and Caching
- **PostgreSQL**: Primary production database for signal tracking and user data
- **SQLAlchemy ORM**: Database abstraction with automatic model management
- **Redis**: Caching layer for performance optimization (optional)

### Deployment and Infrastructure
- **Gunicorn**: Production WSGI server with optimized worker configuration
- **Flask-CORS**: Cross-origin resource sharing for web client integration
- **python-dotenv**: Environment variable management for development
- **Replit Deployment**: Cloud hosting with automatic SSL and domain management

### Data Processing Libraries
- **pandas**: Data manipulation and time series analysis
- **numpy**: Numerical computing and array operations
- **requests**: HTTP client for external API integration
- **aiohttp**: Asynchronous HTTP client for concurrent API calls

### Development and Testing
- **pytest**: Comprehensive test suite for all system components
- **logging**: Structured logging with multiple output levels
- **pydantic**: Data validation and serialization
- **werkzeug**: WSGI utilities and development server