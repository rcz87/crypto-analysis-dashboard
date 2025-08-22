# Cryptocurrency Trading Analysis Platform

## Overview
This platform is a comprehensive AI-powered cryptocurrency trading analysis system designed for professional traders and institutions. It provides AI-powered trading signals, Smart Money Concept (SMC) analysis, and real-time market data integration. The system features multi-agent analysis, machine learning prediction engines, and automated signal generation with Telegram bot integration. It functions as both a web API and a ChatGPT Custom GPT, offering advanced technical analysis, market structure analysis, and institutional-grade trading intelligence across various timeframes and crypto pairs.

## User Preferences
Preferred communication style: Simple, everyday language.
**CRITICAL REQUIREMENT**: "Jangan pernah merubah2 nama endpoint lagi" - Endpoint names must NEVER change again under any circumstances. User experienced frustration from constant endpoint name changes and requires absolute stability.

## System Architecture

### Backend Architecture
The system uses a Flask-based REST API with a modular blueprint architecture. It employs an application factory pattern for environment-aware application creation, supporting both production and development configurations. Database connections are flexible, with PostgreSQL as the primary and SQLite as a fallback.

### Core Trading Engine Components
The platform integrates a Multi-Agent Analysis System utilizing specialized agents, a professional-grade Smart Money Concept (SMC) Engine for market structure analysis, a Self-Learning Signal Engine that improves predictions based on historical performance, and a Hybrid ML Prediction Engine combining LSTM, XGBoost, and ensemble methods for price prediction.

### Data Processing Architecture
OKX API serves as the primary market data source, supplemented by an Enhanced Data Fetcher for multi-source data aggregation and validation. It includes a real-time data pipeline with caching and rate limiting, and a comprehensive data validation system to ensure data quality.

### AI and Analysis Systems
The system features an Explainable AI Engine to provide reasoning for trading decisions, a Crypto News Analyzer for real-time news sentiment, and Prompt Injection Defense for security. Overfitting prevention is managed through statistical validation.

### API Design
The platform offers a ChatGPT Custom GPT integration with a comprehensive OpenAPI 3.1.0 schema and over 25 endpoints. It follows a RESTful architecture with clean and consistent endpoints, optimized CORS configuration for ChatGPT, and built-in rate limiting.

### Performance and Reliability
Performance is ensured through comprehensive system health checks, a circuit breaker pattern to prevent cascade failures, and real-time tracking of signal win rates and profit factors. Multiple layers of fallback are implemented for critical functions.

### Security Architecture
Security is managed through environment-based configuration for sensitive credentials, comprehensive input validation, graceful error handling with informative responses, and secure secret key generation with proper WSGI configuration.

## Recent Updates (August 22, 2025)

### Advanced Trading Features Implemented
1. **Enhanced SMC Analysis** - CHoCH detection, Fair Value Gaps (FVG), Liquidity Sweeps, Breaker Blocks
2. **Multi-Timeframe Analysis** - 1H + 4H + Daily confluence with alignment scoring
3. **Risk Management System** - ATR-based SL/TP, Position Sizing, Kelly Criterion, Scaling Strategies

### New Endpoints Added
- `/api/advanced/smc-analysis` - Enhanced SMC with CHoCH, FVG, liquidity analysis
- `/api/advanced/multi-timeframe` - Multi-timeframe confluence (1H, 4H, Daily)
- `/api/advanced/risk-management` - ATR-based risk calculation and position sizing
- `/api/advanced/complete-analysis` - Combined analysis with all features
- `/api/advanced/status` - Advanced features status check

## External Dependencies

### Market Data Providers
- **OKX Exchange API**: Primary source for cryptocurrency market data, order books, funding rates, and liquidation data.
- **Alternative Data Sources**: Backup integrations for market data redundancy.

### AI and Machine Learning
- **OpenAI GPT API**: For advanced natural language processing, market analysis, and signal explanation.
- **TensorFlow**: For LSTM neural network implementation in time series prediction.
- **XGBoost**: For gradient boosting in ensemble prediction models.
- **scikit-learn**: For traditional machine learning algorithms and data preprocessing.

### Communication and Notifications
- **Telegram Bot API**: For real-time trading signal notifications and user interaction, managed by a Telegram Bot Token and dynamic chat ID system.

### Database and Caching
- **PostgreSQL**: Primary production database for signal tracking and user data.
- **SQLAlchemy ORM**: For database abstraction.
- **Redis**: Optional caching layer for performance optimization.

### Deployment and Infrastructure
- **Gunicorn**: Production WSGI server.
- **Flask-CORS**: For cross-origin resource sharing.
- **python-dotenv**: For environment variable management in development.

### Data Processing Libraries
- **pandas**: For data manipulation and time series analysis.
- **numpy**: For numerical computing and array operations.
- **requests**: For HTTP client operations with external APIs.
- **aiohttp**: For asynchronous HTTP client operations.

### Development and Testing
- **pytest**: For comprehensive testing.
- **logging**: For structured logging.
- **pydantic**: For data validation and serialization.
- **werkzeug**: For WSGI utilities and development server.