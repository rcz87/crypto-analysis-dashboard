"""
📊 Professional Backtesting Engine for Crypto Trading
Similar to Cryptohopper with paper trading and historical analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
import uuid

logger = logging.getLogger(__name__)

class BacktestingEngine:
    """Professional backtesting engine for trading strategies"""
    
    def __init__(self, okx_fetcher=None, ml_engine=None):
        self.okx_fetcher = okx_fetcher
        self.ml_engine = ml_engine
        self.paper_trades = {}
        self.backtest_results = {}
        logger.info("📊 Backtesting Engine initialized")
    
    def run_backtest(self, symbol: str, strategy: str, start_date: str, 
                    end_date: str, initial_balance: float = 10000,
                    timeframe: str = '1H') -> Dict[str, Any]:
        """Run comprehensive backtest on historical data"""
        try:
            backtest_id = str(uuid.uuid4())[:8]
            
            # Get historical data
            historical_data = self._get_historical_data(symbol, start_date, end_date, timeframe)
            if historical_data is None or len(historical_data) < 100:
                return {"error": "Insufficient historical data"}
            
            # Initialize backtest state
            state = {
                'balance': initial_balance,
                'position': 0,
                'entry_price': 0,
                'trades': [],
                'peak_balance': initial_balance,
                'drawdown': 0,
                'max_drawdown': 0
            }
            
            # Run strategy on historical data
            for i in range(50, len(historical_data)):  # Start after warmup period
                current_data = historical_data.iloc[:i+1]
                signal = self._get_strategy_signal(current_data, strategy)
                
                if signal:
                    self._execute_backtest_trade(state, signal, current_data.iloc[-1])
            
            # Calculate final metrics
            final_results = self._calculate_backtest_metrics(state, historical_data)
            final_results['backtest_id'] = backtest_id
            final_results['symbol'] = symbol
            final_results['strategy'] = strategy
            final_results['period'] = f"{start_date} to {end_date}"
            
            # Save results
            self.backtest_results[backtest_id] = final_results
            
            return final_results
            
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return {"error": f"Backtest failed: {str(e)}"}
    
    def start_paper_trading(self, symbol: str, strategy: str, 
                           initial_balance: float = 10000) -> Dict[str, Any]:
        """Start paper trading session"""
        try:
            session_id = str(uuid.uuid4())[:8]
            
            paper_session = {
                'session_id': session_id,
                'symbol': symbol,
                'strategy': strategy,
                'balance': initial_balance,
                'initial_balance': initial_balance,
                'position': 0,
                'entry_price': 0,
                'trades': [],
                'start_time': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat(),
                'status': 'ACTIVE'
            }
            
            self.paper_trades[session_id] = paper_session
            
            return {
                "session_id": session_id,
                "status": "Paper trading started",
                "symbol": symbol,
                "strategy": strategy,
                "initial_balance": initial_balance,
                "current_balance": initial_balance
            }
            
        except Exception as e:
            logger.error(f"Paper trading start error: {e}")
            return {"error": f"Failed to start paper trading: {str(e)}"}
    
    def get_paper_trading_status(self, session_id: str) -> Dict[str, Any]:
        """Get current paper trading status"""
        if session_id not in self.paper_trades:
            return {"error": "Paper trading session not found"}
        
        session = self.paper_trades[session_id]
        
        # Calculate performance metrics
        pnl = session['balance'] - session['initial_balance']
        pnl_pct = (pnl / session['initial_balance']) * 100
        
        return {
            "session_id": session_id,
            "symbol": session['symbol'],
            "strategy": session['strategy'],
            "current_balance": round(session['balance'], 2),
            "initial_balance": session['initial_balance'],
            "pnl": round(pnl, 2),
            "pnl_percentage": round(pnl_pct, 2),
            "current_position": session['position'],
            "entry_price": session['entry_price'],
            "total_trades": len(session['trades']),
            "last_update": session['last_update'],
            "status": session['status'],
            "recent_trades": session['trades'][-5:] if session['trades'] else []
        }
    
    def execute_paper_trade(self, session_id: str) -> Dict[str, Any]:
        """Execute a paper trade based on current market conditions"""
        if session_id not in self.paper_trades:
            return {"error": "Paper trading session not found"}
        
        try:
            session = self.paper_trades[session_id]
            
            # Get current market data
            df = self.okx_fetcher.get_candles(session['symbol'], '1H', limit=100)
            if df is None or df.empty:
                return {"error": "No market data available"}
            
            # Get strategy signal
            signal = self._get_strategy_signal(df, session['strategy'])
            
            if signal:
                trade_result = self._execute_paper_trade_signal(session, signal, df.iloc[-1])
                session['last_update'] = datetime.now().isoformat()
                return trade_result
            else:
                return {
                    "action": "NO_SIGNAL",
                    "message": "No trading signal generated",
                    "current_price": float(df['close'].iloc[-1])
                }
                
        except Exception as e:
            logger.error(f"Paper trade execution error: {e}")
            return {"error": f"Paper trade failed: {str(e)}"}
    
    def _get_historical_data(self, symbol: str, start_date: str, 
                           end_date: str, timeframe: str) -> Optional[pd.DataFrame]:
        """Get historical market data for backtesting"""
        try:
            # Calculate number of candles needed
            days_diff = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days
            
            if timeframe == '1H':
                limit = min(days_diff * 24, 1000)
            elif timeframe == '4H':
                limit = min(days_diff * 6, 1000)
            elif timeframe == '1D':
                limit = min(days_diff, 1000)
            else:
                limit = 500
            
            # Get historical data from OKX
            df = self.okx_fetcher.get_candles(symbol, timeframe, limit=limit)
            
            if df is not None and not df.empty:
                # Filter by date range if possible
                df['timestamp'] = pd.to_datetime(df.index)
                return df
            
            return None
            
        except Exception as e:
            logger.error(f"Historical data fetch error: {e}")
            return None
    
    def _get_strategy_signal(self, df: pd.DataFrame, strategy: str) -> Optional[Dict]:
        """Get trading signal based on strategy"""
        try:
            if strategy == "ML_ENSEMBLE":
                # Use ML prediction
                if self.ml_engine:
                    prediction = self.ml_engine.get_comprehensive_prediction(
                        df.columns[0] if hasattr(df.columns, '__getitem__') else 'BTC-USDT-SWAP'
                    )
                    
                    if prediction and 'trading_signal' in prediction:
                        signal = prediction['trading_signal']
                        if signal['action'] in ['BUY', 'SELL']:
                            return {
                                'action': signal['action'],
                                'strength': signal['strength'],
                                'confidence': prediction['confidence'],
                                'price': prediction['current_price']
                            }
                
            elif strategy == "RSI_MACD":
                return self._rsi_macd_strategy(df)
            
            elif strategy == "SMA_CROSSOVER":
                return self._sma_crossover_strategy(df)
            
            elif strategy == "BREAKOUT":
                return self._breakout_strategy(df)
            
            return None
            
        except Exception as e:
            logger.error(f"Strategy signal error: {e}")
            return None
    
    def _rsi_macd_strategy(self, df: pd.DataFrame) -> Optional[Dict]:
        """RSI + MACD strategy"""
        if len(df) < 50:
            return None
        
        # Calculate RSI
        rsi = self._calculate_rsi(df['close'])
        current_rsi = rsi.iloc[-1]
        
        # Simple MACD
        ema12 = df['close'].ewm(span=12).mean()
        ema26 = df['close'].ewm(span=26).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9).mean()
        
        current_macd = macd.iloc[-1]
        current_signal = macd_signal.iloc[-1]
        
        # Generate signals
        if current_rsi < 30 and current_macd > current_signal:
            return {
                'action': 'BUY',
                'strength': 'STRONG' if current_rsi < 25 else 'MODERATE',
                'confidence': 75,
                'price': float(df['close'].iloc[-1])
            }
        elif current_rsi > 70 and current_macd < current_signal:
            return {
                'action': 'SELL',
                'strength': 'STRONG' if current_rsi > 75 else 'MODERATE',
                'confidence': 75,
                'price': float(df['close'].iloc[-1])
            }
        
        return None
    
    def _sma_crossover_strategy(self, df: pd.DataFrame) -> Optional[Dict]:
        """Simple Moving Average crossover strategy"""
        if len(df) < 50:
            return None
        
        sma20 = df['close'].rolling(20).mean()
        sma50 = df['close'].rolling(50).mean()
        
        current_20 = sma20.iloc[-1]
        current_50 = sma50.iloc[-1]
        prev_20 = sma20.iloc[-2]
        prev_50 = sma50.iloc[-2]
        
        # Golden cross (bullish)
        if prev_20 <= prev_50 and current_20 > current_50:
            return {
                'action': 'BUY',
                'strength': 'MODERATE',
                'confidence': 65,
                'price': float(df['close'].iloc[-1])
            }
        # Death cross (bearish)
        elif prev_20 >= prev_50 and current_20 < current_50:
            return {
                'action': 'SELL',
                'strength': 'MODERATE',
                'confidence': 65,
                'price': float(df['close'].iloc[-1])
            }
        
        return None
    
    def _breakout_strategy(self, df: pd.DataFrame) -> Optional[Dict]:
        """Breakout strategy"""
        if len(df) < 20:
            return None
        
        # Bollinger Bands breakout
        sma20 = df['close'].rolling(20).mean()
        std20 = df['close'].rolling(20).std()
        upper_band = sma20 + (std20 * 2)
        lower_band = sma20 - (std20 * 2)
        
        current_price = df['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        
        # Breakout signals
        if current_price > current_upper:
            return {
                'action': 'BUY',
                'strength': 'STRONG',
                'confidence': 70,
                'price': float(current_price)
            }
        elif current_price < current_lower:
            return {
                'action': 'SELL',
                'strength': 'STRONG',
                'confidence': 70,
                'price': float(current_price)
            }
        
        return None
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _execute_backtest_trade(self, state: Dict, signal: Dict, candle: pd.Series):
        """Execute trade in backtest"""
        current_price = float(candle['close'])
        
        if signal['action'] == 'BUY' and state['position'] <= 0:
            # Close short position if any
            if state['position'] < 0:
                pnl = abs(state['position']) * (state['entry_price'] - current_price)
                state['balance'] += pnl
                
                state['trades'].append({
                    'type': 'CLOSE_SHORT',
                    'price': current_price,
                    'quantity': abs(state['position']),
                    'pnl': pnl,
                    'timestamp': candle.name
                })
            
            # Open long position
            quantity = state['balance'] * 0.95 / current_price  # 95% of balance
            state['position'] = quantity
            state['entry_price'] = current_price
            
            state['trades'].append({
                'type': 'BUY',
                'price': current_price,
                'quantity': quantity,
                'timestamp': candle.name
            })
            
        elif signal['action'] == 'SELL' and state['position'] >= 0:
            # Close long position if any
            if state['position'] > 0:
                pnl = state['position'] * (current_price - state['entry_price'])
                state['balance'] += pnl
                
                state['trades'].append({
                    'type': 'CLOSE_LONG',
                    'price': current_price,
                    'quantity': state['position'],
                    'pnl': pnl,
                    'timestamp': candle.name
                })
            
            # Open short position
            quantity = -(state['balance'] * 0.95 / current_price)
            state['position'] = quantity
            state['entry_price'] = current_price
            
            state['trades'].append({
                'type': 'SELL',
                'price': current_price,
                'quantity': abs(quantity),
                'timestamp': candle.name
            })
        
        # Update drawdown
        if state['balance'] > state['peak_balance']:
            state['peak_balance'] = state['balance']
        
        current_drawdown = (state['peak_balance'] - state['balance']) / state['peak_balance'] * 100
        if current_drawdown > state['max_drawdown']:
            state['max_drawdown'] = current_drawdown
    
    def _execute_paper_trade_signal(self, session: Dict, signal: Dict, candle: pd.Series) -> Dict:
        """Execute paper trade signal"""
        current_price = float(candle['close'])
        
        if signal['action'] == 'BUY' and session['position'] <= 0:
            # Close short and go long
            if session['position'] < 0:
                pnl = abs(session['position']) * (session['entry_price'] - current_price)
                session['balance'] += pnl
            
            # New long position
            quantity = session['balance'] * 0.95 / current_price
            session['position'] = quantity
            session['entry_price'] = current_price
            
            trade_record = {
                'action': 'BUY',
                'price': current_price,
                'quantity': quantity,
                'timestamp': datetime.now().isoformat(),
                'balance_after': session['balance']
            }
            session['trades'].append(trade_record)
            
            return {
                "action": "BUY",
                "price": current_price,
                "quantity": round(quantity, 6),
                "new_balance": round(session['balance'], 2)
            }
            
        elif signal['action'] == 'SELL' and session['position'] >= 0:
            # Close long and go short
            if session['position'] > 0:
                pnl = session['position'] * (current_price - session['entry_price'])
                session['balance'] += pnl
            
            # New short position
            quantity = -(session['balance'] * 0.95 / current_price)
            session['position'] = quantity
            session['entry_price'] = current_price
            
            trade_record = {
                'action': 'SELL',
                'price': current_price,
                'quantity': abs(quantity),
                'timestamp': datetime.now().isoformat(),
                'balance_after': session['balance']
            }
            session['trades'].append(trade_record)
            
            return {
                "action": "SELL",
                "price": current_price,
                "quantity": round(abs(quantity), 6),
                "new_balance": round(session['balance'], 2)
            }
        
        return {"action": "NO_ACTION", "reason": "No valid signal or position conflict"}
    
    def _calculate_backtest_metrics(self, state: Dict, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive backtest metrics"""
        trades = state['trades']
        initial_balance = 10000  # Default
        final_balance = state['balance']
        
        # Basic metrics
        total_return = (final_balance - initial_balance) / initial_balance * 100
        total_trades = len([t for t in trades if t['type'] in ['BUY', 'SELL']])
        
        # Win rate calculation
        profitable_trades = len([t for t in trades if t.get('pnl', 0) > 0])
        losing_trades = len([t for t in trades if t.get('pnl', 0) < 0])
        win_rate = (profitable_trades / (profitable_trades + losing_trades) * 100) if (profitable_trades + losing_trades) > 0 else 0
        
        # Risk metrics
        returns = []
        if len(trades) > 1:
            for trade in trades:
                if 'pnl' in trade:
                    returns.append(trade['pnl'] / initial_balance * 100)
        
        volatility = np.std(returns) if returns else 0
        sharpe_ratio = (np.mean(returns) / volatility) if volatility > 0 else 0
        
        return {
            "performance": {
                "initial_balance": initial_balance,
                "final_balance": round(final_balance, 2),
                "total_return_pct": round(total_return, 2),
                "total_trades": total_trades,
                "win_rate_pct": round(win_rate, 2),
                "max_drawdown_pct": round(state['max_drawdown'], 2)
            },
            "risk_metrics": {
                "volatility": round(volatility, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "profitable_trades": profitable_trades,
                "losing_trades": losing_trades
            },
            "trade_details": trades[-10:],  # Last 10 trades
            "status": "COMPLETED",
            "generated_at": datetime.now().isoformat()
        }