"""
Signal Performance Tracking System
Tracks win/loss ratio, profitability, and performance metrics
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import Column, String, Float, DateTime, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)
Base = declarative_base()

class SignalRecord(Base):
    """Database model for tracking signal performance"""
    __tablename__ = 'signal_records'
    
    id = Column(Integer, primary_key=True)
    signal_id = Column(String, unique=True, nullable=False)
    symbol = Column(String, nullable=False)
    timeframe = Column(String, nullable=False)
    direction = Column(String, nullable=False)
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    confidence = Column(Float)
    signal_time = Column(DateTime, default=datetime.now)
    
    # Result tracking
    exit_price = Column(Float)
    exit_time = Column(DateTime)
    result = Column(String)  # WIN, LOSS, NEUTRAL, PENDING
    profit_loss = Column(Float)
    profit_loss_percent = Column(Float)
    
    # Additional metrics
    max_profit = Column(Float)
    max_drawdown = Column(Float)
    duration_minutes = Column(Integer)
    
    def to_dict(self):
        return {
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'result': self.result,
            'profit_loss_percent': self.profit_loss_percent,
            'signal_time': self.signal_time.isoformat() if self.signal_time else None
        }

class SignalPerformanceTracker:
    """
    Tracks and analyzes trading signal performance
    - Win/loss ratio tracking
    - Average profit/loss calculation
    - Best performing timeframes and pairs
    - Performance analytics
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.use_database = db_session is not None
        
        # In-memory fallback if no database
        if not self.use_database:
            self.memory_records = []
            logger.warning("No database session provided, using in-memory tracking")
        
        logger.info("📊 Signal Performance Tracker initialized")
    
    def record_signal(self, signal_data: Dict[str, Any]) -> str:
        """Record a new signal for tracking"""
        try:
            # Generate unique signal ID
            signal_id = self._generate_signal_id(signal_data)
            
            if self.use_database:
                # Database recording
                record = SignalRecord(
                    signal_id=signal_id,
                    symbol=signal_data.get('symbol'),
                    timeframe=signal_data.get('timeframe', '1H'),
                    direction=signal_data.get('direction'),
                    entry_price=signal_data.get('entry_price'),
                    stop_loss=signal_data.get('stop_loss'),
                    take_profit=signal_data.get('take_profit'),
                    confidence=signal_data.get('confidence'),
                    signal_time=datetime.now(),
                    result='PENDING'
                )
                
                self.db_session.add(record)
                self.db_session.commit()
                
            else:
                # In-memory recording
                self.memory_records.append({
                    'signal_id': signal_id,
                    'symbol': signal_data.get('symbol'),
                    'timeframe': signal_data.get('timeframe', '1H'),
                    'direction': signal_data.get('direction'),
                    'entry_price': signal_data.get('entry_price'),
                    'stop_loss': signal_data.get('stop_loss'),
                    'take_profit': signal_data.get('take_profit'),
                    'confidence': signal_data.get('confidence'),
                    'signal_time': datetime.now(),
                    'result': 'PENDING'
                })
            
            logger.info(f"📊 Signal recorded: {signal_id}")
            return signal_id
            
        except Exception as e:
            logger.error(f"Error recording signal: {e}")
            return ""
    
    def update_signal_result(self, 
                           signal_id: str, 
                           exit_price: float,
                           result: str = None) -> bool:
        """Update signal with exit price and result"""
        try:
            if self.use_database:
                record = self.db_session.query(SignalRecord).filter_by(
                    signal_id=signal_id
                ).first()
                
                if record:
                    # Calculate profit/loss
                    if record.direction in ['BUY', 'LONG']:
                        profit_loss = exit_price - record.entry_price
                    else:
                        profit_loss = record.entry_price - exit_price
                    
                    profit_loss_percent = (profit_loss / record.entry_price) * 100
                    
                    # Determine result if not provided
                    if not result:
                        if profit_loss > 0:
                            result = 'WIN'
                        elif profit_loss < 0:
                            result = 'LOSS'
                        else:
                            result = 'NEUTRAL'
                    
                    # Update record
                    record.exit_price = exit_price
                    record.exit_time = datetime.now()
                    record.result = result
                    record.profit_loss = profit_loss
                    record.profit_loss_percent = profit_loss_percent
                    
                    # Calculate duration
                    if record.signal_time:
                        duration = datetime.now() - record.signal_time
                        record.duration_minutes = int(duration.total_seconds() / 60)
                    
                    self.db_session.commit()
                    logger.info(f"✅ Signal {signal_id} updated: {result} ({profit_loss_percent:.2f}%)")
                    return True
                    
            else:
                # In-memory update
                for record in self.memory_records:
                    if record['signal_id'] == signal_id:
                        # Similar calculations for in-memory
                        if record['direction'] in ['BUY', 'LONG']:
                            profit_loss = exit_price - record['entry_price']
                        else:
                            profit_loss = record['entry_price'] - exit_price
                        
                        profit_loss_percent = (profit_loss / record['entry_price']) * 100
                        
                        record['exit_price'] = exit_price
                        record['exit_time'] = datetime.now()
                        record['result'] = 'WIN' if profit_loss > 0 else 'LOSS'
                        record['profit_loss'] = profit_loss
                        record['profit_loss_percent'] = profit_loss_percent
                        
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating signal result: {e}")
            return False
    
    def get_performance_stats(self, 
                            symbol: Optional[str] = None,
                            timeframe: Optional[str] = None,
                            days: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        try:
            # Get records based on filters
            records = self._get_filtered_records(symbol, timeframe, days)
            
            if not records:
                return {
                    'total_signals': 0,
                    'message': 'No signals found for the given criteria'
                }
            
            # Calculate statistics
            total_signals = len(records)
            wins = [r for r in records if r.get('result') == 'WIN']
            losses = [r for r in records if r.get('result') == 'LOSS']
            pending = [r for r in records if r.get('result') == 'PENDING']
            
            win_count = len(wins)
            loss_count = len(losses)
            
            # Win rate
            completed_signals = win_count + loss_count
            win_rate = (win_count / completed_signals * 100) if completed_signals > 0 else 0
            
            # Profit/Loss calculations
            total_profit = sum(r.get('profit_loss_percent', 0) for r in wins)
            total_loss = sum(r.get('profit_loss_percent', 0) for r in losses)
            net_profit = total_profit + total_loss  # losses are negative
            
            # Average calculations
            avg_win = (total_profit / win_count) if win_count > 0 else 0
            avg_loss = (total_loss / loss_count) if loss_count > 0 else 0
            
            # Profit factor
            profit_factor = abs(total_profit / total_loss) if total_loss != 0 else float('inf')
            
            # Best and worst trades
            all_completed = wins + losses
            if all_completed:
                best_trade = max(all_completed, key=lambda x: x.get('profit_loss_percent', 0))
                worst_trade = min(all_completed, key=lambda x: x.get('profit_loss_percent', 0))
            else:
                best_trade = worst_trade = None
            
            return {
                'period_days': days,
                'total_signals': total_signals,
                'completed_signals': completed_signals,
                'pending_signals': len(pending),
                'performance': {
                    'win_count': win_count,
                    'loss_count': loss_count,
                    'win_rate': round(win_rate, 2),
                    'net_profit_percent': round(net_profit, 2),
                    'average_win': round(avg_win, 2),
                    'average_loss': round(avg_loss, 2),
                    'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 'N/A'
                },
                'best_trade': {
                    'symbol': best_trade.get('symbol'),
                    'profit_percent': round(best_trade.get('profit_loss_percent', 0), 2),
                    'direction': best_trade.get('direction')
                } if best_trade else None,
                'worst_trade': {
                    'symbol': worst_trade.get('symbol'),
                    'loss_percent': round(worst_trade.get('profit_loss_percent', 0), 2),
                    'direction': worst_trade.get('direction')
                } if worst_trade else None,
                'filters_applied': {
                    'symbol': symbol,
                    'timeframe': timeframe
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance stats: {e}")
            return {
                'error': str(e),
                'total_signals': 0
            }
    
    def get_best_performing_pairs(self, days: int = 30, limit: int = 5) -> List[Dict[str, Any]]:
        """Get best performing trading pairs"""
        try:
            records = self._get_filtered_records(None, None, days)
            
            # Group by symbol
            symbol_performance = {}
            
            for record in records:
                symbol = record.get('symbol')
                if not symbol or record.get('result') == 'PENDING':
                    continue
                
                if symbol not in symbol_performance:
                    symbol_performance[symbol] = {
                        'wins': 0,
                        'losses': 0,
                        'total_profit': 0,
                        'signals': 0
                    }
                
                if record.get('result') == 'WIN':
                    symbol_performance[symbol]['wins'] += 1
                else:
                    symbol_performance[symbol]['losses'] += 1
                
                symbol_performance[symbol]['total_profit'] += record.get('profit_loss_percent', 0)
                symbol_performance[symbol]['signals'] += 1
            
            # Calculate metrics for each symbol
            results = []
            for symbol, stats in symbol_performance.items():
                win_rate = (stats['wins'] / stats['signals'] * 100) if stats['signals'] > 0 else 0
                avg_profit = stats['total_profit'] / stats['signals'] if stats['signals'] > 0 else 0
                
                results.append({
                    'symbol': symbol,
                    'win_rate': round(win_rate, 2),
                    'average_profit': round(avg_profit, 2),
                    'total_signals': stats['signals'],
                    'wins': stats['wins'],
                    'losses': stats['losses']
                })
            
            # Sort by average profit
            results.sort(key=lambda x: x['average_profit'], reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error getting best performing pairs: {e}")
            return []
    
    def get_performance_by_timeframe(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics grouped by timeframe"""
        try:
            records = self._get_filtered_records(None, None, days)
            
            # Group by timeframe
            tf_performance = {}
            
            for record in records:
                tf = record.get('timeframe', '1H')
                if record.get('result') == 'PENDING':
                    continue
                
                if tf not in tf_performance:
                    tf_performance[tf] = {
                        'wins': 0,
                        'losses': 0,
                        'total_profit': 0,
                        'signals': 0
                    }
                
                if record.get('result') == 'WIN':
                    tf_performance[tf]['wins'] += 1
                else:
                    tf_performance[tf]['losses'] += 1
                
                tf_performance[tf]['total_profit'] += record.get('profit_loss_percent', 0)
                tf_performance[tf]['signals'] += 1
            
            # Calculate metrics
            results = {}
            for tf, stats in tf_performance.items():
                win_rate = (stats['wins'] / stats['signals'] * 100) if stats['signals'] > 0 else 0
                avg_profit = stats['total_profit'] / stats['signals'] if stats['signals'] > 0 else 0
                
                results[tf] = {
                    'win_rate': round(win_rate, 2),
                    'average_profit': round(avg_profit, 2),
                    'total_signals': stats['signals'],
                    'recommendation': 'OPTIMAL' if win_rate > 60 and avg_profit > 0 else 'SUBOPTIMAL'
                }
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting timeframe performance: {e}")
            return {}
    
    def _generate_signal_id(self, signal_data: Dict[str, Any]) -> str:
        """Generate unique signal ID"""
        symbol = signal_data.get('symbol', 'unknown')
        direction = signal_data.get('direction', 'unknown')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{symbol}_{direction}_{timestamp}"
    
    def _get_filtered_records(self, 
                            symbol: Optional[str],
                            timeframe: Optional[str],
                            days: int) -> List[Dict[str, Any]]:
        """Get filtered records based on criteria"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        if self.use_database:
            query = self.db_session.query(SignalRecord)
            
            if symbol:
                query = query.filter(SignalRecord.symbol == symbol)
            if timeframe:
                query = query.filter(SignalRecord.timeframe == timeframe)
            
            query = query.filter(SignalRecord.signal_time >= cutoff_date)
            
            return [record.to_dict() for record in query.all()]
        else:
            # In-memory filtering
            filtered = self.memory_records
            
            if symbol:
                filtered = [r for r in filtered if r.get('symbol') == symbol]
            if timeframe:
                filtered = [r for r in filtered if r.get('timeframe') == timeframe]
            
            filtered = [r for r in filtered if r.get('signal_time', datetime.now()) >= cutoff_date]
            
            return filtered