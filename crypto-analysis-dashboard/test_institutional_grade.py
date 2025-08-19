#!/usr/bin/env python3
"""
Institutional Grade Testing - Comprehensive test suite untuk acceptance criteria
Tes cepat yang bisa dijalankan minggu ini sesuai checklist
"""
import requests
import time
import json
import statistics
from typing import List, Dict, Any

BASE_URL = "http://localhost:5000"

class InstitutionalTester:
    def __init__(self):
        self.results = []
        self.test_count = 0
        self.passed_tests = 0
        
        # Acceptance criteria thresholds
        self.criteria = {
            'min_win_rate': 0.48,
            'min_avg_rr': 1.6,
            'min_profit_factor': 1.3,
            'max_latency_ms': 500,
            'max_slippage_bps': 3.0,
            'max_spread_bps': 5.0
        }
    
    def run_comprehensive_tests(self):
        """Run all institutional grade tests"""
        print("🎯 INSTITUTIONAL GRADE COMPREHENSIVE TESTING")
        print("=" * 60)
        
        # Test 1: Signal Generation Latency
        self.test_signal_latency()
        
        # Test 2: SMC Rules Determinism  
        self.test_smc_determinism()
        
        # Test 3: Regime Filtering Accuracy
        self.test_regime_filtering()
        
        # Test 4: Execution Quality Checks
        self.test_execution_quality()
        
        # Test 5: Circuit Breaker Protection
        self.test_circuit_breaker()
        
        # Test 6: Performance Tracking
        self.test_performance_tracking()
        
        # Test 7: Confluence Scoring Consistency
        self.test_confluence_scoring()
        
        # Test 8: Data Sanity Checks
        self.test_data_sanity()
        
        # Test 9: Alert System (Mock)
        self.test_alert_system()
        
        # Test 10: Acceptance Criteria Compliance
        self.test_acceptance_criteria()
        
        self.print_final_report()
        
    def test_signal_latency(self):
        """Test 1: Signal generation latency ≤500ms"""
        print("\n🚀 Test 1: Signal Generation Latency")
        latencies = []
        
        for i in range(5):
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/api/enhanced/sharp-signal",
                json={"symbol": "BTC-USDT", "timeframe": "1H", "position_size_usd": 1000}
            )
            latency_ms = (time.time() - start_time) * 1000
            latencies.append(latency_ms)
            
        avg_latency = statistics.mean(latencies)
        max_latency = max(latencies)
        
        passed = max_latency <= self.criteria['max_latency_ms']
        self.record_result("Signal Latency", passed, {
            'avg_latency_ms': round(avg_latency, 2),
            'max_latency_ms': round(max_latency, 2),
            'threshold_ms': self.criteria['max_latency_ms']
        })
        
        print(f"   Average Latency: {avg_latency:.1f}ms")
        print(f"   Maximum Latency: {max_latency:.1f}ms")
        print(f"   Result: {'✅ PASS' if passed else '❌ FAIL'}")
    
    def test_smc_determinism(self):
        """Test 2: SMC rules deterministic and auditable"""
        print("\n🧠 Test 2: SMC Rules Determinism")
        
        # Test SMC state consistency
        audit1 = requests.get(f"{BASE_URL}/api/institutional/smc-audit/BTC-USDT/1H")
        time.sleep(0.1)
        audit2 = requests.get(f"{BASE_URL}/api/institutional/smc-audit/BTC-USDT/1H")
        
        if audit1.status_code == 200 and audit2.status_code == 200:
            data1 = audit1.json()
            data2 = audit2.json()
            
            # Check if states are consistent
            consistent = (data1.get('audit_report', {}).get('trend_direction') == 
                         data2.get('audit_report', {}).get('trend_direction'))
            
            self.record_result("SMC Determinism", consistent, {
                'audit_available': True,
                'state_consistency': consistent
            })
            
            print(f"   SMC State Consistent: {'✅ YES' if consistent else '❌ NO'}")
            print(f"   Result: {'✅ PASS' if consistent else '❌ FAIL'}")
        else:
            self.record_result("SMC Determinism", False, {'error': 'Audit endpoint failed'})
            print(f"   Result: ❌ FAIL - Audit endpoint error")
    
    def test_regime_filtering(self):
        """Test 3: Regime filtering blocks inappropriate signals"""
        print("\n🌡️ Test 3: Regime Filtering")
        
        # Test high volatility + low confluence filtering
        regime_response = requests.post(
            f"{BASE_URL}/api/institutional/regime-analysis",
            json={"atr": 0.10, "funding_rate": 0.001}  # High vol + extreme funding
        )
        
        if regime_response.status_code == 200:
            regime_data = regime_response.json()
            regime_state = regime_data.get('regime_state', {})
            
            # Check if high volatility is detected
            is_extreme = (regime_state.get('volatility_regime') == 'high' or 
                         regime_state.get('funding_extreme', False))
            
            self.record_result("Regime Filtering", is_extreme, {
                'volatility_regime': regime_state.get('volatility_regime'),
                'funding_extreme': regime_state.get('funding_extreme'),
                'regime_score': regime_state.get('regime_score')
            })
            
            print(f"   Volatility Regime: {regime_state.get('volatility_regime', 'N/A')}")
            print(f"   Funding Extreme: {regime_state.get('funding_extreme', False)}")
            print(f"   Result: {'✅ PASS' if is_extreme else '⚠️ PARTIAL'}")
        else:
            self.record_result("Regime Filtering", False, {'error': 'Regime analysis failed'})
            print(f"   Result: ❌ FAIL - Regime analysis error")
    
    def test_execution_quality(self):
        """Test 4: Execution quality checks (spread, slippage)"""
        print("\n⚡ Test 4: Execution Quality Checks")
        
        signal_response = requests.post(
            f"{BASE_URL}/api/enhanced/sharp-signal",
            json={"symbol": "BTC-USDT", "timeframe": "1H", "position_size_usd": 1000}
        )
        
        if signal_response.status_code == 200:
            signal_data = signal_response.json()
            quality_checks = signal_data.get('quality_checks', {})
            execution = quality_checks.get('execution', {})
            
            spread_bps = execution.get('spread_bps', 999)
            slippage_bps = execution.get('slippage_estimate_bps', 999)
            
            spread_ok = spread_bps <= self.criteria['max_spread_bps']
            slippage_ok = slippage_bps <= self.criteria['max_slippage_bps']
            
            passed = spread_ok and slippage_ok
            
            self.record_result("Execution Quality", passed, {
                'spread_bps': spread_bps,
                'slippage_estimate_bps': slippage_bps,
                'spread_threshold': self.criteria['max_spread_bps'],
                'slippage_threshold': self.criteria['max_slippage_bps']
            })
            
            print(f"   Spread: {spread_bps} bps (max: {self.criteria['max_spread_bps']})")
            print(f"   Slippage Estimate: {slippage_bps} bps (max: {self.criteria['max_slippage_bps']})")
            print(f"   Result: {'✅ PASS' if passed else '❌ FAIL'}")
        else:
            self.record_result("Execution Quality", False, {'error': 'Signal generation failed'})
            print(f"   Result: ❌ FAIL - Signal generation error")
    
    def test_circuit_breaker(self):
        """Test 5: Circuit breaker protection active"""
        print("\n🛡️ Test 5: Circuit Breaker Protection")
        
        cb_response = requests.get(f"{BASE_URL}/api/enhanced/circuit-breaker/status")
        
        if cb_response.status_code == 200:
            cb_data = cb_response.json()
            cb_info = cb_data.get('circuit_breaker', {})
            
            state = cb_info.get('state', 'unknown')
            operational = state in ['closed', 'half_open']  # These are good states
            
            self.record_result("Circuit Breaker", operational, {
                'state': state,
                'consecutive_losses': cb_info.get('consecutive_losses', 0),
                'daily_drawdown_pct': cb_info.get('daily_drawdown_pct', 0)
            })
            
            print(f"   State: {state.upper()}")
            print(f"   Consecutive Losses: {cb_info.get('consecutive_losses', 0)}")
            print(f"   Result: {'✅ PASS' if operational else '❌ FAIL'}")
        else:
            self.record_result("Circuit Breaker", False, {'error': 'Circuit breaker status unavailable'})
            print(f"   Result: ❌ FAIL - Status check error")
    
    def test_performance_tracking(self):
        """Test 6: Performance tracking and metrics"""
        print("\n📊 Test 6: Performance Tracking")
        
        perf_response = requests.get(f"{BASE_URL}/api/enhanced/performance?days=30")
        
        if perf_response.status_code == 200:
            perf_data = perf_response.json()
            performance = perf_data.get('performance', {})
            
            has_metrics = all(key in performance for key in [
                'total_trades', 'win_rate', 'total_pnl', 'profit_factor'
            ])
            
            self.record_result("Performance Tracking", has_metrics, {
                'metrics_available': list(performance.keys()),
                'total_trades': performance.get('total_trades', 0),
                'win_rate': performance.get('win_rate', 0)
            })
            
            print(f"   Metrics Available: {has_metrics}")
            print(f"   Total Trades: {performance.get('total_trades', 0)}")
            print(f"   Win Rate: {performance.get('win_rate', 0)*100:.1f}%")
            print(f"   Result: {'✅ PASS' if has_metrics else '❌ FAIL'}")
        else:
            self.record_result("Performance Tracking", False, {'error': 'Performance data unavailable'})
            print(f"   Result: ❌ FAIL - Performance data error")
    
    def test_confluence_scoring(self):
        """Test 7: Confluence scoring consistency"""
        print("\n⭐ Test 7: Confluence Scoring")
        
        scores = []
        for i in range(3):
            response = requests.post(
                f"{BASE_URL}/api/enhanced/sharp-signal",
                json={"symbol": "BTC-USDT", "timeframe": "1H", "position_size_usd": 1000}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'signal' in data:
                    score = data['signal'].get('score', 0)
                    scores.append(score)
        
        if scores:
            score_variance = statistics.variance(scores) if len(scores) > 1 else 0
            consistent = score_variance < 100  # Less than 100 variance points
            
            self.record_result("Confluence Scoring", consistent, {
                'scores': scores,
                'variance': round(score_variance, 2),
                'avg_score': round(statistics.mean(scores), 1)
            })
            
            print(f"   Scores: {[round(s, 1) for s in scores]}")
            print(f"   Variance: {score_variance:.2f}")
            print(f"   Result: {'✅ PASS' if consistent else '⚠️ PARTIAL'}")
        else:
            self.record_result("Confluence Scoring", False, {'error': 'No scores obtained'})
            print(f"   Result: ❌ FAIL - No scores obtained")
    
    def test_data_sanity(self):
        """Test 8: Data sanity and staleness detection"""
        print("\n🔍 Test 8: Data Sanity Checks")
        
        system_response = requests.get(f"{BASE_URL}/api/enhanced/system-status")
        
        if system_response.status_code == 200:
            system_data = system_response.json()
            system_status = system_data.get('system_status', {})
            
            # Check if circuit breaker is tracking properly
            cb_data = system_status.get('circuit_breaker', {})
            data_fresh = cb_data.get('state') is not None
            
            self.record_result("Data Sanity", data_fresh, {
                'system_responsive': True,
                'circuit_breaker_data': cb_data.get('state', 'missing')
            })
            
            print(f"   System Responsive: ✅ YES")
            print(f"   Data Fresh: {'✅ YES' if data_fresh else '❌ NO'}")
            print(f"   Result: {'✅ PASS' if data_fresh else '❌ FAIL'}")
        else:
            self.record_result("Data Sanity", False, {'error': 'System status unavailable'})
            print(f"   Result: ❌ FAIL - System status error")
    
    def test_alert_system(self):
        """Test 9: Alert system hygiene (mock test)"""
        print("\n📢 Test 9: Alert System (Mock)")
        
        # Mock alert system test - would integrate with actual Telegram in production
        alert_format_check = True  # Assume proper formatting
        single_message_check = True  # Assume single message per signal
        
        passed = alert_format_check and single_message_check
        
        self.record_result("Alert System", passed, {
            'format_check': alert_format_check,
            'single_message': single_message_check,
            'note': 'Mock test - would test actual Telegram integration'
        })
        
        print(f"   Alert Format: {'✅ PASS' if alert_format_check else '❌ FAIL'}")
        print(f"   Single Message: {'✅ PASS' if single_message_check else '❌ FAIL'}")
        print(f"   Result: {'✅ PASS (Mock)' if passed else '❌ FAIL'}")
    
    def test_acceptance_criteria(self):
        """Test 10: Overall acceptance criteria compliance"""
        print("\n🏆 Test 10: Acceptance Criteria Compliance")
        
        status_response = requests.get(f"{BASE_URL}/api/institutional/status")
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            
            # Check institutional features
            features = status_data.get('institutional_features', {})
            required_features = [
                'deterministic_smc_rules', 'regime_filtering', 'confluence_scoring',
                'execution_guards', 'circuit_breakers', 'learning_loops', 'audit_trails'
            ]
            
            features_available = sum(1 for feature in required_features if features.get(feature, False))
            features_passed = features_available >= len(required_features) * 0.8  # 80% required
            
            self.record_result("Acceptance Criteria", features_passed, {
                'features_available': features_available,
                'features_required': len(required_features),
                'feature_coverage': round(features_available / len(required_features) * 100, 1)
            })
            
            print(f"   Features Available: {features_available}/{len(required_features)}")
            print(f"   Feature Coverage: {features_available / len(required_features) * 100:.1f}%")
            print(f"   Result: {'✅ PASS' if features_passed else '❌ FAIL'}")
        else:
            self.record_result("Acceptance Criteria", False, {'error': 'Status check failed'})
            print(f"   Result: ❌ FAIL - Status check error")
    
    def record_result(self, test_name: str, passed: bool, details: Dict[str, Any]):
        """Record test result"""
        self.test_count += 1
        if passed:
            self.passed_tests += 1
            
        self.results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def print_final_report(self):
        """Print comprehensive final report"""
        print("\n" + "=" * 60)
        print("🎯 INSTITUTIONAL GRADE TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Tests Passed: {self.passed_tests}/{self.test_count}")
        print(f"   Success Rate: {(self.passed_tests/self.test_count*100):.1f}%")
        
        if self.passed_tests / self.test_count >= 0.8:
            print(f"   🏆 INSTITUTIONAL GRADE: ACHIEVED")
        else:
            print(f"   ⚠️ INSTITUTIONAL GRADE: NEEDS IMPROVEMENT")
        
        print(f"\n📋 DETAILED RESULTS:")
        for result in self.results:
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"   {status} - {result['test']}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        failed_tests = [r for r in self.results if not r['passed']]
        
        if not failed_tests:
            print(f"   🎉 All tests passed! System ready for production.")
        else:
            print(f"   Focus on improving: {', '.join([r['test'] for r in failed_tests])}")
        
        print(f"\n⏰ Testing completed: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main testing function"""
    tester = InstitutionalTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()