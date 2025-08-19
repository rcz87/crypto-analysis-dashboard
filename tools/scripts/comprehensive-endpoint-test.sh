#!/bin/bash
echo "🔍 COMPREHENSIVE ENDPOINT TESTING"
echo "=================================="
echo ""

BASE_URL="http://localhost:5050"

# Function to test endpoint
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local method="${3:-GET}"
    
    echo "Testing: $description"
    echo "URL: $BASE_URL$endpoint"
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTP_CODE:%{http_code}" "$BASE_URL$endpoint" 2>/dev/null)
    else
        response=$(curl -s -w "HTTP_CODE:%{http_code}" -X POST "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | grep -o "HTTP_CODE:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_CODE:[0-9]*$//')
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Status: $http_code - SUCCESS"
        echo "Response preview: $(echo "$body" | cut -c1-100)..."
    elif [ "$http_code" = "404" ]; then
        echo "❌ Status: $http_code - NOT FOUND"
    elif [ "$http_code" = "405" ]; then
        echo "⚠️  Status: $http_code - METHOD NOT ALLOWED"
    else
        echo "⚠️  Status: $http_code - $(echo "$body" | cut -c1-50)..."
    fi
    echo ""
}

echo "1. CORE ENDPOINTS"
echo "=================="
test_endpoint "/" "Main Platform"
test_endpoint "/health" "Health Check"
test_endpoint "/api/gpts/status" "GPTs Status"

echo "2. TRADING SIGNAL ENDPOINTS"
echo "============================"
test_endpoint "/api/gpts/sinyal/tajam" "Sharp Signal (Default)"
test_endpoint "/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H" "Sharp Signal (BTC 1H)"
test_endpoint "/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H&format=json" "Sharp Signal (JSON)"
test_endpoint "/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H&format=narrative" "Sharp Signal (Narrative)"
test_endpoint "/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H&format=both" "Sharp Signal (Both)"

echo "3. AI & ANALYSIS ENDPOINTS"
echo "==========================="
test_endpoint "/api/agent-mode/analyze" "Agent Mode Analysis"
test_endpoint "/api/ai/prediction" "AI Prediction"
test_endpoint "/api/ai/prediction?symbol=BTCUSDT" "AI Prediction (BTC)"
test_endpoint "/api/performance/stats" "Performance Stats"
test_endpoint "/api/performance/metrics" "Performance Metrics"

echo "4. STATEFUL AI ENDPOINTS"
echo "========================="
test_endpoint "/api/state/signal-history" "Signal History"
test_endpoint "/api/state/gpt-queries" "GPT Query Logs"
test_endpoint "/api/state/user-interactions" "User Interactions"

echo "5. SELF-LEARNING ENDPOINTS"
echo "==========================="
test_endpoint "/api/self-learning/evaluate-performance" "Performance Evaluation"
test_endpoint "/api/self-learning/update-models" "Model Updates"
test_endpoint "/api/self-learning/insights" "Learning Insights"

echo "6. CRYPTO NEWS ENDPOINTS"
echo "========================="
test_endpoint "/api/crypto-news/analyze" "News Analysis"
test_endpoint "/api/crypto-news/sentiment" "News Sentiment"
test_endpoint "/api/crypto-news/trending" "Trending Topics"

echo "7. ENHANCED OKX API ENDPOINTS"
echo "=============================="
test_endpoint "/api/okx/funding-rates" "Funding Rates"
test_endpoint "/api/okx/liquidation-analysis" "Liquidation Analysis"
test_endpoint "/api/okx/long-short-ratio" "Long/Short Ratio"
test_endpoint "/api/okx/volume-analysis" "Volume Analysis"

echo "8. SECURITY & MONITORING ENDPOINTS"
echo "==================================="
test_endpoint "/api/security/validate-prompt" "Prompt Validation"
test_endpoint "/api/monitoring/system-health" "System Health"

echo "9. TESTING POST METHODS"
echo "========================"
test_endpoint "/api/gpts/sinyal/tajam" "Sharp Signal (POST)" "POST"

echo ""
echo "=================================="
echo "✅ COMPREHENSIVE ENDPOINT TEST COMPLETED"
echo "Check results above for any failed endpoints"
echo "=================================="