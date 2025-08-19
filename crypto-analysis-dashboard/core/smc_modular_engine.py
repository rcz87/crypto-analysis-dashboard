#!/usr/bin/env python3
"""
SMC Modular Engine: Integration hub for all SMC modular components
Orchestrates BiasBuilder, ExecutionLogicEngine, TradePlanner, NarrativeComposer, MarkdownSignalFormatter
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import asyncio

# Import all SMC modular components
from .smc_bias_builder import BiasBuilder, BiasSignal
from .smc_execution_logic_engine import ExecutionLogicEngine, ExecutionSignal
from .smc_trade_planner import TradePlanner, TradePlan
from .smc_narrative_composer import NarrativeComposer, TradingNarrative, NarrativeStyle
from .smc_markdown_formatter import MarkdownSignalFormatter, FormattedSignal, OutputFormat, MessagePriority

logger = logging.getLogger(__name__)

class SMCModularEngine:
    """
    🚀 SMC Modular Engine
    
    Central orchestrator for all SMC modular components:
    1. BiasBuilder: Market bias determination
    2. ExecutionLogicEngine: Entry validation  
    3. TradePlanner: Trade planning with risk management
    4. NarrativeComposer: Human-readable explanations
    5. MarkdownSignalFormatter: Multi-format output
    
    Real-time reasoning focus with modular OOP architecture
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.SMCModularEngine")
        
        # Initialize all modular components
        self.bias_builder = BiasBuilder()
        self.execution_engine = ExecutionLogicEngine()
        self.trade_planner = TradePlanner()
        self.narrative_composer = NarrativeComposer()
        self.markdown_formatter = MarkdownSignalFormatter()
        
        self.logger.info("🚀 SMC Modular Engine initialized with all components")
    
    async def analyze_complete_signal(self, symbol: str, current_price: float,
                                    market_data: Dict, smc_data: Dict,
                                    account_balance: float = 10000,
                                    risk_percent: float = 1.0,
                                    timeframe: str = "1H") -> Dict[str, Any]:
        """
        Complete SMC signal analysis using all modular components
        
        Args:
            symbol: Trading symbol (e.g., 'SOLUSDT')
            current_price: Current market price
            market_data: OHLCV and volume data
            smc_data: SMC analysis results (CHoCH, BOS, OB, FVG, etc.)
            account_balance: Account balance for position sizing
            risk_percent: Risk percentage per trade
            timeframe: Analysis timeframe
            
        Returns:
            Complete analysis with all component outputs
        """
        try:
            self.logger.info(f"🔍 Starting complete SMC analysis for {symbol} at ${current_price}")
            
            # Extract required data
            ohlcv_data = market_data.get('candles', [])
            volume_data = market_data.get('volume_data', [])
            
            # SMC components
            choch_signals = smc_data.get('choch_signals', [])
            bos_signals = smc_data.get('bos_signals', [])
            order_blocks = smc_data.get('order_blocks', [])
            fvg_signals = smc_data.get('fvg_signals', [])
            liquidity_sweeps = smc_data.get('liquidity_sweeps', [])
            swing_points = smc_data.get('swing_points', {'swing_highs': [], 'swing_lows': []})
            
            # Step 1: Determine Market Bias
            self.logger.info("🧠 Step 1: Determining market bias...")
            bias_signal = self.bias_builder.determine_market_bias(
                data=ohlcv_data,
                choch_signals=choch_signals,
                bos_signals=bos_signals,
                swing_points=swing_points,
                timeframe=timeframe
            )
            
            # Step 2: Validate Entry Logic
            self.logger.info("⚡ Step 2: Validating entry logic...")
            direction = self._determine_trade_direction(bias_signal)
            
            execution_signal = self.execution_engine.validate_entry_signal(
                symbol=symbol,
                direction=direction,
                current_price=current_price,
                choch_signals=choch_signals,
                fvg_signals=fvg_signals,
                volume_data=volume_data,
                price_data=ohlcv_data,
                timeframe=timeframe
            )
            
            # Step 3: Create Trade Plan
            self.logger.info("📊 Step 3: Creating comprehensive trade plan...")
            trade_plan = self.trade_planner.create_trade_plan(
                symbol=symbol,
                direction=direction,
                current_price=current_price,
                order_blocks=order_blocks,
                fvg_signals=fvg_signals,
                liquidity_sweeps=liquidity_sweeps,
                swing_points=swing_points,
                account_balance=account_balance,
                risk_percent=risk_percent,
                timeframe=timeframe
            )
            
            # Step 4: Compose Trading Narrative
            self.logger.info("📝 Step 4: Composing trading narrative...")
            
            # Prepare data for narrative
            bias_dict = self.bias_builder.get_bias_summary(bias_signal)
            execution_dict = self.execution_engine.get_execution_summary(execution_signal)
            trade_plan_dict = self.trade_planner.get_trade_plan_summary(trade_plan)
            smc_components = self._prepare_smc_components(smc_data)
            
            trading_narrative = self.narrative_composer.compose_trading_narrative(
                symbol=symbol,
                direction=direction,
                bias_signal=bias_dict,
                execution_signal=execution_dict,
                trade_plan=trade_plan_dict,
                smc_components=smc_components,
                timeframe=timeframe
            )
            
            # Step 5: Format Output for Multiple Platforms
            self.logger.info("📱 Step 5: Formatting multi-platform output...")
            
            # Determine message priority
            priority = self._determine_message_priority(execution_signal.confidence, trade_plan.plan_quality)
            
            # Prepare narrative data for formatter
            narrative_dict = self.narrative_composer.get_narrative_summary(trading_narrative)
            narrative_dict.update({
                'concise_narrative': trading_narrative.concise_narrative,
                'detailed_narrative': trading_narrative.detailed_narrative,
                'technical_narrative': trading_narrative.technical_narrative,
                'educational_narrative': trading_narrative.educational_narrative
            })
            
            formatted_signal = self.markdown_formatter.format_complete_signal(
                symbol=symbol,
                direction=direction,
                bias_signal=bias_dict,
                execution_signal=execution_dict,
                trade_plan=trade_plan_dict,
                narrative=narrative_dict,
                priority=priority,
                formats=[OutputFormat.TELEGRAM, OutputFormat.CONSOLE, OutputFormat.MARKDOWN, OutputFormat.JSON]
            )
            
            # Compile complete analysis result
            complete_analysis = {
                "metadata": {
                    "symbol": symbol,
                    "current_price": current_price,
                    "timeframe": timeframe,
                    "analysis_timestamp": int(datetime.now().timestamp() * 1000),
                    "engine_version": "1.0.0",
                    "components_used": ["BiasBuilder", "ExecutionLogicEngine", "TradePlanner", "NarrativeComposer", "MarkdownFormatter"]
                },
                
                "bias_analysis": {
                    "bias": bias_signal.bias.value,
                    "strength": bias_signal.strength,
                    "confidence": bias_signal.confidence,
                    "trend_alignment": bias_signal.trend_alignment,
                    "contributing_factors": bias_signal.contributing_factors,
                    "choch_count": bias_signal.choch_count,
                    "bos_count": bias_signal.bos_count,
                    "description": bias_signal.description
                },
                
                "execution_validation": {
                    "validation_result": execution_signal.validation_result.value,
                    "confidence": execution_signal.confidence,
                    "validation_score": execution_signal.validation_score,
                    "confirmations": {
                        "choch": execution_signal.choch_confirmed,
                        "fvg": execution_signal.fvg_confirmed,
                        "delta": execution_signal.delta_confirmed,
                        "rsi": execution_signal.rsi_confirmed,
                        "orderflow": execution_signal.orderflow_confirmed
                    },
                    "rejection_reasons": execution_signal.rejection_reasons,
                    "description": execution_signal.description
                },
                
                "trade_plan": {
                    "entry_price": trade_plan.entry_price,
                    "stop_loss": trade_plan.stop_loss,
                    "take_profit_levels": [trade_plan.take_profit_1, trade_plan.take_profit_2, trade_plan.take_profit_3],
                    "risk_reward_ratio": trade_plan.risk_reward_ratio,
                    "position_size_percent": trade_plan.position_size_percent,
                    "plan_quality": trade_plan.plan_quality.value,
                    "quality_score": trade_plan.quality_score,
                    "plan_notes": trade_plan.plan_notes,
                    "smc_components_used": {
                        "order_block": trade_plan.order_block_used is not None,
                        "fvg": trade_plan.fvg_used is not None,
                        "liquidity_levels": len(trade_plan.liquidity_levels)
                    }
                },
                
                "narrative": {
                    "confidence": trading_narrative.narrative_confidence,
                    "complexity_score": trading_narrative.complexity_score,
                    "readability_score": trading_narrative.readability_score,
                    "key_levels": trading_narrative.key_levels,
                    "confidence_factors": trading_narrative.confidence_factors,
                    "risk_factors": trading_narrative.risk_factors,
                    "narratives": {
                        "concise": trading_narrative.concise_narrative,
                        "detailed": trading_narrative.detailed_narrative,
                        "technical": trading_narrative.technical_narrative,
                        "educational": trading_narrative.educational_narrative
                    }
                },
                
                "formatted_outputs": {
                    "telegram_message": formatted_signal.telegram_message,
                    "console_output": formatted_signal.console_output,
                    "markdown_content": formatted_signal.markdown_content,
                    "json_data": formatted_signal.json_data,
                    "message_properties": {
                        "length": formatted_signal.message_length,
                        "estimated_tokens": formatted_signal.estimated_tokens,
                        "readability_score": formatted_signal.readability_score,
                        "priority": formatted_signal.priority.value,
                        "urgency_indicators": formatted_signal.urgency_indicators
                    }
                },
                
                "overall_assessment": {
                    "trade_recommendation": self._get_overall_recommendation(bias_signal, execution_signal, trade_plan),
                    "confidence_level": self._calculate_overall_confidence(bias_signal, execution_signal, trading_narrative),
                    "risk_level": self._assess_overall_risk(execution_signal, trade_plan),
                    "setup_quality": self._assess_setup_quality(bias_signal, execution_signal, trade_plan),
                    "key_strengths": self._identify_key_strengths(bias_signal, execution_signal, trade_plan),
                    "key_risks": self._identify_key_risks(execution_signal, trade_plan),
                    "action_items": self._generate_action_items(execution_signal, trade_plan)
                }
            }
            
            self.logger.info(f"✅ Complete SMC analysis finished for {symbol}")
            self.logger.info(f"   Bias: {bias_signal.bias.value} ({bias_signal.confidence:.1%})")
            self.logger.info(f"   Validation: {execution_signal.validation_result.value} ({execution_signal.confidence:.1%})")
            self.logger.info(f"   Plan Quality: {trade_plan.plan_quality.value} (R/R: {trade_plan.risk_reward_ratio:.1f}:1)")
            
            return complete_analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error in complete SMC analysis: {e}")
            return self._get_error_analysis(symbol, str(e))
    
    def _determine_trade_direction(self, bias_signal: BiasSignal) -> str:
        """Determine trade direction from bias signal"""
        if bias_signal.bias.value == 'bullish':
            return 'LONG'
        elif bias_signal.bias.value == 'bearish':
            return 'SHORT'
        else:
            return 'NEUTRAL'
    
    def _determine_message_priority(self, execution_confidence: float, plan_quality) -> MessagePriority:
        """Determine message priority based on signal quality"""
        if execution_confidence > 0.8 and plan_quality.value == 'excellent':
            return MessagePriority.URGENT
        elif execution_confidence > 0.7 and plan_quality.value in ['excellent', 'good']:
            return MessagePriority.HIGH
        elif execution_confidence > 0.5:
            return MessagePriority.MEDIUM
        else:
            return MessagePriority.LOW
    
    def _prepare_smc_components(self, smc_data: Dict) -> Dict[str, Any]:
        """Prepare SMC components data for narrative"""
        return {
            "choch_count": len(smc_data.get('choch_signals', [])),
            "bos_count": len(smc_data.get('bos_signals', [])),
            "order_blocks_count": len(smc_data.get('order_blocks', [])),
            "fvg_count": len(smc_data.get('fvg_signals', [])),
            "liquidity_sweeps_count": len(smc_data.get('liquidity_sweeps', [])),
            "order_blocks": smc_data.get('order_blocks', [])[:3],  # Top 3 for narrative
            "fvg_signals": smc_data.get('fvg_signals', [])[:3],    # Top 3 for narrative
            "swing_points": smc_data.get('swing_points', {})
        }
    
    def _get_overall_recommendation(self, bias_signal: BiasSignal, execution_signal: ExecutionSignal, trade_plan: TradePlan) -> str:
        """Get overall trade recommendation"""
        if (bias_signal.confidence > 0.8 and 
            execution_signal.validation_result.value == 'valid' and
            trade_plan.plan_quality.value in ['excellent', 'good']):
            return "STRONG_BUY" if bias_signal.bias.value == 'bullish' else "STRONG_SELL"
        elif (bias_signal.confidence > 0.6 and 
              execution_signal.validation_result.value in ['valid', 'pending'] and
              trade_plan.plan_quality.value != 'poor'):
            return "BUY" if bias_signal.bias.value == 'bullish' else "SELL"
        elif bias_signal.confidence > 0.4 and execution_signal.confidence > 0.4:
            return "WEAK_BUY" if bias_signal.bias.value == 'bullish' else "WEAK_SELL"
        else:
            return "HOLD"
    
    def _calculate_overall_confidence(self, bias_signal: BiasSignal, execution_signal: ExecutionSignal, narrative: TradingNarrative) -> float:
        """Calculate overall confidence score"""
        return (bias_signal.confidence * 0.4 + execution_signal.confidence * 0.4 + narrative.narrative_confidence * 0.2)
    
    def _assess_overall_risk(self, execution_signal: ExecutionSignal, trade_plan: TradePlan) -> str:
        """Assess overall risk level"""
        if (execution_signal.confidence > 0.8 and 
            trade_plan.plan_quality.value == 'excellent' and
            trade_plan.risk_reward_ratio >= 2.5):
            return "LOW"
        elif (execution_signal.confidence > 0.6 and 
              trade_plan.plan_quality.value in ['good', 'excellent'] and
              trade_plan.risk_reward_ratio >= 1.5):
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _assess_setup_quality(self, bias_signal: BiasSignal, execution_signal: ExecutionSignal, trade_plan: TradePlan) -> str:
        """Assess overall setup quality"""
        confidence_score = (bias_signal.confidence + execution_signal.confidence) / 2
        
        if (confidence_score > 0.8 and 
            trade_plan.plan_quality.value == 'excellent' and
            execution_signal.validation_result.value == 'valid'):
            return "PREMIUM"
        elif (confidence_score > 0.7 and 
              trade_plan.plan_quality.value in ['excellent', 'good']):
            return "HIGH_QUALITY"
        elif confidence_score > 0.5 and trade_plan.plan_quality.value != 'poor':
            return "AVERAGE"
        else:
            return "BELOW_AVERAGE"
    
    def _identify_key_strengths(self, bias_signal: BiasSignal, execution_signal: ExecutionSignal, trade_plan: TradePlan) -> List[str]:
        """Identify key strengths of the setup"""
        strengths = []
        
        if bias_signal.confidence > 0.8:
            strengths.append("High market bias confidence")
        
        if execution_signal.validation_result.value == 'valid':
            strengths.append("Fully validated entry signal")
        
        if trade_plan.risk_reward_ratio >= 3.0:
            strengths.append("Excellent risk/reward ratio")
        
        if trade_plan.plan_quality.value == 'excellent':
            strengths.append("Premium trade plan quality")
        
        if bias_signal.trend_alignment in ['fully_aligned_bullish', 'fully_aligned_bearish']:
            strengths.append("Perfect trend alignment")
        
        confirmed_count = sum([
            execution_signal.choch_confirmed,
            execution_signal.fvg_confirmed,
            execution_signal.delta_confirmed,
            execution_signal.rsi_confirmed,
            execution_signal.orderflow_confirmed
        ])
        
        if confirmed_count >= 4:
            strengths.append("Strong confluence confirmation")
        
        return strengths
    
    def _identify_key_risks(self, execution_signal: ExecutionSignal, trade_plan: TradePlan) -> List[str]:
        """Identify key risks of the setup"""
        risks = []
        
        if execution_signal.confidence < 0.5:
            risks.append("Low execution confidence")
        
        if trade_plan.risk_reward_ratio < 1.5:
            risks.append("Poor risk/reward ratio")
        
        if trade_plan.plan_quality.value == 'poor':
            risks.append("Low quality trade plan")
        
        if execution_signal.validation_result.value == 'invalid':
            risks.append("Failed entry validation")
        
        if len(execution_signal.rejection_reasons) > 2:
            risks.append("Multiple validation failures")
        
        return risks
    
    def _generate_action_items(self, execution_signal: ExecutionSignal, trade_plan: TradePlan) -> List[str]:
        """Generate actionable items based on analysis"""
        actions = []
        
        if execution_signal.validation_result.value == 'valid':
            actions.append("Consider entry execution")
            actions.append(f"Set stop loss at ${trade_plan.stop_loss:.4f}")
            actions.append(f"Target first TP at ${trade_plan.take_profit_1:.4f}")
        elif execution_signal.validation_result.value == 'pending':
            actions.append("Wait for additional confirmation")
            actions.append("Monitor key validation criteria")
        else:
            actions.append("Do not execute - validation failed")
            actions.append("Wait for better setup")
        
        if trade_plan.risk_reward_ratio < 2.0:
            actions.append("Consider improving R/R ratio")
        
        actions.append("Apply proper position sizing")
        actions.append("Monitor market conditions")
        
        return actions
    
    def _get_error_analysis(self, symbol: str, error_message: str) -> Dict[str, Any]:
        """Get error analysis response"""
        return {
            "metadata": {
                "symbol": symbol,
                "analysis_timestamp": int(datetime.now().timestamp() * 1000),
                "status": "error",
                "error_message": error_message
            },
            "bias_analysis": {"bias": "unknown", "confidence": 0.0},
            "execution_validation": {"validation_result": "error", "confidence": 0.0},
            "trade_plan": {"plan_quality": "error", "risk_reward_ratio": 0.0},
            "narrative": {"confidence": 0.0},
            "formatted_outputs": {
                "telegram_message": f"❌ Analisis error untuk {symbol}: {error_message}",
                "console_output": f"Error analyzing {symbol}: {error_message}",
                "markdown_content": f"# Analysis Error\n\nError for {symbol}: {error_message}",
                "json_data": {"error": error_message, "symbol": symbol}
            },
            "overall_assessment": {
                "trade_recommendation": "HOLD",
                "confidence_level": 0.0,
                "risk_level": "HIGH",
                "setup_quality": "ERROR"
            }
        }
    
    async def get_quick_signal(self, symbol: str, current_price: float, 
                             simplified_data: Dict, timeframe: str = "1H") -> str:
        """
        Get quick formatted signal for immediate use (Telegram)
        
        Returns:
            Ready-to-send Telegram message
        """
        try:
            # Simplified analysis for quick response
            complete_analysis = await self.analyze_complete_signal(
                symbol=symbol,
                current_price=current_price,
                market_data=simplified_data,
                smc_data=simplified_data,
                timeframe=timeframe
            )
            
            return complete_analysis['formatted_outputs']['telegram_message']
            
        except Exception as e:
            self.logger.error(f"❌ Error in quick signal: {e}")
            return f"❌ Quick signal error untuk {symbol}: {str(e)}"