"""
Advanced Trading Endpoints
Integrates Enhanced SMC, Multi-Timeframe, and Risk Management
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import logging
from datetime import datetime
import pandas as pd

# Import enhanced modules
from core.enhanced_smc_advanced import EnhancedSMCAdvanced
from core.enhanced_multi_timeframe import EnhancedMultiTimeframe
from core.risk_management_atr import RiskManagementATR
from core.okx_fetcher import OKXFetcher

# Initialize components
logger = logging.getLogger(__name__)
advanced_trading_bp = Blueprint('advanced_trading', __name__)

# Initialize analyzers
smc_advanced = EnhancedSMCAdvanced()
mtf_analyzer = EnhancedMultiTimeframe()
risk_manager = RiskManagementATR()
okx_fetcher = OKXFetcher()

@advanced_trading_bp.route('/api/advanced/smc-analysis', methods=['GET', 'POST'])
@cross_origin()
def advanced_smc_analysis():
    """
    Enhanced SMC Analysis with CHoCH, FVG, and Liquidity Sweeps
    Supports both GET and POST methods for ChatGPT compatibility
    """
    try:
        # Handle both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = {}
        
        # Extract parameters
        symbol = data.get('symbol', request.args.get('symbol', 'BTC-USDT'))
        timeframe = data.get('timeframe', request.args.get('timeframe', '1H'))
        
        # Normalize symbol for OKX
        okx_symbol = symbol if '-' in symbol else symbol.replace('USDT', '-USDT')
        
        logger.info(f"🎯 Advanced SMC analysis for {okx_symbol} {timeframe}")
        
        # Fetch market data
        market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, limit=100)
        
        if not market_data or 'candles' not in market_data:
            return jsonify({
                'success': False,
                'error': 'Unable to fetch market data'
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(market_data['candles'])
        
        # Perform advanced SMC analysis
        smc_result = smc_advanced.analyze_complete_smc(df, okx_symbol)
        
        # Add current market price
        current_price = float(df['close'].iloc[-1]) if not df.empty else 0
        smc_result['current_price'] = current_price
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'analysis': smc_result,
            'features': {
                'choch_detected': smc_result['choch']['detected'],
                'fvg_count': len(smc_result['fair_value_gaps']),
                'liquidity_sweep': smc_result['liquidity_sweeps']['sweep_detected'],
                'order_blocks': len(smc_result['order_blocks']),
                'confidence': smc_result['confidence']['score']
            }
        })
        
    except Exception as e:
        logger.error(f"Advanced SMC analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_trading_bp.route('/api/advanced/multi-timeframe', methods=['GET', 'POST'])
@cross_origin()
def multi_timeframe_analysis():
    """
    Multi-Timeframe Analysis (1H + 4H + Daily)
    Provides confluence across multiple timeframes
    """
    try:
        # Handle both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = {}
        
        symbol = data.get('symbol', request.args.get('symbol', 'BTC-USDT'))
        
        # Normalize symbol
        okx_symbol = symbol if '-' in symbol else symbol.replace('USDT', '-USDT')
        
        logger.info(f"📊 Multi-timeframe analysis for {okx_symbol}")
        
        # Perform multi-timeframe analysis
        mtf_result = mtf_analyzer.analyze_all_timeframes(okx_symbol)
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'analysis': mtf_result,
            'summary': {
                'confluence_score': mtf_result['confluence']['score'],
                'bias': mtf_result['confluence']['bias'],
                'aligned': mtf_result['alignment']['aligned'],
                'recommendation': mtf_result['recommendation']['action'],
                'confidence': mtf_result['recommendation']['confidence']
            }
        })
        
    except Exception as e:
        logger.error(f"Multi-timeframe analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_trading_bp.route('/api/advanced/risk-management', methods=['GET', 'POST'])
@cross_origin()
def risk_management_calculation():
    """
    Risk Management with ATR-based Stop Loss and Take Profit
    Calculates position sizing and risk parameters
    """
    try:
        # Handle both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = {}
        
        # Extract parameters
        symbol = data.get('symbol', request.args.get('symbol', 'BTC-USDT'))
        timeframe = data.get('timeframe', request.args.get('timeframe', '1H'))
        signal_type = data.get('signal_type', request.args.get('signal_type', 'BUY'))
        confidence = float(data.get('confidence', request.args.get('confidence', 70)))
        account_balance = float(data.get('account_balance', request.args.get('account_balance', 10000)))
        risk_per_trade = float(data.get('risk_per_trade', request.args.get('risk_per_trade', 2)))
        
        # Normalize symbol
        okx_symbol = symbol if '-' in symbol else symbol.replace('USDT', '-USDT')
        
        logger.info(f"💰 Risk management calculation for {okx_symbol}")
        
        # Update risk manager settings if provided
        if account_balance != risk_manager.account_balance:
            risk_manager.update_account_balance(account_balance)
        if risk_per_trade != risk_manager.risk_per_trade:
            risk_manager.risk_per_trade = risk_per_trade
        
        # Fetch market data
        market_data = okx_fetcher.get_historical_data(okx_symbol, timeframe, limit=50)
        
        if not market_data or 'candles' not in market_data:
            return jsonify({
                'success': False,
                'error': 'Unable to fetch market data'
            }), 400
        
        # Convert to DataFrame
        df = pd.DataFrame(market_data['candles'])
        
        # Calculate risk parameters
        risk_params = risk_manager.calculate_risk_parameters(
            df, 
            signal_type=signal_type,
            confidence=confidence
        )
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'risk_management': risk_params,
            'summary': {
                'entry': risk_params['entry_price'],
                'stop_loss': risk_params['stop_loss'],
                'take_profit': risk_params['take_profit_levels']['tp2'],
                'position_size_units': risk_params['position_sizing']['units'],
                'risk_reward_ratio': risk_params['reward_metrics']['rr_ratio_tp2'],
                'max_loss': risk_params['risk_metrics']['max_loss_dollar'],
                'risk_level': risk_params['risk_level']
            }
        })
        
    except Exception as e:
        logger.error(f"Risk management calculation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_trading_bp.route('/api/advanced/complete-analysis', methods=['GET', 'POST'])
@cross_origin()
def complete_trading_analysis():
    """
    Complete Trading Analysis combining SMC, Multi-Timeframe, and Risk Management
    This is the ultimate endpoint for comprehensive trading decisions
    """
    try:
        # Handle both GET and POST
        if request.method == 'POST':
            data = request.get_json() or {}
        else:
            data = {}
        
        # Extract parameters
        symbol = data.get('symbol', request.args.get('symbol', 'BTC-USDT'))
        account_balance = float(data.get('account_balance', request.args.get('account_balance', 10000)))
        risk_per_trade = float(data.get('risk_per_trade', request.args.get('risk_per_trade', 2)))
        
        # Normalize symbol
        okx_symbol = symbol if '-' in symbol else symbol.replace('USDT', '-USDT')
        
        logger.info(f"🚀 Complete trading analysis for {okx_symbol}")
        
        # 1. Multi-Timeframe Analysis
        mtf_result = mtf_analyzer.analyze_all_timeframes(okx_symbol)
        
        # 2. Advanced SMC Analysis on primary timeframe (1H)
        market_data = okx_fetcher.get_historical_data(okx_symbol, '1H', limit=100)
        if market_data and 'candles' in market_data:
            df = pd.DataFrame(market_data['candles'])
            smc_result = smc_advanced.analyze_complete_smc(df, okx_symbol)
        else:
            smc_result = {'error': 'Unable to fetch data for SMC analysis'}
        
        # 3. Determine signal from combined analysis
        signal_type = 'HOLD'
        combined_confidence = 50
        
        # Combine signals from MTF and SMC
        if mtf_result['recommendation']['action'] in ['BUY', 'STRONG_BUY']:
            if smc_result.get('recommendation', {}).get('action') == 'BUY':
                signal_type = 'BUY'
                combined_confidence = (mtf_result['recommendation']['confidence'] + 
                                      smc_result['recommendation']['confidence']) / 2
            elif smc_result.get('recommendation', {}).get('action') != 'SELL':
                signal_type = 'BUY'
                combined_confidence = mtf_result['recommendation']['confidence'] * 0.8
        
        elif mtf_result['recommendation']['action'] in ['SELL', 'STRONG_SELL']:
            if smc_result.get('recommendation', {}).get('action') == 'SELL':
                signal_type = 'SELL'
                combined_confidence = (mtf_result['recommendation']['confidence'] + 
                                      smc_result['recommendation']['confidence']) / 2
            elif smc_result.get('recommendation', {}).get('action') != 'BUY':
                signal_type = 'SELL'
                combined_confidence = mtf_result['recommendation']['confidence'] * 0.8
        
        # 4. Risk Management Calculation
        risk_params = {}
        if signal_type != 'HOLD' and df is not None:
            if account_balance != risk_manager.account_balance:
                risk_manager.update_account_balance(account_balance)
            if risk_per_trade != risk_manager.risk_per_trade:
                risk_manager.risk_per_trade = risk_per_trade
            
            risk_params = risk_manager.calculate_risk_parameters(
                df,
                signal_type=signal_type,
                confidence=combined_confidence
            )
        
        # 5. Generate comprehensive trading decision
        trading_decision = {
            'action': signal_type,
            'confidence': combined_confidence,
            'entry_price': risk_params.get('entry_price', 0),
            'stop_loss': risk_params.get('stop_loss', 0),
            'take_profit': risk_params.get('take_profit_levels', {}).get('tp2', 0),
            'position_size': risk_params.get('position_sizing', {}).get('units', 0),
            'risk_reward_ratio': risk_params.get('reward_metrics', {}).get('rr_ratio_tp2', 0),
            'risk_level': risk_params.get('risk_level', 'UNKNOWN')
        }
        
        # 6. Key insights
        key_insights = []
        
        # MTF insights
        if mtf_result['alignment']['aligned']:
            key_insights.append(f"✅ All timeframes aligned {mtf_result['confluence']['bias']}")
        else:
            key_insights.append("⚠️ Timeframes not fully aligned")
        
        # SMC insights
        if smc_result.get('choch', {}).get('detected'):
            key_insights.append(f"🔄 {smc_result['choch']['type']} detected")
        if smc_result.get('fair_value_gaps'):
            key_insights.append(f"📊 {len(smc_result['fair_value_gaps'])} FVG zones available")
        if smc_result.get('liquidity_sweeps', {}).get('sweep_detected'):
            key_insights.append(f"💧 {smc_result['liquidity_sweeps']['sweep_type']} detected")
        
        # Risk insights
        if risk_params:
            if risk_params.get('volatility', {}).get('regime') == 'HIGH':
                key_insights.append("⚠️ High volatility - wider stops recommended")
            if risk_params.get('reward_metrics', {}).get('rr_ratio_tp2', 0) >= 2:
                key_insights.append("✅ Favorable risk/reward ratio")
        
        return jsonify({
            'success': True,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'trading_decision': trading_decision,
            'key_insights': key_insights,
            'detailed_analysis': {
                'multi_timeframe': {
                    'confluence_score': mtf_result['confluence']['score'],
                    'bias': mtf_result['confluence']['bias'],
                    'aligned': mtf_result['alignment']['aligned'],
                    'key_levels': mtf_result.get('key_levels', {})
                },
                'smc_analysis': {
                    'market_structure': smc_result.get('market_structure', {}),
                    'choch': smc_result.get('choch', {}),
                    'fvg_count': len(smc_result.get('fair_value_gaps', [])),
                    'liquidity_sweep': smc_result.get('liquidity_sweeps', {}),
                    'confidence': smc_result.get('confidence', {})
                },
                'risk_management': {
                    'atr': risk_params.get('risk_metrics', {}).get('atr', 0),
                    'volatility_regime': risk_params.get('volatility', {}).get('regime', 'UNKNOWN'),
                    'position_sizing': risk_params.get('position_sizing', {}),
                    'scaling_strategy': risk_params.get('scaling_strategy', {}),
                    'trailing_stop': risk_params.get('trailing_stop', {})
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Complete analysis error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@advanced_trading_bp.route('/api/advanced/status', methods=['GET'])
@cross_origin()
def advanced_trading_status():
    """
    Status endpoint for advanced trading features
    """
    return jsonify({
        'success': True,
        'status': 'operational',
        'features': {
            'enhanced_smc': {
                'enabled': True,
                'capabilities': ['CHoCH', 'FVG', 'Liquidity Sweeps', 'Order Blocks', 'Breaker Blocks']
            },
            'multi_timeframe': {
                'enabled': True,
                'timeframes': ['1H', '4H', '1D'],
                'confluence_scoring': True
            },
            'risk_management': {
                'enabled': True,
                'features': ['ATR-based SL/TP', 'Position Sizing', 'Kelly Criterion', 'Scaling Strategy']
            }
        },
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })