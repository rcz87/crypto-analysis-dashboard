"""
Performance API - Advanced Signal Performance Analytics
Provides comprehensive trading performance metrics using PostgreSQL signal history
"""

import logging
from flask import Blueprint, jsonify, request
from sqlalchemy import create_engine, desc, func, and_
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import numpy as np

# Create performance blueprint
performance_api = Blueprint('performance_api', __name__, url_prefix='/api/performance')

logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    engine = None
    SessionLocal = None
    logger.warning("DATABASE_URL not found - performance API will use mock data")

def get_db_session():
    """Get database session"""
    if SessionLocal:
        return SessionLocal()
    return None

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """Calculate Sharpe Ratio"""
    if len(returns) == 0:
        return 0.0
    
    excess_returns = np.array(returns) - risk_free_rate
    if np.std(excess_returns) == 0:
        return 0.0
    
    return np.mean(excess_returns) / np.std(excess_returns)

def calculate_max_drawdown(returns):
    """Calculate Maximum Drawdown"""
    if len(returns) == 0:
        return 0.0
    
    cumulative = np.cumprod(1 + np.array(returns) / 100)
    peak = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - peak) / peak
    return abs(np.min(drawdown)) * 100

def calculate_profit_factor(wins, losses):
    """Calculate Profit Factor"""
    total_wins = sum([w for w in wins if w > 0])
    total_losses = abs(sum([l for l in losses if l < 0]))
    
    if total_losses == 0:
        return float('inf') if total_wins > 0 else 0.0
    
    return total_wins / total_losses

def get_performance_metrics_from_db(symbol=None, days=30):
    """Get performance metrics from database using existing signal_history table"""
    session = get_db_session()
    if not session:
        return None
    
    try:
        # Use raw SQL to query existing table structure
        from sqlalchemy import text
        
        # Build base query
        base_query = """
        SELECT symbol, action, confidence, entry_price, execution_price, 
               pnl_percentage, outcome, created_at, closed_at
        FROM signal_history 
        WHERE pnl_percentage IS NOT NULL 
        AND outcome IS NOT NULL
        """
        
        # Add symbol filter
        if symbol:
            base_query += f" AND symbol = '{symbol}'"
        
        # Add time filter
        if days:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            base_query += f" AND created_at >= '{cutoff_date}'"
        
        base_query += " ORDER BY created_at DESC"
        
        result = session.execute(text(base_query))
        signals = result.fetchall()
        
        if not signals:
            return {
                'total_signals': 0,
                'win_rate': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'profit_factor': 0.0,
                'average_pnl': 0.0,
                'total_pnl': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'note': 'No closed signals found in database'
            }
        
        # Extract data from existing schema
        pnl_values = [float(s.pnl_percentage) for s in signals if s.pnl_percentage is not None]
        wins = [float(s.pnl_percentage) for s in signals if s.outcome == 'WIN' and s.pnl_percentage is not None]
        losses = [float(s.pnl_percentage) for s in signals if s.outcome == 'LOSS' and s.pnl_percentage is not None]
        
        # Calculate metrics
        total_signals = len(signals)
        win_count = len(wins)
        win_rate = (win_count / total_signals * 100) if total_signals > 0 else 0.0
        
        sharpe_ratio = calculate_sharpe_ratio(pnl_values)
        max_drawdown = calculate_max_drawdown(pnl_values)
        profit_factor = calculate_profit_factor(wins, losses)
        
        average_pnl = np.mean(pnl_values) if pnl_values else 0.0
        total_pnl = sum(pnl_values) if pnl_values else 0.0
        best_trade = max(pnl_values) if pnl_values else 0.0
        worst_trade = min(pnl_values) if pnl_values else 0.0
        
        avg_win = np.mean(wins) if wins else 0.0
        avg_loss = np.mean(losses) if losses else 0.0
        
        return {
            'total_signals': total_signals,
            'win_rate': round(win_rate, 2),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'max_drawdown': round(max_drawdown, 2),
            'profit_factor': round(profit_factor, 2),
            'average_pnl': round(average_pnl, 2),
            'total_pnl': round(total_pnl, 2),
            'best_trade': round(best_trade, 2),
            'worst_trade': round(worst_trade, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'wins': win_count,
            'losses': total_signals - win_count,
            'period_days': days,
            'symbol_filter': symbol
        }
        
    except Exception as e:
        logger.error(f"Database error in performance metrics: {e}")
        return None
    finally:
        session.close()

def get_mock_performance_metrics():
    """Mock performance data for development/testing"""
    return {
        'total_signals': 156,
        'win_rate': 68.5,
        'sharpe_ratio': 1.85,
        'max_drawdown': 12.3,
        'profit_factor': 2.4,
        'average_pnl': 2.8,
        'total_pnl': 436.8,
        'best_trade': 18.5,
        'worst_trade': -8.2,
        'avg_win': 5.6,
        'avg_loss': -2.8,
        'wins': 107,
        'losses': 49,
        'period_days': 30,
        'symbol_filter': None,
        'note': 'Mock data - Database not available'
    }

@performance_api.route('/', methods=['GET'])
def get_performance():
    """
    Get comprehensive performance metrics
    Query Parameters:
    - symbol: Filter by specific symbol (optional)
    - days: Number of days to look back (default: 30)
    """
    try:
        # Get query parameters
        symbol = request.args.get('symbol', '').upper()
        days = int(request.args.get('days', 30))
        
        # Validate parameters
        if days < 1 or days > 365:
            return jsonify({
                "status": "error",
                "message": "Days parameter must be between 1 and 365"
            }), 400
        
        if symbol and len(symbol) < 3:
            return jsonify({
                "status": "error", 
                "message": "Symbol must be at least 3 characters"
            }), 400
        
        # Get performance metrics
        metrics = get_performance_metrics_from_db(symbol if symbol else None, days)
        
        if metrics is None:
            logger.warning("Database unavailable, using mock performance data")
            metrics = get_mock_performance_metrics()
        
        # Add metadata
        metadata = {
            'timestamp': datetime.utcnow().isoformat(),
            'query_symbol': symbol if symbol else 'ALL',
            'query_period': f'{days} days',
            'data_source': 'PostgreSQL' if DATABASE_URL else 'Mock Data'
        }
        
        return jsonify({
            "status": "success",
            "data": {
                **metrics,
                'metadata': metadata
            }
        })
        
    except ValueError as e:
        return jsonify({
            "status": "error",
            "message": f"Invalid parameter: {str(e)}"
        }), 400
    except Exception as e:
        logger.error(f"Performance API error: {e}")
        return jsonify({
            "status": "error",
            "message": "Internal server error"
        }), 500

@performance_api.route('/summary', methods=['GET'])
def get_performance_summary():
    """Get simplified performance summary"""
    try:
        # Get basic metrics
        metrics = get_performance_metrics_from_db(None, 30)
        
        if metrics is None:
            metrics = get_mock_performance_metrics()
        
        # Create simplified summary
        summary = {
            'win_rate': metrics['win_rate'],
            'total_signals': metrics['total_signals'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'total_pnl': metrics['total_pnl'],
            'status': 'profitable' if metrics['total_pnl'] > 0 else 'unprofitable',
            'performance_grade': 'A' if metrics['win_rate'] >= 70 else 'B' if metrics['win_rate'] >= 60 else 'C'
        }
        
        return jsonify({
            "status": "success",
            "data": summary
        })
        
    except Exception as e:
        logger.error(f"Performance summary error: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get performance summary"
        }), 500

@performance_api.route('/metrics', methods=['GET'])
def get_detailed_metrics():
    """Get detailed performance metrics with advanced calculations"""
    try:
        symbol = request.args.get('symbol', '').upper()
        days = int(request.args.get('days', 30))
        
        metrics = get_performance_metrics_from_db(symbol if symbol else None, days)
        
        if metrics is None:
            metrics = get_mock_performance_metrics()
        
        # Add advanced metrics
        advanced_metrics = {
            'kelly_criterion': 0.0,  # Could be calculated if we have more data
            'sortino_ratio': 0.0,    # Could be calculated with downside deviation
            'calmar_ratio': metrics['total_pnl'] / metrics['max_drawdown'] if metrics['max_drawdown'] > 0 else 0,
            'recovery_factor': metrics['total_pnl'] / metrics['max_drawdown'] if metrics['max_drawdown'] > 0 else 0,
            'expectancy': (metrics['win_rate'] / 100 * metrics['avg_win']) + ((100 - metrics['win_rate']) / 100 * metrics['avg_loss'])
        }
        
        return jsonify({
            "status": "success",
            "data": {
                **metrics,
                'advanced_metrics': advanced_metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Detailed metrics error: {e}")
        return jsonify({
            "status": "error",
            "message": "Failed to get detailed metrics"
        }), 500

# Initialize database tables if needed
def init_performance_tables():
    """Initialize performance tracking tables"""
    if engine:
        try:
            # Try multiple possible locations for SQLAlchemy Base
            base = None
            try:
                from models.signal_history import Base as SignalBase
                base = SignalBase
            except Exception:
                try:
                    from models import Base as ModelsBase
                    base = ModelsBase
                except Exception:
                    base = None

            if base:
                base.metadata.create_all(bind=engine)
                logger.info("✅ Performance tracking tables initialized")
            else:
                logger.warning("No SQLAlchemy Base found for performance tables initialization; skipping.")
        except Exception as e:
            logger.error(f"Failed to initialize performance tables: {e}")

# Initialize on import
init_performance_tables()

logger.info("📊 Performance API initialized with comprehensive metrics")