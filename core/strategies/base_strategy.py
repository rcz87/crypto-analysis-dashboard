"""
Base Strategy Class
All trading strategies should inherit from this base class
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    
    def __init__(self, name: str = "Base Strategy"):
        self.name = name
        self.parameters = {}
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate trading signals from historical data
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            List of signal dictionaries with format:
            {
                'timestamp': datetime,
                'action': 'BUY'|'SELL'|'HOLD',
                'price': float,
                'confidence': int (0-100),
                'reason': str
            }
        """
        pass
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators (to be overridden by strategies)"""
        return data.copy()
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Validate that data has required columns"""
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required_cols)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get strategy parameters"""
        return self.parameters
    
    def set_parameters(self, parameters: Dict[str, Any]):
        """Set strategy parameters"""
        self.parameters.update(parameters)