# 🚀 CryptoSage AI Trading Analysis Platform

Enterprise-grade cryptocurrency trading analysis platform powered by artificial intelligence, featuring Smart Money Concept (SMC) analysis, machine learning predictions, and real-time market data integration.

## 📋 Table of Contents

- [🏗️ Architecture Overview](#architecture-overview)
- [⚡ Quick Start](#quick-start)
- [🛠️ Installation](#installation)
- [🔧 Configuration](#configuration)
- [🚀 Deployment](#deployment)
- [🧪 Testing](#testing)
- [📊 API Documentation](#api-documentation)
- [🔍 Monitoring](#monitoring)
- [🛡️ Security](#security)
- [🔄 Maintenance](#maintenance)

## 🏗️ Architecture Overview

### Core Components
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask API     │───▶│  AI Engine      │───▶│  Trading Engine │
│   (50+ endpoints)│    │  (GPT-5 + ML)   │    │  (SMC Analysis) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   Redis Cache   │    │  Real-time Data │
│   Database      │    │   (Optional)    │    │  (OKX API)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Features
- **AI-Powered Analysis**: GPT-5 integration for intelligent signal generation
- **Smart Money Concept**: Advanced SMC pattern recognition (CHoCH, FVG, Order Blocks)
- **Machine Learning**: LSTM + XGBoost ensemble for price prediction
- **Real-time Data**: Live market data from OKX exchange
- **Telegram Integration**: Automated trading signal notifications
- **Auto-scaling**: Intelligent resource management and connection pooling

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (auto-configured in Docker)
- OpenAI API Key
- OKX API credentials (optional for full features)

### 1-Minute Setup
```bash
# Clone repository
git clone https://github.com/rcz87/crypto-analysis-dashboard.git
cd crypto-analysis-dashboard

# Setup environment
cp .env.example .env
nano .env  # Add your API keys

# Run with Docker
docker-compose -f docker-compose-vps.yml up -d

# Access the API
curl http://localhost:5050/health
```

## 🛠️ Installation

### Local Development
```bash
# Install Python dependencies
pip install -r requirements-prod.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from main import app, db; app.app_context().push(); db.create_all()"

# Start development server
python main.py
```

### Production VPS Deployment
```bash
# Automated deployment (recommended)
bash tools/scripts/deploy-vps-root.sh

# Manual deployment
docker-compose -f docker-compose-vps.yml up --build -d
```

## 🔧 Configuration

### Environment Variables (.env)

#### Required Variables
```bash
# OpenAI API (REQUIRED)
OPENAI_API_KEY=your_openai_api_key_here

# Database (auto-configured in Docker)
DATABASE_URL=postgresql://crypto_user:password@localhost:5432/crypto_trading

# Flask Configuration
FLASK_ENV=production
FLASK_SECRET_KEY=your_super_secret_key_change_this
```

#### Optional Variables
```bash
# OKX Exchange API (for live market data)
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase

# Telegram Bot (for signal notifications)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
ADMIN_CHAT_ID=your_telegram_chat_id

# Redis Cache (optional)
REDIS_URL=redis://localhost:6379/0

# Rate Limiting
API_RATE_LIMIT=100
API_RATE_LIMIT_WINDOW=3600
```

### Configuration Files
- `gunicorn.conf.py` - Production server configuration
- `nginx/nginx.conf` - Reverse proxy configuration
- `docker-compose-vps.yml` - Docker deployment configuration

## 🚀 Deployment

### VPS Deployment (Production)

#### Automated Deployment
```bash
# Run the automated deployment script
bash tools/scripts/deploy-vps-root.sh

# Script will:
# 1. Install Docker & Docker Compose
# 2. Setup environment file
# 3. Build and deploy containers
# 4. Configure health checks
# 5. Setup automatic updates (optional)
```

#### Manual Deployment Steps
```bash
# 1. Prepare environment
cp .env.vps.example .env
nano .env  # Configure your API keys

# 2. Deploy with Docker Compose
docker-compose -f docker-compose-vps.yml down
docker-compose -f docker-compose-vps.yml up --build -d

# 3. Verify deployment
docker-compose -f docker-compose-vps.yml ps
curl http://localhost:5050/health
```

#### Service URLs After Deployment
- **Main API**: `http://YOUR-VPS-IP:5050/`
- **Health Check**: `http://YOUR-VPS-IP:5050/health`
- **GPTs Integration**: `http://YOUR-VPS-IP:5050/api/gpts/sinyal/tajam`
- **Telegram Status**: `http://YOUR-VPS-IP:5050/api/gpts/telegram/status`

### Replit Deployment
```bash
# Start application workflow
# The platform will automatically detect and run the Flask app
```

## 🧪 Testing

### Available Test Scripts
```bash
# Comprehensive system test
python test_comprehensive_system_review.py

# API endpoints test
python test_25_endpoints.py

# Enhanced features test
python test_enhanced_features.py

# Telegram integration test
python test_telegram_signal.py

# ML prediction engine test
python test_ml_prediction_engine.py

# SMC analysis test
python test_smc_modular_system.py

# Smoke test (basic functionality)
python test_smoke.py
```

### API Testing with cURL
```bash
# Health check
curl http://localhost:5050/health

# GPTs main endpoint
curl "http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTC-USDT&timeframe=1H"

# System performance
curl http://localhost:5050/api/performance/stats

# Telegram status
curl http://localhost:5050/api/gpts/telegram/status
```

## 📊 API Documentation

### Core Endpoints

#### GPTs Integration
- `GET /api/gpts/sinyal/tajam` - Main trading signals endpoint
- `GET /api/gpts/status` - API status and health
- `GET /api/gpts/analisis/mendalam` - Deep market analysis

#### Telegram Integration
- `GET /api/gpts/telegram/status` - Telegram bot status
- `POST /api/gpts/telegram/send` - Send trading signals
- `GET /api/gpts/telegram/test` - Test message delivery

#### System Monitoring
- `GET /health` - Application health check
- `GET /api/performance/stats` - System performance metrics
- `GET /api/system/status` - Detailed system status

### API Authentication
```bash
# API Key in header (if enabled)
curl -H "X-API-Key: your_api_key" http://localhost:5050/api/endpoint

# Bearer token authentication
curl -H "Authorization: Bearer your_token" http://localhost:5050/api/endpoint
```

## 🔍 Monitoring

### Application Logs
```bash
# Docker deployment logs
docker-compose -f docker-compose-vps.yml logs -f

# Application-specific logs
docker logs crypto_trading_app -f

# Nginx logs
docker logs crypto_nginx -f
```

### Performance Monitoring
```bash
# System resource usage
docker stats

# Application metrics
curl http://localhost:5050/api/performance/stats

# Database performance
docker exec -it crypto_postgres psql -U crypto_user -d crypto_trading -c "\dt+"
```

### Health Monitoring
- **Health Endpoint**: `/health` - Basic application health
- **System Metrics**: Built-in system resource monitoring
- **Auto-scaling**: Intelligent connection pool management
- **Error Tracking**: Comprehensive error logging and alerting

## 🛡️ Security

### Security Features
- **Rate Limiting**: API endpoint protection
- **Input Validation**: Pydantic-based request validation
- **SQL Injection Protection**: SQLAlchemy ORM protection
- **Secure Headers**: Security headers via Nginx
- **Non-root Container**: Application runs with non-privileged user

### Security Best Practices
```bash
# Change default passwords
nano .env  # Update POSTGRES_PASSWORD and FLASK_SECRET_KEY

# Enable Firewall (on VPS)
ufw enable
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 5050  # Application

# SSL/TLS Configuration
# Update nginx/nginx.conf with your domain and SSL certificates
```

## 🔄 Maintenance

### Regular Maintenance Tasks

#### Daily
```bash
# Check application health
curl http://localhost:5050/health

# Monitor resource usage
docker stats --no-stream

# Review error logs
docker-compose -f docker-compose-vps.yml logs --since=24h | grep ERROR
```

#### Weekly
```bash
# Update application
git pull origin main
docker-compose -f docker-compose-vps.yml up -d --build

# Clean unused Docker resources
docker system prune -f

# Backup database
docker exec crypto_postgres pg_dump -U crypto_user crypto_trading > backup_$(date +%Y%m%d).sql
```

#### Monthly
```bash
# Update system packages (VPS)
sudo apt update && sudo apt upgrade -y

# Review performance metrics
curl http://localhost:5050/api/performance/stats

# Check disk usage
df -h
docker system df
```

### Common Issues and Solutions

#### Application Won't Start
```bash
# Check container logs
docker-compose -f docker-compose-vps.yml logs

# Verify environment variables
docker exec crypto_trading_app env | grep -E "(DATABASE_URL|OPENAI_API_KEY)"

# Restart services
docker-compose -f docker-compose-vps.yml restart
```

#### Database Connection Issues
```bash
# Check database container
docker logs crypto_postgres

# Test database connection
docker exec -it crypto_postgres psql -U crypto_user -d crypto_trading -c "SELECT 1;"

# Recreate database if needed
docker-compose -f docker-compose-vps.yml down -v
docker-compose -f docker-compose-vps.yml up -d
```

#### High Resource Usage
```bash
# Check resource usage
docker stats

# Scale down if needed (edit docker-compose-vps.yml)
# Reduce worker processes in gunicorn.conf.py

# Clear application cache
curl -X POST http://localhost:5050/api/system/clear-cache
```

### Scaling and Optimization

#### Horizontal Scaling
- Deploy multiple application containers
- Use load balancer (nginx upstream)
- Implement Redis for session management

#### Performance Optimization
- Enable Redis caching
- Optimize database queries
- Configure CDN for static assets
- Implement database connection pooling

### Automated Updates
```bash
# Setup automatic daily updates (optional during deployment)
# Creates cron job that runs at 3 AM daily:
# 0 3 * * * /usr/local/bin/crypto-app-update.sh >> /var/log/crypto-app-update.log 2>&1
```

---

## 📞 Support

### Repository Information
- **GitHub**: https://github.com/rcz87/crypto-analysis-dashboard
- **Platform**: Built for Replit with VPS deployment support
- **License**: Private repository

### Platform Architecture
- **Framework**: Flask with enterprise-grade architecture
- **Database**: PostgreSQL with SQLite fallback
- **AI Integration**: OpenAI GPT-5 with custom reasoning engine
- **Deployment**: Docker containers with Nginx reverse proxy

### Version Information
- **Current Version**: Production-ready
- **Last Updated**: August 2025
- **Python Version**: 3.11+
- **Docker Support**: Full containerization

---

**🚀 Ready for production deployment! Follow the deployment section to get started.**