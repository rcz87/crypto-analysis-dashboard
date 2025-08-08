"""
Signal Logger - Records trading signals to database for performance tracking
"""

import logging
from datetime import datetime
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None
    logger.warning("DATABASE_URL not available - signal logging disabled")

def log_signal_to_db(signal_data):
    """
    Log trading signal to database for performance tracking
    
    Args:
        signal_data (dict): Signal data containing symbol, signal, confidence, etc.
    """
    if not SessionLocal:
        logger.warning("Database not available - skipping signal logging")
        return False
    
    session = SessionLocal()
    try:
        from models.signal_history import SignalHistory
        
        # Extract signal information
        symbol = signal_data.get('symbol', 'UNKNOWN')
        timeframe = signal_data.get('timeframe', '1H')
        signal_type = signal_data.get('signal', 'NEUTRAL')
        confidence = signal_data.get('confidence', 0.0)
        current_price = signal_data.get('current_price', 0.0)
        
        # Extract risk management data
        risk_mgmt = signal_data.get('risk_management', {})
        entry_price = risk_mgmt.get('entry_price', current_price)
        stop_loss = risk_mgmt.get('stop_loss')
        take_profit = risk_mgmt.get('take_profit')
        
        # Create signal history record
        signal_record = SignalHistory(
            symbol=symbol,
            timeframe=timeframe,
            signal_type=signal_type,
            confidence=confidence,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            created_at=datetime.utcnow(),
            signal_source='GPTs_API',
            notes=f"AI Signal - Confidence: {confidence}%"
        )
        
        session.add(signal_record)
        session.commit()
        
        logger.info(f"✅ Signal logged to database: {symbol} {signal_type} @ {entry_price}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to log signal to database: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def update_signal_outcome(signal_id, exit_price, is_win=None):
    """
    Update signal with exit price and outcome
    
    Args:
        signal_id (int): Signal ID in database
        exit_price (float): Exit price
        is_win (bool): Whether trade was profitable
    """
    if not SessionLocal:
        return False
    
    session = SessionLocal()
    try:
        from models.signal_history import SignalHistory
        
        signal = session.query(SignalHistory).filter(SignalHistory.id == signal_id).first()
        if not signal:
            logger.warning(f"Signal ID {signal_id} not found")
            return False
        
        # Calculate PnL
        if signal.signal_type == 'BUY':
            pnl = ((exit_price - signal.entry_price) / signal.entry_price) * 100
        elif signal.signal_type == 'SELL':
            pnl = ((signal.entry_price - exit_price) / signal.entry_price) * 100
        else:  # NEUTRAL
            pnl = 0.0
        
        # Determine win/loss if not specified
        if is_win is None:
            is_win = pnl > 0
        
        # Update signal
        signal.exit_price = exit_price
        signal.pnl = pnl
        signal.win = is_win
        signal.is_closed = True
        signal.closed_at = datetime.utcnow()
        
        session.commit()
        
        logger.info(f"✅ Signal {signal_id} updated: PnL {pnl:.2f}% ({'WIN' if is_win else 'LOSS'})")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update signal outcome: {e}")
        session.rollback()
        return False
    finally:
        session.close()

def get_recent_signals(limit=10, symbol=None):
    """Get recent signals from database"""
    if not SessionLocal:
        return []
    
    session = SessionLocal()
    try:
        from models.signal_history import SignalHistory
        from sqlalchemy import desc
        
        query = session.query(SignalHistory)
        if symbol:
            query = query.filter(SignalHistory.symbol == symbol)
        
        signals = query.order_by(desc(SignalHistory.created_at)).limit(limit).all()
        return [signal.to_dict() for signal in signals]
        
    except Exception as e:
        logger.error(f"Failed to get recent signals: {e}")
        return []
    finally:
        session.close()

def create_sample_data():
    """Create sample signal data for testing"""
    if not SessionLocal:
        logger.warning("Database not available - cannot create sample data")
        return False
    
    session = SessionLocal()
    try:
        from models.signal_history import SignalHistory
        import random
        from datetime import timedelta
        
        # Create sample signals for last 30 days
        symbols = ['BTCUSDT', 'ETHUSDT', 'SOLUSDT', 'ADAUSDT']
        signals = ['BUY', 'SELL', 'NEUTRAL']
        
        for i in range(50):  # Create 50 sample signals
            symbol = random.choice(symbols)
            signal_type = random.choice(signals)
            confidence = random.uniform(30, 95)
            entry_price = random.uniform(100, 50000)
            
            # Create random outcome
            is_win = random.choice([True, False, True])  # 67% win rate
            pnl = random.uniform(1, 15) if is_win else random.uniform(-10, -1)
            exit_price = entry_price * (1 + pnl/100)
            
            created_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            signal_record = SignalHistory(
                symbol=symbol,
                timeframe='1H',
                signal_type=signal_type,
                confidence=confidence,
                entry_price=entry_price,
                exit_price=exit_price,
                pnl=pnl,
                win=is_win,
                is_closed=True,
                created_at=created_time,
                closed_at=created_time + timedelta(hours=random.randint(1, 24)),
                signal_source='Sample_Data'
            )
            
            session.add(signal_record)
        
        session.commit()
        logger.info("✅ Sample signal data created for testing")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create sample data: {e}")
        session.rollback()
        return False
    finally:
        session.close()

logger.info("📊 Signal Logger initialized")