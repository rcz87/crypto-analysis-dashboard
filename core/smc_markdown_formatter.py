#!/usr/bin/env python3
"""
MarkdownSignalFormatter: SMC Signal Output Formatter
Mengubah output menjadi teks siap kirim (Telegram/Console) dengan format Markdown
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OutputFormat(Enum):
    """Output format options"""
    TELEGRAM = "telegram"
    CONSOLE = "console" 
    MARKDOWN = "markdown"
    JSON = "json"
    HTML = "html"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

@dataclass
class FormattedSignal:
    """Structure for formatted signal output"""
    symbol: str
    direction: str
    format_type: OutputFormat
    priority: MessagePriority
    timestamp: int
    
    # Formatted outputs
    telegram_message: str
    console_output: str
    markdown_content: str
    json_data: Dict[str, Any]
    html_content: str
    
    # Message properties
    message_length: int
    estimated_tokens: int
    readability_score: float
    urgency_indicators: List[str]

class MarkdownSignalFormatter:
    """
    📝 SMC Signal Markdown Formatter
    
    Menghasilkan output yang siap pakai untuk berbagai platform:
    - Telegram: HTML formatted dengan emoji dan struktur clean
    - Console: Clean text dengan color coding
    - Markdown: Full documentation format
    - JSON: Structured data untuk API
    - HTML: Web-ready formatted content
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.MarkdownSignalFormatter")
        
        # Emoji mappings for different signal types
        self.signal_emojis = {
            "BUY": "🟢", "LONG": "🟢", "BULLISH": "🟢",
            "SELL": "🔴", "SHORT": "🔴", "BEARISH": "🔴", 
            "NEUTRAL": "⚪", "HOLD": "🟡", "WAIT": "🟡"
        }
        
        self.confidence_emojis = {
            0.9: "🔥", 0.8: "💪", 0.7: "👍", 
            0.6: "👌", 0.5: "🤔", 0.4: "⚠️", 0.3: "❗"
        }
        
        self.priority_emojis = {
            MessagePriority.URGENT: "🚨",
            MessagePriority.HIGH: "⚡",
            MessagePriority.MEDIUM: "📊",
            MessagePriority.LOW: "💡"
        }
        
        # Format templates
        self.telegram_template = """
{priority_emoji} <b>{signal_emoji} SHARP SIGNAL - {symbol}</b> {signal_emoji}

📊 <b>Pair:</b> {symbol}
📈 <b>Signal:</b> {direction}
💯 <b>Confidence:</b> {confidence}% {confidence_emoji}
⏰ <b>Timeframe:</b> {timeframe}

💰 <b>Entry Price:</b> ${entry_price:,.4f}
🛡 <b>Stop Loss:</b> ${stop_loss:,.4f} ({sl_distance:.1f}%)
🎯 <b>Take Profit 1:</b> ${tp1:,.4f} ({tp1_distance:.1f}%)
🎯 <b>Take Profit 2:</b> ${tp2:,.4f} ({tp2_distance:.1f}%)
🎯 <b>Take Profit 3:</b> ${tp3:,.4f} ({tp3_distance:.1f}%)
⚖️ <b>Risk/Reward:</b> {rr_ratio:.1f}:1

{narrative_section}

{smc_section}

{risk_section}

⏰ <b>Generated:</b> {timestamp}
<i>RZC GPS Trading Bot - Smart Money Concept Analysis</i>
"""
        
        self.logger.info("📝 MarkdownSignalFormatter initialized with multi-format support")
    
    def format_complete_signal(self, symbol: str, direction: str,
                             bias_signal: Dict, execution_signal: Dict,
                             trade_plan: Dict, narrative: Dict,
                             priority: MessagePriority = MessagePriority.MEDIUM,
                             formats: List[OutputFormat] = None) -> FormattedSignal:
        """
        Format complete signal for all output formats
        
        Args:
            symbol: Trading symbol
            direction: Trade direction
            bias_signal: Market bias analysis
            execution_signal: Entry validation results
            trade_plan: Complete trade plan
            narrative: Trading narrative
            priority: Message priority level
            formats: List of formats to generate (default: all)
            
        Returns:
            FormattedSignal with all format outputs
        """
        try:
            self.logger.info(f"📝 Formatting complete signal for {direction} {symbol}")
            
            if formats is None:
                formats = list(OutputFormat)
            
            # Generate all format outputs
            formatted_outputs = {}
            
            if OutputFormat.TELEGRAM in formats:
                formatted_outputs['telegram'] = self._format_telegram_message(
                    symbol, direction, bias_signal, execution_signal, trade_plan, narrative, priority
                )
            
            if OutputFormat.CONSOLE in formats:
                formatted_outputs['console'] = self._format_console_output(
                    symbol, direction, bias_signal, execution_signal, trade_plan, narrative
                )
            
            if OutputFormat.MARKDOWN in formats:
                formatted_outputs['markdown'] = self._format_markdown_content(
                    symbol, direction, bias_signal, execution_signal, trade_plan, narrative
                )
            
            if OutputFormat.JSON in formats:
                formatted_outputs['json'] = self._format_json_data(
                    symbol, direction, bias_signal, execution_signal, trade_plan, narrative
                )
            
            if OutputFormat.HTML in formats:
                formatted_outputs['html'] = self._format_html_content(
                    symbol, direction, bias_signal, execution_signal, trade_plan, narrative
                )
            
            # Calculate message properties
            telegram_msg = formatted_outputs.get('telegram', '')
            message_length = len(telegram_msg)
            estimated_tokens = self._estimate_tokens(telegram_msg)
            readability_score = self._calculate_readability(telegram_msg)
            urgency_indicators = self._identify_urgency_indicators(execution_signal, trade_plan)
            
            # Create formatted signal
            formatted_signal = FormattedSignal(
                symbol=symbol,
                direction=direction,
                format_type=OutputFormat.TELEGRAM,  # Primary format
                priority=priority,
                timestamp=int(datetime.now().timestamp() * 1000),
                telegram_message=formatted_outputs.get('telegram', ''),
                console_output=formatted_outputs.get('console', ''),
                markdown_content=formatted_outputs.get('markdown', ''),
                json_data=formatted_outputs.get('json', {}),
                html_content=formatted_outputs.get('html', ''),
                message_length=message_length,
                estimated_tokens=estimated_tokens,
                readability_score=readability_score,
                urgency_indicators=urgency_indicators
            )
            
            self.logger.info(f"✅ Signal formatted: {message_length} chars, {readability_score:.1%} readability")
            
            return formatted_signal
            
        except Exception as e:
            self.logger.error(f"❌ Error formatting signal: {e}")
            return self._get_default_formatted_signal(symbol, direction, priority)
    
    def _format_telegram_message(self, symbol: str, direction: str,
                                bias_signal: Dict, execution_signal: Dict,
                                trade_plan: Dict, narrative: Dict,
                                priority: MessagePriority) -> str:
        """Format message for Telegram with HTML markup"""
        try:
            # Extract key data
            confidence = bias_signal.get('confidence', 0.5) * 100
            entry_price = trade_plan.get('entry_price', 0)
            stop_loss = trade_plan.get('stop_loss', 0)
            tp_levels = trade_plan.get('take_profit_levels', [0, 0, 0])
            rr_ratio = trade_plan.get('risk_reward_ratio', 0)
            timeframe = trade_plan.get('timeframe', '1H')
            
            # Calculate distances
            sl_distance = abs(entry_price - stop_loss) / entry_price * 100 if entry_price > 0 else 0
            tp_distances = []
            for tp in tp_levels[:3]:
                if entry_price > 0:
                    tp_dist = abs(tp - entry_price) / entry_price * 100
                    tp_distances.append(tp_dist)
                else:
                    tp_distances.append(0)
            
            # Get emojis
            signal_emoji = self.signal_emojis.get(direction.upper(), "📊")
            confidence_emoji = self._get_confidence_emoji(confidence / 100)
            priority_emoji = self.priority_emojis.get(priority, "📊")
            
            # Create narrative section
            narrative_text = narrative.get('concise_narrative', 'Analisis SMC komprehensif tersedia.')
            if len(narrative_text) > 200:
                narrative_text = narrative_text[:200] + "..."
            
            narrative_section = f"""
📝 <b>Market Analysis:</b>
{narrative_text}"""
            
            # Create SMC section
            smc_section = f"""
🧠 <b>SMC Components:</b>
• CHoCH: {bias_signal.get('choch_count', 0)} patterns
• BOS: {bias_signal.get('bos_count', 0)} signals  
• Bias: {bias_signal.get('bias', 'neutral').title()}
• Validation: {execution_signal.get('validation_result', 'pending').title()}"""
            
            # Create risk section
            risk_assessment = execution_signal.get('risk_assessment', 'medium')
            plan_quality = trade_plan.get('plan_quality', 'average')
            
            risk_section = f"""
⚠️ <b>Risk Management:</b>
• Plan Quality: {plan_quality.title()}
• Risk Level: {risk_assessment.title()}
• Position Size: {trade_plan.get('position_size_percent', 1.0):.1f}%"""
            
            # Format timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S WIB')
            
            # Apply template
            telegram_message = self.telegram_template.format(
                priority_emoji=priority_emoji,
                signal_emoji=signal_emoji,
                symbol=symbol,
                direction=direction.upper(),
                confidence=confidence,
                confidence_emoji=confidence_emoji,
                timeframe=timeframe,
                entry_price=entry_price,
                stop_loss=stop_loss,
                sl_distance=sl_distance,
                tp1=tp_levels[0] if len(tp_levels) > 0 else 0,
                tp2=tp_levels[1] if len(tp_levels) > 1 else 0,
                tp3=tp_levels[2] if len(tp_levels) > 2 else 0,
                tp1_distance=tp_distances[0] if len(tp_distances) > 0 else 0,
                tp2_distance=tp_distances[1] if len(tp_distances) > 1 else 0,
                tp3_distance=tp_distances[2] if len(tp_distances) > 2 else 0,
                rr_ratio=rr_ratio,
                narrative_section=narrative_section,
                smc_section=smc_section,
                risk_section=risk_section,
                timestamp=timestamp
            )
            
            return telegram_message.strip()
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error formatting Telegram message: {e}")
            return self._get_fallback_telegram_message(symbol, direction, confidence)
    
    def _format_console_output(self, symbol: str, direction: str,
                              bias_signal: Dict, execution_signal: Dict,
                              trade_plan: Dict, narrative: Dict) -> str:
        """Format output for console display"""
        try:
            confidence = bias_signal.get('confidence', 0.5) * 100
            entry_price = trade_plan.get('entry_price', 0)
            stop_loss = trade_plan.get('stop_loss', 0)
            take_profit = trade_plan.get('take_profit_levels', [0])[0]
            rr_ratio = trade_plan.get('risk_reward_ratio', 0)
            
            console_output = f"""
=== SHARP SIGNAL ANALYSIS ===
Symbol: {symbol}
Direction: {direction.upper()}
Confidence: {confidence:.1f}%
Timeframe: {trade_plan.get('timeframe', '1H')}

=== TRADE SETUP ===
Entry Price: ${entry_price:,.4f}
Stop Loss: ${stop_loss:,.4f}
Take Profit: ${take_profit:,.4f}
Risk/Reward: {rr_ratio:.1f}:1

=== SMC ANALYSIS ===
Market Bias: {bias_signal.get('bias', 'neutral').title()}
CHoCH Patterns: {bias_signal.get('choch_count', 0)}
BOS Signals: {bias_signal.get('bos_count', 0)}
Validation: {execution_signal.get('validation_result', 'pending').title()}

=== NARRATIVE ===
{narrative.get('concise_narrative', 'Analysis in progress')[:300]}...

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            return console_output.strip()
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error formatting console output: {e}")
            return f"Console output error for {direction} {symbol}: {str(e)}"
    
    def _format_markdown_content(self, symbol: str, direction: str,
                                bias_signal: Dict, execution_signal: Dict,
                                trade_plan: Dict, narrative: Dict) -> str:
        """Format content as Markdown documentation"""
        try:
            markdown_content = f"""
# {direction.upper()} Signal Analysis - {symbol}

## Market Overview
- **Symbol**: {symbol}
- **Direction**: {direction.upper()}
- **Confidence**: {bias_signal.get('confidence', 0.5) * 100:.1f}%
- **Timeframe**: {trade_plan.get('timeframe', '1H')}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Trade Setup
| Parameter | Value | Notes |
|-----------|-------|-------|
| Entry Price | ${trade_plan.get('entry_price', 0):,.4f} | {trade_plan.get('entry_reason', 'Market entry')} |
| Stop Loss | ${trade_plan.get('stop_loss', 0):,.4f} | {trade_plan.get('stop_loss_reason', 'Risk management')} |
| Take Profit 1 | ${trade_plan.get('take_profit_levels', [0])[0]:,.4f} | {trade_plan.get('tp1_reason', 'First target')} |
| Risk/Reward | {trade_plan.get('risk_reward_ratio', 0):.1f}:1 | Risk management ratio |

## Smart Money Concept Analysis
- **Market Bias**: {bias_signal.get('bias', 'neutral').title()}
- **Bias Strength**: {bias_signal.get('strength', 0.5) * 100:.1f}%
- **CHoCH Patterns**: {bias_signal.get('choch_count', 0)}
- **BOS Signals**: {bias_signal.get('bos_count', 0)}
- **Trend Alignment**: {bias_signal.get('trend_alignment', 'mixed')}

## Validation Results
- **Validation Status**: {execution_signal.get('validation_result', 'pending').title()}
- **Validation Score**: {execution_signal.get('validation_score', 0):.2f}
- **Risk Assessment**: {execution_signal.get('risk_assessment', 'medium').title()}

### Confirmations
{self._format_confirmations_markdown(execution_signal.get('confirmations', {}))}

## Trading Narrative
{narrative.get('detailed_narrative', 'Detailed analysis not available')}

## Risk Management
- **Plan Quality**: {trade_plan.get('plan_quality', 'average').title()}
- **Position Size**: {trade_plan.get('position_size_percent', 1.0):.1f}%
- **Max Risk**: {trade_plan.get('max_risk_percent', 1.0):.1f}%

---
*Generated by RZC GPS Trading Bot using Smart Money Concept analysis*
"""
            
            return markdown_content.strip()
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error formatting Markdown content: {e}")
            return f"# Markdown Format Error\n\nError formatting {direction} {symbol}: {str(e)}"
    
    def _format_json_data(self, symbol: str, direction: str,
                         bias_signal: Dict, execution_signal: Dict,
                         trade_plan: Dict, narrative: Dict) -> Dict[str, Any]:
        """Format data as structured JSON"""
        try:
            json_data = {
                "signal_info": {
                    "symbol": symbol,
                    "direction": direction.upper(),
                    "timeframe": trade_plan.get('timeframe', '1H'),
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "confidence": bias_signal.get('confidence', 0.5),
                    "priority": "medium"
                },
                "trade_setup": {
                    "entry_price": trade_plan.get('entry_price', 0),
                    "stop_loss": trade_plan.get('stop_loss', 0),
                    "take_profit_levels": trade_plan.get('take_profit_levels', []),
                    "risk_reward_ratio": trade_plan.get('risk_reward_ratio', 0),
                    "position_size_percent": trade_plan.get('position_size_percent', 1.0),
                    "plan_quality": trade_plan.get('plan_quality', 'average')
                },
                "smc_analysis": {
                    "market_bias": bias_signal.get('bias', 'neutral'),
                    "bias_strength": bias_signal.get('strength', 0.5),
                    "choch_count": bias_signal.get('choch_count', 0),
                    "bos_count": bias_signal.get('bos_count', 0),
                    "trend_alignment": bias_signal.get('trend_alignment', 'mixed'),
                    "contributing_factors": bias_signal.get('contributing_factors', [])
                },
                "validation": {
                    "result": execution_signal.get('validation_result', 'pending'),
                    "score": execution_signal.get('validation_score', 0),
                    "confirmations": execution_signal.get('confirmations', {}),
                    "rejection_reasons": execution_signal.get('rejection_reasons', []),
                    "risk_assessment": execution_signal.get('risk_assessment', 'medium')
                },
                "narrative": {
                    "concise": narrative.get('concise_narrative', ''),
                    "detailed": narrative.get('detailed_narrative', ''),
                    "technical": narrative.get('technical_narrative', ''),
                    "confidence": narrative.get('narrative_confidence', 0.5),
                    "complexity_score": narrative.get('complexity_score', 0.5)
                },
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "1.0",
                    "source": "RZC_GPS_Trading_Bot",
                    "analysis_type": "SMC_Complete"
                }
            }
            
            return json_data
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error formatting JSON data: {e}")
            return {
                "error": f"JSON formatting error for {direction} {symbol}",
                "details": str(e),
                "timestamp": int(datetime.now().timestamp() * 1000)
            }
    
    def _format_html_content(self, symbol: str, direction: str,
                            bias_signal: Dict, execution_signal: Dict,
                            trade_plan: Dict, narrative: Dict) -> str:
        """Format content as HTML"""
        try:
            signal_class = direction.lower()
            confidence = bias_signal.get('confidence', 0.5) * 100
            
            html_content = f"""
<div class="signal-analysis {signal_class}">
    <div class="signal-header">
        <h2 class="signal-title">{direction.upper()} Signal - {symbol}</h2>
        <div class="confidence-badge">{confidence:.1f}%</div>
    </div>
    
    <div class="trade-setup">
        <h3>Trade Setup</h3>
        <table class="setup-table">
            <tr><td>Entry Price</td><td>${trade_plan.get('entry_price', 0):,.4f}</td></tr>
            <tr><td>Stop Loss</td><td>${trade_plan.get('stop_loss', 0):,.4f}</td></tr>
            <tr><td>Take Profit</td><td>${trade_plan.get('take_profit_levels', [0])[0]:,.4f}</td></tr>
            <tr><td>Risk/Reward</td><td>{trade_plan.get('risk_reward_ratio', 0):.1f}:1</td></tr>
        </table>
    </div>
    
    <div class="smc-analysis">
        <h3>Smart Money Concept Analysis</h3>
        <ul>
            <li>Market Bias: <strong>{bias_signal.get('bias', 'neutral').title()}</strong></li>
            <li>CHoCH Patterns: {bias_signal.get('choch_count', 0)}</li>
            <li>BOS Signals: {bias_signal.get('bos_count', 0)}</li>
            <li>Validation: {execution_signal.get('validation_result', 'pending').title()}</li>
        </ul>
    </div>
    
    <div class="narrative-section">
        <h3>Analysis Narrative</h3>
        <p>{narrative.get('concise_narrative', 'Analysis in progress')}</p>
    </div>
    
    <div class="timestamp">
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</div>
"""
            
            return html_content.strip()
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error formatting HTML content: {e}")
            return f"<div class='error'>HTML formatting error for {direction} {symbol}: {str(e)}</div>"
    
    def _format_confirmations_markdown(self, confirmations: Dict[str, bool]) -> str:
        """Format confirmations as Markdown list"""
        if not confirmations:
            return "- No confirmations available"
        
        formatted_confirmations = []
        for component, status in confirmations.items():
            status_icon = "✅" if status else "❌"
            component_name = component.upper().replace('_', ' ')
            formatted_confirmations.append(f"- {status_icon} {component_name}")
        
        return "\n".join(formatted_confirmations)
    
    def _get_confidence_emoji(self, confidence: float) -> str:
        """Get emoji based on confidence level"""
        for threshold in sorted(self.confidence_emojis.keys(), reverse=True):
            if confidence >= threshold:
                return self.confidence_emojis[threshold]
        return "❓"
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Simple estimation: ~4 characters per token
        return max(len(text) // 4, 1)
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (simplified)"""
        try:
            if not text:
                return 0.0
            
            words = len(text.split())
            sentences = text.count('.') + text.count('!') + text.count('?')
            
            if sentences == 0:
                return 0.5
            
            avg_words_per_sentence = words / sentences
            
            # Optimal range: 10-20 words per sentence
            if 10 <= avg_words_per_sentence <= 20:
                return 0.9
            elif 8 <= avg_words_per_sentence <= 25:
                return 0.7
            else:
                return 0.5
                
        except Exception:
            return 0.5
    
    def _identify_urgency_indicators(self, execution_signal: Dict, trade_plan: Dict) -> List[str]:
        """Identify factors that indicate message urgency"""
        indicators = []
        
        # High confidence signal
        if execution_signal.get('confidence', 0) > 0.8:
            indicators.append("High confidence signal")
        
        # Excellent plan quality
        if trade_plan.get('plan_quality') == 'excellent':
            indicators.append("Excellent trade setup")
        
        # High risk/reward ratio
        rr_ratio = trade_plan.get('risk_reward_ratio', 0)
        if rr_ratio >= 3.0:
            indicators.append("High R/R ratio")
        
        # Validation status
        if execution_signal.get('validation_result') == 'valid':
            indicators.append("Fully validated entry")
        
        return indicators
    
    def _get_fallback_telegram_message(self, symbol: str, direction: str, confidence: float) -> str:
        """Get fallback Telegram message for errors"""
        signal_emoji = self.signal_emojis.get(direction.upper(), "📊")
        
        return f"""
{signal_emoji} <b>SIGNAL ANALYSIS - {symbol}</b>

📊 <b>Direction:</b> {direction.upper()}
💯 <b>Confidence:</b> {confidence:.1f}%

⚠️ <b>Status:</b> Analysis in progress
📝 <b>Note:</b> Detailed analysis being processed

⏰ <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB
<i>RZC GPS Trading Bot</i>
"""
    
    def _get_default_formatted_signal(self, symbol: str, direction: str, priority: MessagePriority) -> FormattedSignal:
        """Get default formatted signal for error cases"""
        fallback_message = self._get_fallback_telegram_message(symbol, direction, 50.0)
        
        return FormattedSignal(
            symbol=symbol,
            direction=direction,
            format_type=OutputFormat.TELEGRAM,
            priority=priority,
            timestamp=int(datetime.now().timestamp() * 1000),
            telegram_message=fallback_message,
            console_output=f"Signal analysis for {direction} {symbol} in progress",
            markdown_content=f"# {direction} {symbol}\n\nAnalysis in progress...",
            json_data={"error": "Formatting error", "symbol": symbol, "direction": direction},
            html_content=f"<div>Signal analysis for {direction} {symbol} in progress</div>",
            message_length=len(fallback_message),
            estimated_tokens=len(fallback_message) // 4,
            readability_score=0.7,
            urgency_indicators=["Analysis in progress"]
        )
    
    def get_formatted_output(self, formatted_signal: FormattedSignal, output_format: OutputFormat) -> Union[str, Dict]:
        """
        Get specific formatted output
        
        Returns:
            Formatted content in requested format
        """
        format_map = {
            OutputFormat.TELEGRAM: formatted_signal.telegram_message,
            OutputFormat.CONSOLE: formatted_signal.console_output,
            OutputFormat.MARKDOWN: formatted_signal.markdown_content,
            OutputFormat.JSON: formatted_signal.json_data,
            OutputFormat.HTML: formatted_signal.html_content
        }
        
        return format_map.get(output_format, formatted_signal.telegram_message)
    
    def get_formatting_summary(self, formatted_signal: FormattedSignal) -> Dict[str, Any]:
        """
        Get summary of formatting results
        
        Returns:
            Dictionary with formatting metrics
        """
        return {
            "symbol": formatted_signal.symbol,
            "direction": formatted_signal.direction,
            "priority": formatted_signal.priority.value,
            "timestamp": formatted_signal.timestamp,
            "message_properties": {
                "length": formatted_signal.message_length,
                "estimated_tokens": formatted_signal.estimated_tokens,
                "readability_score": formatted_signal.readability_score
            },
            "urgency_indicators": formatted_signal.urgency_indicators,
            "formats_available": {
                "telegram": len(formatted_signal.telegram_message) > 0,
                "console": len(formatted_signal.console_output) > 0,
                "markdown": len(formatted_signal.markdown_content) > 0,
                "json": len(formatted_signal.json_data) > 0,
                "html": len(formatted_signal.html_content) > 0
            }
        }