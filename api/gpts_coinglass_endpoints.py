#!/usr/bin/env python3
"""
GPTs API Endpoints for CoinGlass Integration
Provides ChatGPT Custom GPT access to enhanced SMC-CoinGlass analysis
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import traceback

from typing import Dict, Any, Optional, List
from core.enhanced_smc_coinglass_integration import get_enhanced_smc_coinglass_integration
from core.coinglass_analyzer import get_coinglass_analyzer

# Create blueprint
gpts_coinglass_bp = Blueprint('gpts_coinglass', __name__, url_prefix='/api/gpts/coinglass')

# Get integrations
integration = get_enhanced_smc_coinglass_integration()
coinglass = get_coinglass_analyzer()

logger = logging.getLogger(__name__)

@gpts_coinglass_bp.route('/liquidity-map', methods=['GET'])
def get_liquidity_map():
    """
    Get comprehensive liquidity map combining SMC + CoinGlass data
    
    Query Parameters:
    - symbol: Trading pair (default: BTCUSDT)
    - timeframe: Analysis timeframe (default: 1h)
    
    Returns enhanced liquidity analysis with:
    - SMC zones with liquidation confluence
    - High-impact liquidation clusters
    - Entry/exit recommendations
    - Sweep probabilities
    """
    try:
        # Validate parameters
        symbol = request.args.get('symbol', 'BTCUSDT').upper()
        timeframe = request.args.get('timeframe', '1h')
        
        # Create enhanced liquidity map
        liquidity_map = integration.create_enhanced_liquidity_map(
            symbol=symbol,
            timeframe=timeframe
        )
        
        # Generate trading summary
        trading_summary = integration.get_trading_summary(liquidity_map)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': liquidity_map.symbol,
                'current_price': liquidity_map.current_price,
                'analysis_timestamp': liquidity_map.timestamp.isoformat(),
                
                # Core data
                'smc_zones': [
                    {
                        'type': zone.zone_type,
                        'price': zone.price_level,
                        'strength': zone.strength,
                        'timeframe': zone.timeframe,
                        'liquidation_confluence': zone.liquidation_confluence,
                        'liquidation_volume': zone.liquidation_volume,
                        'confluence_score': zone.confluence_score,
                        'risk_score': zone.risk_score
                    }
                    for zone in liquidity_map.smc_zones
                ],
                
                'confluent_levels': liquidity_map.confluent_levels,
                'liquidity_magnets': liquidity_map.liquidity_magnets,
                'entry_zones': liquidity_map.entry_zones,
                
                # Probabilities
                'sweep_probabilities': liquidity_map.sweep_probabilities,
                
                # Risk management
                'invalidation_levels': liquidity_map.invalidation_levels,
                'target_levels': liquidity_map.target_levels,
                
                # Summary
                'trading_summary': trading_summary
            },
            'metadata': {
                'enhanced_zones_count': len(liquidity_map.smc_zones),
                'confluent_levels_count': len(liquidity_map.confluent_levels),
                'entry_opportunities': len(liquidity_map.entry_zones),
                'api_version': '1.0.0'
            }
        })
        
    except Exception as e:
        logger.error(f"Liquidity map error: {e}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': {
                'message': f"Liquidity analysis failed: {str(e)}",
                'code': 500
            }
        }), 500

@gpts_coinglass_bp.route('/liquidation-heatmap', methods=['GET'])
def get_liquidation_heatmap():
    """
    Get CoinGlass liquidation heatmap data
    
    Returns liquidation zones and clusters for price level analysis
    """
    try:
        symbol = validate_symbol(request.args.get('symbol', 'BTCUSDT'))
        
        # Get liquidation zones
        liquidation_zones = coinglass.get_liquidation_heatmap(symbol)
        
        # Process zones for GPTs consumption
        processed_zones = []
        total_long_volume = 0
        total_short_volume = 0
        
        for zone in liquidation_zones:
            zone_data = {
                'price': zone.price,
                'volume': zone.volume,
                'side': zone.side,
                'strength': zone.strength,
                'timestamp': zone.timestamp.isoformat()
            }
            processed_zones.append(zone_data)
            
            if zone.side == 'long':
                total_long_volume += zone.volume
            else:
                total_short_volume += zone.volume
        
        # Calculate insights
        total_volume = total_long_volume + total_short_volume
        long_dominance = (total_long_volume / total_volume * 100) if total_volume > 0 else 50
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'liquidation_zones': processed_zones,
                'analysis': {
                    'total_liquidation_volume': total_volume,
                    'long_liquidation_volume': total_long_volume,
                    'short_liquidation_volume': total_short_volume,
                    'long_dominance_percent': round(long_dominance, 2),
                    'short_dominance_percent': round(100 - long_dominance, 2),
                    'high_impact_zones_count': len([z for z in liquidation_zones if z.strength > 70])
                },
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except GPTsError as e:
        return handle_gpts_error(e)
    except Exception as e:
        logger.error(f"Liquidation heatmap error: {e}")
        return handle_gpts_error(GPTsError(f"Liquidation data retrieval failed: {str(e)}", 500))

@gpts_coinglass_bp.route('/market-sentiment', methods=['GET'])
def get_market_sentiment():
    """
    Get comprehensive market sentiment from CoinGlass data
    
    Combines OI, funding rates, and liquidation patterns
    """
    try:
        symbol = validate_symbol(request.args.get('symbol', 'BTCUSDT'))
        
        # Get sentiment analysis
        sentiment_data = coinglass.get_market_sentiment_score(symbol)
        
        # Get additional data for context
        oi_data = coinglass.get_open_interest_data(symbol)
        funding_rates = coinglass.get_funding_rates(symbol)
        
        # Prepare comprehensive response
        response_data = {
            'symbol': symbol,
            'sentiment_analysis': sentiment_data,
            'supporting_data': {
                'open_interest': {
                    'total_oi': oi_data.total_oi if oi_data else 0,
                    'oi_change_24h': oi_data.oi_change_percent if oi_data else 0,
                    'long_ratio': oi_data.long_ratio if oi_data else 50,
                    'short_ratio': oi_data.short_ratio if oi_data else 50
                } if oi_data else None,
                'funding_rates': [
                    {
                        'exchange': rate.exchange,
                        'funding_rate': rate.funding_rate,
                        'predicted_rate': rate.predicted_rate
                    }
                    for rate in funding_rates
                ] if funding_rates else []
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': response_data
        })
        
    except GPTsError as e:
        return handle_gpts_error(e)
    except Exception as e:
        logger.error(f"Market sentiment error: {e}")
        return handle_gpts_error(GPTsError(f"Sentiment analysis failed: {str(e)}", 500))

@gpts_coinglass_bp.route('/confluence-analysis', methods=['GET'])
def get_confluence_analysis():
    """
    Get confluence analysis between SMC levels and liquidation zones
    
    Identifies high-probability trading opportunities
    """
    try:
        symbol = validate_symbol(request.args.get('symbol', 'BTCUSDT'))
        timeframe = validate_timeframe(request.args.get('timeframe', '1h'))
        
        # Create liquidity map
        liquidity_map = integration.create_enhanced_liquidity_map(symbol, timeframe)
        
        # Focus on confluence analysis
        confluence_data = {
            'symbol': symbol,
            'analysis_timeframe': timeframe,
            'current_price': liquidity_map.current_price,
            
            # Confluence levels with detailed metrics
            'confluent_levels': [
                {
                    **level,
                    'trading_recommendation': _get_level_recommendation(level, liquidity_map.current_price),
                    'risk_reward_ratio': _calculate_risk_reward(level, liquidity_map)
                }
                for level in liquidity_map.confluent_levels[:5]  # Top 5
            ],
            
            # Entry zone analysis
            'optimal_entry_zones': [
                {
                    **zone,
                    'confidence_level': _calculate_confidence(zone),
                    'volume_confirmation': zone.get('volume_support', 0) > 10000000  # $10M threshold
                }
                for zone in liquidity_map.entry_zones[:3]  # Top 3
            ],
            
            # Directional bias with reasoning
            'directional_analysis': {
                'sweep_probabilities': liquidity_map.sweep_probabilities,
                'primary_bias': _determine_primary_bias(liquidity_map),
                'key_levels_to_watch': liquidity_map.target_levels[:3]
            },
            
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'data': confluence_data,
            'metadata': {
                'confluence_levels_analyzed': len(liquidity_map.confluent_levels),
                'entry_opportunities_identified': len(liquidity_map.entry_zones),
                'analysis_quality': 'high' if len(liquidity_map.confluent_levels) > 3 else 'medium'
            }
        })
        
    except GPTsError as e:
        return handle_gpts_error(e)
    except Exception as e:
        logger.error(f"Confluence analysis error: {e}")
        return handle_gpts_error(GPTsError(f"Confluence analysis failed: {str(e)}", 500))

@gpts_coinglass_bp.route('/trading-opportunities', methods=['GET'])
def get_trading_opportunities():
    """
    Get actionable trading opportunities with entry/exit levels
    
    Provides ready-to-use trading setups based on SMC-CoinGlass confluence
    """
    try:
        symbol = validate_symbol(request.args.get('symbol', 'BTCUSDT'))
        timeframe = validate_timeframe(request.args.get('timeframe', '1h'))
        
        # Get liquidity map and summary
        liquidity_map = integration.create_enhanced_liquidity_map(symbol, timeframe)
        trading_summary = integration.get_trading_summary(liquidity_map)
        
        # Generate trading opportunities
        opportunities = []
        
        for i, entry_zone in enumerate(liquidity_map.entry_zones[:3]):  # Top 3 opportunities
            opportunity = {
                'opportunity_id': f"{symbol}_{i+1}",
                'setup_type': entry_zone['type'],
                'entry_price': entry_zone['price'],
                'smc_zone_type': entry_zone['smc_zone'],
                'strength_score': entry_zone['strength'],
                'risk_level': entry_zone['risk_level'],
                
                # Risk management
                'stop_loss': _calculate_stop_loss(entry_zone, liquidity_map),
                'take_profit_levels': _calculate_take_profits(entry_zone, liquidity_map),
                
                # Supporting data
                'liquidation_volume_support': entry_zone.get('volume_support', 0),
                'confluence_factors': _identify_confluence_factors(entry_zone, liquidity_map),
                
                # Timing
                'validity_timeframe': entry_zone.get('timeframe', timeframe),
                'priority_score': _calculate_opportunity_priority(entry_zone, liquidity_map)
            }
            opportunities.append(opportunity)
        
        return jsonify({
            'success': True,
            'data': {
                'symbol': symbol,
                'current_price': liquidity_map.current_price,
                'market_bias': trading_summary['directional_bias']['bias'],
                'overall_risk_assessment': trading_summary['overall_risk'],
                
                'trading_opportunities': opportunities,
                
                'market_context': {
                    'key_invalidation_levels': liquidity_map.invalidation_levels,
                    'liquidity_magnet_targets': [
                        {
                            'price': magnet['price'],
                            'probability': magnet.get('probability', 0),
                            'volume': magnet['volume']
                        }
                        for magnet in liquidity_map.liquidity_magnets[:3]
                    ],
                    'sweep_probabilities': liquidity_map.sweep_probabilities
                },
                
                'action_items': trading_summary.get('action_items', []),
                'timestamp': datetime.now().isoformat()
            },
            'metadata': {
                'opportunities_identified': len(opportunities),
                'analysis_quality': _assess_analysis_quality(liquidity_map),
                'data_freshness': 'real-time' if coinglass.api_key else 'demo'
            }
        })
        
    except GPTsError as e:
        return handle_gpts_error(e)
    except Exception as e:
        logger.error(f"Trading opportunities error: {e}")
        return handle_gpts_error(GPTsError(f"Trading opportunities analysis failed: {str(e)}", 500))

@gpts_coinglass_bp.route('/system-status', methods=['GET'])
def get_system_status():
    """Get CoinGlass integration system status"""
    try:
        coinglass_status = coinglass.get_system_status()
        
        return jsonify({
            'success': True,
            'data': {
                'coinglass_integration': coinglass_status,
                'enhanced_smc_integration': {
                    'status': 'operational',
                    'confluence_analysis': 'enabled',
                    'liquidity_mapping': 'enabled',
                    'risk_management': 'enabled'
                },
                'api_endpoints': [
                    '/liquidity-map',
                    '/liquidation-heatmap', 
                    '/market-sentiment',
                    '/confluence-analysis',
                    '/trading-opportunities'
                ],
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"System status error: {e}")
        return handle_gpts_error(GPTsError(f"System status check failed: {str(e)}", 500))

# Helper functions
def _get_level_recommendation(level: Dict, current_price: float) -> str:
    """Get trading recommendation for confluence level"""
    distance = level['distance_percent']
    confluence_score = level['confluence_score']
    
    if abs(distance) < 2 and confluence_score > 80:
        return "Strong setup - monitor for entry"
    elif abs(distance) < 5 and confluence_score > 70:
        return "Good setup - wait for confirmation"
    elif confluence_score > 60:
        return "Potential setup - needs additional confirmation"
    else:
        return "Watch zone - lower probability"

def _calculate_risk_reward(level: Dict, liquidity_map) -> float:
    """Calculate risk/reward ratio for level"""
    try:
        entry_price = level['price']
        
        # Find nearest target
        targets = liquidity_map.target_levels
        if not targets:
            return 1.0
        
        # Find appropriate target based on level side
        target_price = targets[0]  # Use first target as default
        
        # Estimate stop loss (simplified)
        risk_distance = abs(entry_price * 0.02)  # 2% risk
        reward_distance = abs(target_price - entry_price)
        
        if risk_distance > 0:
            return round(reward_distance / risk_distance, 2)
        return 1.0
        
    except Exception:
        return 1.0

def _calculate_confidence(zone: Dict) -> str:
    """Calculate confidence level for entry zone"""
    strength = zone.get('strength', 0)
    
    if strength > 85:
        return 'Very High'
    elif strength > 75:
        return 'High'
    elif strength > 65:
        return 'Medium'
    else:
        return 'Low'

def _determine_primary_bias(liquidity_map) -> str:
    """Determine primary market bias"""
    upside_prob = liquidity_map.sweep_probabilities.get('upside_sweep', 50)
    downside_prob = liquidity_map.sweep_probabilities.get('downside_sweep', 50)
    
    if upside_prob > 60:
        return 'Bullish'
    elif downside_prob > 60:
        return 'Bearish'
    else:
        return 'Neutral'

def _calculate_stop_loss(entry_zone: Dict, liquidity_map) -> Optional[float]:
    """Calculate stop loss for entry zone"""
    try:
        entry_price = entry_zone['price']
        entry_type = entry_zone['type']
        
        # Use invalidation levels if available
        if liquidity_map.invalidation_levels:
            if entry_type == 'long':
                return min([level for level in liquidity_map.invalidation_levels if level < entry_price], default=entry_price * 0.98)
            else:
                return max([level for level in liquidity_map.invalidation_levels if level > entry_price], default=entry_price * 1.02)
        
        # Fallback: 2% risk
        if entry_type == 'long':
            return entry_price * 0.98
        else:
            return entry_price * 1.02
            
    except Exception:
        return None

def _calculate_take_profits(entry_zone: Dict, liquidity_map) -> List[float]:
    """Calculate take profit levels"""
    try:
        entry_price = entry_zone['price']
        entry_type = entry_zone['type']
        
        # Use liquidity magnets as targets
        targets = []
        for magnet in liquidity_map.liquidity_magnets:
            magnet_price = magnet['price']
            
            if entry_type == 'long' and magnet_price > entry_price:
                targets.append(magnet_price)
            elif entry_type == 'short' and magnet_price < entry_price:
                targets.append(magnet_price)
        
        return sorted(targets)[:3]  # Max 3 targets
        
    except Exception:
        return []

def _identify_confluence_factors(entry_zone: Dict, liquidity_map) -> List[str]:
    """Identify factors supporting the entry zone"""
    factors = []
    
    if entry_zone.get('volume_support', 0) > 10000000:
        factors.append("High liquidation volume support")
    
    if entry_zone.get('strength', 0) > 80:
        factors.append("Strong SMC zone confluence")
    
    # Check for nearby confluent levels
    entry_price = entry_zone['price']
    nearby_confluent = any(
        abs(level['price'] - entry_price) / entry_price < 0.01
        for level in liquidity_map.confluent_levels
    )
    if nearby_confluent:
        factors.append("Multiple level confluence")
    
    return factors

def _calculate_opportunity_priority(entry_zone: Dict, liquidity_map) -> int:
    """Calculate priority score (1-100)"""
    score = entry_zone.get('strength', 50)
    
    # Boost for volume support
    if entry_zone.get('volume_support', 0) > 50000000:
        score += 15
    
    # Boost for risk level
    risk_level = entry_zone.get('risk_level', 'Medium')
    if risk_level == 'Low':
        score += 10
    elif risk_level in ['Medium-High', 'High']:
        score -= 10
    
    return min(100, max(1, int(score)))

def _assess_analysis_quality(liquidity_map) -> str:
    """Assess overall analysis quality"""
    if len(liquidity_map.confluent_levels) > 5 and len(liquidity_map.entry_zones) > 2:
        return 'excellent'
    elif len(liquidity_map.confluent_levels) > 3:
        return 'good'
    elif len(liquidity_map.confluent_levels) > 1:
        return 'fair'
    else:
        return 'limited'