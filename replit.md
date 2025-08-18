# Cryptocurrency GPTs & Telegram Bot - Focused Platform

## Overview
This project is a focused cryptocurrency trading platform designed for GPTs integration and Telegram bot functionality. It provides Smart Money Concept (SMC) analysis, AI-powered trading insights, and real-time market data processing via a clean API. The platform aims to be a production-ready system capable of continuous self-improvement and robust security, offering advanced features like multi-timeframe analysis, risk management, and performance tracking. Its business vision includes scaling for sophisticated trading analysis via ChatGPT Custom GPT integration.

## User Preferences
Preferred communication style: Simple, everyday language.
User language preference: Indonesian (Bahasa Indonesia)
User confirmed project is comprehensive cryptocurrency trading AI platform with 65+ core modules
User wants analysis and recommendations for next steps in development
Successfully fixed all major deployment issues for VPS Hostinger deployment
Core modules now production-ready: OKX fetcher, SMC analyzer, signal generator, GPTs API routes
Project focus: GPTs API and Telegram bot functionality only
Architecture preference: Clean, minimal codebase without unnecessary dashboard components
Data integrity preference: Always use authentic data from real market sources, never mock/placeholder data

## System Architecture
The system architecture is streamlined and focused on core functionalities, prioritizing an API-driven interaction over a traditional GUI.

### UI/UX Decisions
Signal notifications are formatted professionally with HTML markup, proper number formatting, and clear displays for comprehensive technical indicators and AI market analysis. Dynamic emoji indicators are used to convey confidence levels of alerts.

### Technical Implementations
- **Backend**: Flask-based API (`gpts_api_simple.py`) as the main entry point, with a modular architecture.
- **Core Services**: All essential functionalities are organized within the `core/` directory.
- **AI Engine**: Utilizes OpenAI GPT-4o for market analysis and self-reflection, including a Stateful AI Signal Engine with self-learning and a Natural Language Narrative Enhancement feature for comprehensive explanations in Indonesian.
- **Machine Learning**: Incorporates Random Forest, XGBoost, and LSTM for predictions, leveraging real OKX data. A HybridPredictor combines these with an ensemble voting strategy, featuring 19 technical indicators and automatic retraining.
- **Telegram Integration**: Enhanced notification system with retry mechanism, professional signal formatting, and anti-spam protection.
- **Smart Money Concept (SMC) Analyzer**: Professional SMC analyzer detecting key SMC concepts (CHoCH, BOS, Order Blocks, FVG, liquidity sweeps, premium/discount zones), with an Auto-Context Injection System and enhanced pattern recognition.
- **Multi-Timeframe Analyzer**: Analyzes multiple timeframes (15M, 1H, 4H) for signal confirmation.
- **Risk Management Calculator**: Automatic position sizing based on account balance and risk tolerance.
- **Signal Performance Tracker**: Tracks win/loss ratios and analyzes performance.
- **Advanced Alert System**: Rule-based alert filtering with customizable conditions and priority levels, including real-time monitoring and webhook capabilities.
- **Volume Profile Analyzer**: Calculates Point of Control (POC) and Value Area.
- **Multi-Role Agent System**: Includes specialized trading agents (Technical Analyst, Sentiment Watcher, Risk Manager, Trade Executor, Narrative Maker).
- **Input Validation**: Pydantic-based validation for all GPTs endpoints.
- **Error Handling**: Global exception handlers provide structured error responses and mask internal errors.
- **Security Hardening**: Includes rate limiting, API authentication (including API key protection), secure logging, comprehensive vulnerability remediation, CORS headers, and prompt injection defense.
- **Database**: PostgreSQL for data persistence; Redis for caching and signal deduplication.
- **Crypto News Analyzer**: Real-time crypto news sentiment analysis using GPT-4o.
- **Enhanced OKX API Maximizer**: Optimized to maximum capacity with 1440 candles per request, 16 supported timeframes (1m-3M excluding 8H), real-time ticker, order book depth 400, 100% success rate with authentic OKX data, and comprehensive endpoint coverage for market data, ticker, and order book.
- **Enterprise-Grade Security & Quality Systems**: Includes Explainable AI Engine, Advanced Data Validation Pipeline, and Overfitting Prevention System.
- **Signal Engines**: Features an "Enhanced Signal Engine" (weight matrix) and a "Sharp Signal Engine" (AI reasoning, SMC, risk management) providing comprehensive market analysis with confidence levels and transparent reasoning.
- **Prompt Book Blueprint**: Dedicated Flask blueprint for clean API management with specific endpoints for ChatGPT Custom GPT compatibility.
- **SMC Zones Endpoint**: Comprehensive SMC zones data for chart visualization with filtering and proximity alerts.
- **Keep-Alive**: Anti-sleep system with self-ping mechanism.

### System Design Choices
The project prioritizes a focused architecture around GPTs API and Telegram bot functionalities. It emphasizes high reliability through retry mechanisms, comprehensive health monitoring, and robust error handling. The system is designed for scalability and production readiness, with a strong emphasis on security and continuous self-improvement capabilities. The design ensures minimal dependencies on specific dashboard components, making it flexible for integration into various front-end applications or direct API consumption. The core components are optimized for VPS deployment with a clean Flask architecture.

## External Dependencies

### APIs and Services
- **OKX Exchange API**: For authentic market data.
- **OpenAI GPT-4o**: For AI-powered market analysis and self-reflection.
- **Telegram Bot API**: For real-time notifications.
- **Redis**: For caching and signal deduplication.

### Key Libraries
- **Backend**: Flask, SQLAlchemy, pandas, numpy.
- **ML/AI**: scikit-learn, xgboost, tensorflow, 'ta' (technical analysis library).
- **Database**: PostgreSQL with psycopg2 driver.