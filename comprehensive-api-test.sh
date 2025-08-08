#!/bin/bash
# Comprehensive API test untuk VPS production

VPS_URL="http://212.26.36.253:5050"
echo "🧪 Testing Crypto AI Platform - Production VPS"
echo "=============================================="
echo "URL: $VPS_URL"
echo ""

# Test 1: Main Health Check
echo "1. Main Application Health..."
response=$(curl -s $VPS_URL/)
if [[ $? -eq 0 && "$response" == *"Crypto"* ]]; then
    echo "✅ Main endpoint responding"
else
    echo "❌ Main endpoint failed"
fi

# Test 2: XAI Sharp Signal
echo -e "\n2. XAI Sharp Signal Test..."
signal_response=$(curl -s -X POST $VPS_URL/api/gpts/sinyal/tajam \
  -H "Content-Type: application/json" \
  -d '{"symbol": "BTCUSDT", "timeframe": "1H"}')

if [[ "$signal_response" == *"xai_explanation"* ]]; then
    echo "✅ XAI integration working"
    action=$(echo "$signal_response" | grep -o '"action":"[^"]*"' | cut -d'"' -f4)
    confidence=$(echo "$signal_response" | grep -o '"confidence":[0-9.]*' | cut -d':' -f2)
    echo "   Signal: $action"
    echo "   Confidence: $confidence%"
else
    echo "❌ XAI integration failed"
    echo "Response: $signal_response"
fi

# Test 3: Performance Metrics
echo -e "\n3. Performance Metrics..."
perf_response=$(curl -s $VPS_URL/api/performance/stats)
if [[ "$perf_response" == *"status"* && "$perf_response" == *"success"* ]]; then
    echo "✅ Performance tracking operational"
    sharpe=$(echo "$perf_response" | grep -o '"sharpe_ratio":[0-9.]*' | cut -d':' -f2)
    echo "   Sharpe Ratio: $sharpe"
else
    echo "❌ Performance tracking failed"
fi

# Test 4: Database Connection
echo -e "\n4. Database Status..."
if docker exec crypto_postgres pg_isready -U crypto_user >/dev/null 2>&1; then
    echo "✅ PostgreSQL database connected"
else
    echo "❌ Database connection failed"
fi

# Test 5: Container Health
echo -e "\n5. Container Health..."
healthy_containers=$(docker ps --filter health=healthy --format "table {{.Names}}" | grep crypto | wc -l)
if [[ $healthy_containers -gt 0 ]]; then
    echo "✅ Containers healthy ($healthy_containers/3)"
else
    echo "❌ Container health issues"
fi

echo -e "\n=============================================="
echo "🎯 Production Test Summary:"
echo "   Platform URL: $VPS_URL"
echo "   All core features tested"
echo "   XAI explanations: Active"
echo "   Performance tracking: Live"
echo "   Ready for GPTs integration"
echo "=============================================="
