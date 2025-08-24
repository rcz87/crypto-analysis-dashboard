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


class HollySignalBacktest(db.Model):
    """Store Holly Signal Engine backtesting results"""
    __tablename__ = 'holly_signal_backtests'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    strategy_name = db.Column(db.String(50), nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    
    # Performance metrics
    win_rate = db.Column(db.Float, nullable=False)
    risk_reward_ratio = db.Column(db.Float, nullable=False)
    total_trades = db.Column(db.Integer, nullable=False)
    winning_trades = db.Column(db.Integer, nullable=False)
    losing_trades = db.Column(db.Integer, nullable=False)
    average_return = db.Column(db.Float, nullable=False)
    sharpe_ratio = db.Column(db.Float)
    max_drawdown = db.Column(db.Float)
    
    # Signal details
    confidence_score = db.Column(db.Float, nullable=False)
    signal_strength = db.Column(db.String(20))  # STRONG, MODERATE, WEAK
    recommended_action = db.Column(db.String(20))  # BUY, SELL, HOLD
    
    # Execution details
    backtest_period_days = db.Column(db.Integer, default=30)
    execution_time_ms = db.Column(db.Integer)  # Execution time in milliseconds
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'strategy_name': self.strategy_name,
            'timeframe': self.timeframe,
            'win_rate': self.win_rate,
            'risk_reward_ratio': self.risk_reward_ratio,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'average_return': self.average_return,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'confidence_score': self.confidence_score,
            'signal_strength': self.signal_strength,
            'recommended_action': self.recommended_action,
            'backtest_period_days': self.backtest_period_days,
            'execution_time_ms': self.execution_time_ms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class NewsSentiment(db.Model):
    """Store news sentiment analysis results"""
    __tablename__ = 'news_sentiments'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    
    # News details
    headline = db.Column(db.Text, nullable=False)
    source = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text)
    published_at = db.Column(db.DateTime)
    
    # Sentiment analysis
    sentiment_score = db.Column(db.Float, nullable=False)  # -1 to 1
    sentiment_label = db.Column(db.String(20), nullable=False)  # POSITIVE, NEGATIVE, NEUTRAL
    confidence = db.Column(db.Float, nullable=False)
    
    # Market impact assessment
    market_impact = db.Column(db.String(20))  # HIGH, MEDIUM, LOW
    price_impact_prediction = db.Column(db.Float)  # Predicted price change %
    relevance_score = db.Column(db.Float)  # 0 to 1
    
    # AI analysis
    ai_summary = db.Column(db.Text)
    key_topics = db.Column(db.JSON)  # List of extracted key topics
    entities_mentioned = db.Column(db.JSON)  # Companies, people, etc.
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'headline': self.headline,
            'source': self.source,
            'url': self.url,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'sentiment_score': self.sentiment_score,
            'sentiment_label': self.sentiment_label,
            'confidence': self.confidence,
            'market_impact': self.market_impact,
            'price_impact_prediction': self.price_impact_prediction,
            'relevance_score': self.relevance_score,
            'ai_summary': self.ai_summary,
            'key_topics': self.key_topics,
            'entities_mentioned': self.entities_mentioned,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
        }


class HollyStrategyPerformance(db.Model):
    """Track individual strategy performance over time"""
    __tablename__ = 'holly_strategy_performance'
    
    id = db.Column(db.Integer, primary_key=True)
    strategy_name = db.Column(db.String(50), nullable=False)
    
    # Cumulative performance metrics
    total_signals = db.Column(db.Integer, default=0)
    successful_signals = db.Column(db.Integer, default=0)
    failed_signals = db.Column(db.Integer, default=0)
    cumulative_return = db.Column(db.Float, default=0.0)
    average_confidence = db.Column(db.Float, default=0.0)
    
    # Recent performance (last 7 days)
    recent_win_rate = db.Column(db.Float)
    recent_avg_return = db.Column(db.Float)
    recent_signal_count = db.Column(db.Integer, default=0)
    
    # Strategy configuration
    is_active = db.Column(db.Boolean, default=True)
    min_confidence_threshold = db.Column(db.Float, default=60.0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_signal_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'strategy_name': self.strategy_name,
            'total_signals': self.total_signals,
            'successful_signals': self.successful_signals,
            'failed_signals': self.failed_signals,
            'cumulative_return': self.cumulative_return,
            'average_confidence': self.average_confidence,
            'recent_win_rate': self.recent_win_rate,
            'recent_avg_return': self.recent_avg_return,
            'recent_signal_count': self.recent_signal_count,
            'is_active': self.is_active,
            'min_confidence_threshold': self.min_confidence_threshold,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_signal_at': self.last_signal_at.isoformat() if self.last_signal_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }