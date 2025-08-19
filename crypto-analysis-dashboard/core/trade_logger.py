#!/usr/bin/env python3
"""
TradeLogger - Mencatat features dan outcome untuk learning loop
Format JSONL untuk mudah diproses ML models
"""
import logging
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class TradeEntry:
    """Single trade entry for logging"""
    trade_id: str
    timestamp: float
    symbol: str
    signal_type: str  # tajam, quick, etc.
    
    # Entry features
    entry_price: float
    signal_direction: str  # BUY/SELL
    timeframe: str
    
    # Feature scores
    smc_score: float
    orderbook_score: float
    volatility_score: float
    momentum_score: float
    funding_score: float
    news_score: float
    total_score: float
    confidence: str
    
    # Market conditions at entry
    spread_bps: float
    depth_score: float
    slippage_estimate: float
    liquidity_score: float
    
    # SMC features
    structure_break: bool
    order_block_quality: float
    fvg_count: int
    market_bias: str
    
    # Technical features
    rsi: Optional[float] = None
    macd_signal: Optional[float] = None
    ema_trend: Optional[str] = None
    volume_ratio: Optional[float] = None
    
    # Execution details
    execution_approved: bool = True
    execution_warnings: Optional[List[str]] = None
    
    # Outcome (filled later)
    outcome: Optional[str] = None  # win/loss/pending
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    hold_time_minutes: Optional[int] = None
    max_favorable: Optional[float] = None
    max_adverse: Optional[float] = None
    exit_reason: Optional[str] = None
    
    def __post_init__(self):
        if self.execution_warnings is None:
            self.execution_warnings = []

class TradeLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Main trade log file
        self.trade_log_file = self.log_dir / "trade_log.jsonl"
        
        # Active trades tracking
        self.active_trades: Dict[str, TradeEntry] = {}
        self.active_trades_file = self.log_dir / "active_trades.json"
        
        # Load active trades on startup
        self._load_active_trades()
    
    def log_signal_entry(self, 
                        signal_data: Dict[str, Any],
                        scoring_data: Dict[str, Any],
                        execution_data: Dict[str, Any],
                        market_features: Dict[str, Any]) -> str:
        """
        Log new signal entry with all features
        Returns trade_id for tracking
        """
        try:
            # Generate unique trade ID
            trade_id = self._generate_trade_id(signal_data)
            
            # Extract features from various sources
            trade_entry = TradeEntry(
                trade_id=trade_id,
                timestamp=time.time(),
                symbol=signal_data.get('symbol', 'UNKNOWN'),
                signal_type=signal_data.get('type', 'unknown'),
                
                # Entry data
                entry_price=float(signal_data.get('entry_price', 0)),
                signal_direction=signal_data.get('direction', 'HOLD'),
                timeframe=signal_data.get('timeframe', '1H'),
                
                # Scoring features
                smc_score=scoring_data.get('smc_score', 0.0),
                orderbook_score=scoring_data.get('orderbook_score', 0.0),
                volatility_score=scoring_data.get('volatility_score', 0.0),
                momentum_score=scoring_data.get('momentum_score', 0.0),
                funding_score=scoring_data.get('funding_score', 0.0),
                news_score=scoring_data.get('news_score', 0.0),
                total_score=scoring_data.get('total_score', 0.0),
                confidence=scoring_data.get('confidence', 'LOW'),
                
                # Execution conditions
                spread_bps=execution_data.get('spread_bps', 999.9),
                depth_score=execution_data.get('depth_score', 0.0),
                slippage_estimate=execution_data.get('slippage_estimate', 999.9),
                liquidity_score=execution_data.get('liquidity_score', 0.0),
                execution_approved=execution_data.get('approved', False),
                execution_warnings=execution_data.get('warnings', []),
                
                # SMC features
                structure_break=market_features.get('structure_break', False),
                order_block_quality=market_features.get('ob_quality', 0.0),
                fvg_count=market_features.get('fvg_count', 0),
                market_bias=market_features.get('market_bias', 'neutral'),
                
                # Technical indicators
                rsi=market_features.get('rsi'),
                macd_signal=market_features.get('macd_signal'),
                ema_trend=market_features.get('ema_trend'),
                volume_ratio=market_features.get('volume_ratio')
            )
            
            # Add to active trades
            self.active_trades[trade_id] = trade_entry
            self._save_active_trades()
            
            logger.info(f"Trade entry logged: {trade_id} - {signal_data.get('symbol')} {signal_data.get('direction')}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Failed to log trade entry: {e}")
            return f"error_{int(time.time())}"
    
    def update_trade_outcome(self, 
                           trade_id: str,
                           outcome: str,  # win/loss
                           exit_price: float,
                           pnl: float,
                           hold_time_minutes: int,
                           max_favorable: float = 0.0,
                           max_adverse: float = 0.0,
                           exit_reason: str = "manual"):
        """
        Update trade with final outcome
        """
        try:
            if trade_id not in self.active_trades:
                logger.warning(f"Trade ID {trade_id} not found in active trades")
                return
            
            trade_entry = self.active_trades[trade_id]
            
            # Update outcome fields
            trade_entry.outcome = outcome
            trade_entry.exit_price = exit_price
            trade_entry.pnl = pnl
            trade_entry.hold_time_minutes = hold_time_minutes
            trade_entry.max_favorable = max_favorable
            trade_entry.max_adverse = max_adverse
            trade_entry.exit_reason = exit_reason
            
            # Write completed trade to log file
            self._write_trade_to_log(trade_entry)
            
            # Remove from active trades
            del self.active_trades[trade_id]
            self._save_active_trades()
            
            logger.info(f"Trade outcome updated: {trade_id} - {outcome} ({pnl:+.2f})")
            
        except Exception as e:
            logger.error(f"Failed to update trade outcome: {e}")
    
    def get_active_trades(self) -> Dict[str, TradeEntry]:
        """Get all active trades"""
        return self.active_trades.copy()
    
    def get_recent_performance(self, days: int = 30) -> Dict[str, Any]:
        """Get recent trading performance metrics"""
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            trades = self._read_trades_since(cutoff_time)
            
            if not trades:
                return {'total_trades': 0}
            
            completed_trades = [t for t in trades if t.outcome in ['win', 'loss']]
            
            if not completed_trades:
                return {'total_trades': len(trades), 'completed_trades': 0}
            
            # Calculate metrics
            wins = len([t for t in completed_trades if t.outcome == 'win'])
            losses = len([t for t in completed_trades if t.outcome == 'loss'])
            total_pnl = sum(t.pnl for t in completed_trades if t.pnl)
            
            win_pnls = [t.pnl for t in completed_trades if t.outcome == 'win' and t.pnl]
            loss_pnls = [abs(t.pnl) for t in completed_trades if t.outcome == 'loss' and t.pnl]
            
            avg_win = sum(win_pnls) / len(win_pnls) if win_pnls else 0
            avg_loss = sum(loss_pnls) / len(loss_pnls) if loss_pnls else 0
            
            return {
                'total_trades': len(completed_trades),
                'wins': wins,
                'losses': losses,
                'win_rate': wins / len(completed_trades) if completed_trades else 0,
                'total_pnl': total_pnl,
                'avg_win': avg_win,
                'avg_loss': avg_loss,
                'profit_factor': (avg_win * wins) / (avg_loss * losses) if avg_loss > 0 and losses > 0 else 0,
                'avg_hold_time': sum(t.hold_time_minutes for t in completed_trades if t.hold_time_minutes) / len(completed_trades)
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {e}")
            return {'error': str(e)}
    
    def export_training_data(self, days: int = 90) -> str:
        """
        Export recent trade data for ML training
        Returns filename of exported data
        """
        try:
            cutoff_time = time.time() - (days * 24 * 3600)
            trades = self._read_trades_since(cutoff_time)
            
            # Filter completed trades only
            completed_trades = [t for t in trades if t.outcome in ['win', 'loss']]
            
            export_file = self.log_dir / f"training_data_{int(time.time())}.jsonl"
            
            with open(export_file, 'w') as f:
                for trade in completed_trades:
                    # Convert to feature vector format for ML
                    features = self._trade_to_features(trade)
                    f.write(json.dumps(features) + '\n')
            
            logger.info(f"Exported {len(completed_trades)} trades to {export_file}")
            return str(export_file)
            
        except Exception as e:
            logger.error(f"Failed to export training data: {e}")
            return ""
    
    def _generate_trade_id(self, signal_data: Dict[str, Any]) -> str:
        """Generate unique trade ID"""
        base_string = f"{signal_data.get('symbol', 'UNK')}_{signal_data.get('direction', 'UNK')}_{int(time.time())}"
        hash_obj = hashlib.md5(base_string.encode())
        return hash_obj.hexdigest()[:12]
    
    def _write_trade_to_log(self, trade_entry: TradeEntry):
        """Write completed trade to JSONL log file"""
        try:
            with open(self.trade_log_file, 'a') as f:
                json_line = json.dumps(asdict(trade_entry))
                f.write(json_line + '\n')
        except Exception as e:
            logger.error(f"Failed to write trade to log: {e}")
    
    def _read_trades_since(self, cutoff_time: float) -> List[TradeEntry]:
        """Read trades from log file since cutoff time"""
        trades = []
        
        if not self.trade_log_file.exists():
            return trades
        
        try:
            with open(self.trade_log_file, 'r') as f:
                for line in f:
                    trade_data = json.loads(line.strip())
                    if trade_data.get('timestamp', 0) >= cutoff_time:
                        trades.append(TradeEntry(**trade_data))
        except Exception as e:
            logger.error(f"Failed to read trades from log: {e}")
        
        return trades
    
    def _trade_to_features(self, trade: TradeEntry) -> Dict[str, Any]:
        """Convert trade entry to ML feature format"""
        return {
            'features': {
                'smc_score': trade.smc_score,
                'orderbook_score': trade.orderbook_score,
                'volatility_score': trade.volatility_score,
                'momentum_score': trade.momentum_score,
                'funding_score': trade.funding_score,
                'news_score': trade.news_score,
                'total_score': trade.total_score,
                'spread_bps': trade.spread_bps,
                'depth_score': trade.depth_score,
                'liquidity_score': trade.liquidity_score,
                'structure_break': int(trade.structure_break),
                'ob_quality': trade.order_block_quality,
                'fvg_count': trade.fvg_count,
                'timeframe': trade.timeframe,
                'symbol': trade.symbol
            },
            'target': {
                'outcome': 1 if trade.outcome == 'win' else 0,
                'pnl': trade.pnl,
                'hold_time': trade.hold_time_minutes
            }
        }
    
    def _load_active_trades(self):
        """Load active trades from file"""
        if self.active_trades_file.exists():
            try:
                with open(self.active_trades_file, 'r') as f:
                    data = json.load(f)
                    self.active_trades = {k: TradeEntry(**v) for k, v in data.items()}
            except Exception as e:
                logger.warning(f"Failed to load active trades: {e}")
                self.active_trades = {}
    
    def _save_active_trades(self):
        """Save active trades to file"""
        try:
            data = {k: asdict(v) for k, v in self.active_trades.items()}
            with open(self.active_trades_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save active trades: {e}")