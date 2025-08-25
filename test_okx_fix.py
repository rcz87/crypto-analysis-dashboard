#!/usr/bin/env python3
"""
Quick test script to verify OKX fetcher fix
"""
import sys
import json
sys.path.append('.')

from core.okx_fetcher import OKXFetcher

def test_okx_fetcher():
    print("🧪 Testing OKX Fetcher Update...")
    
    fetcher = OKXFetcher()
    
    # Test ticker data
    print("\n📊 Testing ticker data...")
    ticker = fetcher.get_ticker_data('BTC-USDT')
    if ticker and 'last_price' in ticker:
        print(f"✅ Ticker success: ${ticker['last_price']:.2f}")
    else:
        print(f"❌ Ticker failed: {ticker}")
    
    # Test historical data (might trigger fallback)
    print("\n📈 Testing historical data...")
    hist = fetcher.get_historical_data('BTC-USDT', '1H', 2)
    
    print(f"Status: {hist.get('status', 'unknown')}")
    print(f"Count: {hist.get('count', 0)} candles")
    
    if hist.get('candles'):
        close_price = hist['candles'][0].get('close', 0)
        print(f"💰 Latest close price: ${close_price:.2f}")
        
        # Check if using real or fallback data
        base_price = hist.get('base_price_used', None)
        if base_price:
            print(f"📊 Base price used: ${base_price:.2f}")
            if base_price > 100000:
                print("✅ SUCCESS: Using real/updated price data!")
            else:
                print("❌ ISSUE: Still using old mock price")
        
        # Check if price looks realistic
        if close_price > 100000:
            print("✅ Price looks realistic (>$100k)")
        elif close_price > 50000:
            print("⚠️  Price updated but still low")
        else:
            print(f"❌ Price too low: ${close_price:.2f}")
    
    return hist

if __name__ == "__main__":
    test_okx_fetcher()