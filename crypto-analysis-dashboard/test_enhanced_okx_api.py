#!/usr/bin/env python3
"""
Test script untuk Enhanced OKX API Features
Testing semua fitur gratis yang bisa dimaksimalkan
"""

from core.enhanced_okx_fetcher import EnhancedOKXFetcher
import json
from datetime import datetime

def test_enhanced_okx_features():
    """
    Test semua fitur enhanced OKX API
    """
    
    print("🚀 Testing Enhanced OKX API Features...")
    
    fetcher = EnhancedOKXFetcher()
    
    # Test 1: Liquidation Orders
    print("\n🔥 Testing Liquidation Orders...")
    liquidations = fetcher.get_liquidation_orders(limit=10)
    if liquidations:
        print(f"✅ Fetched {len(liquidations)} liquidation orders")
        print(f"📊 Sample: {json.dumps(liquidations[0], indent=2)}")
    else:
        print("❌ Failed to fetch liquidation orders")
    
    # Test 2: Enhanced Liquidation Analysis
    print("\n📊 Testing Enhanced Liquidation Analysis...")
    liq_analysis = fetcher.get_enhanced_liquidation_analysis(limit=50)
    if liq_analysis.get('total_liquidations', 0) > 0:
        print(f"✅ Analysis completed:")
        print(f"   - Total liquidations: {liq_analysis['total_liquidations']}")
        print(f"   - Total loss: ${liq_analysis['total_loss']:,.2f}")
        print(f"   - Long liquidations: {liq_analysis['long_liquidations']}")
        print(f"   - Short liquidations: {liq_analysis['short_liquidations']}")
        print(f"   - Long ratio: {liq_analysis['long_ratio']:.2%}")
        print(f"   - Short ratio: {liq_analysis['short_ratio']:.2%}")
        
        if liq_analysis['top_symbols']:
            print(f"   - Top liquidated symbol: {list(liq_analysis['top_symbols'].keys())[0]}")
    else:
        print("❌ No liquidation analysis data")
    
    # Test 3: Position Tiers
    print("\n📊 Testing Position Tiers...")
    tiers = fetcher.get_position_tiers(symbol="BTC-USDT-SWAP")
    if tiers:
        print(f"✅ Fetched {len(tiers)} position tiers for BTC-USDT-SWAP")
        if tiers:
            print(f"📊 Max leverage: {tiers[0]['max_leverage']}x")
            print(f"📊 IMR: {tiers[0]['imr']:.4f}")
            print(f"📊 MMR: {tiers[0]['mmr']:.4f}")
    else:
        print("❌ Failed to fetch position tiers")
    
    # Test 4: Funding Rate History
    print("\n📈 Testing Funding Rate History...")
    funding_history = fetcher.get_funding_rate_history("BTC-USDT-SWAP", limit=10)
    if funding_history:
        print(f"✅ Fetched {len(funding_history)} funding rate records")
        latest = funding_history[0]
        print(f"📊 Latest funding rate: {latest['funding_rate']:.6f} ({latest['funding_rate'] * 100:.4f}%)")
    else:
        print("❌ Failed to fetch funding rate history")
    
    # Test 5: Price Limits
    print("\n⚡ Testing Price Limits...")
    price_limit = fetcher.get_price_limit("BTC-USDT-SWAP")
    if price_limit:
        print(f"✅ Price limits for BTC-USDT-SWAP:")
        print(f"   - Buy limit: ${price_limit['buy_limit']:,.2f}")
        print(f"   - Sell limit: ${price_limit['sell_limit']:,.2f}")
    else:
        print("❌ Failed to fetch price limits")
    
    # Test 6: Interest Rates
    print("\n💰 Testing Interest Rates...")
    interest_rates = fetcher.get_interest_rate_loan_quota("BTC")
    if interest_rates:
        print(f"✅ Fetched {len(interest_rates)} interest rate records")
        if interest_rates:
            btc_rate = interest_rates[0]
            print(f"📊 BTC interest rate: {btc_rate['interest_rate']:.6f}")
            print(f"📊 BTC loan quota: {btc_rate['loan_quota']:,.2f}")
    else:
        print("❌ Failed to fetch interest rates")
    
    # Test 7: Insurance Fund
    print("\n🛡️ Testing Insurance Fund...")
    insurance = fetcher.get_insurance_fund(currency="BTC")
    if insurance:
        print(f"✅ Fetched {len(insurance)} insurance fund records")
        if insurance:
            btc_insurance = insurance[0]
            print(f"📊 BTC insurance fund: {btc_insurance['amount']:,.2f} BTC")
    else:
        print("❌ Failed to fetch insurance fund data")
    
    # Test 8: Option Summary
    print("\n📊 Testing Option Summary...")
    option_summary = fetcher.get_option_summary("BTC")
    if option_summary:
        print(f"✅ Fetched {len(option_summary)} option records")
        if option_summary:
            sample_option = option_summary[0]
            print(f"📊 Sample option: {sample_option['inst_id']}")
            print(f"📊 Delta: {sample_option['delta']:.4f}")
            print(f"📊 Gamma: {sample_option['gamma']:.4f}")
    else:
        print("❌ Failed to fetch option summary")
    
    # Test 9: Comprehensive Market Data
    print("\n🔥 Testing Comprehensive Market Data...")
    comprehensive = fetcher.get_comprehensive_market_data("BTC-USDT-SWAP")
    if comprehensive and comprehensive.get('data'):
        print(f"✅ Comprehensive market data compiled for BTC-USDT-SWAP")
        data_keys = list(comprehensive['data'].keys())
        print(f"📊 Data sections: {', '.join(data_keys)}")
        
        # Check ticker data
        if comprehensive['data'].get('ticker'):
            ticker = comprehensive['data']['ticker'][0] if comprehensive['data']['ticker'] else {}
            if ticker:
                print(f"📊 Current price: ${float(ticker.get('last', 0)):,.2f}")
                print(f"📊 24h volume: {float(ticker.get('vol24h', 0)):,.2f}")
    else:
        print("❌ Failed to fetch comprehensive market data")
    
    print("\n📋 Summary:")
    print("✅ Enhanced OKX API testing completed")
    print("📊 Available enhanced features:")
    print("   - Real-time liquidation tracking")
    print("   - Enhanced liquidation analysis")
    print("   - Position tier information")
    print("   - Funding rate history")
    print("   - Price limit monitoring")
    print("   - Interest rate tracking")
    print("   - Insurance fund monitoring")
    print("   - Options market data")
    print("   - Comprehensive market analysis")

if __name__ == "__main__":
    test_enhanced_okx_features()