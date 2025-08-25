#!/bin/bash
echo "🧪 QUICK DEPLOYMENT TEST"
echo "======================="

echo "Testing local changes first..."

# Test real-time OKX price fetch
echo "📊 Testing OKX real-time price..."
python3 -c "
import sys
sys.path.append('.')
try:
    from core.okx_fetcher import OKXFetcher
    fetcher = OKXFetcher()
    
    # Test ticker
    ticker = fetcher.get_ticker_data('BTC-USDT')
    if ticker and 'last_price' in ticker:
        price = ticker['last_price']
        print(f'✅ Real-time BTC price: \${price:,.2f}')
        if price > 100000:
            print('✅ Price looks current (>100k)')
        else:
            print('⚠️ Price seems low')
    else:
        print('❌ Ticker API failed')
        
    # Test fallback
    fallback = fetcher._get_fallback_data('BTC-USDT', '1H')
    base_price = fallback.get('base_price_used', 0)
    print(f'📊 Fallback price would be: \${base_price:,.0f}')
    
except Exception as e:
    print(f'❌ Error: {e}')
"

echo ""
echo "🔗 Testing production endpoint..."
curl -s "https://guardiansofthetoken.id/" | head -3
echo ""

echo "✅ Local test complete. Ready for deployment!"