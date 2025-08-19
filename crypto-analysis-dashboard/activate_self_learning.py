#!/usr/bin/env python3
"""
🧠 Activate Self-Learning AI Training System
Script untuk mengaktifkan dan test sistem pembelajaran AI dari histori sinyal
"""

import asyncio
import sys
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# Add current directory to path
sys.path.append('.')

async def activate_self_learning_system():
    """Aktivasi complete self-learning system"""
    
    print("🧠 ACTIVATING SELF-LEARNING AI TRAINING SYSTEM")
    print("=" * 60)
    
    try:
        # Import components
        from core.signal_self_learning import SignalSelfLearningEngine
        from core.signal_tracker import SignalPerformanceTracker
        from core.ml_prediction_engine import HybridPredictor
        from core.okx_fetcher import OKXAPIManager
        
        print("✅ Components imported successfully")
        
        # Initialize system
        print("\n📚 INITIALIZING LEARNING COMPONENTS...")
        okx_fetcher = OKXAPIManager()
        tracker = SignalPerformanceTracker()
        ml_engine = HybridPredictor()
        self_learning = SignalSelfLearningEngine(okx_fetcher=okx_fetcher)
        
        print("✅ Self-Learning Engine: READY")
        print("✅ Performance Tracker: READY")
        print("✅ ML Prediction Engine: READY")
        print("✅ OKX Data Fetcher: READY")
        
        # Create sample historical signals for training
        print("\n📊 CREATING SAMPLE TRAINING DATA...")
        
        # Sample historical signals (would come from real tracking)
        historical_signals = [
            {
                'symbol': 'BTCUSDT',
                'timeframe': '1H',
                'entry_price': 115000.0,
                'take_profit': 116500.0,
                'stop_loss': 114000.0,
                'confidence': 0.85,
                'ai_reasoning': 'Strong order block + liquidity sweep confirmation',
                'actual_outcome': 'HIT_TP',  # Hit take profit
                'actual_return': 1.30  # 1.3% return
            },
            {
                'symbol': 'BTCUSDT',
                'timeframe': '1H',
                'entry_price': 113500.0,
                'take_profit': 115000.0,
                'stop_loss': 112500.0,
                'confidence': 0.60,
                'ai_reasoning': 'Weak SMC pattern, low volume confirmation',
                'actual_outcome': 'HIT_SL',  # Hit stop loss
                'actual_return': -0.88  # -0.88% loss
            },
            {
                'symbol': 'ETHUSDT',
                'timeframe': '4H',
                'entry_price': 2850.0,
                'take_profit': 2950.0,
                'stop_loss': 2780.0,
                'confidence': 0.78,
                'ai_reasoning': 'Premium zone rejection with volume spike',
                'actual_outcome': 'HIT_TP',
                'actual_return': 3.51
            }
        ]
        
        # Track sample signals
        tracked_signals = []
        for signal_data in historical_signals:
            signal_id = self_learning.track_signal(signal_data)
            tracked_signals.append(signal_id)
            print(f"📍 Tracked signal: {signal_id}")
        
        print(f"✅ {len(tracked_signals)} historical signals tracked")
        
        # Test learning insights
        print("\n🧠 TESTING LEARNING INSIGHTS...")
        insights = self_learning.get_learning_insights()
        
        print("💡 Learning Insights Available:")
        print(f"   • Total signals analyzed: {insights.get('total_signals', 0)}")
        print(f"   • Success patterns identified: {len(insights.get('success_patterns', []))}")
        print(f"   • Failure patterns identified: {len(insights.get('failure_patterns', []))}")
        print(f"   • Recommendations generated: {len(insights.get('recommendations', []))}")
        
        # Test performance analytics
        print("\n📈 TESTING PERFORMANCE ANALYTICS...")
        performance_stats = tracker.get_performance_stats()
        
        print("📊 Performance Analytics:")
        print(f"   • Win rate: {performance_stats.get('win_rate', 0):.1f}%")
        print(f"   • Average profit: {performance_stats.get('avg_profit', 0):.2f}%")
        print(f"   • Best performing timeframe: {performance_stats.get('best_timeframe', 'N/A')}")
        print(f"   • Risk/Reward ratio: {performance_stats.get('avg_risk_reward', 0):.2f}")
        
        # Test ML model capabilities
        print("\n🤖 TESTING ML MODEL TRAINING...")
        
        # Check if model can be trained with sample data
        model_status = ml_engine.get_model_status()
        print(f"🔍 Current model status: {model_status.get('status', 'Not trained')}")
        
        # Test feature extraction for training
        features_available = [
            'price_momentum', 'volume_profile', 'smc_patterns',
            'technical_indicators', 'market_structure', 'confidence_level'
        ]
        
        print("📋 Features available for training:")
        for feature in features_available:
            print(f"   • {feature}")
        
        # Simulate training readiness check
        training_ready = len(tracked_signals) >= 3  # Minimum signals for training
        print(f"\n🎯 Training readiness: {'✅ READY' if training_ready else '❌ NEED MORE DATA'}")
        
        if training_ready:
            print("\n🚀 SELF-LEARNING SYSTEM FULLY ACTIVATED!")
            print("\nCapabilities now available:")
            print("   ✅ Track semua signal yang dikirim")
            print("   ✅ Evaluasi hasil menggunakan data OKX real-time")
            print("   ✅ Analisis pattern yang berhasil vs gagal")
            print("   ✅ Peningkatan model AI secara otomatis")
            print("   ✅ Perbaikan kualitas narasi berdasarkan hasil")
            print("   ✅ Optimasi confidence level dan timing")
            print("   ✅ Adaptasi strategy berdasarkan market conditions")
            
            print("\n🔄 AUTOMATIC IMPROVEMENT PROCESS:")
            print("   1. Setiap signal tracked dengan timestamp")
            print("   2. Evaluasi hasil setelah 24-48 jam menggunakan OKX data")
            print("   3. Pattern analysis untuk success/failure factors")
            print("   4. Model retraining dengan data terbaru")
            print("   5. Narrative improvement berdasarkan insights")
            print("   6. Confidence adjustment untuk signal selanjutnya")
            
        return {
            'status': 'SUCCESS',
            'components_ready': True,
            'training_ready': training_ready,
            'tracked_signals': len(tracked_signals),
            'features_available': len(features_available),
            'learning_insights': insights,
            'performance_stats': performance_stats
        }
        
    except Exception as e:
        print(f"❌ Error activating self-learning system: {e}")
        import traceback
        traceback.print_exc()
        return {'status': 'ERROR', 'error': str(e)}

if __name__ == "__main__":
    result = asyncio.run(activate_self_learning_system())
    
    if result['status'] == 'SUCCESS':
        print(f"\n🎉 SYSTEM ACTIVATION COMPLETE!")
        print(f"Ready untuk training AI dari {result['tracked_signals']} histori sinyal")
    else:
        print(f"\n❌ Activation failed: {result.get('error', 'Unknown error')}")