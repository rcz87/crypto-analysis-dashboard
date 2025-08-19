#!/usr/bin/env python3
"""
Event-Driven Backtester dengan Metrik Lengkap
Implementasi backtesting realistis untuk strategi trading
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from enum import Enum

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

@dataclass
class Order:
    """Order representation"""
    symbol: str
    side: OrderSide
    quantity: float
    order_type: OrderType
    price: Optional[float] = None
    timestamp: Optional[datetime] = None
    order_id: Optional[str] = None

@dataclass
class Trade:
    """Executed trade"""
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    commission: float

@dataclass
class Position:
    """Current position"""
    symbol: str
    quantity: float
    avg_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0

@dataclass
class BacktestMetrics:
    """Comprehensive backtest metrics"""
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_factor: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    largest_win: float
    largest_loss: float
    calmar_ratio: float
    omega_ratio: float
    daily_returns: List[float] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)

class EventDrivenBacktester:
    """
    Event-driven backtester untuk simulasi trading yang realistis
    """
    
    def __init__(self, initial_capital: float = 100000, 
                 commission_rate: float = 0.001,
                 slippage_rate: float = 0.0005):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        
        self.positions: Dict[str, Position] = {}
        self.orders: List[Order] = []
        self.trades: List[Trade] = []
        self.equity_curve = [initial_capital]
        self.daily_returns = []
        
        self.logger = logging.getLogger(__name__)
        
    def run_backtest(self, 
                    data: pd.DataFrame,
                    strategy_func,
                    start_date: Optional[datetime] = None,
                    end_date: Optional[datetime] = None) -> BacktestMetrics:
        """
        Run event-driven backtest
        
        Args:
            data: DataFrame dengan columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
            strategy_func: Function yang menghasilkan signals
            start_date: Tanggal mulai backtest
            end_date: Tanggal akhir backtest
        """
        # Filter data by date range
        if start_date:
            data = data[data['timestamp'] >= start_date]
        if end_date:
            data = data[data['timestamp'] <= end_date]
        
        # Reset state
        self.capital = self.initial_capital
        self.positions = {}
        self.orders = []
        self.trades = []
        self.equity_curve = [self.initial_capital]
        self.daily_returns = []
        
        previous_equity = self.initial_capital
        daily_equity = []
        
        # Main event loop
        for idx, row in data.iterrows():
            current_time = row['timestamp']
            current_price = row['close']
            
            # Update positions with current price
            self._update_positions(current_price)
            
            # Generate signal from strategy
            signal = strategy_func(data[:idx+1], self.positions, self.capital)
            
            # Process signal
            if signal:
                self._process_signal(signal, current_price, current_time)
            
            # Calculate current equity
            current_equity = self._calculate_equity(current_price)
            self.equity_curve.append(current_equity)
            daily_equity.append(current_equity)
            
            # Calculate daily returns
            if len(daily_equity) >= 2:
                daily_return = (daily_equity[-1] - daily_equity[-2]) / daily_equity[-2]
                self.daily_returns.append(daily_return)
        
        # Calculate metrics
        return self._calculate_metrics()
    
    def _update_positions(self, current_price: float):
        """Update unrealized P&L for all positions"""
        for symbol, position in self.positions.items():
            if position.quantity > 0:
                position.unrealized_pnl = (current_price - position.avg_price) * position.quantity
            elif position.quantity < 0:
                position.unrealized_pnl = (position.avg_price - current_price) * abs(position.quantity)
    
    def _process_signal(self, signal: Dict[str, Any], 
                       current_price: float, 
                       current_time: datetime):
        """Process trading signal"""
        action = signal.get('action')
        quantity = signal.get('quantity', 0)
        symbol = signal.get('symbol', 'BTC-USDT')
        
        if action == 'BUY' and quantity > 0:
            self._execute_buy(symbol, quantity, current_price, current_time)
        elif action == 'SELL' and quantity > 0:
            self._execute_sell(symbol, quantity, current_price, current_time)
        elif action == 'CLOSE':
            self._close_position(symbol, current_price, current_time)
    
    def _execute_buy(self, symbol: str, quantity: float, 
                    price: float, timestamp: datetime):
        """Execute buy order"""
        # Apply slippage
        execution_price = price * (1 + self.slippage_rate)
        
        # Calculate cost including commission
        cost = quantity * execution_price
        commission = cost * self.commission_rate
        total_cost = cost + commission
        
        # Check if we have enough capital
        if total_cost > self.capital:
            self.logger.warning(f"Insufficient capital for buy order: {total_cost} > {self.capital}")
            return
        
        # Update capital
        self.capital -= total_cost
        
        # Update or create position
        if symbol in self.positions:
            position = self.positions[symbol]
            new_quantity = position.quantity + quantity
            new_avg_price = ((position.quantity * position.avg_price) + 
                           (quantity * execution_price)) / new_quantity
            position.quantity = new_quantity
            position.avg_price = new_avg_price
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                quantity=quantity,
                avg_price=execution_price
            )
        
        # Record trade
        trade = Trade(
            order_id=f"BUY_{timestamp.timestamp()}",
            symbol=symbol,
            side=OrderSide.BUY,
            quantity=quantity,
            price=execution_price,
            timestamp=timestamp,
            commission=commission
        )
        self.trades.append(trade)
    
    def _execute_sell(self, symbol: str, quantity: float, 
                     price: float, timestamp: datetime):
        """Execute sell order"""
        if symbol not in self.positions or self.positions[symbol].quantity <= 0:
            self.logger.warning(f"No position to sell for {symbol}")
            return
        
        position = self.positions[symbol]
        sell_quantity = min(quantity, position.quantity)
        
        # Apply slippage
        execution_price = price * (1 - self.slippage_rate)
        
        # Calculate proceeds
        proceeds = sell_quantity * execution_price
        commission = proceeds * self.commission_rate
        net_proceeds = proceeds - commission
        
        # Calculate realized P&L
        realized_pnl = (execution_price - position.avg_price) * sell_quantity - commission
        position.realized_pnl += realized_pnl
        
        # Update position
        position.quantity -= sell_quantity
        if position.quantity == 0:
            del self.positions[symbol]
        
        # Update capital
        self.capital += net_proceeds
        
        # Record trade
        trade = Trade(
            order_id=f"SELL_{timestamp.timestamp()}",
            symbol=symbol,
            side=OrderSide.SELL,
            quantity=sell_quantity,
            price=execution_price,
            timestamp=timestamp,
            commission=commission
        )
        self.trades.append(trade)
    
    def _close_position(self, symbol: str, price: float, timestamp: datetime):
        """Close entire position"""
        if symbol in self.positions:
            position = self.positions[symbol]
            self._execute_sell(symbol, position.quantity, price, timestamp)
    
    def _calculate_equity(self, current_price: float) -> float:
        """Calculate total equity (cash + positions)"""
        equity = self.capital
        for symbol, position in self.positions.items():
            equity += position.quantity * current_price
        return equity
    
    def _calculate_metrics(self) -> BacktestMetrics:
        """Calculate comprehensive backtest metrics"""
        if not self.equity_curve or len(self.equity_curve) < 2:
            return BacktestMetrics(
                total_return=0, sharpe_ratio=0, sortino_ratio=0,
                max_drawdown=0, max_drawdown_duration=0, win_rate=0,
                profit_factor=0, total_trades=0, winning_trades=0,
                losing_trades=0, avg_win=0, avg_loss=0,
                largest_win=0, largest_loss=0, calmar_ratio=0,
                omega_ratio=0
            )
        
        # Total return
        total_return = (self.equity_curve[-1] - self.initial_capital) / self.initial_capital
        
        # Convert to numpy array for calculations
        returns = np.array(self.daily_returns)
        if len(returns) == 0:
            returns = np.array([0])
        
        # Sharpe ratio (annualized)
        if returns.std() > 0:
            sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std()
        else:
            sharpe_ratio = 0
        
        # Sortino ratio (downside deviation)
        downside_returns = returns[returns < 0]
        if len(downside_returns) > 0 and downside_returns.std() > 0:
            sortino_ratio = np.sqrt(252) * returns.mean() / downside_returns.std()
        else:
            sortino_ratio = 0
        
        # Maximum drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        # Drawdown duration
        dd_duration = self._calculate_drawdown_duration(equity_array)
        
        # Trade statistics
        trade_pnls = []
        for i, trade in enumerate(self.trades):
            if trade.side == OrderSide.SELL:
                # Find corresponding buy
                buy_price = self._find_buy_price(trade.symbol, i)
                if buy_price:
                    pnl = (trade.price - buy_price) * trade.quantity - trade.commission
                    trade_pnls.append(pnl)
        
        if trade_pnls:
            trade_pnls = np.array(trade_pnls)
            winning_trades = len(trade_pnls[trade_pnls > 0])
            losing_trades = len(trade_pnls[trade_pnls <= 0])
            total_trades = len(trade_pnls)
            
            win_rate = winning_trades / total_trades if total_trades > 0 else 0
            
            # Profit factor
            gross_profit = trade_pnls[trade_pnls > 0].sum() if winning_trades > 0 else 0
            gross_loss = abs(trade_pnls[trade_pnls <= 0].sum()) if losing_trades > 0 else 1
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
            
            # Average win/loss
            avg_win = trade_pnls[trade_pnls > 0].mean() if winning_trades > 0 else 0
            avg_loss = trade_pnls[trade_pnls <= 0].mean() if losing_trades > 0 else 0
            
            # Largest win/loss
            largest_win = trade_pnls.max() if len(trade_pnls) > 0 else 0
            largest_loss = trade_pnls.min() if len(trade_pnls) > 0 else 0
        else:
            winning_trades = losing_trades = total_trades = 0
            win_rate = profit_factor = avg_win = avg_loss = 0
            largest_win = largest_loss = 0
        
        # Calmar ratio
        calmar_ratio = total_return / max_drawdown if max_drawdown > 0 else 0
        
        # Omega ratio (simplified)
        threshold = 0
        gains = returns[returns > threshold] - threshold
        losses = threshold - returns[returns <= threshold]
        omega_ratio = gains.sum() / losses.sum() if losses.sum() > 0 else 0
        
        return BacktestMetrics(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=dd_duration,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            calmar_ratio=calmar_ratio,
            omega_ratio=omega_ratio,
            daily_returns=self.daily_returns,
            equity_curve=self.equity_curve
        )
    
    def _calculate_drawdown_duration(self, equity_array: np.ndarray) -> int:
        """Calculate maximum drawdown duration in days"""
        running_max = np.maximum.accumulate(equity_array)
        is_drawdown = equity_array < running_max
        
        if not is_drawdown.any():
            return 0
        
        # Find consecutive drawdown periods
        drawdown_periods = []
        current_duration = 0
        
        for i in range(len(is_drawdown)):
            if is_drawdown[i]:
                current_duration += 1
            else:
                if current_duration > 0:
                    drawdown_periods.append(current_duration)
                current_duration = 0
        
        if current_duration > 0:
            drawdown_periods.append(current_duration)
        
        return max(drawdown_periods) if drawdown_periods else 0
    
    def _find_buy_price(self, symbol: str, sell_index: int) -> Optional[float]:
        """Find average buy price before sell trade"""
        buy_prices = []
        for i in range(sell_index):
            trade = self.trades[i]
            if trade.symbol == symbol and trade.side == OrderSide.BUY:
                buy_prices.append(trade.price)
        
        return np.mean(buy_prices) if buy_prices else None
    
    def generate_report(self, metrics: BacktestMetrics) -> str:
        """Generate comprehensive backtest report"""
        report = "=" * 60 + "\n"
        report += "BACKTEST REPORT\n"
        report += "=" * 60 + "\n\n"
        
        report += f"Initial Capital: ${self.initial_capital:,.2f}\n"
        report += f"Final Capital: ${self.equity_curve[-1]:,.2f}\n"
        report += f"Total Return: {metrics.total_return:.2%}\n\n"
        
        report += "RISK METRICS\n"
        report += "-" * 30 + "\n"
        report += f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}\n"
        report += f"Sortino Ratio: {metrics.sortino_ratio:.2f}\n"
        report += f"Max Drawdown: {metrics.max_drawdown:.2%}\n"
        report += f"Max DD Duration: {metrics.max_drawdown_duration} days\n"
        report += f"Calmar Ratio: {metrics.calmar_ratio:.2f}\n"
        report += f"Omega Ratio: {metrics.omega_ratio:.2f}\n\n"
        
        report += "TRADE STATISTICS\n"
        report += "-" * 30 + "\n"
        report += f"Total Trades: {metrics.total_trades}\n"
        report += f"Winning Trades: {metrics.winning_trades}\n"
        report += f"Losing Trades: {metrics.losing_trades}\n"
        report += f"Win Rate: {metrics.win_rate:.2%}\n"
        report += f"Profit Factor: {metrics.profit_factor:.2f}\n"
        report += f"Average Win: ${metrics.avg_win:,.2f}\n"
        report += f"Average Loss: ${metrics.avg_loss:,.2f}\n"
        report += f"Largest Win: ${metrics.largest_win:,.2f}\n"
        report += f"Largest Loss: ${metrics.largest_loss:,.2f}\n"
        
        return report

# Example strategy function
def example_strategy(data: pd.DataFrame, positions: Dict, capital: float) -> Optional[Dict]:
    """
    Example strategy for testing
    Simple MA crossover
    """
    if len(data) < 20:
        return None
    
    # Calculate moving averages
    ma_short = data['close'].rolling(5).mean().iloc[-1]
    ma_long = data['close'].rolling(20).mean().iloc[-1]
    
    current_price = data['close'].iloc[-1]
    symbol = 'BTC-USDT'
    
    # Generate signal
    if ma_short > ma_long and symbol not in positions:
        # Buy signal
        quantity = (capital * 0.1) / current_price  # Use 10% of capital
        return {'action': 'BUY', 'quantity': quantity, 'symbol': symbol}
    elif ma_short < ma_long and symbol in positions:
        # Sell signal
        return {'action': 'CLOSE', 'symbol': symbol}
    
    return None

if __name__ == "__main__":
    # Test backtester
    import yfinance as yf
    
    # Get sample data
    data = yf.download('BTC-USD', start='2023-01-01', end='2023-12-31')
    data = data.reset_index()
    data.columns = ['timestamp', 'open', 'high', 'low', 'close', 'adj_close', 'volume']
    
    # Run backtest
    backtester = EventDrivenBacktester(initial_capital=100000)
    metrics = backtester.run_backtest(data, example_strategy)
    
    # Print report
    print(backtester.generate_report(metrics))