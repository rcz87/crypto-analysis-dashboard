"""
Main orchestrator for coordinating trading analysis components
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import time

logger = logging.getLogger(__name__)

class MainOrchestrator:
    """Main orchestrator for coordinating trading analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.last_run = None
        self.run_count = 0
        
    def run(self):
        """Run the main trading analysis cycle"""
        try:
            self.logger.info("Starting trading analysis cycle")
            start_time = time.time()
            
            # Import components
            from core.okx_fetcher import OKXAPIManager
            from core.analyzer import TechnicalAnalyzer
            
            # Initialize components
            api_manager = OKXAPIManager()
            analyzer = TechnicalAnalyzer()
            
            # Get symbols from config
            symbols = ['BTC-USDT', 'ETH-USDT', 'SOL-USDT', 'TIA-USDT', 'RENDER-USDT']
            
            results = []
            
            for symbol in symbols:
                try:
                    # Fetch data
                    df = api_manager.get_candles(symbol, '1H', limit=100)
                    
                    if df is not None and not df.empty:
                        # Run analysis
                        analysis = analyzer.analyze(df, symbol, '1H')
                        results.append({
                            'symbol': symbol,
                            'analysis': analysis,
                            'timestamp': datetime.now()
                        })
                        
                except Exception as e:
                    self.logger.error(f"Error analyzing {symbol}: {e}")
                    continue
            
            # Update metrics
            self.run_count += 1
            self.last_run = datetime.now()
            
            execution_time = time.time() - start_time
            self.logger.info(f"Analysis cycle completed in {execution_time:.2f}s")
            
            return results
            
        except Exception as e:
            self.logger.error(f"Orchestrator error: {e}", exc_info=True)
            return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'run_count': self.run_count,
            'status': 'active'
        }