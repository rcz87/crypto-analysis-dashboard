#!/usr/bin/env python3
"""
📈 Backtest Builder - Historical Strategy Performance Testing
Sistem untuk testing performa strategy pada data historis
"""

import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class BacktestResult:
    """Results dari backtesting session"""
    backtest_id: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    total_signals: int
    successful_signals: int
    failed_signals: int
    success_rate: float
    total_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    execution_time_seconds: float
    signal_details: List[Dict[str, Any]]

@dataclass
class BacktestConfiguration:
    """Configuration untuk backtesting"""
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    initial_capital: float
    position_size_percent: float
    confidence_threshold: float
    max_concurrent_positions: int
    commission_percent: float
    slippage_percent: float
    model_type: str
    custom_parameters: Dict[str, Any]

class BacktestBuilder:
    """
    📈 Backtest Builder untuk comprehensive strategy testing
    
    Features:
    - Historical data backtesting
    - Multiple timeframe support
    - Risk management integration
    - Performance metrics calculation
    - Strategy comparison
    - Monte Carlo simulation
    """
    
    def __init__(self, okx_fetcher=None, ai_engine=None, db_session=None):
        """Initialize Backtest Builder"""
        self.okx_fetcher = okx_fetcher
        self.ai_engine = ai_engine
        self.db_session = db_session
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        logger.info("📈 Backtest Builder initialized")
    
    async def run_backtest(self, config: BacktestConfiguration) -> BacktestResult:
        """
        Run comprehensive backtest with given configuration
        
        Args:
            config: Backtest configuration
            
        Returns:
            BacktestResult: Complete backtest results
        """
        start_time = datetime.now()
        backtest_id = self._generate_backtest_id(config)
        
        try:
            logger.info(f"📈 Starting backtest: {backtest_id} for {config.symbol} {config.timeframe}")
            
            # Get historical data
            historical_data = await self._fetch_historical_data(config)
            if historical_data is None or len(historical_data) == 0:
                raise ValueError("No historical data available for backtesting")
            
            # Generate signals on historical data
            signals = await self._generate_historical_signals(historical_data, config)
            
            # Simulate trading
            trading_results = self._simulate_trading(signals, historical_data, config)
            
            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(trading_results, config)
            
            # Build result
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = BacktestResult(
                backtest_id=backtest_id,
                symbol=config.symbol,
                timeframe=config.timeframe,
                start_date=config.start_date,
                end_date=config.end_date,
                total_signals=len(signals),
                successful_signals=performance_metrics['successful_signals'],
                failed_signals=performance_metrics['failed_signals'],
                success_rate=performance_metrics['success_rate'],
                total_return=performance_metrics['total_return'],
                max_drawdown=performance_metrics['max_drawdown'],
                sharpe_ratio=performance_metrics['sharpe_ratio'],
                win_rate=performance_metrics['win_rate'],
                avg_win=performance_metrics['avg_win'],
                avg_loss=performance_metrics['avg_loss'],
                profit_factor=performance_metrics['profit_factor'],
                execution_time_seconds=execution_time,
                signal_details=trading_results
            )
            
            # Save results
            await self._save_backtest_results(result)
            
            logger.info(f"📈 Backtest completed: {backtest_id} - Success rate: {result.success_rate:.1f}%")
            return result
            
        except Exception as e:
            logger.error(f"Error in backtesting: {e}")
            raise
    
    async def compare_strategies(self, configs: List[BacktestConfiguration]) -> Dict[str, Any]:
        """
        Compare multiple strategies using backtesting
        
        Args:
            configs: List of backtest configurations to compare
            
        Returns:
            comparison: Strategy comparison results
        """
        try:
            logger.info(f"📈 Starting strategy comparison with {len(configs)} configurations")
            
            # Run backtests concurrently
            tasks = [self.run_backtest(config) for config in configs]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter successful results
            successful_results = [r for r in results if isinstance(r, BacktestResult)]
            failed_results = [r for r in results if isinstance(r, Exception)]
            
            if not successful_results:
                return {'error': 'All backtests failed', 'failures': [str(e) for e in failed_results]}
            
            # Build comparison
            comparison = {
                'total_strategies': len(configs),
                'successful_backtests': len(successful_results),
                'failed_backtests': len(failed_results),
                'comparison_metrics': self._build_strategy_comparison(successful_results),
                'detailed_results': [asdict(result) for result in successful_results],
                'best_strategy': self._identify_best_strategy(successful_results),
                'worst_strategy': self._identify_worst_strategy(successful_results),
                'optimization_insights': self._generate_optimization_insights(successful_results)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error in strategy comparison: {e}")
            return {'error': str(e)}
    
    async def optimize_parameters(self, base_config: BacktestConfiguration, 
                                parameter_ranges: Dict[str, List[Any]]) -> Dict[str, Any]:
        """
        Optimize strategy parameters using grid search
        
        Args:
            base_config: Base configuration
            parameter_ranges: Parameter ranges to test
            
        Returns:
            optimization_results: Parameter optimization results
        """
        try:
            logger.info(f"📈 Starting parameter optimization for {base_config.symbol}")
            
            # Generate parameter combinations
            parameter_combinations = self._generate_parameter_combinations(parameter_ranges)
            
            if len(parameter_combinations) > 50:
                logger.warning(f"Large parameter space ({len(parameter_combinations)} combinations) - limiting to 50")
                parameter_combinations = parameter_combinations[:50]
            
            # Create configurations for each combination
            configs = []
            for i, params in enumerate(parameter_combinations):
                config = BacktestConfiguration(
                    symbol=base_config.symbol,
                    timeframe=base_config.timeframe,
                    start_date=base_config.start_date,
                    end_date=base_config.end_date,
                    initial_capital=base_config.initial_capital,
                    position_size_percent=params.get('position_size_percent', base_config.position_size_percent),
                    confidence_threshold=params.get('confidence_threshold', base_config.confidence_threshold),
                    max_concurrent_positions=params.get('max_concurrent_positions', base_config.max_concurrent_positions),
                    commission_percent=params.get('commission_percent', base_config.commission_percent),
                    slippage_percent=params.get('slippage_percent', base_config.slippage_percent),
                    model_type=base_config.model_type,
                    custom_parameters={**base_config.custom_parameters, **params}
                )
                configs.append(config)
            
            # Run optimization backtests
            optimization_results = await self.compare_strategies(configs)
            
            # Add optimization-specific analysis
            if 'detailed_results' in optimization_results:
                optimization_results['parameter_analysis'] = self._analyze_parameter_impact(
                    optimization_results['detailed_results'], parameter_ranges
                )
                optimization_results['optimal_parameters'] = self._find_optimal_parameters(
                    optimization_results['detailed_results'], parameter_ranges
                )
            
            return optimization_results
            
        except Exception as e:
            logger.error(f"Error in parameter optimization: {e}")
            return {'error': str(e)}
    
    async def monte_carlo_simulation(self, config: BacktestConfiguration, 
                                   num_simulations: int = 1000) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation untuk risk assessment
        
        Args:
            config: Backtest configuration
            num_simulations: Number of simulations to run
            
        Returns:
            simulation_results: Monte Carlo simulation results
        """
        try:
            logger.info(f"📈 Starting Monte Carlo simulation ({num_simulations} runs)")
            
            # Run base backtest
            base_result = await self.run_backtest(config)
            
            # Extract signal details for simulation
            signal_returns = [signal.get('return_percent', 0) for signal in base_result.signal_details]
            
            if not signal_returns:
                return {'error': 'No signal returns available for simulation'}
            
            # Run Monte Carlo simulations
            simulation_results = []
            
            for i in range(num_simulations):
                # Randomly sample from historical returns
                simulated_returns = np.random.choice(signal_returns, size=len(signal_returns), replace=True)
                
                # Calculate simulation metrics
                cumulative_return = np.prod(1 + np.array(simulated_returns) / 100) - 1
                max_drawdown = self._calculate_max_drawdown_from_returns(simulated_returns)
                
                simulation_results.append({
                    'simulation_id': i + 1,
                    'total_return': cumulative_return * 100,
                    'max_drawdown': max_drawdown,
                    'final_equity': config.initial_capital * (1 + cumulative_return)
                })
            
            # Analyze simulation results
            returns = [sim['total_return'] for sim in simulation_results]
            drawdowns = [sim['max_drawdown'] for sim in simulation_results]
            
            analysis = {
                'base_backtest': asdict(base_result),
                'simulation_summary': {
                    'num_simulations': num_simulations,
                    'avg_return': np.mean(returns),
                    'std_return': np.std(returns),
                    'min_return': np.min(returns),
                    'max_return': np.max(returns),
                    'percentile_5': np.percentile(returns, 5),
                    'percentile_95': np.percentile(returns, 95),
                    'probability_positive': sum(1 for r in returns if r > 0) / len(returns) * 100,
                    'avg_max_drawdown': np.mean(drawdowns),
                    'worst_drawdown': np.min(drawdowns)
                },
                'risk_metrics': {
                    'var_95': np.percentile(returns, 5),  # Value at Risk
                    'cvar_95': np.mean([r for r in returns if r <= np.percentile(returns, 5)]),  # Conditional VaR
                    'downside_deviation': np.std([r for r in returns if r < 0]),
                    'upside_deviation': np.std([r for r in returns if r > 0])
                },
                'detailed_simulations': simulation_results
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in Monte Carlo simulation: {e}")
            return {'error': str(e)}
    
    def get_backtest_history(self, symbol: str = None, timeframe: str = None, 
                           limit: int = 20) -> List[Dict[str, Any]]:
        """Get history of backtests"""
        try:
            if not self.db_session:
                return []
            
            # This would query a backtests table if it existed
            # For now, return empty list
            return []
            
        except Exception as e:
            logger.error(f"Error getting backtest history: {e}")
            return []
    
    async def _fetch_historical_data(self, config: BacktestConfiguration) -> Optional[pd.DataFrame]:
        """Fetch historical market data untuk backtesting"""
        try:
            if not self.okx_fetcher:
                # Generate mock data for testing
                return self._generate_mock_historical_data(config)
            
            # Parse dates
            start_date = datetime.fromisoformat(config.start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(config.end_date.replace('Z', '+00:00'))
            
            # Calculate number of candles needed
            timeframe_minutes = self._timeframe_to_minutes(config.timeframe)
            total_minutes = (end_date - start_date).total_seconds() / 60
            num_candles = int(total_minutes / timeframe_minutes)
            
            # Fetch data in chunks if needed
            max_candles_per_request = 1000
            all_candles = []
            
            current_end = end_date
            while len(all_candles) < num_candles and current_end > start_date:
                chunk_size = min(max_candles_per_request, num_candles - len(all_candles))
                
                candles = self.okx_fetcher.get_candles(
                    symbol=config.symbol,
                    timeframe=config.timeframe,
                    limit=chunk_size,
                    end_time=current_end
                )
                
                if not candles:
                    break
                
                all_candles.extend(candles)
                
                # Update current_end for next chunk
                if candles:
                    current_end = datetime.fromisoformat(candles[-1]['timestamp'].replace('Z', '+00:00'))
                    current_end -= timedelta(minutes=timeframe_minutes)
            
            if not all_candles:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(all_candles)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            
            # Convert price columns to float
            for col in ['open', 'high', 'low', 'close', 'volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    async def _generate_historical_signals(self, historical_data: pd.DataFrame, 
                                         config: BacktestConfiguration) -> List[Dict[str, Any]]:
        """Generate trading signals pada historical data"""
        try:
            signals = []
            
            # Process data in windows
            window_size = 100  # Process 100 candles at a time
            
            for i in range(window_size, len(historical_data), 20):  # Step by 20 for efficiency
                window_data = historical_data.iloc[max(0, i-window_size):i]
                
                if len(window_data) < 50:  # Need minimum data for analysis
                    continue
                
                # Generate signal using AI engine
                if self.ai_engine:
                    try:
                        current_candle = historical_data.iloc[i]
                        
                        # Prepare analysis data
                        analysis_data = {
                            'price_data': window_data.to_dict('records'),
                            'current_price': float(current_candle['close']),
                            'symbol': config.symbol,
                            'timeframe': config.timeframe
                        }
                        
                        # Generate signal
                        signal_response = self.ai_engine.generate_ai_snapshot(
                            symbol=config.symbol,
                            timeframe=config.timeframe,
                            analysis_result=analysis_data,
                            quick_mode=True
                        )
                        
                        # Parse signal (simplified)
                        signal = self._parse_ai_signal_response(signal_response, current_candle, config)
                        
                        if signal and signal.get('confidence', 0) >= config.confidence_threshold:
                            signals.append(signal)
                            
                    except Exception as e:
                        logger.debug(f"Error generating signal for candle {i}: {e}")
                        continue
                else:
                    # Fallback: generate mock signals
                    signal = self._generate_mock_signal(historical_data.iloc[i], config)
                    if signal and signal.get('confidence', 0) >= config.confidence_threshold:
                        signals.append(signal)
            
            logger.info(f"📈 Generated {len(signals)} signals for backtesting")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating historical signals: {e}")
            return []
    
    def _simulate_trading(self, signals: List[Dict[str, Any]], 
                         historical_data: pd.DataFrame, 
                         config: BacktestConfiguration) -> List[Dict[str, Any]]:
        """Simulate trading execution dan calculate results"""
        try:
            results = []
            current_capital = config.initial_capital
            open_positions = []
            max_equity = current_capital
            min_equity = current_capital
            
            # Create price lookup untuk fast access
            price_lookup = {}
            for _, row in historical_data.iterrows():
                timestamp = row['timestamp']
                price_lookup[timestamp] = {
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close'])
                }
            
            for signal in signals:
                try:
                    # Check if we can open new position
                    if len(open_positions) >= config.max_concurrent_positions:
                        continue
                    
                    # Calculate position size
                    position_value = current_capital * (config.position_size_percent / 100)
                    entry_price = signal['entry_price']
                    quantity = position_value / entry_price
                    
                    # Account for commission
                    commission = position_value * (config.commission_percent / 100)
                    current_capital -= commission
                    
                    # Create position
                    position = {
                        'signal_id': signal['signal_id'],
                        'entry_time': signal['timestamp'],
                        'entry_price': entry_price * (1 + config.slippage_percent / 100),  # Apply slippage
                        'quantity': quantity,
                        'action': signal['action'],
                        'take_profit': signal.get('take_profit'),
                        'stop_loss': signal.get('stop_loss'),
                        'confidence': signal['confidence']
                    }
                    
                    open_positions.append(position)
                    
                    # Simulate position management
                    exit_result = self._simulate_position_exit(position, price_lookup, config)
                    
                    if exit_result:
                        # Close position
                        open_positions.remove(position)
                        
                        # Calculate P&L
                        pnl = exit_result['exit_price'] * quantity - entry_price * quantity
                        pnl_percent = (pnl / (entry_price * quantity)) * 100
                        
                        # Apply commission untuk exit
                        exit_commission = exit_result['exit_price'] * quantity * (config.commission_percent / 100)
                        pnl -= exit_commission
                        
                        # Update capital
                        current_capital += pnl
                        
                        # Track equity for drawdown calculation
                        max_equity = max(max_equity, current_capital)
                        min_equity = min(min_equity, current_capital)
                        
                        # Record result
                        result = {
                            **position,
                            'exit_time': exit_result['exit_time'],
                            'exit_price': exit_result['exit_price'],
                            'exit_reason': exit_result['exit_reason'],
                            'pnl': pnl,
                            'pnl_percent': pnl_percent,
                            'return_percent': pnl_percent,
                            'capital_after': current_capital,
                            'success': pnl > 0
                        }
                        
                        results.append(result)
                
                except Exception as e:
                    logger.debug(f"Error simulating signal: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error in trading simulation: {e}")
            return []
    
    def _simulate_position_exit(self, position: Dict[str, Any], 
                               price_lookup: Dict[str, Dict[str, float]], 
                               config: BacktestConfiguration) -> Optional[Dict[str, Any]]:
        """Simulate when dan how position exits"""
        try:
            entry_time = pd.to_datetime(position['entry_time'])
            entry_price = position['entry_price']
            take_profit = position.get('take_profit')
            stop_loss = position.get('stop_loss')
            action = position['action']
            
            # Look for exit conditions dalam subsequent candles
            for timestamp, prices in price_lookup.items():
                if timestamp <= entry_time:
                    continue
                
                # Check time-based exit (max holding period)
                time_diff = (timestamp - entry_time).total_seconds() / 3600  # Hours
                if time_diff > 48:  # Max 48 hours holding
                    return {
                        'exit_time': timestamp,
                        'exit_price': prices['close'],
                        'exit_reason': 'TIME_LIMIT'
                    }
                
                # Check price-based exits
                if action.upper() in ['BUY', 'LONG']:
                    # Long position
                    if take_profit and prices['high'] >= take_profit:
                        return {
                            'exit_time': timestamp,
                            'exit_price': take_profit,
                            'exit_reason': 'TAKE_PROFIT'
                        }
                    elif stop_loss and prices['low'] <= stop_loss:
                        return {
                            'exit_time': timestamp,
                            'exit_price': stop_loss,
                            'exit_reason': 'STOP_LOSS'
                        }
                
                elif action.upper() in ['SELL', 'SHORT']:
                    # Short position
                    if take_profit and prices['low'] <= take_profit:
                        return {
                            'exit_time': timestamp,
                            'exit_price': take_profit,
                            'exit_reason': 'TAKE_PROFIT'
                        }
                    elif stop_loss and prices['high'] >= stop_loss:
                        return {
                            'exit_time': timestamp,
                            'exit_price': stop_loss,
                            'exit_reason': 'STOP_LOSS'
                        }
            
            # If no exit condition met, exit at last available price
            last_timestamp = max(price_lookup.keys())
            return {
                'exit_time': last_timestamp,
                'exit_price': price_lookup[last_timestamp]['close'],
                'exit_reason': 'END_OF_DATA'
            }
            
        except Exception as e:
            logger.debug(f"Error simulating position exit: {e}")
            return None
    
    def _calculate_performance_metrics(self, trading_results: List[Dict[str, Any]], 
                                     config: BacktestConfiguration) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        try:
            if not trading_results:
                return {
                    'successful_signals': 0,
                    'failed_signals': 0,
                    'success_rate': 0.0,
                    'total_return': 0.0,
                    'max_drawdown': 0.0,
                    'sharpe_ratio': 0.0,
                    'win_rate': 0.0,
                    'avg_win': 0.0,
                    'avg_loss': 0.0,
                    'profit_factor': 0.0
                }
            
            # Basic metrics
            successful_signals = sum(1 for r in trading_results if r.get('success', False))
            failed_signals = len(trading_results) - successful_signals
            success_rate = (successful_signals / len(trading_results)) * 100
            
            # Return calculations
            returns = [r.get('return_percent', 0) for r in trading_results]
            total_return = ((trading_results[-1]['capital_after'] / config.initial_capital) - 1) * 100
            
            # Win/Loss analysis
            wins = [r for r in returns if r > 0]
            losses = [r for r in returns if r < 0]
            
            win_rate = (len(wins) / len(returns)) * 100 if returns else 0
            avg_win = np.mean(wins) if wins else 0
            avg_loss = np.mean([abs(l) for l in losses]) if losses else 0
            
            # Profit factor
            total_wins = sum(wins) if wins else 0
            total_losses = sum([abs(l) for l in losses]) if losses else 0
            profit_factor = total_wins / total_losses if total_losses > 0 else float('inf') if total_wins > 0 else 0
            
            # Risk metrics
            max_drawdown = self._calculate_max_drawdown([r['capital_after'] for r in trading_results])
            sharpe_ratio = self._calculate_sharpe_ratio(returns)
            
            return {
                'successful_signals': successful_signals,
                'failed_signals': failed_signals,
                'success_rate': success_rate,
                'total_return': total_return,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'win_rate': win_rate,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {}
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown"""
        try:
            if not equity_curve:
                return 0.0
            
            peak = equity_curve[0]
            max_dd = 0.0
            
            for equity in equity_curve:
                if equity > peak:
                    peak = equity
                
                drawdown = (peak - equity) / peak * 100
                max_dd = max(max_dd, drawdown)
            
            return max_dd
            
        except Exception:
            return 0.0
    
    def _calculate_max_drawdown_from_returns(self, returns: List[float]) -> float:
        """Calculate max drawdown dari return series"""
        try:
            if not returns:
                return 0.0
            
            cumulative = [1]
            for ret in returns:
                cumulative.append(cumulative[-1] * (1 + ret / 100))
            
            peak = cumulative[0]
            max_dd = 0.0
            
            for value in cumulative:
                if value > peak:
                    peak = value
                
                drawdown = (peak - value) / peak * 100
                max_dd = max(max_dd, drawdown)
            
            return max_dd
            
        except Exception:
            return 0.0
    
    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 2.0) -> float:
        """Calculate Sharpe ratio"""
        try:
            if not returns or len(returns) < 2:
                return 0.0
            
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return == 0:
                return 0.0
            
            # Convert annual risk-free rate to period rate
            period_risk_free = risk_free_rate / 252  # Assuming daily periods
            
            sharpe = (avg_return - period_risk_free) / std_return
            
            # Annualize
            sharpe_annual = sharpe * np.sqrt(252)
            
            return sharpe_annual
            
        except Exception:
            return 0.0
    
    def _generate_backtest_id(self, config: BacktestConfiguration) -> str:
        """Generate unique backtest ID"""
        import hashlib
        
        config_str = f"{config.symbol}{config.timeframe}{config.start_date}{config.end_date}{datetime.now().isoformat()}"
        hash_obj = hashlib.md5(config_str.encode())
        return f"BT_{hash_obj.hexdigest()[:12].upper()}"
    
    def _generate_mock_historical_data(self, config: BacktestConfiguration) -> pd.DataFrame:
        """Generate mock historical data untuk testing"""
        try:
            start_date = datetime.fromisoformat(config.start_date.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(config.end_date.replace('Z', '+00:00'))
            
            timeframe_minutes = self._timeframe_to_minutes(config.timeframe)
            
            # Generate timestamps
            timestamps = []
            current = start_date
            while current <= end_date:
                timestamps.append(current)
                current += timedelta(minutes=timeframe_minutes)
            
            # Generate price data (random walk)
            np.random.seed(42)  # For reproducible results
            base_price = 50000 if 'BTC' in config.symbol else 150
            
            prices = []
            current_price = base_price
            
            for _ in timestamps:
                # Random walk dengan slight upward bias
                change_percent = np.random.normal(0.001, 0.02)  # 0.1% drift, 2% volatility
                current_price *= (1 + change_percent)
                
                # Generate OHLC
                high = current_price * (1 + abs(np.random.normal(0, 0.01)))
                low = current_price * (1 - abs(np.random.normal(0, 0.01)))
                open_price = low + (high - low) * np.random.random()
                close_price = low + (high - low) * np.random.random()
                volume = np.random.uniform(1000, 10000)
                
                prices.append({
                    'timestamp': timestamps[len(prices)],
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close_price,
                    'volume': volume
                })
            
            return pd.DataFrame(prices)
            
        except Exception as e:
            logger.error(f"Error generating mock data: {e}")
            return pd.DataFrame()
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        timeframe_map = {
            '1M': 1,
            '5M': 5,
            '15M': 15,
            '30M': 30,
            '1H': 60,
            '4H': 240,
            '1D': 1440
        }
        return timeframe_map.get(timeframe, 60)
    
    def _parse_ai_signal_response(self, signal_response: str, candle: pd.Series, 
                                config: BacktestConfiguration) -> Optional[Dict[str, Any]]:
        """Parse AI signal response into structured signal"""
        try:
            # Simple parsing logic (would be more sophisticated in practice)
            signal_response_lower = signal_response.lower()
            
            # Extract action
            action = 'HOLD'
            if any(word in signal_response_lower for word in ['buy', 'long', 'bullish']):
                action = 'BUY'
            elif any(word in signal_response_lower for word in ['sell', 'short', 'bearish']):
                action = 'SELL'
            
            if action == 'HOLD':
                return None
            
            # Extract confidence (simplified)
            confidence = 75  # Default
            if 'high confidence' in signal_response_lower or 'strong' in signal_response_lower:
                confidence = 85
            elif 'low confidence' in signal_response_lower or 'weak' in signal_response_lower:
                confidence = 65
            
            # Calculate TP/SL levels (simplified)
            entry_price = float(candle['close'])
            
            if action == 'BUY':
                take_profit = entry_price * 1.03  # 3% profit target
                stop_loss = entry_price * 0.98    # 2% stop loss
            else:
                take_profit = entry_price * 0.97  # 3% profit target
                stop_loss = entry_price * 1.02    # 2% stop loss
            
            return {
                'signal_id': f"SIG_{int(candle.name)}_{action}",
                'timestamp': candle['timestamp'],
                'symbol': config.symbol,
                'timeframe': config.timeframe,
                'action': action,
                'confidence': confidence,
                'entry_price': entry_price,
                'take_profit': take_profit,
                'stop_loss': stop_loss,
                'reasoning': signal_response[:200]  # Truncate for storage
            }
            
        except Exception as e:
            logger.debug(f"Error parsing AI signal response: {e}")
            return None
    
    def _generate_mock_signal(self, candle: pd.Series, config: BacktestConfiguration) -> Optional[Dict[str, Any]]:
        """Generate mock signal untuk testing"""
        try:
            # Simple mock signal generation
            np.random.seed(int(candle.name))
            
            # Random signal generation
            if np.random.random() < 0.1:  # 10% chance of signal
                action = np.random.choice(['BUY', 'SELL'])
                confidence = np.random.uniform(60, 95)
                entry_price = float(candle['close'])
                
                if action == 'BUY':
                    take_profit = entry_price * np.random.uniform(1.02, 1.05)
                    stop_loss = entry_price * np.random.uniform(0.96, 0.99)
                else:
                    take_profit = entry_price * np.random.uniform(0.95, 0.98)
                    stop_loss = entry_price * np.random.uniform(1.01, 1.04)
                
                return {
                    'signal_id': f"MOCK_{int(candle.name)}_{action}",
                    'timestamp': candle['timestamp'],
                    'symbol': config.symbol,
                    'timeframe': config.timeframe,
                    'action': action,
                    'confidence': confidence,
                    'entry_price': entry_price,
                    'take_profit': take_profit,
                    'stop_loss': stop_loss,
                    'reasoning': f"Mock {action} signal with {confidence:.1f}% confidence"
                }
            
            return None
            
        except Exception:
            return None
    
    async def _save_backtest_results(self, result: BacktestResult):
        """Save backtest results to database"""
        try:
            if self.db_session:
                # This would save to a backtests table if it existed
                pass
                
        except Exception as e:
            logger.error(f"Error saving backtest results: {e}")

# Export
__all__ = [
    'BacktestBuilder', 'BacktestResult', 'BacktestConfiguration'
]