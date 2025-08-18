#!/usr/bin/env python3
"""
CircuitBreaker - Sistem perlindungan untuk mencegah over-signaling
Memblokir sinyal saat kondisi tidak ideal atau performance buruk
"""
import logging
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)

class BreakerState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking signals
    HALF_OPEN = "half_open" # Testing recovery

@dataclass
class BreakerEvent:
    timestamp: float
    event_type: str  # loss, drawdown, consecutive_loss, etc.
    value: float
    symbol: str
    reason: str

@dataclass
class BreakerStatus:
    state: BreakerState
    reason: str
    triggered_at: Optional[float]
    recovery_at: Optional[float]
    consecutive_losses: int
    daily_drawdown: float
    total_signals_today: int
    blocked_signals_count: int

class CircuitBreaker:
    def __init__(self, data_dir: str = "logs"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Circuit breaker thresholds
        self.thresholds = {
            'max_consecutive_losses': 4,     # 4 loss berturut-turut
            'max_daily_drawdown_pct': 5.0,   # 5% DD harian
            'max_signals_per_hour': 20,      # Anti-spam
            'min_win_rate_30d': 0.35,        # 35% win rate minimum
            'max_daily_signals': 50,         # Max sinyal per hari
            'recovery_test_duration': 3600,  # 1 jam testing saat half-open
            'cooling_period': 7200,          # 2 jam cooling sebelum half-open
        }
        
        # State management
        self.state = BreakerState.CLOSED
        self.triggered_at: Optional[float] = None
        self.recovery_at: Optional[float] = None
        self.events: List[BreakerEvent] = []
        self.consecutive_losses = 0
        self.daily_stats = self._load_daily_stats()
        
        # Load previous state
        self._load_state()
    
    def check_signal_permission(self, symbol: str, signal_type: str = "general") -> tuple[bool, str]:
        """
        Check if signal dapat dikirim atau harus diblokir
        Returns: (allowed, reason)
        """
        try:
            current_time = time.time()
            
            # Update state based on time
            self._update_state(current_time)
            
            # Check current state
            if self.state == BreakerState.OPEN:
                self._increment_blocked_count()
                return False, f"Circuit breaker OPEN: {self._get_block_reason()}"
            
            # Rate limiting checks
            if not self._check_rate_limits(current_time):
                self._increment_blocked_count()
                return False, "Rate limit exceeded"
            
            # Performance-based checks
            if not self._check_performance_metrics():
                self._trigger_breaker("Poor performance metrics", current_time)
                self._increment_blocked_count()
                return False, "Performance-based block"
            
            # Half-open state: allow limited signals for testing
            if self.state == BreakerState.HALF_OPEN:
                return True, "Half-open: testing recovery"
            
            # Normal operation
            return True, "Signal approved"
            
        except Exception as e:
            logger.error(f"Circuit breaker check error: {e}")
            return False, f"Circuit breaker error: {str(e)}"
    
    def record_signal_outcome(self, symbol: str, outcome: str, pnl: float = 0.0, details: Dict[str, Any] = None):
        """
        Record hasil sinyal untuk tracking performance
        outcome: 'win', 'loss', 'pending'
        """
        try:
            current_time = time.time()
            
            # Update daily stats
            today = self._get_today_key()
            if today not in self.daily_stats:
                self.daily_stats[today] = {
                    'signals': 0,
                    'wins': 0,
                    'losses': 0,
                    'total_pnl': 0.0,
                    'consecutive_losses': 0
                }
            
            stats = self.daily_stats[today]
            
            if outcome == 'win':
                stats['wins'] += 1
                self.consecutive_losses = 0  # Reset
                stats['consecutive_losses'] = 0
            elif outcome == 'loss':
                stats['losses'] += 1
                self.consecutive_losses += 1
                stats['consecutive_losses'] = self.consecutive_losses
                
                # Record loss event
                self.events.append(BreakerEvent(
                    timestamp=current_time,
                    event_type='loss',
                    value=pnl,
                    symbol=symbol,
                    reason=f"Loss recorded: {pnl:.2f}"
                ))
                
                # Check consecutive loss threshold
                if self.consecutive_losses >= self.thresholds['max_consecutive_losses']:
                    self._trigger_breaker(f"{self.consecutive_losses} consecutive losses", current_time)
            
            stats['total_pnl'] += pnl
            stats['signals'] += 1
            
            # Check daily drawdown
            daily_dd_pct = abs(min(0, stats['total_pnl']) / 10000) * 100  # Assume 10k account
            if daily_dd_pct >= self.thresholds['max_daily_drawdown_pct']:
                self._trigger_breaker(f"Daily drawdown {daily_dd_pct:.1f}%", current_time)
            
            self._save_daily_stats()
            self._save_state()
            
        except Exception as e:
            logger.error(f"Error recording signal outcome: {e}")
    
    def force_open(self, reason: str = "Manual override"):
        """Manually open circuit breaker"""
        self._trigger_breaker(reason, time.time())
        logger.warning(f"Circuit breaker manually opened: {reason}")
    
    def force_reset(self, reason: str = "Manual reset"):
        """Manually reset circuit breaker"""
        self.state = BreakerState.CLOSED
        self.triggered_at = None
        self.recovery_at = None
        self.consecutive_losses = 0
        self._save_state()
        logger.info(f"Circuit breaker manually reset: {reason}")
    
    def get_status(self) -> BreakerStatus:
        """Get current circuit breaker status"""
        today_stats = self.daily_stats.get(self._get_today_key(), {})
        
        return BreakerStatus(
            state=self.state,
            reason=self._get_block_reason(),
            triggered_at=self.triggered_at,
            recovery_at=self.recovery_at,
            consecutive_losses=self.consecutive_losses,
            daily_drawdown=abs(min(0, today_stats.get('total_pnl', 0)) / 10000) * 100,
            total_signals_today=today_stats.get('signals', 0),
            blocked_signals_count=self._get_blocked_count_today()
        )
    
    def _update_state(self, current_time: float):
        """Update circuit breaker state based on time"""
        if self.state == BreakerState.OPEN and self.triggered_at:
            # Check if cooling period has passed
            cooling_elapsed = current_time - self.triggered_at
            if cooling_elapsed >= self.thresholds['cooling_period']:
                self.state = BreakerState.HALF_OPEN
                self.recovery_at = current_time
                logger.info("Circuit breaker moved to HALF_OPEN state")
        
        elif self.state == BreakerState.HALF_OPEN and self.recovery_at:
            # Check if recovery test period has passed
            recovery_elapsed = current_time - self.recovery_at
            if recovery_elapsed >= self.thresholds['recovery_test_duration']:
                # Check if performance improved during half-open
                if self._check_recovery_performance():
                    self.state = BreakerState.CLOSED
                    self.triggered_at = None
                    self.recovery_at = None
                    logger.info("Circuit breaker CLOSED - recovery successful")
                else:
                    self.state = BreakerState.OPEN
                    self.triggered_at = current_time
                    self.recovery_at = None
                    logger.warning("Circuit breaker back to OPEN - recovery failed")
    
    def _check_rate_limits(self, current_time: float) -> bool:
        """Check various rate limits"""
        try:
            # Hourly signal limit
            hour_ago = current_time - 3600
            recent_signals = len([e for e in self.events if e.timestamp > hour_ago])
            if recent_signals >= self.thresholds['max_signals_per_hour']:
                return False
            
            # Daily signal limit  
            today_stats = self.daily_stats.get(self._get_today_key(), {})
            if today_stats.get('signals', 0) >= self.thresholds['max_daily_signals']:
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Rate limit check error: {e}")
            return False
    
    def _check_performance_metrics(self) -> bool:
        """Check if recent performance meets minimum standards"""
        try:
            # Check 30-day win rate
            thirty_days_ago = time.time() - (30 * 24 * 3600)
            recent_days = [day for day, stats in self.daily_stats.items() 
                          if self._day_to_timestamp(day) > thirty_days_ago]
            
            if recent_days:
                total_signals = sum(self.daily_stats[day].get('signals', 0) for day in recent_days)
                total_wins = sum(self.daily_stats[day].get('wins', 0) for day in recent_days)
                
                if total_signals >= 10:  # Minimum sample size
                    win_rate = total_wins / total_signals
                    if win_rate < self.thresholds['min_win_rate_30d']:
                        return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Performance check error: {e}")
            return True  # Default to allowing signals on error
    
    def _check_recovery_performance(self) -> bool:
        """Check if performance during half-open period was acceptable"""
        if not self.recovery_at:
            return False
            
        # Simple recovery check: no new consecutive losses during recovery
        return self.consecutive_losses < self.thresholds['max_consecutive_losses']
    
    def _trigger_breaker(self, reason: str, timestamp: float):
        """Trigger circuit breaker to OPEN state"""
        self.state = BreakerState.OPEN
        self.triggered_at = timestamp
        self.recovery_at = None
        
        # Log event
        self.events.append(BreakerEvent(
            timestamp=timestamp,
            event_type='breaker_triggered',
            value=0.0,
            symbol='ALL',
            reason=reason
        ))
        
        self._save_state()
        logger.warning(f"Circuit breaker TRIGGERED: {reason}")
    
    def _get_block_reason(self) -> str:
        """Get reason for current block"""
        if self.state == BreakerState.CLOSED:
            return "Normal operation"
        elif self.state == BreakerState.HALF_OPEN:
            return "Testing recovery"
        else:
            if self.events:
                return self.events[-1].reason
            return "Circuit breaker opened"
    
    def _get_today_key(self) -> str:
        """Get today's date key"""
        return time.strftime("%Y-%m-%d", time.gmtime())
    
    def _day_to_timestamp(self, day_key: str) -> float:
        """Convert day key to timestamp"""
        return time.mktime(time.strptime(day_key, "%Y-%m-%d"))
    
    def _get_blocked_count_today(self) -> int:
        """Get number of blocked signals today"""
        today = self._get_today_key()
        blocked_file = self.data_dir / f"blocked_{today}.json"
        
        if blocked_file.exists():
            try:
                with open(blocked_file, 'r') as f:
                    data = json.load(f)
                    return data.get('count', 0)
            except:
                pass
        return 0
    
    def _increment_blocked_count(self):
        """Increment today's blocked signal counter"""
        today = self._get_today_key()
        blocked_file = self.data_dir / f"blocked_{today}.json"
        
        count = self._get_blocked_count_today() + 1
        
        try:
            with open(blocked_file, 'w') as f:
                json.dump({'count': count, 'date': today}, f)
        except Exception as e:
            logger.warning(f"Failed to update blocked count: {e}")
    
    def _load_daily_stats(self) -> Dict[str, Any]:
        """Load daily statistics from file"""
        stats_file = self.data_dir / "daily_stats.json"
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load daily stats: {e}")
        
        return {}
    
    def _save_daily_stats(self):
        """Save daily statistics to file"""
        stats_file = self.data_dir / "daily_stats.json"
        
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.daily_stats, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save daily stats: {e}")
    
    def _load_state(self):
        """Load circuit breaker state from file"""
        state_file = self.data_dir / "circuit_breaker_state.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.state = BreakerState(data.get('state', 'closed'))
                    self.triggered_at = data.get('triggered_at')
                    self.recovery_at = data.get('recovery_at')
                    self.consecutive_losses = data.get('consecutive_losses', 0)
            except Exception as e:
                logger.warning(f"Failed to load circuit breaker state: {e}")
    
    def _save_state(self):
        """Save circuit breaker state to file"""
        state_file = self.data_dir / "circuit_breaker_state.json"
        
        try:
            state_data = {
                'state': self.state.value,
                'triggered_at': self.triggered_at,
                'recovery_at': self.recovery_at,
                'consecutive_losses': self.consecutive_losses,
                'last_updated': time.time()
            }
            
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save circuit breaker state: {e}")