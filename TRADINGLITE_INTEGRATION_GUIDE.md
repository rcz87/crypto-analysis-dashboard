# TradingLite Gold Integration Guide

## Overview
Integrasi TradingLite Gold subscription dengan sistem trading analysis kita. Fitur utama:
- 🔥 **Liquidity Heatmaps** - Real-time liquidity analysis
- 📊 **Order Flow Analysis** - Buy/sell pressure monitoring  
- 📨 **Auto-Forward ke Telegram** - Sinyal kuat otomatis dikirim ke Telegram
- 📝 **LitScript Generator** - Custom indicators untuk TradingLite

## Setup Steps

### 1. Connect TradingLite
```bash
curl -X POST http://localhost:5000/api/tradinglite/connect \
  -H "Content-Type: application/json" \
  -d '{
    "account_token": "YOUR_TRADINGLITE_TOKEN",
    "workspace_id": "YOUR_WORKSPACE_ID"
  }'
```

### 2. Setup Telegram Bridge
```bash
curl -X POST http://localhost:5000/api/tradinglite/telegram/setup \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_bot_token": "YOUR_BOT_TOKEN",
    "chat_ids": ["YOUR_CHAT_ID"]
  }'
```

### 3. Test Telegram Integration
```bash
curl -X POST http://localhost:5000/api/tradinglite/telegram/test
```

## API Endpoints

### Core Endpoints
- `POST /api/tradinglite/connect` - Connect ke TradingLite
- `GET /api/tradinglite/liquidity-analysis` - Get liquidity heatmap data
- `GET /api/tradinglite/order-flow-analysis` - Get order flow analysis
- `POST /api/tradinglite/combined-signal` - Combined signal (TradingLite + System)
- `GET /api/tradinglite/status` - Check connection status

### Telegram Bridge
- `POST /api/tradinglite/telegram/setup` - Setup Telegram forwarding
- `POST /api/tradinglite/telegram/test` - Test Telegram bridge
- `PUT /api/tradinglite/telegram/settings` - Update forwarding thresholds

### LitScript Generation
- `POST /api/tradinglite/litscript/generate` - Generate custom indicators

## Auto-Forward Settings

Default thresholds untuk auto-forward ke Telegram:
- **Liquidity Score** > 80 - Forward liquidity-based signals
- **Order Flow Pressure** > 70% - Forward order flow signals

### Update Thresholds
```bash
curl -X PUT http://localhost:5000/api/tradinglite/telegram/settings \
  -H "Content-Type: application/json" \
  -d '{
    "liquidity_score_min": 85,
    "order_flow_strength": 75,
    "enable_auto_forward": true
  }'
```

## Signal Flow

```
TradingLite WebSocket → Real-time Data
        ↓
Liquidity & Order Flow Analysis
        ↓
Signal Generation (Thresholds Check)
        ↓
Auto-Forward to Telegram (if enabled)
        ↓
Your Telegram Bot/Channel
```

## Example Telegram Notification

```
🟢 TRADINGLITE SIGNAL ALERT 🟢

📊 Signal Type: LIQUIDITY
📈 Action: BUY
💪 Strength: STRONG

📝 Reason: Strong bid liquidity dominance

📊 Liquidity Analysis:
• Score: 85.0/100
• Bid Dominance: ✅ Yes
• Walls Detected: 3

📈 Order Flow Analysis:
• Direction: BULLISH
• Buy Pressure: 75.0%
• Cumulative Delta: 1,500

⏰ 2025-08-22 12:30:00 UTC
🎯 Source: TradingLite Gold Analysis
```

## LitScript Examples

### Generate SMC Indicator
```bash
curl -X POST http://localhost:5000/api/tradinglite/litscript/generate \
  -H "Content-Type: application/json" \
  -d '{"indicator_type": "smc"}'
```

### Generate Liquidity Heatmap
```bash
curl -X POST http://localhost:5000/api/tradinglite/litscript/generate \
  -H "Content-Type: application/json" \
  -d '{"indicator_type": "liquidity"}'
```

### Generate Order Flow Indicator  
```bash
curl -X POST http://localhost:5000/api/tradinglite/litscript/generate \
  -H "Content-Type: application/json" \
  -d '{"indicator_type": "orderflow"}'
```

## Environment Variables

Required:
- `TRADINGLITE_TOKEN` - Your TradingLite account token
- `TRADINGLITE_WORKSPACE` - Your workspace ID
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token (optional, for auto-forward)

## Troubleshooting

### Connection Failed
- Check your TradingLite credentials
- Ensure Gold subscription is active
- Verify workspace ID is correct

### Telegram Not Receiving Signals
- Check bot token is valid
- Verify chat ID is correct
- Ensure bot is admin in channel/group
- Check threshold settings

### No Data Available
- Wait a few seconds after connection
- Data starts flowing after WebSocket establishes
- Check `/api/tradinglite/status` for metrics

## Support

For issues with:
- **TradingLite API**: Contact TradingLite support
- **Telegram Bot**: Check @BotFather documentation
- **Integration**: Check system logs or restart service