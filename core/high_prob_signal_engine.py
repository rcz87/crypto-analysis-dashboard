"""
High Probability Signal Engine - Holly-like Module
Backtest multiple strategies and select signals with highest probability
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
import importlib
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class HighProbSignalEngine:
    """
    Holly-like engine that backtests multiple strategies and selects highest probability signals
    """
    
    def __init__(self, okx_fetcher=None, lookback_days: int = 30):
        self.okx_fetcher = okx_fetcher
        self.lookback_days = lookback_days
        self.strategies = {}
        self.performance_cache = {}
        
        # Performance thresholds for signal selection
        self.min_win_rate = 0.6  # 60% minimum win rate
        self.min_risk_reward = 1.5  # 1:1.5 minimum risk-reward ratio
        self.max_drawdown = 0.15  # 15% maximum drawdown
        
        # Load all available strategies
        self._load_strategies()
        
        logger.info(f"🎯 High Probability Signal Engine initialized with {len(self.strategies)} strategies")
    
    def _load_strategies(self):
        """Load all strategy modules from strategies/ directory"""
        try:
            strategies_dir = Path(__file__).parent / "strategies"
            if not strategies_dir.exists():
                logger.warning("Strategies directory not found")
                return
            
            for strategy_file in strategies_dir.glob("*.py"):
                if strategy_file.name.startswith("__"):
                    continue
                
                strategy_name = strategy_file.stem
                try:
                    # Dynamic import of strategy module
                    module_path = f"core.strategies.{strategy_name}"
                    module = importlib.import_module(module_path)
                    
                    # Each strategy module should have a Strategy class
                    if hasattr(module, 'Strategy'):
                        self.strategies[strategy_name] = module.Strategy()
                        logger.info(f"✅ Loaded strategy: {strategy_name}")
                    else:
                        logger.warning(f"⚠️ Strategy {strategy_name} missing Strategy class")
                        
                except Exception as e:
                    logger.error(f"❌ Failed to load strategy {strategy_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error loading strategies: {e}")
    
    def generate_high_prob_signal(self, symbol: str, timeframe: str = "1H") -> Dict[str, Any]:
        """
        Generate highest probability signal by backtesting all strategies
        """
        try:
            logger.info(f"🔍 Generating high probability signal for {symbol} on {timeframe}")
            
            # Get historical data for backtesting
            historical_data = self._get_historical_data(symbol, timeframe)
            if historical_data.empty:
                return self._get_fallback_signal(symbol)
            
            # Backtest all strategies
            strategy_results = []
            for strategy_name, strategy in self.strategies.items():
                try:
                    result = self._backtest_strategy(strategy, historical_data, symbol, strategy_name)
                    if result:
                        strategy_results.append(result)
                except Exception as e:
                    logger.error(f"Backtest failed for {strategy_name}: {e}")
            
            if not strategy_results:
                return self._get_fallback_signal(symbol)
            
            # Select best performing strategy
            best_strategy = self._select_best_strategy(strategy_results)
            
            # Generate current signal from best strategy
            current_signal = self._generate_current_signal(
                self.strategies[best_strategy['name']], 
                historical_data, 
                symbol, 
                best_strategy
            )
            
            return current_signal
            
        except Exception as e:
            logger.error(f"High prob signal generation error: {e}")
            return self._get_fallback_signal(symbol)
    
    def _get_historical_data(self, symbol: str, timeframe: str) -> pd.DataFrame:
        """Get historical data for backtesting"""
        try:
            if not self.okx_fetcher:
                # Generate sample data for testing
                return self._generate_sample_data()
            
            # Calculate the number of periods needed
            periods_map = {
                "1m": self.lookback_days * 24 * 60,
                "5m": self.lookback_days * 24 * 12,
                "15m": self.lookback_days * 24 * 4,
                "1H": self.lookback_days * 24,
                "4H": self.lookback_days * 6,
                "1D": self.lookback_days
            }
            
            limit = periods_map.get(timeframe, self.lookback_days * 24)
            
            # Fetch historical data from OKX
            candles = self.okx_fetcher.get_historical_candles(symbol, timeframe, limit)
            
            if not candles:
                return self._generate_sample_data()
            
            # Convert to DataFrame
            df = pd.DataFrame(candles)
            
            # Ensure numeric columns
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Add timestamp
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df.dropna()
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample OHLCV data for testing"""
        periods = 720  # 30 days of hourly data
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
        
        # Generate realistic price movement
        initial_price = 50000
        price_changes = np.random.normal(0, 0.01, periods)  # 1% volatility
        prices = [initial_price]
        
        for change in price_changes[1:]:
            new_price = prices[-1] * (1 + change)
            prices.append(new_price)
        
        # Generate OHLCV data
        data = []
        for i, (date, price) in enumerate(zip(dates, prices)):
            volatility = abs(np.random.normal(0, 0.005))  # 0.5% intraday volatility
            
            open_price = price
            high = open_price * (1 + volatility)
            low = open_price * (1 - volatility)
            close = open_price + np.random.normal(0, open_price * 0.003)
            volume = np.random.uniform(1000, 10000)
            
            data.append({
                'timestamp': date,
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        return pd.DataFrame(data)
    
    def _backtest_strategy(self, strategy, data: pd.DataFrame, symbol: str, strategy_name: str) -> Optional[Dict]:
        """Backtest a single strategy"""
        try:
            # Generate signals from strategy
            signals = strategy.generate_signals(data)
            
            # Calculate performance metrics
            performance = self._calculate_performance(data, signals, symbol, strategy_name)
            
            # Only return if strategy meets minimum criteria
            if (performance['win_rate'] >= self.min_win_rate and 
                performance['risk_reward_ratio'] >= self.min_risk_reward and
                performance['max_drawdown'] <= self.max_drawdown):
                
                return {
                    'name': strategy_name,
                    'performance': performance,
                    'signals': signals,
                    'strategy': strategy
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Backtest error for {strategy_name}: {e}")
            return None
    
    def _calculate_performance(self, data: pd.DataFrame, signals: List[Dict], symbol: str, strategy_name: str) -> Dict:
        """Calculate strategy performance metrics"""
        try:
            if not signals:
                return {
                    'win_rate': 0.0,
                    'risk_reward_ratio': 0.0,
                    'max_drawdown': 1.0,
                    'total_trades': 0,
                    'profit_factor': 0.0
                }
            
            trades = []
            equity_curve = [10000]  # Starting capital
            current_position = None
            
            for signal in signals:
                signal_time = signal.get('timestamp')
                action = signal.get('action', 'HOLD')
                price = signal.get('price', 0)
                
                if action == 'BUY' and current_position is None:
                    current_position = {
                        'entry_price': price,
                        'entry_time': signal_time,
                        'type': 'LONG'
                    }
                
                elif action == 'SELL' and current_position is not None:
                    # Calculate trade result
                    pnl_pct = (price - current_position['entry_price']) / current_position['entry_price']
                    
                    trades.append({
                        'entry_price': current_position['entry_price'],
                        'exit_price': price,
                        'pnl_pct': pnl_pct,
                        'duration': signal_time - current_position['entry_time'] if signal_time and current_position['entry_time'] else timedelta(hours=1)
                    })
                    
                    # Update equity curve
                    new_equity = equity_curve[-1] * (1 + pnl_pct)
                    equity_curve.append(new_equity)
                    
                    current_position = None
            
            if not trades:
                return {
                    'win_rate': 0.0,
                    'risk_reward_ratio': 0.0,
                    'max_drawdown': 1.0,
                    'total_trades': 0,
                    'profit_factor': 0.0
                }
            
            # Calculate metrics
            winning_trades = [t for t in trades if t['pnl_pct'] > 0]
            losing_trades = [t for t in trades if t['pnl_pct'] < 0]
            
            win_rate = len(winning_trades) / len(trades) if trades else 0
            
            avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
            avg_loss = abs(np.mean([t['pnl_pct'] for t in losing_trades])) if losing_trades else 0.01
            
            risk_reward_ratio = avg_win / avg_loss if avg_loss > 0 else 0
            
            # Calculate maximum drawdown
            peak = equity_curve[0]
            max_drawdown = 0
            for equity in equity_curve:
                if equity > peak:
                    peak = equity
                drawdown = (peak - equity) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # Profit factor
            total_wins = sum([t['pnl_pct'] for t in winning_trades])
            total_losses = abs(sum([t['pnl_pct'] for t in losing_trades]))
            profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
            
            return {
                'win_rate': win_rate,
                'risk_reward_ratio': risk_reward_ratio,
                'max_drawdown': max_drawdown,
                'total_trades': len(trades),
                'profit_factor': profit_factor,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'total_return': (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
            }
            
        except Exception as e:
            logger.error(f"Performance calculation error: {e}")
            return {
                'win_rate': 0.0,
                'risk_reward_ratio': 0.0,
                'max_drawdown': 1.0,
                'total_trades': 0,
                'profit_factor': 0.0
            }
    
    def _select_best_strategy(self, strategy_results: List[Dict]) -> Dict:
        """Select the best performing strategy based on composite score"""
        try:
            best_strategy = None
            best_score = -1
            
            for result in strategy_results:
                perf = result['performance']
                
                # Composite score calculation
                score = (
                    perf['win_rate'] * 0.3 +
                    min(perf['risk_reward_ratio'] / 3.0, 1.0) * 0.25 +  # Cap at 3.0
                    (1 - perf['max_drawdown']) * 0.2 +
                    min(perf['profit_factor'] / 2.0, 1.0) * 0.15 +  # Cap at 2.0
                    min(perf['total_return'], 0.5) * 0.1  # Cap at 50%
                )
                
                logger.info(f"Strategy {result['name']}: Score={score:.3f}, WinRate={perf['win_rate']:.2f}, RR={perf['risk_reward_ratio']:.2f}")
                
                if score > best_score:
                    best_score = score
                    best_strategy = result
            
            if best_strategy:
                logger.info(f"🏆 Best strategy selected: {best_strategy['name']} (Score: {best_score:.3f})")
                return best_strategy
            
            return strategy_results[0] if strategy_results else None
            
        except Exception as e:
            logger.error(f"Strategy selection error: {e}")
            return strategy_results[0] if strategy_results else None
    
    def _generate_current_signal(self, strategy, data: pd.DataFrame, symbol: str, best_strategy: Dict) -> Dict[str, Any]:
        """Generate current signal from the best strategy"""
        try:
            # Get the most recent signal from strategy
            current_signals = strategy.generate_signals(data.tail(50))  # Last 50 periods for context
            
            if not current_signals:
                return self._get_fallback_signal(symbol)
            
            # Get the latest signal
            latest_signal = current_signals[-1]
            current_price = float(data['close'].iloc[-1])
            
            # Calculate confidence based on strategy performance
            performance = best_strategy['performance']
            base_confidence = int(performance['win_rate'] * 100)
            
            # Adjust confidence based on other metrics
            if performance['risk_reward_ratio'] > 2.0:
                base_confidence += 10
            if performance['max_drawdown'] < 0.10:
                base_confidence += 5
            if performance['profit_factor'] > 1.5:
                base_confidence += 5
            
            confidence = min(base_confidence, 95)  # Cap at 95%
            
            # Calculate stop loss and take profit based on strategy
            stop_loss_pct = 0.02  # 2% default
            take_profit_pct = stop_loss_pct * performance['risk_reward_ratio']
            
            action = latest_signal.get('action', 'HOLD')
            
            if action == 'BUY':
                stop_loss = current_price * (1 - stop_loss_pct)
                take_profit = current_price * (1 + take_profit_pct)
            elif action == 'SELL':
                stop_loss = current_price * (1 + stop_loss_pct)
                take_profit = current_price * (1 - take_profit_pct)
            else:
                stop_loss = current_price * 0.98
                take_profit = current_price * 1.02
                action = 'WAIT'
            
            return {
                'status': 'success',
                'symbol': symbol,
                'strategy_used': best_strategy['name'],
                'signal': {
                    'action': action,
                    'confidence': confidence,
                    'entry_price': current_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'risk_reward_ratio': performance['risk_reward_ratio']
                },
                'strategy_performance': {
                    'win_rate': f"{performance['win_rate']*100:.1f}%",
                    'total_trades': performance['total_trades'],
                    'profit_factor': f"{performance['profit_factor']:.2f}",
                    'max_drawdown': f"{performance['max_drawdown']*100:.1f}%"
                },
                'reasoning': f"Signal generated by {best_strategy['name']} strategy with {performance['win_rate']*100:.1f}% historical win rate and {performance['risk_reward_ratio']:.1f}:1 risk-reward ratio",
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Current signal generation error: {e}")
            return self._get_fallback_signal(symbol)
    
    def _get_fallback_signal(self, symbol: str) -> Dict[str, Any]:
        """Fallback signal when no strategies are available or working"""
        return {
            'status': 'success',
            'symbol': symbol,
            'strategy_used': 'fallback',
            'signal': {
                'action': 'WAIT',
                'confidence': 50,
                'entry_price': 0,
                'stop_loss': 0,
                'take_profit': 0,
                'risk_reward_ratio': 1.0
            },
            'strategy_performance': {
                'win_rate': 'N/A',
                'total_trades': 0,
                'profit_factor': 'N/A',
                'max_drawdown': 'N/A'
            },
            'reasoning': 'No suitable strategies available, returning neutral signal',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_strategy_rankings(self, symbol: str, timeframe: str = "1H") -> List[Dict]:
        """Get performance rankings of all strategies"""
        try:
            historical_data = self._get_historical_data(symbol, timeframe)
            if historical_data.empty:
                return []
            
            rankings = []
            for strategy_name, strategy in self.strategies.items():
                try:
                    result = self._backtest_strategy(strategy, historical_data, symbol, strategy_name)
                    if result:
                        rankings.append({
                            'name': strategy_name,
                            'performance': result['performance'],
                            'rank_score': (
                                result['performance']['win_rate'] * 0.4 +
                                min(result['performance']['risk_reward_ratio'] / 3.0, 1.0) * 0.3 +
                                (1 - result['performance']['max_drawdown']) * 0.3
                            )
                        })
                except Exception as e:
                    logger.error(f"Ranking error for {strategy_name}: {e}")
            
            # Sort by rank score
            rankings.sort(key=lambda x: x['rank_score'], reverse=True)
            
            return rankings
            
        except Exception as e:
            logger.error(f"Strategy ranking error: {e}")
            return []