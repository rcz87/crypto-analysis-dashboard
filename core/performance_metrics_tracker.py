#!/usr/bin/env python3
"""
Performance Metrics Tracker Implementation
Implements Sharpe Ratio, Max Drawdown, Win Rate calculations
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from collections import deque
import json

@dataclass
class PerformanceMetrics:
    """Complete performance metrics"""
    # Basic metrics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    # Return metrics
    total_return: float = 0.0
    average_return: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    
    # Risk metrics
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    
    # Profit metrics
    profit_factor: float = 0.0
    expectancy: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    
    # Additional metrics
    calmar_ratio: float = 0.0
    recovery_factor: float = 0.0
    risk_reward_ratio: float = 0.0
    consecutive_wins: int = 0
    consecutive_losses: int = 0
    
    # Time-based metrics
    daily_returns: List[float] = field(default_factory=list)
    monthly_returns: List[float] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)

class PerformanceTracker:
    """
    Real-time performance tracking and calculation
    """
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.trades = []
        self.daily_returns = deque(maxlen=252)  # 1 year of daily returns
        self.equity_curve = [initial_capital]
        self.peak_equity = initial_capital
        self.drawdown_start = None
        self.logger = logging.getLogger(__name__)
        
    def add_trade(self, trade: Dict[str, Any]):
        """
        Add a new trade and update metrics
        
        Args:
            trade: Dict with keys: entry_price, exit_price, quantity, 
                   entry_time, exit_time, side (BUY/SELL), commission
        """
        # Calculate P&L
        if trade['side'] == 'BUY':
            pnl = (trade['exit_price'] - trade['entry_price']) * trade['quantity']
        else:  # SELL/SHORT
            pnl = (trade['entry_price'] - trade['exit_price']) * trade['quantity']
        
        pnl -= trade.get('commission', 0)
        
        # Update capital
        self.current_capital += pnl
        self.equity_curve.append(self.current_capital)
        
        # Store trade
        trade['pnl'] = pnl
        trade['return'] = pnl / self.current_capital
        self.trades.append(trade)
        
        # Update peak for drawdown calculation
        if self.current_capital > self.peak_equity:
            self.peak_equity = self.current_capital
            self.drawdown_start = None
        elif self.drawdown_start is None:
            self.drawdown_start = trade['exit_time']
        
        # Calculate daily return
        if len(self.trades) > 1:
            prev_time = self.trades[-2]['exit_time']
            if trade['exit_time'].date() != prev_time.date():
                daily_return = (self.current_capital - self.equity_curve[-2]) / self.equity_curve[-2]
                self.daily_returns.append(daily_return)
    
    def calculate_metrics(self) -> PerformanceMetrics:
        """Calculate all performance metrics"""
        if not self.trades:
            return PerformanceMetrics()
        
        # Basic trade statistics
        pnls = [t['pnl'] for t in self.trades]
        returns = [t['return'] for t in self.trades]
        
        winning_trades = [p for p in pnls if p > 0]
        losing_trades = [p for p in pnls if p <= 0]
        
        metrics = PerformanceMetrics(
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=len(winning_trades) / len(self.trades) if self.trades else 0
        )
        
        # Return metrics
        metrics.total_return = (self.current_capital - self.initial_capital) / self.initial_capital
        metrics.average_return = np.mean(returns) if returns else 0
        metrics.best_trade = max(pnls) if pnls else 0
        metrics.worst_trade = min(pnls) if pnls else 0
        
        # Calculate Sharpe Ratio (annualized)
        if len(self.daily_returns) > 1:
            daily_returns_array = np.array(self.daily_returns)
            if daily_returns_array.std() > 0:
                metrics.sharpe_ratio = np.sqrt(252) * daily_returns_array.mean() / daily_returns_array.std()
        
        # Calculate Sortino Ratio
        if len(self.daily_returns) > 1:
            downside_returns = [r for r in self.daily_returns if r < 0]
            if downside_returns and np.std(downside_returns) > 0:
                metrics.sortino_ratio = np.sqrt(252) * np.mean(self.daily_returns) / np.std(downside_returns)
        
        # Calculate Maximum Drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        metrics.max_drawdown = abs(drawdown.min()) if len(drawdown) > 0 else 0
        
        # Drawdown duration
        if self.drawdown_start and self.current_capital < self.peak_equity:
            metrics.max_drawdown_duration = (datetime.now() - self.drawdown_start).days
        
        # Profit Factor
        gross_profit = sum(winning_trades) if winning_trades else 0
        gross_loss = abs(sum(losing_trades)) if losing_trades else 1
        metrics.profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Expectancy
        metrics.avg_win = np.mean(winning_trades) if winning_trades else 0
        metrics.avg_loss = abs(np.mean(losing_trades)) if losing_trades else 0
        metrics.expectancy = (metrics.win_rate * metrics.avg_win) - ((1 - metrics.win_rate) * metrics.avg_loss)
        
        # Risk-Reward Ratio
        if metrics.avg_loss > 0:
            metrics.risk_reward_ratio = metrics.avg_win / metrics.avg_loss
        
        # Calmar Ratio
        if metrics.max_drawdown > 0:
            metrics.calmar_ratio = metrics.total_return / metrics.max_drawdown
        
        # Recovery Factor
        total_profit = self.current_capital - self.initial_capital
        if metrics.max_drawdown > 0 and total_profit > 0:
            metrics.recovery_factor = total_profit / (metrics.max_drawdown * self.initial_capital)
        
        # Consecutive wins/losses
        current_streak = 0
        streak_type = None
        max_win_streak = 0
        max_loss_streak = 0
        
        for pnl in pnls:
            if pnl > 0:
                if streak_type == 'win':
                    current_streak += 1
                else:
                    current_streak = 1
                    streak_type = 'win'
                max_win_streak = max(max_win_streak, current_streak)
            else:
                if streak_type == 'loss':
                    current_streak += 1
                else:
                    current_streak = 1
                    streak_type = 'loss'
                max_loss_streak = max(max_loss_streak, current_streak)
        
        metrics.consecutive_wins = max_win_streak
        metrics.consecutive_losses = max_loss_streak
        
        # Store curves
        metrics.daily_returns = list(self.daily_returns)
        metrics.equity_curve = self.equity_curve.copy()
        
        return metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for API response"""
        metrics = self.calculate_metrics()
        
        return {
            'overview': {
                'total_return': f"{metrics.total_return:.2%}",
                'sharpe_ratio': round(metrics.sharpe_ratio, 2),
                'max_drawdown': f"{metrics.max_drawdown:.2%}",
                'win_rate': f"{metrics.win_rate:.2%}"
            },
            'risk_metrics': {
                'sharpe_ratio': round(metrics.sharpe_ratio, 2),
                'sortino_ratio': round(metrics.sortino_ratio, 2),
                'max_drawdown': f"{metrics.max_drawdown:.2%}",
                'max_drawdown_duration': f"{metrics.max_drawdown_duration} days",
                'calmar_ratio': round(metrics.calmar_ratio, 2),
                'recovery_factor': round(metrics.recovery_factor, 2)
            },
            'trade_statistics': {
                'total_trades': metrics.total_trades,
                'winning_trades': metrics.winning_trades,
                'losing_trades': metrics.losing_trades,
                'win_rate': f"{metrics.win_rate:.2%}",
                'profit_factor': round(metrics.profit_factor, 2),
                'expectancy': f"${metrics.expectancy:.2f}",
                'risk_reward_ratio': round(metrics.risk_reward_ratio, 2)
            },
            'profit_metrics': {
                'average_win': f"${metrics.avg_win:.2f}",
                'average_loss': f"${metrics.avg_loss:.2f}",
                'best_trade': f"${metrics.best_trade:.2f}",
                'worst_trade': f"${metrics.worst_trade:.2f}",
                'consecutive_wins': metrics.consecutive_wins,
                'consecutive_losses': metrics.consecutive_losses
            },
            'current_status': {
                'initial_capital': f"${self.initial_capital:,.2f}",
                'current_capital': f"${self.current_capital:,.2f}",
                'total_pnl': f"${self.current_capital - self.initial_capital:,.2f}",
                'total_return': f"{metrics.total_return:.2%}"
            }
        }
    
    def generate_performance_report(self) -> str:
        """Generate detailed performance report"""
        metrics = self.calculate_metrics()
        
        report = []
        report.append("=" * 60)
        report.append("PERFORMANCE REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overview
        report.append("OVERVIEW")
        report.append("-" * 30)
        report.append(f"Initial Capital: ${self.initial_capital:,.2f}")
        report.append(f"Current Capital: ${self.current_capital:,.2f}")
        report.append(f"Total Return: {metrics.total_return:.2%}")
        report.append(f"Total Trades: {metrics.total_trades}")
        report.append("")
        
        # Risk Metrics
        report.append("RISK METRICS")
        report.append("-" * 30)
        report.append(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        report.append(f"Sortino Ratio: {metrics.sortino_ratio:.2f}")
        report.append(f"Max Drawdown: {metrics.max_drawdown:.2%}")
        report.append(f"Max DD Duration: {metrics.max_drawdown_duration} days")
        report.append(f"Calmar Ratio: {metrics.calmar_ratio:.2f}")
        report.append(f"Recovery Factor: {metrics.recovery_factor:.2f}")
        report.append("")
        
        # Trade Statistics
        report.append("TRADE STATISTICS")
        report.append("-" * 30)
        report.append(f"Total Trades: {metrics.total_trades}")
        report.append(f"Winning Trades: {metrics.winning_trades}")
        report.append(f"Losing Trades: {metrics.losing_trades}")
        report.append(f"Win Rate: {metrics.win_rate:.2%}")
        report.append(f"Profit Factor: {metrics.profit_factor:.2f}")
        report.append(f"Expectancy: ${metrics.expectancy:.2f}")
        report.append(f"Risk/Reward: {metrics.risk_reward_ratio:.2f}")
        report.append("")
        
        # Profit Metrics
        report.append("PROFIT METRICS")
        report.append("-" * 30)
        report.append(f"Average Win: ${metrics.avg_win:.2f}")
        report.append(f"Average Loss: ${metrics.avg_loss:.2f}")
        report.append(f"Best Trade: ${metrics.best_trade:.2f}")
        report.append(f"Worst Trade: ${metrics.worst_trade:.2f}")
        report.append(f"Max Consecutive Wins: {metrics.consecutive_wins}")
        report.append(f"Max Consecutive Losses: {metrics.consecutive_losses}")
        
        return "\n".join(report)
    
    def save_metrics(self, filepath: str):
        """Save metrics to file"""
        metrics = self.calculate_metrics()
        data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics.__dict__,
            'trades': self.trades,
            'current_capital': self.current_capital
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

# Singleton instance
performance_tracker = PerformanceTracker()

if __name__ == "__main__":
    # Test with sample trades
    tracker = PerformanceTracker(initial_capital=100000)
    
    # Simulate some trades
    sample_trades = [
        {'entry_price': 50000, 'exit_price': 51000, 'quantity': 0.1, 
         'side': 'BUY', 'entry_time': datetime.now() - timedelta(days=10),
         'exit_time': datetime.now() - timedelta(days=9), 'commission': 10},
        
        {'entry_price': 51000, 'exit_price': 50500, 'quantity': 0.1,
         'side': 'BUY', 'entry_time': datetime.now() - timedelta(days=8),
         'exit_time': datetime.now() - timedelta(days=7), 'commission': 10},
        
        {'entry_price': 50500, 'exit_price': 52000, 'quantity': 0.15,
         'side': 'BUY', 'entry_time': datetime.now() - timedelta(days=6),
         'exit_time': datetime.now() - timedelta(days=5), 'commission': 15},
    ]
    
    for trade in sample_trades:
        tracker.add_trade(trade)
    
    # Get performance summary
    summary = tracker.get_performance_summary()
    print(json.dumps(summary, indent=2))
    
    # Generate report
    print("\n" + tracker.generate_performance_report())