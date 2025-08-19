# 🚀 Cryptocurrency Trading AI Platform

A cutting-edge cryptocurrency trading platform leveraging advanced machine learning, real-time market analysis, and intelligent automation for professional trading insights.

## ✨ Key Features

- **🤖 AI-Powered Analysis**: GPT-4o integration for intelligent market analysis
- **📊 Smart Money Concepts**: Professional SMC analysis with CHoCH, BOS, Order Blocks
- **⚡ Real-time Data**: OKX Exchange integration for authentic market data
- **📱 Telegram Notifications**: Real-time trading signal alerts
- **🔄 Multi-Timeframe Analysis**: 15M, 1H, 4H confluence analysis
- **💰 Risk Management**: Automated position sizing and capital protection
- **📈 Performance Tracking**: Signal win/loss analytics and optimization

## 🏗️ Architecture

### Core Components
- **GPTs API**: 22+ endpoints optimized for ChatGPT integration
- **Smart Signal Engine**: Multi-model ML prediction with technical analysis
- **Professional SMC Analyzer**: Advanced market structure analysis
- **Risk Manager**: Capital protection and position sizing
- **Alert System**: Customizable notifications with priority levels

### Technology Stack
- **Backend**: Python Flask, PostgreSQL
- **AI/ML**: OpenAI GPT-4o, NumPy, scikit-learn
- **Market Data**: OKX Exchange API
- **Notifications**: Telegram Bot API
- **Deployment**: Docker, Nginx, Gunicorn

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 16+
- OKX Exchange API credentials
- OpenAI API key

### Local Development
```bash
git clone https://github.com/your-username/crypto-trading-ai.git
cd crypto-trading-ai

# Install dependencies
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
python gpts_api_simple.py
```

### VPS Deployment (Hostinger/Linux)
```bash
# Auto deployment script
chmod +x deploy-vps.sh
./deploy-vps.sh
```

See [VPS_HOSTINGER_GUIDE.md](VPS_HOSTINGER_GUIDE.md) for detailed deployment instructions.

## 📚 API Documentation

### Core Endpoints
- `GET /health` - Health check
- `GET /api/gpts/market-data` - Real-time market data
- `GET /api/gpts/trading-signals` - AI trading signals
- `GET /api/gpts/smc-analysis` - Smart Money Concept analysis
- `GET /api/gpts/risk-analysis` - Risk management insights

### Authentication
Configure API keys in environment variables:
```env
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase
OPENAI_API_KEY=your_openai_api_key
```

## 🛠️ Configuration

### Environment Variables
```env
# Required
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret_key
OKX_PASSPHRASE=your_okx_passphrase
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:pass@localhost:5432/crypto_trading

# Optional
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

### Production Settings
- **Gunicorn**: Production WSGI server
- **Nginx**: Reverse proxy and SSL termination  
- **PostgreSQL**: Primary database
- **Docker**: Containerized deployment

## 📊 Performance

- **Response Time**: <500ms average
- **Throughput**: 1000+ requests/minute
- **Uptime**: 99.9% availability target
- **Memory Usage**: Optimized <100MB base
- **Docker Image**: Ultra-optimized 50-100MB

## 🔒 Security

- **API Rate Limiting**: 10 requests/second
- **Environment Isolation**: Production/development separation
- **Input Validation**: Pydantic-based validation
- **Error Handling**: Secure error responses
- **SSL/HTTPS**: Let's Encrypt integration

## 📈 Recent Updates

- **August 2025**: Deployment size optimization (8GB → 100MB)
- **SMC Integration**: Professional Smart Money Concept analysis
- **AI Enhancement**: GPT-4o integration for market analysis
- **Multi-Timeframe**: Confluence analysis across timeframes
- **Risk Management**: Automated position sizing
- **Alert System**: Enhanced notification system

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation**: [VPS_HOSTINGER_GUIDE.md](VPS_HOSTINGER_GUIDE.md)
- **Issues**: GitHub Issues
- **Deployment**: See deployment guides

## ⚠️ Disclaimer

This software is for educational and informational purposes only. Trading cryptocurrencies involves substantial risk of loss. Users should conduct their own research and consult with qualified financial advisors before making trading decisions.

---

**🎯 Built for professional traders seeking AI-powered market insights and automation.**