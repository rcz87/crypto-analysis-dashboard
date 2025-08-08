# Stateful AI Signal Engine - Integration Guide

## 🎯 Overview

**Stateful AI Signal Engine** adalah sistem pelacakan dan analytics yang lengkap untuk cryptocurrency trading platform Anda. Sistem ini menyimpan dan mengingat:

1. **History sinyal** yang pernah dikirim
2. **History pertanyaan** pengguna GPT dan responnya  
3. **Tracking interaksi** pengguna (klik, eksekusi, feedback)
4. **Analytics dan performance** tracking

## 🗄️ Database Schema

### **SignalHistory** - Menyimpan semua sinyal AI
```sql
- signal_id (unique): Identifier unik
- symbol: Trading pair (BTCUSDT, ETHUSDT)
- timeframe: Timeframe analysis (1H, 4H, 1D)
- action: BUY, SELL, HOLD
- confidence: Confidence level (0-100)
- entry_price, take_profit, stop_loss
- ai_reasoning: Penjelasan AI
- smc_analysis: Smart Money Concepts (JSON)
- technical_indicators: Data teknikal (JSON)
- is_executed: Apakah signal dieksekusi
- outcome: WIN, LOSS, BREAKEVEN, PENDING
- pnl_percentage: Profit/Loss %
```

### **GPTQueryLog** - Log semua query GPT
```sql
- query_id (unique): Identifier unik
- endpoint: API endpoint yang dipanggil
- request_params: Parameter request (JSON)
- user_query: Pertanyaan original user
- response_data: Data response (JSON)
- processing_time_ms: Waktu processing
- ai_model_used: Model AI (GPT-4o)
- tokens_used: Token yang digunakan
- confidence_score: Score confidence
```

### **UserInteraction** - Track interaksi user
```sql
- interaction_id (unique): Identifier unik
- signal_id: Reference ke signal
- interaction_type: CLICK, EXECUTE, FEEDBACK, SHARE
- interaction_source: TELEGRAM, CHAT_GPT, API
- interaction_data: Data tambahan (JSON)
- user_id: User identifier
```

## 🚀 API Endpoints

### **Base URL:** `/api/gpts/state/`

### 1. **Track Signal** - `POST /track-signal`
Menyimpan signal yang dihasilkan AI engine.

**Request:**
```json
{
  "signal_data": {
    "symbol": "BTCUSDT",
    "timeframe": "1H", 
    "action": "BUY",
    "confidence": 85.5,
    "entry_price": 45000.0,
    "take_profit": 46500.0,
    "stop_loss": 44200.0,
    "ai_reasoning": "Strong bullish momentum...",
    "smc_analysis": {
      "order_blocks": ["45000-45200"],
      "fvg": "44800-45000"
    }
  },
  "source": "ChatGPT"
}
```

**Response:**
```json
{
  "success": true,
  "signal_id": "sig_a1b2c3d4e5f6_1691234567",
  "processing_time_ms": 156,
  "api_version": "1.0.0"
}
```

### 2. **Signal History** - `GET /signal-history`
Mengambil history signal dengan filter.

**Query Params:**
- `limit`: Max records (default: 50, max: 100)
- `symbol`: Filter by trading pair
- `timeframe`: Filter by timeframe
- `days`: Filter by days (default: 7)

**Example:**
```
GET /api/gpts/state/signal-history?limit=20&symbol=BTCUSDT&days=30
```

### 3. **Execute Signal** - `POST /signal/{signal_id}/execute`
Mark signal sebagai executed.

**Request:**
```json
{
  "execution_price": 45100.0,
  "source": "TELEGRAM",
  "user_id": "telegram_123456"
}
```

### 4. **Log GPT Query** - `POST /log-query`
Log query dan response GPT.

**Request:**
```json
{
  "query_data": {
    "endpoint": "/api/gpts/signal",
    "method": "POST",
    "params": {"symbol": "BTCUSDT"},
    "user_query": "Give me Bitcoin signal"
  },
  "response_data": {
    "status_code": 200,
    "data": {"confidence": 85.5},
    "processing_time_ms": 1250
  }
}
```

### 5. **Analytics Endpoints**

#### **Signal Analytics** - `GET /analytics/signals?days=30`
Performance analytics untuk signals.

**Response:**
```json
{
  "analytics": {
    "total_signals": 156,
    "executed_signals": 89,
    "execution_rate": 57.05,
    "winning_signals": 67,
    "win_rate": 75.28,
    "top_symbols": [
      {"symbol": "BTCUSDT", "count": 45, "avg_confidence": 82.3}
    ]
  }
}
```

#### **Query Analytics** - `GET /analytics/queries?days=7`
Analytics untuk GPT queries.

#### **Interaction Analytics** - `GET /analytics/interactions?days=7`
Analytics untuk user interactions.

## 🔧 Integration Examples

### **1. Automatic Signal Tracking**
Gunakan decorator untuk auto-track signals dari existing endpoints:

```python
from core.stateful_signal_helper import track_signal_generation

@track_signal_generation(endpoint_name="/api/gpts/signal")
def get_trading_signal():
    # Your existing signal logic
    signal_data = generate_signal()
    return jsonify(signal_data)
```

### **2. Manual Signal Tracking**
Track signal secara manual:

```python
from core.enhanced_signal_integrator import track_signal

# Generate signal
signal_data = {
    "symbol": "BTCUSDT",
    "action": "BUY", 
    "confidence": 85.5,
    "entry_price": 45000.0
}

# Track signal
signal_id = track_signal(signal_data, source_engine="sharp_signal")
```

### **3. Telegram Integration**
Track interaction dari Telegram:

```python
from core.enhanced_signal_integrator import track_telegram_click

# Ketika user klik signal di Telegram
interaction_id = track_telegram_click(
    signal_id="sig_a1b2c3d4e5f6_1691234567",
    chat_id="123456789",
    username="trader_user"
)
```

### **4. Performance Update**
Update outcome signal setelah close position:

```python
from core.enhanced_signal_integrator import get_enhanced_integrator

integrator = get_enhanced_integrator()
success = integrator.update_signal_performance(
    signal_id="sig_a1b2c3d4e5f6_1691234567",
    outcome="WIN",
    pnl_percentage=12.5
)
```

## 📊 Analytics Dashboard

### **Comprehensive Analytics**
Get semua analytics data:

```python
from core.enhanced_signal_integrator import get_enhanced_integrator

integrator = get_enhanced_integrator()
analytics = integrator.get_comprehensive_analytics()

print(f"Signals today: {analytics['summary']['total_signals_today']}")
print(f"Win rate: {analytics['summary']['win_rate_month']}%")
print(f"Execution rate: {analytics['summary']['execution_rate_week']}%")
```

### **Cache Management**
Analytics di-cache otomatis untuk performance:

```python
from core.stateful_signal_helper import cache_analytics_data, get_cached_analytics_data

# Cache manual
cache_analytics_data("signals", 7, analytics_data, expire_seconds=300)

# Get cached data
cached = get_cached_analytics_data("signals", 7)
```

## 🛠️ Service Layer

### **StateManager** - Core Service
```python
from services.state_manager import get_state_manager

state_manager = get_state_manager()

# Save signal
signal_id = state_manager.save_signal_history(signal_data)

# Get history 
signals = state_manager.get_signal_history(limit=50)

# Track interaction
interaction_id = state_manager.track_user_interaction(signal_id, interaction_data)
```

### **Enhanced Integrator** - High-level Integration
```python
from core.enhanced_signal_integrator import get_enhanced_integrator

integrator = get_enhanced_integrator()

# Track dari any engine
signal_id = integrator.track_signal_from_engine(signal_data, "sharp_signal")

# Get analytics
analytics = integrator.get_comprehensive_analytics()
```

## 🔄 Data Flow

```
1. AI Engine generates signal
   ↓
2. Stateful Engine tracks signal → SignalHistory table
   ↓
3. User interacts (click/execute) → UserInteraction table
   ↓
4. GPT processes query → GPTQueryLog table
   ↓
5. Analytics aggregates data → Cached results
   ↓
6. Dashboard displays insights
```

## 🗂️ File Structure

```
📁 Stateful AI Signal Engine/
├── 📄 models.py                    # Database models (SignalHistory, GPTQueryLog, UserInteraction)
├── 📁 services/
│   └── 📄 state_manager.py         # Core state management service
├── 📁 api/
│   └── 📄 state_endpoints.py       # REST API endpoints
├── 📁 core/
│   ├── 📄 stateful_signal_helper.py     # Helper functions dan decorators
│   └── 📄 enhanced_signal_integrator.py # High-level integration layer
└── 📄 test_stateful_engine.py      # Test suite
```

## 📈 Benefits

### **For Developers:**
- ✅ **Automatic tracking** dengan decorators
- ✅ **Comprehensive analytics** out-of-the-box  
- ✅ **Performance monitoring** real-time
- ✅ **Easy integration** dengan existing code

### **For Business:**
- 📊 **Signal performance** tracking
- 👥 **User behavior** analytics
- 🎯 **Conversion rates** monitoring
- 🔍 **AI model** performance insights

### **For Users:**
- 📱 **Better Telegram** experience dengan tracking
- 🤖 **Smarter ChatGPT** integration
- 📈 **Performance feedback** untuk signals
- 🎯 **Personalized** recommendations

## 🚀 Production Ready

- ✅ **PostgreSQL** untuk persistent storage
- ✅ **Redis** untuk caching dan performance
- ✅ **Error handling** comprehensive
- ✅ **CORS** configured untuk ChatGPT
- ✅ **Logging** dan monitoring
- ✅ **Cleanup** mechanisms untuk maintenance

---

**Stateful AI Signal Engine** siap production dan terintegrasi penuh dengan cryptocurrency trading platform Anda! 🎯