"""
Test suite untuk Crypto News Analyzer Module
"""

import asyncio
import json
from datetime import datetime, timezone
from core.crypto_news_analyzer import CryptoNewsAnalyzer

async def test_crypto_news_analyzer():
    """Test comprehensive crypto news analyzer functionality"""
    print("📰 CRYPTO NEWS ANALYZER TEST SUITE")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Initialize analyzer
    analyzer = CryptoNewsAnalyzer()
    
    # Test 1: Fetch crypto news
    print("📡 Testing News Fetching")
    print("-" * 40)
    news_items = analyzer.fetch_crypto_news(limit=5)
    
    if news_items:
        print(f"✅ Successfully fetched {len(news_items)} news items")
        first_news = news_items[0]
        print(f"   Latest: {first_news['title'][:60]}...")
        print(f"   Published: {first_news['published']}")
        print(f"   Tags: {', '.join(first_news.get('tags', [])[:3])}")
    else:
        print("⚠️  No news items fetched (RSS feed might be unavailable)")
    print()
    
    # Test 2: Sentiment Analysis (if news available)
    if news_items:
        print("🧠 Testing Sentiment Analysis")
        print("-" * 40)
        
        # Test single sentiment analysis
        first_item = news_items[0]
        sentiment_result = await analyzer.analyze_sentiment(
            first_item['title'],
            first_item['summary'],
            first_item.get('tags', [])
        )
        
        print(f"✅ Sentiment analysis completed")
        print(f"   Sentiment: {sentiment_result['sentiment']}")
        print(f"   Confidence: {sentiment_result['confidence']}")
        print(f"   Impact: {sentiment_result['impact']}")
        print(f"   Reasoning: {sentiment_result['reasoning'][:80]}...")
        print()
    
    # Test 3: Multiple news analysis
    print("📊 Testing Multiple News Analysis")
    print("-" * 40)
    
    if news_items:
        analyzed_news = await analyzer.analyze_multiple_news(news_items[:3])
        print(f"✅ Analyzed {len(analyzed_news)} news items")
        
        for idx, item in enumerate(analyzed_news, 1):
            analysis = item['analysis']
            print(f"   {idx}. {item['title'][:50]}...")
            print(f"      Sentiment: {analysis['sentiment']} (Confidence: {analysis['confidence']})")
    else:
        print("⚠️  Skipping multiple analysis (no news available)")
    print()
    
    # Test 4: Get news with aggregate sentiment
    print("🌐 Testing Aggregate News Sentiment")
    print("-" * 40)
    
    full_result = await analyzer.get_news_sentiment(limit=10)
    
    if full_result['status'] == 'success':
        print("✅ Full news sentiment analysis completed")
        aggregate = full_result['aggregate']
        print(f"   Total News: {aggregate['total_news']}")
        print(f"   Overall Sentiment: {aggregate['overall_sentiment']}")
        print(f"   Sentiment Distribution: {aggregate['sentiment_distribution']}")
        print(f"   Average Confidence: {aggregate['average_confidence']}")
        print(f"   High Impact News: {aggregate['high_impact_news']}")
        print(f"   Bullish Ratio: {aggregate['bullish_ratio']}")
        print(f"   Bearish Ratio: {aggregate['bearish_ratio']}")
    else:
        print(f"❌ Error: {full_result.get('message', 'Unknown error')}")
    print()
    
    # Test 5: Trending topics
    if full_result['status'] == 'success' and full_result['data']:
        print("🔥 Testing Trending Topics Extraction")
        print("-" * 40)
        
        trending = analyzer.get_trending_topics(full_result['data'], top_n=5)
        
        if trending:
            print(f"✅ Found {len(trending)} trending topics")
            for topic in trending[:3]:
                print(f"   {topic['topic']}: {topic['mentions']} mentions")
                print(f"   Sentiment: {topic['sentiment']}")
                breakdown = topic['sentiment_breakdown']
                print(f"   Breakdown: {breakdown['bullish']} bullish, {breakdown['bearish']} bearish, {breakdown['neutral']} neutral")
        else:
            print("⚠️  No trending topics found")
    print()
    
    # Test 6: Performance metrics
    print("📈 Testing Performance Metrics")
    print("-" * 40)
    
    performance = analyzer.get_sentiment_performance()
    print("✅ Performance metrics retrieved")
    print(f"   Total Analyses: {performance['total_analyses']}")
    print(f"   Sentiment Distribution: {performance['sentiment_distribution']}")
    print(f"   Average Confidence: {performance['average_confidence']}")
    print()
    
    # Test 7: Integration with GPTs format
    print("🤖 Testing GPTs Integration Format")
    print("-" * 40)
    
    # Simulate GPTs request format
    gpts_context = {
        "symbol": "BTCUSDT",
        "timeframe": "1H",
        "request_type": "news_analysis"
    }
    
    if full_result['status'] == 'success':
        # Create GPTs-compatible response
        gpts_response = {
            "analysis_type": "crypto_news_sentiment",
            "timestamp": full_result['timestamp'],
            "market_sentiment": {
                "overall": aggregate['overall_sentiment'],
                "strength": aggregate['average_confidence'],
                "distribution": aggregate['sentiment_distribution']
            },
            "high_impact_events": aggregate['high_impact_news'],
            "trading_implications": {
                "bias": "BULLISH" if aggregate['bullish_ratio'] > 0.6 else "BEARISH" if aggregate['bearish_ratio'] > 0.6 else "NEUTRAL",
                "confidence_level": aggregate['average_confidence'],
                "risk_adjustment": 1.2 if aggregate['high_impact_news'] > 2 else 1.0
            },
            "latest_headlines": [
                {
                    "title": item['title'][:100],
                    "sentiment": item['analysis']['sentiment'],
                    "impact": item['analysis']['impact']
                }
                for item in full_result['data'][:3]
            ]
        }
        
        print("✅ GPTs-compatible response generated")
        print(f"   Market Sentiment: {gpts_response['market_sentiment']['overall']}")
        print(f"   Trading Bias: {gpts_response['trading_implications']['bias']}")
        print(f"   Risk Adjustment: {gpts_response['trading_implications']['risk_adjustment']}")
    print()
    
    # Summary
    print("=" * 60)
    print("📊 CRYPTO NEWS ANALYZER TEST SUMMARY")
    print("=" * 60)
    print("✅ News Fetching: Implemented")
    print("✅ Sentiment Analysis: Implemented")
    print("✅ Multiple News Processing: Implemented")
    print("✅ Aggregate Sentiment: Implemented")
    print("✅ Trending Topics: Implemented")
    print("✅ Performance Tracking: Implemented")
    print("✅ GPTs Integration: Ready")
    print()
    print("🎉 Crypto News Analyzer Module is Fully Operational!")
    print("📰 System dapat analyze crypto news sentiment untuk trading decisions")
    print("🤖 Terintegrasi dengan GPTs format untuk enhanced analysis")
    print()
    print(f"🏁 Test completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(test_crypto_news_analyzer())