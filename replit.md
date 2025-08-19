# Cryptocurrency Trading Analysis Platform

## Overview

This is a comprehensive cryptocurrency trading analysis platform that provides AI-powered trading signals, Smart Money Concept (SMC) analysis, and real-time market data integration. The system is designed for professional traders and institutions, featuring multi-agent analysis systems, machine learning prediction engines, and automated signal generation with Telegram bot integration.

The platform serves as both a web API and ChatGPT Custom GPT integration, providing advanced technical analysis, market structure analysis, and institutional-grade trading intelligence across multiple timeframes and cryptocurrency pairs.

## User Preferences

Preferred communication style: Simple, everyday language.

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