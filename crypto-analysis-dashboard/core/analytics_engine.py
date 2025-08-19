"""
Analytics Engine - Advanced Analytics & Evaluation
Menghitung performance metrics untuk signals dan trading
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy import func, and_, or_, desc

from models import GPTQueryLog, SignalHistory, UserInteraction, db
from core.redis_manager import redis_manager

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """
    Engine untuk advanced analytics dan evaluation
    """
    
    def __init__(self):
        self.redis_client = redis_manager.redis_client
        logger.info("📊 Analytics Engine initialized")
    
    def get_signal_analytics(self, days: int = 30, symbol: str = None, 
                           use_cache: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive signal analytics
        
        Args:
            days: Time period in days
            symbol: Filter by symbol
            use_cache: Whether to use cached results
            
        Returns:
            Signal analytics data
        """
        cache_key = f"signal_analytics_{days}d_{symbol or 'all'}"
        
        # Try cache first
        if use_cache:
            cached_data = self._get_cached_analytics('signals', f"{days}d")
            if cached_data and (not symbol or cached_data.get('symbol') == symbol):
                return cached_data
        
        try:
            date_from = datetime.utcnow() - timedelta(days=days)
            
            # Base query
            query = db.session.query(SignalHistory).filter(
                SignalHistory.created_at >= date_from
            )
            
            # Apply symbol filter
            if symbol:
                query = query.filter(SignalHistory.symbol == symbol)
            
            # Total signals
            total_signals = query.count()
            
            # Executed signals
            executed_signals = query.filter(SignalHistory.is_executed == True).count()
            execution_rate = (executed_signals / total_signals * 100) if total_signals > 0 else 0
            
            # Closed signals (with outcome)
            closed_signals = query.filter(SignalHistory.outcome.isnot(None)).count()
            
            # Winning signals
            winning_signals = query.filter(SignalHistory.outcome == 'WIN').count()
            losing_signals = query.filter(SignalHistory.outcome == 'LOSS').count()
            breakeven_signals = query.filter(SignalHistory.outcome == 'BREAKEVEN').count()
            
            # Win rate
            win_rate = (winning_signals / closed_signals * 100) if closed_signals > 0 else 0
            
            # Average confidence
            avg_confidence = query.with_entities(
                func.avg(SignalHistory.confidence)
            ).scalar() or 0
            
            # Total profit/loss
            total_pnl = query.filter(
                SignalHistory.pnl_percentage.isnot(None)
            ).with_entities(
                func.sum(SignalHistory.pnl_percentage)
            ).scalar() or 0
            
            # Average PnL per trade
            avg_pnl = query.filter(
                SignalHistory.pnl_percentage.isnot(None)
            ).with_entities(
                func.avg(SignalHistory.pnl_percentage)
            ).scalar() or 0
            
            # Best and worst trades
            best_trade = query.filter(
                SignalHistory.pnl_percentage.isnot(None)
            ).order_by(desc(SignalHistory.pnl_percentage)).first()
            
            worst_trade = query.filter(
                SignalHistory.pnl_percentage.isnot(None)
            ).order_by(SignalHistory.pnl_percentage).first()
            
            # Average Risk/Reward ratio
            avg_rr = query.filter(
                SignalHistory.risk_reward_ratio.isnot(None)
            ).with_entities(
                func.avg(SignalHistory.risk_reward_ratio)
            ).scalar() or 0
            
            # Top performing symbols
            top_symbols = db.session.query(
                SignalHistory.symbol,
                func.count(SignalHistory.id).label('total_signals'),
                func.avg(SignalHistory.confidence).label('avg_confidence'),
                func.sum(
                    func.case([(SignalHistory.outcome == 'WIN', 1)], else_=0)
                ).label('wins'),
                func.avg(SignalHistory.pnl_percentage).label('avg_pnl')
            ).filter(
                SignalHistory.created_at >= date_from
            ).group_by(
                SignalHistory.symbol
            ).order_by(
                desc('avg_pnl')
            ).limit(10).all()
            
            # Performance by timeframe
            timeframe_performance = db.session.query(
                SignalHistory.timeframe,
                func.count(SignalHistory.id).label('total_signals'),
                func.avg(SignalHistory.confidence).label('avg_confidence'),
                func.sum(
                    func.case([(SignalHistory.outcome == 'WIN', 1)], else_=0)
                ).label('wins'),
                func.count(
                    func.case([(SignalHistory.outcome.isnot(None), 1)], else_=None)
                ).label('closed_signals')
            ).filter(
                SignalHistory.created_at >= date_from
            ).group_by(
                SignalHistory.timeframe
            ).all()
            
            # Performance by action (BUY vs SELL)
            action_performance = db.session.query(
                SignalHistory.action,
                func.count(SignalHistory.id).label('total_signals'),
                func.sum(
                    func.case([(SignalHistory.outcome == 'WIN', 1)], else_=0)
                ).label('wins'),
                func.avg(SignalHistory.pnl_percentage).label('avg_pnl')
            ).filter(
                SignalHistory.created_at >= date_from,
                SignalHistory.outcome.isnot(None)
            ).group_by(
                SignalHistory.action
            ).all()
            
            # Daily performance
            daily_performance = db.session.query(
                func.date(SignalHistory.created_at).label('date'),
                func.count(SignalHistory.id).label('signals'),
                func.sum(SignalHistory.pnl_percentage).label('daily_pnl')
            ).filter(
                SignalHistory.created_at >= date_from,
                SignalHistory.pnl_percentage.isnot(None)
            ).group_by(
                func.date(SignalHistory.created_at)
            ).order_by('date').all()
            
            # Confidence distribution
            confidence_ranges = [
                (90, 100, 'ULTRA_HIGH'),
                (80, 90, 'HIGH'),
                (70, 80, 'MEDIUM'),
                (0, 70, 'LOW')
            ]
            
            confidence_distribution = []
            for min_conf, max_conf, label in confidence_ranges:
                count = query.filter(
                    SignalHistory.confidence >= min_conf,
                    SignalHistory.confidence < max_conf
                ).count()
                
                wins = query.filter(
                    SignalHistory.confidence >= min_conf,
                    SignalHistory.confidence < max_conf,
                    SignalHistory.outcome == 'win'
                ).count()
                
                win_rate_range = (wins / count * 100) if count > 0 else 0
                
                confidence_distribution.append({
                    'range': f"{min_conf}-{max_conf}%",
                    'label': label,
                    'count': count,
                    'wins': wins,
                    'win_rate': round(win_rate_range, 2)
                })
            
            analytics_data = {
                'period_days': days,
                'symbol_filter': symbol,
                'summary': {
                    'total_signals': total_signals,
                    'executed_signals': executed_signals,
                    'execution_rate': round(execution_rate, 2),
                    'closed_signals': closed_signals,
                    'winning_signals': winning_signals,
                    'losing_signals': losing_signals,
                    'breakeven_signals': breakeven_signals,
                    'win_rate': round(win_rate, 2),
                    'avg_confidence': round(float(avg_confidence), 2),
                    'total_pnl': round(float(total_pnl), 2),
                    'avg_pnl': round(float(avg_pnl), 2),
                    'avg_risk_reward': round(float(avg_rr), 2)
                },
                'best_trade': {
                    'signal_id': best_trade.signal_id if best_trade else None,
                    'symbol': best_trade.symbol if best_trade else None,
                    'pnl_percentage': float(best_trade.pnl_percentage) if best_trade and best_trade.pnl_percentage else 0
                },
                'worst_trade': {
                    'signal_id': worst_trade.signal_id if worst_trade else None,
                    'symbol': worst_trade.symbol if worst_trade else None,
                    'pnl_percentage': float(worst_trade.pnl_percentage) if worst_trade and worst_trade.pnl_percentage else 0
                },
                'top_symbols': [
                    {
                        'symbol': row.symbol,
                        'total_signals': row.total_signals,
                        'avg_confidence': round(float(row.avg_confidence or 0), 2),
                        'wins': row.wins,
                        'win_rate': round((row.wins / row.total_signals * 100) if row.total_signals > 0 else 0, 2),
                        'avg_pnl': round(float(row.avg_pnl or 0), 2)
                    } for row in top_symbols
                ],
                'timeframe_performance': [
                    {
                        'timeframe': row.timeframe,
                        'total_signals': row.total_signals,
                        'avg_confidence': round(float(row.avg_confidence or 0), 2),
                        'wins': row.wins,
                        'win_rate': round((row.wins / row.closed_signals * 100) if row.closed_signals > 0 else 0, 2)
                    } for row in timeframe_performance
                ],
                'action_performance': [
                    {
                        'action': row.action,
                        'total_signals': row.total_signals,
                        'wins': row.wins,
                        'win_rate': round((row.wins / row.total_signals * 100) if row.total_signals > 0 else 0, 2),
                        'avg_pnl': round(float(row.avg_pnl or 0), 2)
                    } for row in action_performance
                ],
                'daily_performance': [
                    {
                        'date': str(row.date),
                        'signals': row.signals,
                        'daily_pnl': round(float(row.daily_pnl or 0), 2)
                    } for row in daily_performance
                ],
                'confidence_distribution': confidence_distribution
            }
            
            # Cache results
            if use_cache:
                self._cache_analytics('signals', f"{days}d", analytics_data)
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"❌ Failed to get signal analytics: {e}")
            return {'error': str(e)}
    
    def get_comprehensive_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive analytics report
        
        Args:
            days: Time period in days
            
        Returns:
            Comprehensive analytics report
        """
        try:
            # Get signal analytics
            signal_analytics = self.get_signal_analytics(days)
            
            # Get query analytics
            from core.query_logger import get_query_logger
            query_logger = get_query_logger()
            query_analytics = query_logger.get_query_analytics(days)
            
            # Get interaction analytics
            interaction_analytics = self._get_interaction_analytics(days)
            
            # Calculate overall performance score
            performance_score = self._calculate_performance_score(signal_analytics)
            
            return {
                'report_period_days': days,
                'generated_at': datetime.utcnow().isoformat(),
                'performance_score': performance_score,
                'signals': signal_analytics,
                'queries': query_analytics,
                'interactions': interaction_analytics,
                'recommendations': self._generate_recommendations(signal_analytics, query_analytics)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to generate comprehensive report: {e}")
            return {'error': str(e)}
    
    def _get_interaction_analytics(self, days: int) -> Dict[str, Any]:
        """Get user interaction analytics"""
        try:
            date_from = datetime.utcnow() - timedelta(days=days)
            
            # Total interactions
            total_interactions = db.session.query(UserInteraction).filter(
                UserInteraction.created_at >= date_from
            ).count()
            
            # Interactions by type
            interaction_types = db.session.query(
                UserInteraction.interaction_type,
                func.count(UserInteraction.id).label('count')
            ).filter(
                UserInteraction.created_at >= date_from
            ).group_by(
                UserInteraction.interaction_type
            ).all()
            
            # Interactions by source
            interaction_sources = db.session.query(
                UserInteraction.interaction_source,
                func.count(UserInteraction.id).label('count')
            ).filter(
                UserInteraction.created_at >= date_from
            ).group_by(
                UserInteraction.interaction_source
            ).all()
            
            return {
                'period_days': days,
                'total_interactions': total_interactions,
                'by_type': [{'type': t[0], 'count': t[1]} for t in interaction_types],
                'by_source': [{'source': s[0], 'count': s[1]} for s in interaction_sources]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get interaction analytics: {e}")
            return {'error': str(e)}
    
    def _calculate_performance_score(self, signal_analytics: Dict) -> float:
        """
        Calculate overall performance score (0-100)
        
        Args:
            signal_analytics: Signal analytics data
            
        Returns:
            Performance score
        """
        try:
            summary = signal_analytics.get('summary', {})
            
            # Components of score
            win_rate = summary.get('win_rate', 0)
            execution_rate = summary.get('execution_rate', 0)
            avg_confidence = summary.get('avg_confidence', 0)
            avg_pnl = summary.get('avg_pnl', 0)
            
            # Weighted score calculation
            score = (
                win_rate * 0.4 +           # 40% weight for win rate
                execution_rate * 0.2 +     # 20% weight for execution rate
                avg_confidence * 0.2 +     # 20% weight for confidence
                min(max(avg_pnl * 5, 0), 20) * 0.2  # 20% weight for profitability (capped at 20)
            )
            
            return round(min(score, 100), 2)
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate performance score: {e}")
            return 0.0
    
    def _generate_recommendations(self, signal_analytics: Dict, query_analytics: Dict) -> List[str]:
        """
        Generate AI recommendations based on analytics
        
        Args:
            signal_analytics: Signal analytics data
            query_analytics: Query analytics data
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        try:
            summary = signal_analytics.get('summary', {})
            win_rate = summary.get('win_rate', 0)
            execution_rate = summary.get('execution_rate', 0)
            avg_confidence = summary.get('avg_confidence', 0)
            
            # Win rate recommendations
            if win_rate < 50:
                recommendations.append("❌ Win rate di bawah 50%. Pertimbangkan untuk menyesuaikan strategi trading atau threshold confidence.")
            elif win_rate > 75:
                recommendations.append("✅ Win rate sangat baik! Pertahankan strategi saat ini.")
            
            # Execution rate recommendations
            if execution_rate < 30:
                recommendations.append("⚠️ Execution rate rendah. Signals mungkin tidak actionable atau user tidak engaged.")
            elif execution_rate > 70:
                recommendations.append("✅ Execution rate tinggi menunjukkan signals berkualitas dan user engaged.")
            
            # Confidence recommendations
            if avg_confidence < 70:
                recommendations.append("📊 Average confidence rendah. Pertimbangkan untuk meningkatkan kualitas analisis.")
            elif avg_confidence > 85:
                recommendations.append("🎯 Confidence level sangat baik. AI engine bekerja optimal.")
            
            # Query patterns
            if query_analytics.get('success_rate', 0) < 95:
                recommendations.append("🔧 Success rate queries bisa ditingkatkan. Check error handling.")
            
            # Top performing analysis
            top_symbols = signal_analytics.get('top_symbols', [])
            if top_symbols and len(top_symbols) > 0:
                best_symbol = top_symbols[0]
                recommendations.append(f"🏆 {best_symbol['symbol']} adalah symbol terbaik dengan win rate {best_symbol['win_rate']}%.")
            
            if not recommendations:
                recommendations.append("📈 Analytics menunjukkan performa stabil. Continue monitoring.")
            
        except Exception as e:
            logger.error(f"❌ Failed to generate recommendations: {e}")
            recommendations.append("❌ Error generating recommendations.")
        
        return recommendations
    
    def _get_cached_analytics(self, analytics_type: str, time_period: str) -> Optional[Dict]:
        """Get cached analytics data using Redis"""
        try:
            cache_key = f"analytics:{analytics_type}:{time_period}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                logger.info(f"📊 Using cached analytics: {analytics_type} - {time_period}")
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to get cached analytics: {e}")
            return None
    
    def _cache_analytics(self, analytics_type: str, time_period: str, 
                        data: Dict, expire_minutes: int = 15):
        """Cache analytics data using Redis"""
        try:
            cache_key = f"analytics:{analytics_type}:{time_period}"
            expire_seconds = expire_minutes * 60
            
            self.redis_client.setex(
                cache_key, 
                expire_seconds, 
                json.dumps(data)
            )
            
            logger.info(f"💾 Analytics cached: {analytics_type} - {time_period}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cache analytics: {e}")

# Singleton instance
analytics_engine_instance = None

def get_analytics_engine() -> AnalyticsEngine:
    """Get singleton instance of AnalyticsEngine"""
    global analytics_engine_instance
    if analytics_engine_instance is None:
        analytics_engine_instance = AnalyticsEngine()
    return analytics_engine_instance

logger.info("📊 Analytics Engine module loaded")