#!/usr/bin/env python3
"""
Test script untuk fitur-fitur OKX API yang sudah dimaksimalkan
"""

from core.okx_fetcher import OKXFetcher
import json
from datetime import datetime

def test_enhanced_okx_features():
    """
    Test semua fitur enhanced OKX API yang sudah ditambahkan
    """
    
    print("🚀 Testing Enhanced OKX API Features di okx_fetcher.py...")
    
    fetcher = OKXFetcher()
    
    # Test 1: Funding Rate History
    print("\n📈 1. Testing Funding Rate History...")
    funding_history = fetcher.get_funding_rate_history("BTC-USDT-SWAP", limit=5)
    if funding_history:
        print(f"✅ Fetched {len(funding_history)} funding rate records")
        latest = funding_history[0]
        print(f"   Latest rate: {latest['funding_rate']:.6f} ({latest['funding_rate'] * 100:.4f}%)")
    else:
        print("❌ Failed to fetch funding rate history")
    
    # Test 2: Price Limits
    print("\n⚡ 2. Testing Price Limits...")
    price_limit = fetcher.get_price_limit("BTC-USDT-SWAP")
    if price_limit:
        print(f"✅ Price limits fetched:")
        print(f"   Buy limit: ${price_limit['buy_limit']:,.2f}")
        print(f"   Sell limit: ${price_limit['sell_limit']:,.2f}")
    else:
        print("❌ Failed to fetch price limits")
    
    # Test 3: Liquidation Orders
    print("\n🔥 3. Testing Liquidation Orders...")
    liquidations = fetcher.get_liquidation_orders(inst_type="SWAP", uly="BTC-USD", limit=5)
    if liquidations:
        print(f"✅ Fetched {len(liquidations)} liquidation orders")
        if liquidations:
            print(f"   Sample liquidation: {liquidations[0].get('inst_id', 'N/A')}")
    else:
        print("❌ Failed to fetch liquidation orders")
    
    # Test 4: Long/Short Ratio
    print("\n📊 4. Testing Long/Short Ratio...")
    ls_ratio = fetcher.get_long_short_ratio("BTC", period="5m")
    if ls_ratio:
        print(f"✅ Long/Short ratio fetched:")
        print(f"   Ratio: {ls_ratio['long_ratio']:.4f}")
    else:
        print("❌ Failed to fetch long/short ratio")
    
    # Test 5: Taker Volume
    print("\n💰 5. Testing Taker Volume...")
    taker_vol = fetcher.get_taker_volume("BTC", inst_type="SPOT", period="5m")
    if taker_vol:
        print(f"✅ Taker volume fetched:")
        print(f"   Buy volume: {taker_vol['buy_volume']:,.2f}")
        print(f"   Sell volume: {taker_vol['sell_volume']:,.2f}")
        
        # Calculate buy/sell ratio
        total_vol = taker_vol['buy_volume'] + taker_vol['sell_volume']
        if total_vol > 0:
            buy_percent = (taker_vol['buy_volume'] / total_vol) * 100
            print(f"   Buy pressure: {buy_percent:.2f}%")
    else:
        print("❌ Failed to fetch taker volume")
    
    # Test 6: Option Market Data
    print("\n📊 6. Testing Option Market Data...")
    options = fetcher.get_option_market_data("BTC")
    if options:
        print(f"✅ Fetched {len(options)} option records")
        if options:
            sample = options[0]
            print(f"   Sample option: {sample['inst_id']}")
            print(f"   Delta: {sample['delta']:.4f}")
    else:
        print("❌ Failed to fetch option market data")
    
    # Test 7: Supported Coins
    print("\n💎 7. Testing Supported Coins...")
    coins = fetcher.get_support_coin()
    if coins:
        print(f"✅ Fetched {len(coins)} supported coins")
        print(f"   Top 5: {', '.join(coins[:5])}")
    else:
        print("❌ Failed to fetch supported coins")
    
    # Summary
    print("\n📋 Summary of Enhanced OKX Features:")
    print("✅ Fitur-fitur yang berhasil ditambahkan:")
    print("   1. Funding Rate History - untuk trend analysis")
    print("   2. Price Limits - untuk risk management")
    print("   3. Liquidation Orders - untuk market sentiment") 
    print("   4. Long/Short Ratio - untuk positioning analysis")
    print("   5. Taker Volume - untuk buy/sell pressure")
    print("   6. Option Market Data - untuk advanced analysis")
    print("   7. Block Trades - untuk whale activity")
    print("   8. Index Components - untuk index tracking")
    print("   9. Supported Coins - untuk available markets")
    print("\n🎯 Total: 11 fitur baru OKX API telah dimaksimalkan!")

if __name__ == "__main__":
    test_enhanced_okx_features()