# Cryptocurrency Trading Analysis Platform

## Overview
This platform is a comprehensive AI-powered cryptocurrency trading analysis system designed for professional traders and institutions. It provides AI-powered trading signals, Smart Money Concept (SMC) analysis, and real-time market data integration. The system features multi-agent analysis, machine learning prediction engines, and automated signal generation with Telegram bot integration. It functions as both a web API and a ChatGPT Custom GPT, offering advanced technical analysis, market structure analysis, and institutional-grade trading intelligence across various timeframes and crypto pairs. The business vision is to provide a robust, production-ready system with institutional-grade features to professional traders.

## User Preferences
- Preferred communication style: Simple, everyday language
- **CRITICAL REQUIREMENT**: "Jangan pernah merubah2 nama endpoint lagi" - Endpoint names must NEVER change again under any circumstances
- User experienced frustration from constant endpoint name changes and requires absolute stability

## System Architecture
The platform is built on a Flask backend with a Blueprint architecture, served by Gunicorn. PostgreSQL is used for the database with SQLAlchemy ORM. Core architectural decisions include an API versioning strategy (v1 deprecated, v2 current) to ensure stability, multi-level caching (Redis optional) and database pooling for performance, and asynchronous operations.

### Key Features:
- **Enhanced SMC Analysis**: Includes CHoCH, FVG, liquidity sweeps, order blocks, breaker blocks, swing point analysis, and market structure (BOS) detection.
- **Multi-Timeframe Analysis**: Analyzes 1H, 4H, and Daily timeframes for confluence, alignment detection, and key level identification.
- **Risk Management System**: Features ATR-based SL/TP, account risk-based position sizing, Kelly Criterion, scaling strategies, volatility regime classification, trailing stops, and R:R optimization.
- **AI-Powered Analysis**: Integrates with GPT-4 for advanced market reasoning, explainable AI, market narratives, confidence scoring, and comprehensive risk assessment.
- **Machine Learning Models**: Utilizes LSTM Networks, XGBoost, and ensemble methods (LSTM, XGBoost, Transformer, RL) for price movement prediction and signal generation, with continuous self-learning and overfitting prevention.
- **Real-Time Data Integration**: Connects to OKX Exchange via WebSocket for real-time price, order, funding, and liquidation data across multiple timeframes.
- **Telegram Bot Integration**: Provides instant signal notifications, performance updates, custom alerts, and interactive commands.

### Backend Module Organization:
- `core/`: Contains modules for enhanced SMC, multi-timeframe analysis, risk management, professional SMC analysis, OKX API integration, AI reasoning, core technical analysis, ML models, signal engine, multi-agent system, and Telegram integration.
- `api/`: Organizes endpoints for advanced trading, AI reasoning, SMC context, signal generation, market data, and utility functions.

### UI/UX Decisions:
The system primarily functions as a web API and ChatGPT Custom GPT, implying a focus on programmatic access and interaction rather than a dedicated graphical user interface. Documentation is self-service and interactive via `/api/docs/`, providing code examples for various languages.

## External Dependencies

### Market Data Providers
- **OKX Exchange API**: Primary source for all cryptocurrency market data.

### AI and Machine Learning
- **OpenAI GPT-4**: For advanced reasoning and analysis.
- **TensorFlow**: Used for LSTM neural networks.
- **XGBoost**: For gradient boosting models.
- **scikit-learn**: For various machine learning utilities and preprocessing.

### Communication Services
- **Telegram Bot API**: For real-time signal notifications and alerts.
- **WebSocket**: For real-time data streaming from exchanges.

### Infrastructure
- **PostgreSQL**: The primary relational database.
- **Redis**: Optional caching layer for performance.
- **Gunicorn**: Production WSGI server for the Flask application.
- **Flask-CORS**: Handles Cross-Origin Resource Sharing.

### Python Libraries
- **pandas**: For data manipulation and analysis.
- **numpy**: For numerical computing.
- **requests**: For making HTTP requests.
- **aiohttp**: For asynchronous HTTP client operations.
- **SQLAlchemy**: As the Object Relational Mapper (ORM) for database interactions.
- **python-dotenv**: For managing environment variables.