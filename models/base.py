from app import db
from datetime import datetime

class TradingSignal(db.Model):
    """Basic trading signal model for database testing"""
    __tablename__ = 'trading_signals'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    signal_type = db.Column(db.String(10), nullable=False)  # 'BUY', 'SELL'
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    confidence = db.Column(db.Float, default=0.0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'signal_type': self.signal_type,
            'price': self.price,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'confidence': self.confidence
        }