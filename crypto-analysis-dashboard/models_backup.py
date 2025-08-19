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
    """Enhanced signal tracking and performance history with self-learning capabilities"""
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
    self_reflection = db.Column(db.Text)  # AI analysis of why signal succeeded/failed
    evaluation_timestamp = db.Column(db.DateTime)  # When signal was evaluated
    signal_timestamp = db.Column(db.DateTime)  # Original signal timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for better query performance
    __table_args__ = (
        db.Index('idx_signal_symbol_timeframe', 'symbol', 'timeframe'),
        db.Index('idx_signal_outcome', 'outcome'),
        db.Index('idx_signal_created_at', 'created_at'),
        db.Index('idx_signal_evaluation', 'evaluation_timestamp'),
    )
    
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
            'self_reflection': self.self_reflection,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat() if self.evaluation_timestamp else None,
            'signal_timestamp': self.signal_timestamp.isoformat() if self.signal_timestamp else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class SystemHealth(db.Model):
    """Store system health metrics"""
    __tablename__ = 'system_health'
    
    id = db.Column(db.Integer, primary_key=True)
    endpoint = db.Column(db.String(100), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    response_time = db.Column(db.Float, nullable=False)  # in milliseconds
    is_healthy = db.Column(db.Boolean, nullable=False)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    error_message = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'endpoint': self.endpoint,
            'status_code': self.status_code,
            'response_time': self.response_time,
            'is_healthy': self.is_healthy,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None,
            'error_message': self.error_message
        }


class SignalHistory(db.Model):
    """History of all trading signals generated by the AI engine"""
    __tablename__ = 'signal_history'
    
    id = db.Column(db.Integer, primary_key=True)
    signal_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    timeframe = db.Column(db.String(10), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = db.Column(db.Float, nullable=False)
    entry_price = db.Column(db.Float, nullable=False)
    take_profit = db.Column(db.Float)
    stop_loss = db.Column(db.Float)
    risk_reward_ratio = db.Column(db.Float)
    
    # AI Analysis Data
    ai_reasoning = db.Column(db.Text)
    smc_analysis = db.Column(db.Text)  # JSON string of SMC indicators
    technical_indicators = db.Column(db.Text)  # JSON string of technical data
    market_conditions = db.Column(db.String(50))  # BULLISH, BEARISH, SIDEWAYS
    
    # Execution Tracking
    is_executed = db.Column(db.Boolean, default=False)
    executed_at = db.Column(db.DateTime)
    execution_price = db.Column(db.Float)
    execution_source = db.Column(db.String(20))  # TELEGRAM, API, MANUAL
    
    # Performance Tracking
    outcome = db.Column(db.String(20))  # WIN, LOSS, BREAKEVEN, PENDING
    pnl_percentage = db.Column(db.Float)
    closed_at = db.Column(db.DateTime)
    
    # Metadata
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'action': self.action,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'take_profit': self.take_profit,
            'stop_loss': self.stop_loss,
            'risk_reward_ratio': self.risk_reward_ratio,
            'ai_reasoning': self.ai_reasoning,
            'smc_analysis': json.loads(self.smc_analysis) if self.smc_analysis else None,
            'technical_indicators': json.loads(self.technical_indicators) if self.technical_indicators else None,
            'market_conditions': self.market_conditions,
            'is_executed': self.is_executed,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'execution_price': self.execution_price,
            'execution_source': self.execution_source,
            'outcome': self.outcome,
            'pnl_percentage': self.pnl_percentage,
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class GPTQueryLog(db.Model):
    """Log of all GPT queries and responses for analytics and improvement"""
    __tablename__ = 'gpt_query_log'
    
    id = db.Column(db.Integer, primary_key=True)
    query_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    # Request Data
    endpoint = db.Column(db.String(100), nullable=False, index=True)
    method = db.Column(db.String(10), nullable=False)
    request_params = db.Column(db.Text)  # JSON string
    user_query = db.Column(db.Text)
    
    # Response Data
    response_status = db.Column(db.Integer, nullable=False)
    response_data = db.Column(db.Text)  # JSON string
    processing_time_ms = db.Column(db.Integer)
    
    # AI Processing Details
    ai_model_used = db.Column(db.String(50))
    tokens_used = db.Column(db.Integer)
    ai_reasoning_time_ms = db.Column(db.Integer)
    confidence_score = db.Column(db.Float)
    
    # Context & Source
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    session_id = db.Column(db.String(100))
    referer = db.Column(db.String(255))
    
    # Analytics
    is_successful = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)
    feedback_rating = db.Column(db.Integer)  # 1-5 rating
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'query_id': self.query_id,
            'endpoint': self.endpoint,
            'method': self.method,
            'request_params': json.loads(self.request_params) if self.request_params else None,
            'user_query': self.user_query,
            'response_status': self.response_status,
            'response_data': json.loads(self.response_data) if self.response_data else None,
            'processing_time_ms': self.processing_time_ms,
            'ai_model_used': self.ai_model_used,
            'tokens_used': self.tokens_used,
            'ai_reasoning_time_ms': self.ai_reasoning_time_ms,
            'confidence_score': self.confidence_score,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'session_id': self.session_id,
            'referer': self.referer,
            'is_successful': self.is_successful,
            'error_message': self.error_message,
            'feedback_rating': self.feedback_rating,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserInteraction(db.Model):
    """Track user interactions with signals (clicks, executions, feedback)"""
    __tablename__ = 'user_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    interaction_id = db.Column(db.String(50), unique=True, nullable=False)
    signal_id = db.Column(db.String(50), db.ForeignKey('signal_history.signal_id'), nullable=False)
    
    # Interaction Details
    interaction_type = db.Column(db.String(30), nullable=False)  # CLICK, EXECUTE, FEEDBACK, SHARE
    interaction_source = db.Column(db.String(20), nullable=False)  # TELEGRAM, CHAT_GPT, API
    interaction_data = db.Column(db.Text)  # JSON string
    
    # User Context
    user_id = db.Column(db.String(100))
    user_agent = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))
    
    # Timing
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    signal = db.relationship('SignalHistory', backref='interactions')
    
    def to_dict(self):
        return {
            'id': self.id,
            'interaction_id': self.interaction_id,
            'signal_id': self.signal_id,
            'interaction_type': self.interaction_type,
            'interaction_source': self.interaction_source,
            'interaction_data': json.loads(self.interaction_data) if self.interaction_data else None,
            'user_id': self.user_id,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Initialize database function
def initialize_database(app):
    """Initialize database with app context"""
    try:
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

if __name__ == "__main__":
    from main import create_app
    app = create_app()
    initialize_database(app)