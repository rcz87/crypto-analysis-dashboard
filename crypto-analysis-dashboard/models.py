from app import db
from flask_login import UserMixin
import json
from datetime import datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # ensure password hash field has length of at least 256
    password_hash = db.Column(db.String(256))


class TradingSignal(db.Model):
    """Store trading signals for GPTs and Telegram"""
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # BUY/SELL
    confidence = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    take_profit = db.Column(db.Float, nullable=True)
    stop_loss = db.Column(db.Float, nullable=True)
    timeframe = db.Column(db.String(10), nullable=False)
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(50), default='GPTs_API')
    telegram_sent = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'direction': self.direction,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'take_profit': self.take_profit,
            'stop_loss': self.stop_loss,
            'timeframe': self.timeframe,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'source': self.source,
            'telegram_sent': self.telegram_sent
        }


class TelegramUser(db.Model):
    """Store Telegram user data"""
    __tablename__ = 'telegram_users'
    
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_notification = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'chat_id': self.chat_id,
            'username': self.username,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_notification': self.last_notification.isoformat() if self.last_notification else None
        }


class SignalHistory(db.Model):
    """Enhanced signal tracking and performance history"""
    __tablename__ = 'signal_history'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.String(50), unique=True, nullable=False)  # Unique tracking ID
    symbol = db.Column(db.String(20), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    signal_type = db.Column(db.String(20), nullable=False)  # BUY, SELL, HOLD
    confidence = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    take_profit = db.Column(db.Float, nullable=False)
    stop_loss = db.Column(db.Float, nullable=False)
    outcome = db.Column(db.String(20))  # HIT_TP, HIT_SL, FAILED, UNTOUCHED, PENDING
    actual_return = db.Column(db.Float)
    ai_reasoning = db.Column(db.Text)  # Original AI reasoning for the signal
    signal_timestamp = db.Column(db.DateTime)  # Original signal timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'signal_type': self.signal_type,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'take_profit': self.take_profit,
            'stop_loss': self.stop_loss,
            'outcome': self.outcome,
            'actual_return': self.actual_return,
            'ai_reasoning': self.ai_reasoning,
            'signal_timestamp': self.signal_timestamp.isoformat() if self.signal_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }