"""
Configuration for Holly High Probability Signal Engine
Centralized configuration for thresholds and parameters
"""

import os
from typing import Dict, Any

class HollyConfig:
    """Configuration class for Holly Signal Engine"""
    
    # Performance Thresholds (dapat di-override via environment variables)
    MIN_WIN_RATE = float(os.getenv('HOLLY_MIN_WIN_RATE', '0.55'))  # Minimum 55% win rate
    MIN_RISK_REWARD = float(os.getenv('HOLLY_MIN_RISK_REWARD', '1.5'))  # Minimum 1.5:1 RR
    MAX_DRAWDOWN = float(os.getenv('HOLLY_MAX_DRAWDOWN', '0.15'))  # Maximum 15% drawdown
    MIN_PROFIT_FACTOR = float(os.getenv('HOLLY_MIN_PROFIT_FACTOR', '1.3'))  # Minimum profit factor
    
    # Backtesting Parameters
    DEFAULT_LOOKBACK_DAYS = int(os.getenv('HOLLY_LOOKBACK_DAYS', '30'))
    DEFAULT_INITIAL_CAPITAL = float(os.getenv('HOLLY_INITIAL_CAPITAL', '10000'))
    DEFAULT_POSITION_SIZE = float(os.getenv('HOLLY_POSITION_SIZE', '0.02'))  # 2% per trade
    
    # Strategy Selection
    MIN_TRADES_FOR_VALIDATION = int(os.getenv('HOLLY_MIN_TRADES', '10'))
    STRATEGY_TIMEOUT_SECONDS = int(os.getenv('HOLLY_STRATEGY_TIMEOUT', '30'))
    
    # Caching
    CACHE_TTL_SECONDS = int(os.getenv('HOLLY_CACHE_TTL', '300'))  # 5 minutes
    MAX_CACHE_SIZE = int(os.getenv('HOLLY_MAX_CACHE_SIZE', '100'))
    
    # API Rate Limiting
    MAX_CONCURRENT_BACKTESTS = int(os.getenv('HOLLY_MAX_CONCURRENT', '5'))
    BACKTEST_COOLDOWN_SECONDS = int(os.getenv('HOLLY_BACKTEST_COOLDOWN', '1'))
    
    # Signal Validation Schema
    REQUIRED_SIGNAL_FIELDS = ['action', 'timestamp', 'price']
    OPTIONAL_SIGNAL_FIELDS = ['confidence', 'stop_loss', 'take_profit', 'reason', 'indicators']
    VALID_ACTIONS = ['BUY', 'SELL', 'HOLD']
    
    # Strategy Weights for Scoring
    WEIGHT_WIN_RATE = float(os.getenv('HOLLY_WEIGHT_WIN_RATE', '0.3'))
    WEIGHT_RISK_REWARD = float(os.getenv('HOLLY_WEIGHT_RR', '0.25'))
    WEIGHT_PROFIT_FACTOR = float(os.getenv('HOLLY_WEIGHT_PF', '0.25'))
    WEIGHT_SHARPE_RATIO = float(os.getenv('HOLLY_WEIGHT_SHARPE', '0.2'))
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            'thresholds': {
                'min_win_rate': cls.MIN_WIN_RATE,
                'min_risk_reward': cls.MIN_RISK_REWARD,
                'max_drawdown': cls.MAX_DRAWDOWN,
                'min_profit_factor': cls.MIN_PROFIT_FACTOR,
                'min_trades': cls.MIN_TRADES_FOR_VALIDATION
            },
            'backtesting': {
                'lookback_days': cls.DEFAULT_LOOKBACK_DAYS,
                'initial_capital': cls.DEFAULT_INITIAL_CAPITAL,
                'position_size': cls.DEFAULT_POSITION_SIZE,
                'timeout': cls.STRATEGY_TIMEOUT_SECONDS
            },
            'caching': {
                'ttl': cls.CACHE_TTL_SECONDS,
                'max_size': cls.MAX_CACHE_SIZE
            },
            'api': {
                'max_concurrent': cls.MAX_CONCURRENT_BACKTESTS,
                'cooldown': cls.BACKTEST_COOLDOWN_SECONDS
            },
            'weights': {
                'win_rate': cls.WEIGHT_WIN_RATE,
                'risk_reward': cls.WEIGHT_RISK_REWARD,
                'profit_factor': cls.WEIGHT_PROFIT_FACTOR,
                'sharpe_ratio': cls.WEIGHT_SHARPE_RATIO
            }
        }
    
    @classmethod
    def validate_signal(cls, signal: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate signal format consistency
        Returns: (is_valid, error_message)
        """
        if not signal:
            return False, "Signal is empty"
        
        # Check required fields
        for field in cls.REQUIRED_SIGNAL_FIELDS:
            if field not in signal:
                return False, f"Missing required field: {field}"
        
        # Validate action
        if signal.get('action') not in cls.VALID_ACTIONS:
            return False, f"Invalid action: {signal.get('action')}. Must be one of {cls.VALID_ACTIONS}"
        
        # Validate price is numeric
        try:
            float(signal.get('price', 0))
        except (ValueError, TypeError):
            return False, "Price must be numeric"
        
        # Validate timestamp
        if not signal.get('timestamp'):
            return False, "Timestamp is required"
        
        return True, "Valid signal"
    
    @classmethod
    def normalize_signal(cls, signal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize signal to ensure consistent format
        Adds default values for optional fields
        """
        normalized = {
            'action': signal.get('action', 'HOLD'),
            'timestamp': signal.get('timestamp'),
            'price': float(signal.get('price', 0)),
            'confidence': float(signal.get('confidence', 0.5)),
            'stop_loss': float(signal.get('stop_loss', 0)) if signal.get('stop_loss') else None,
            'take_profit': float(signal.get('take_profit', 0)) if signal.get('take_profit') else None,
            'reason': signal.get('reason', 'Strategy signal'),
            'indicators': signal.get('indicators', {})
        }
        return normalized