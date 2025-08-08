# GPTs Integration Guide
## Cryptocurrency Trading Platform API

Base URL: `https://gpts.guardiansofthetoken.id/api/gpts/`

## 🎯 Available Endpoints

### 1. Trading Signal Analysis
**GET/POST** `/signal`

Get comprehensive trading signals with AI analysis, SMC indicators, and risk management.

**Parameters:**
- `symbol` (string): Trading pair (e.g., "BTCUSDT", "ETHUSDT")
- `timeframe` (string): Chart timeframe ("1H", "4H", "1D")
- `confidence` (float): Minimum confidence threshold (0.75 default)

**Example Request:**
```bash
GET https://gpts.guardiansofthetoken.id/api/gpts/signal?symbol=BTCUSDT&tf=1H
```

**Response:**
```json
{
  "signal": {
    "action": "BUY/SELL/HOLD",
    "confidence": 85.2,
    "entry_price": 45000.0,
    "take_profit": 46500.0,
    "stop_loss": 44200.0,
    "current_price": 45000.0,
    "risk_reward_ratio": 1.8,
    "ai_reasoning": "Technical analysis summary..."
  }
}
```

### 2. Enhanced Sharp Signal
**POST** `/sinyal/tajam`

Advanced signal with Smart Money Concepts, multi-timeframe analysis, and volume profile.

**Request Body:**
```json
{
  "symbol": "BTCUSDT",
  "timeframe": "1H"
}
```

**Response Features:**
- SMC analysis (Order Blocks, FVG, CHoCH)
- Multi-timeframe confluence
- Volume profile analysis
- Professional risk management
- AI narrative with reasoning

### 3. Market Narrative
**GET** `/narrative`

AI-powered market analysis and storytelling.

**Parameters:**
- `symbol` (string): Trading pair
- `timeframe` (string): Analysis timeframe

### 4. Chart Data
**GET** `/chart`

Real-time OHLCV data for charting.

**Parameters:**
- `symbol` (string): Trading pair
- `timeframe` (string): Chart timeframe
- `limit` (integer): Number of candles (default: 100)

### 5. API Status
**GET** `/status`

Check API health and available services.

## 🤖 ChatGPT Integration

### For ChatGPT Custom GPTs:

**Action Schema:**
```yaml
openapi: 3.0.0
info:
  title: Cryptocurrency Trading API
  version: 1.0.0
  description: Professional cryptocurrency trading signals with AI analysis
servers:
  - url: https://gpts.guardiansofthetoken.id
paths:
  /api/gpts/signal:
    get:
      operationId: getTradingSignal
      summary: Get trading signal analysis
      parameters:
        - name: symbol
          in: query
          schema:
            type: string
            default: BTCUSDT
        - name: tf
          in: query
          schema:
            type: string
            default: 1H
        - name: confidence
          in: query
          schema:
            type: number
            default: 0.75
      responses:
        '200':
          description: Trading signal with analysis
  /api/gpts/sinyal/tajam:
    post:
      operationId: getSharpSignal
      summary: Get enhanced trading signal with SMC analysis
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                symbol:
                  type: string
                  default: BTCUSDT
                timeframe:
                  type: string
                  default: 1H
      responses:
        '200':
          description: Enhanced signal with SMC and MTF analysis
```

### GPT Instructions:
```
You are a professional cryptocurrency trading assistant. Use the trading API to:

1. **Signal Analysis**: Call /api/gpts/signal for basic trading signals
2. **Advanced Analysis**: Use /api/gpts/sinyal/tajam for comprehensive SMC analysis
3. **Market Context**: Get /api/gpts/narrative for market storytelling

Always include:
- Current market sentiment
- Risk management advice
- Entry/exit strategy
- Confidence level interpretation

Format responses professionally with clear action items.
```

## 🔧 Development Workflow

### Current Setup:
- **Local Development**: Edit in Replit
- **Production**: Auto-deploy via GitHub Actions
- **Monitoring**: Real-time health checks

### Deployment Process:
1. Edit code in Replit
2. Commit and push to GitHub
3. Automatic deployment to VPS
4. Health verification

### URL Structure:
```
Production: https://gpts.guardiansofthetoken.id/api/gpts/
Development: http://localhost:5000/api/gpts/
Health Check: https://gpts.guardiansofthetoken.id/health
```

## 📊 Features

### ✅ Currently Available:
- Real-time OKX market data
- AI-powered analysis (OpenAI GPT-4o)
- Smart Money Concepts (SMC)
- Multi-timeframe analysis
- Risk management calculations
- Telegram notifications
- Professional signal formatting

### 🚀 Advanced Features:
- Volume profile analysis
- Order block detection
- Liquidity sweep identification
- Fair value gaps (FVG)
- Change of character (CHoCH)
- Break of structure (BOS)
- Premium/discount zone mapping

## 🔐 Security & Performance

- SSL/TLS encryption
- Rate limiting (20 req/s for API, 50 req/s for GPTs)
- CORS configured for ChatGPT
- Professional error handling
- Request validation
- Health monitoring

## 📱 Integration Examples

### For Trading Bots:
```python
import requests

response = requests.get(
    "https://gpts.guardiansofthetoken.id/api/gpts/signal",
    params={"symbol": "BTCUSDT", "tf": "1H"}
)
signal = response.json()
```

### For Web Applications:
```javascript
fetch('https://gpts.guardiansofthetoken.id/api/gpts/signal?symbol=BTCUSDT&tf=1H')
  .then(response => response.json())
  .then(data => console.log(data));
```

### For ChatGPT:
Simply ask: "Get me a trading signal for Bitcoin" and the GPT will automatically call the appropriate endpoint.

---

**Ready for ChatGPT Integration!** 🚀
Your cryptocurrency trading platform is now fully operational with professional-grade signals and AI analysis.