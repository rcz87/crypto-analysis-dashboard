#!/usr/bin/env python3
"""
NarrativeComposer: SMC Narrative Generation Module
Menyusun narasi singkat menjelaskan kenapa sinyal muncul berdasarkan analisis SMC
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class NarrativeStyle(Enum):
    """Narrative output styles"""
    CONCISE = "concise"
    DETAILED = "detailed"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"

@dataclass
class TradingNarrative:
    """Structure for trading narrative"""
    symbol: str
    direction: str
    timeframe: str
    timestamp: int
    
    # Core narrative components
    market_context: str
    signal_reasoning: str
    smc_analysis: str
    risk_assessment: str
    trade_rationale: str
    
    # Supporting details
    key_levels: List[str]
    indicators_summary: List[str]
    confidence_factors: List[str]
    risk_factors: List[str]
    
    # Complete narratives
    concise_narrative: str
    detailed_narrative: str
    technical_narrative: str
    educational_narrative: str
    
    # Metadata
    narrative_confidence: float
    complexity_score: float
    readability_score: float

class NarrativeComposer:
    """
    📝 SMC Narrative Composer
    
    Menghasilkan narasi trading yang komprehensif berdasarkan:
    - Market structure analysis
    - SMC pattern confluence
    - Entry/exit reasoning
    - Risk management rationale
    - Educational insights
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.NarrativeComposer")
        
        # Narrative templates
        self.market_context_templates = {
            "bullish": "Market menunjukkan struktur bullish dengan {structure_details}",
            "bearish": "Market menampilkan struktur bearish dengan {structure_details}", 
            "neutral": "Market dalam kondisi consolidation dengan {structure_details}",
            "mixed": "Market menunjukkan sinyal campuran dengan {structure_details}"
        }
        
        self.signal_templates = {
            "buy": "Signal BUY terbentuk dari {signal_triggers}",
            "sell": "Signal SELL terkonfirmasi melalui {signal_triggers}",
            "neutral": "Signal NEUTRAL mengindikasikan {signal_triggers}"
        }
        
        # Indonesian language patterns
        self.indonesian_connectors = [
            "berdasarkan", "mengindikasikan", "menunjukkan", "mengkonfirmasi",
            "didukung oleh", "diperkuat dengan", "sejalan dengan", "bertentangan dengan"
        ]
        
        self.confidence_descriptors = {
            0.9: "sangat tinggi", 0.8: "tinggi", 0.7: "cukup tinggi",
            0.6: "sedang", 0.5: "rendah", 0.4: "sangat rendah"
        }
        
        self.logger.info("📝 NarrativeComposer initialized with Indonesian language support")
    
    def compose_trading_narrative(self, symbol: str, direction: str, 
                                bias_signal: Dict, execution_signal: Dict,
                                trade_plan: Dict, smc_components: Dict,
                                timeframe: str = "1H") -> TradingNarrative:
        """
        Compose comprehensive trading narrative
        
        Args:
            symbol: Trading symbol
            direction: Trade direction
            bias_signal: Market bias analysis
            execution_signal: Entry validation results
            trade_plan: Complete trade plan
            smc_components: SMC analysis components
            timeframe: Analysis timeframe
            
        Returns:
            Complete TradingNarrative with all narrative styles
        """
        try:
            self.logger.info(f"📝 Composing narrative for {direction} {symbol}")
            
            # 1. Generate core narrative components
            market_context = self._compose_market_context(bias_signal, smc_components)
            signal_reasoning = self._compose_signal_reasoning(execution_signal, smc_components)
            smc_analysis = self._compose_smc_analysis(smc_components)
            risk_assessment = self._compose_risk_assessment(trade_plan, execution_signal)
            trade_rationale = self._compose_trade_rationale(bias_signal, execution_signal, trade_plan)
            
            # 2. Extract supporting details
            key_levels = self._extract_key_levels(trade_plan, smc_components)
            indicators_summary = self._extract_indicators_summary(execution_signal, smc_components)
            confidence_factors = self._extract_confidence_factors(bias_signal, execution_signal)
            risk_factors = self._extract_risk_factors(trade_plan, execution_signal)
            
            # 3. Generate different narrative styles
            concise_narrative = self._generate_concise_narrative(
                symbol, direction, market_context, signal_reasoning, trade_rationale
            )
            
            detailed_narrative = self._generate_detailed_narrative(
                symbol, direction, market_context, signal_reasoning, 
                smc_analysis, risk_assessment, trade_rationale
            )
            
            technical_narrative = self._generate_technical_narrative(
                symbol, direction, smc_components, execution_signal, trade_plan
            )
            
            educational_narrative = self._generate_educational_narrative(
                symbol, direction, smc_components, bias_signal, execution_signal
            )
            
            # 4. Calculate narrative metrics
            narrative_confidence = self._calculate_narrative_confidence(bias_signal, execution_signal)
            complexity_score = self._calculate_complexity_score(smc_components, execution_signal)
            readability_score = self._calculate_readability_score(detailed_narrative)
            
            # Create narrative object
            narrative = TradingNarrative(
                symbol=symbol,
                direction=direction,
                timeframe=timeframe,
                timestamp=int(datetime.now().timestamp() * 1000),
                market_context=market_context,
                signal_reasoning=signal_reasoning,
                smc_analysis=smc_analysis,
                risk_assessment=risk_assessment,
                trade_rationale=trade_rationale,
                key_levels=key_levels,
                indicators_summary=indicators_summary,
                confidence_factors=confidence_factors,
                risk_factors=risk_factors,
                concise_narrative=concise_narrative,
                detailed_narrative=detailed_narrative,
                technical_narrative=technical_narrative,
                educational_narrative=educational_narrative,
                narrative_confidence=narrative_confidence,
                complexity_score=complexity_score,
                readability_score=readability_score
            )
            
            self.logger.info(f"✅ Narrative composed with {narrative_confidence:.1%} confidence")
            
            return narrative
            
        except Exception as e:
            self.logger.error(f"❌ Error composing narrative: {e}")
            return self._get_default_narrative(symbol, direction, timeframe)
    
    def _compose_market_context(self, bias_signal: Dict, smc_components: Dict) -> str:
        """Compose market context description"""
        try:
            bias = bias_signal.get('bias', 'neutral')
            strength = bias_signal.get('strength', 0.5)
            confidence = bias_signal.get('confidence', 0.5)
            
            # Structure details from SMC
            structure_details = []
            
            if smc_components.get('choch_count', 0) > 0:
                structure_details.append(f"{smc_components['choch_count']} CHoCH pattern")
            
            if smc_components.get('bos_count', 0) > 0:
                structure_details.append(f"{smc_components['bos_count']} BOS breakout")
            
            if smc_components.get('order_blocks_count', 0) > 0:
                structure_details.append(f"{smc_components['order_blocks_count']} order blocks")
            
            structure_text = ", ".join(structure_details) if structure_details else "struktur konsolidasi"
            
            # Get confidence descriptor
            confidence_desc = self._get_confidence_descriptor(confidence)
            
            # Compose context
            context = f"Market menunjukkan bias {bias} dengan kekuatan {strength:.1%} dan confidence {confidence_desc}. "
            context += f"Struktur market didukung oleh {structure_text}. "
            
            # Add trend alignment info
            alignment = bias_signal.get('trend_alignment', 'mixed_signals')
            if alignment == 'fully_aligned_bullish':
                context += "Semua timeframe selaras bullish."
            elif alignment == 'fully_aligned_bearish':
                context += "Semua timeframe selaras bearish."
            elif alignment == 'mostly_bullish':
                context += "Mayoritas indikator bullish."
            elif alignment == 'mostly_bearish':
                context += "Mayoritas indikator bearish."
            else:
                context += "Sinyal campuran dari berbagai indikator."
            
            return context
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error composing market context: {e}")
            return "Market dalam kondisi analisis dengan struktur yang sedang dipelajari."
    
    def _compose_signal_reasoning(self, execution_signal: Dict, smc_components: Dict) -> str:
        """Compose signal reasoning explanation"""
        try:
            direction = execution_signal.get('direction', 'NEUTRAL')
            validation_result = execution_signal.get('validation_result', 'invalid')
            confidence = execution_signal.get('confidence', 0.0)
            
            # Get confirmation details
            confirmations = execution_signal.get('confirmations', {})
            confirmed_components = [comp for comp, status in confirmations.items() if status]
            
            reasoning = f"Signal {direction} "
            
            if validation_result == 'valid':
                reasoning += f"tervalidasi dengan confidence {confidence:.1%}. "
            elif validation_result == 'pending':
                reasoning += f"menunggu konfirmasi dengan confidence {confidence:.1%}. "
            else:
                reasoning += f"belum tervalidasi dengan confidence {confidence:.1%}. "
            
            # Add confirmation details
            if confirmed_components:
                comp_names = {
                    'choch': 'CHoCH',
                    'fvg': 'FVG',
                    'delta': 'Volume Delta',
                    'rsi': 'RSI',
                    'orderflow': 'Order Flow'
                }
                
                confirmed_list = [comp_names.get(comp, comp) for comp in confirmed_components]
                reasoning += f"Dikonfirmasi oleh: {', '.join(confirmed_list)}. "
            
            # Add rejection reasons if any
            rejection_reasons = execution_signal.get('rejection_reasons', [])
            if rejection_reasons:
                reasoning += f"Perhatian: {', '.join(rejection_reasons[:2])}."
            
            return reasoning
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error composing signal reasoning: {e}")
            return "Signal sedang dalam proses validasi berdasarkan kriteria SMC."
    
    def _compose_smc_analysis(self, smc_components: Dict) -> str:
        """Compose SMC-specific analysis"""
        try:
            analysis_parts = []
            
            # CHoCH Analysis
            choch_count = smc_components.get('choch_count', 0)
            if choch_count > 0:
                analysis_parts.append(f"Terdeteksi {choch_count} Change of Character (CHoCH) yang mengindikasikan perubahan struktur market")
            
            # BOS Analysis
            bos_count = smc_components.get('bos_count', 0)
            if bos_count > 0:
                analysis_parts.append(f"Terdapat {bos_count} Break of Structure (BOS) yang mengkonfirmasi continuasi trend")
            
            # Order Blocks
            ob_count = smc_components.get('order_blocks_count', 0)
            if ob_count > 0:
                analysis_parts.append(f"Diidentifikasi {ob_count} Order Blocks sebagai zona institutional interest")
            
            # FVG Analysis
            fvg_count = smc_components.get('fvg_count', 0)
            if fvg_count > 0:
                analysis_parts.append(f"Ditemukan {fvg_count} Fair Value Gaps yang berpotensi sebagai area retracement")
            
            # Liquidity Analysis
            liquidity_count = smc_components.get('liquidity_sweeps_count', 0)
            if liquidity_count > 0:
                analysis_parts.append(f"Analisis liquidity menunjukkan {liquidity_count} sweep patterns")
            
            if analysis_parts:
                return "Analisis Smart Money Concept: " + ". ".join(analysis_parts) + "."
            else:
                return "Analisis SMC menunjukkan kondisi market dalam fase observasi dengan pattern yang sedang terbentuk."
                
        except Exception as e:
            self.logger.warning(f"⚠️ Error composing SMC analysis: {e}")
            return "Analisis Smart Money Concept sedang diproses untuk memberikan insight yang akurat."
    
    def _compose_risk_assessment(self, trade_plan: Dict, execution_signal: Dict) -> str:
        """Compose risk assessment description"""
        try:
            risk_reward = trade_plan.get('risk_reward_ratio', 0.0)
            risk_percent = trade_plan.get('max_risk_percent', 1.0)
            plan_quality = trade_plan.get('plan_quality', 'average')
            execution_risk = execution_signal.get('risk_assessment', 'medium')
            
            assessment = f"Manajemen risiko: R/R ratio {risk_reward:.1f}:1 dengan maksimal risiko {risk_percent}% per trade. "
            
            # Plan quality description
            quality_desc = {
                'excellent': 'sangat baik',
                'good': 'baik', 
                'average': 'rata-rata',
                'poor': 'kurang'
            }
            
            assessment += f"Kualitas rencana trading: {quality_desc.get(plan_quality, 'rata-rata')}. "
            
            # Execution risk
            risk_desc = {
                'low': 'rendah',
                'medium': 'sedang',
                'high': 'tinggi'
            }
            
            assessment += f"Level risiko eksekusi: {risk_desc.get(execution_risk, 'sedang')}."
            
            # Add stop loss info
            stop_loss = trade_plan.get('stop_loss', 0)
            entry_price = trade_plan.get('entry_price', 0)
            if stop_loss > 0 and entry_price > 0:
                stop_distance = abs(entry_price - stop_loss) / entry_price * 100
                assessment += f" Stop loss ditempatkan pada jarak {stop_distance:.1f}% dari entry."
            
            return assessment
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error composing risk assessment: {e}")
            return "Manajemen risiko mengikuti prinsip konservatif dengan R/R ratio yang menguntungkan."
    
    def _compose_trade_rationale(self, bias_signal: Dict, execution_signal: Dict, trade_plan: Dict) -> str:
        """Compose overall trade rationale"""
        try:
            bias = bias_signal.get('bias', 'neutral')
            bias_confidence = bias_signal.get('confidence', 0.5)
            execution_confidence = execution_signal.get('confidence', 0.5)
            plan_quality = trade_plan.get('plan_quality', 'average')
            
            # Overall confidence
            overall_confidence = (bias_confidence + execution_confidence) / 2
            
            rationale = f"Rasional trading: Market bias {bias} dengan confidence {bias_confidence:.1%}, "
            rationale += f"validasi entry {execution_confidence:.1%}, dan kualitas plan {plan_quality}. "
            
            # Recommendation based on overall assessment
            if overall_confidence >= 0.8 and plan_quality in ['excellent', 'good']:
                rationale += "Setup trading ini sangat menarik untuk dieksekusi."
            elif overall_confidence >= 0.6 and plan_quality in ['good', 'average']:
                rationale += "Setup trading layak dipertimbangkan dengan monitoring ketat."
            elif overall_confidence >= 0.4:
                rationale += "Setup trading memerlukan konfirmasi tambahan sebelum eksekusi."
            else:
                rationale += "Setup trading belum optimal, disarankan menunggu konfirmasi lebih lanjut."
            
            return rationale
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error composing trade rationale: {e}")
            return "Rasional trading berdasarkan analisis komprehensif SMC dengan pendekatan konservatif."
    
    def _extract_key_levels(self, trade_plan: Dict, smc_components: Dict) -> List[str]:
        """Extract key price levels from analysis"""
        levels = []
        
        try:
            # Entry and exits
            entry_price = trade_plan.get('entry_price', 0)
            if entry_price > 0:
                levels.append(f"Entry: ${entry_price:.4f}")
            
            stop_loss = trade_plan.get('stop_loss', 0)
            if stop_loss > 0:
                levels.append(f"Stop Loss: ${stop_loss:.4f}")
            
            # Take profits
            tp_levels = trade_plan.get('take_profit_levels', [])
            for i, tp in enumerate(tp_levels[:3], 1):
                if tp > 0:
                    levels.append(f"TP{i}: ${tp:.4f}")
            
            # SMC levels
            if smc_components.get('order_blocks'):
                ob_price = smc_components['order_blocks'][0].get('price', 0)
                if ob_price > 0:
                    levels.append(f"Order Block: ${ob_price:.4f}")
            
            return levels
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting key levels: {e}")
            return ["Key levels sedang dianalisis"]
    
    def _extract_indicators_summary(self, execution_signal: Dict, smc_components: Dict) -> List[str]:
        """Extract summary of indicators and confirmations"""
        summary = []
        
        try:
            confirmations = execution_signal.get('confirmations', {})
            
            for indicator, status in confirmations.items():
                status_text = "✅" if status else "❌"
                indicator_names = {
                    'choch': 'CHoCH Confirmation',
                    'fvg': 'FVG Presence', 
                    'delta': 'Volume Delta',
                    'rsi': 'RSI Alignment',
                    'orderflow': 'Order Flow'
                }
                
                name = indicator_names.get(indicator, indicator.upper())
                summary.append(f"{status_text} {name}")
            
            return summary
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting indicators summary: {e}")
            return ["Indikator sedang diproses"]
    
    def _extract_confidence_factors(self, bias_signal: Dict, execution_signal: Dict) -> List[str]:
        """Extract factors contributing to confidence"""
        factors = []
        
        try:
            # Bias factors
            bias_factors = bias_signal.get('contributing_factors', [])
            factors.extend(bias_factors[:3])  # Top 3
            
            # Execution factors
            if execution_signal.get('validation_result') == 'valid':
                factors.append("Entry signal tervalidasi")
            
            validation_score = execution_signal.get('validation_score', 0)
            if validation_score > 0.7:
                factors.append("Score validasi tinggi")
            
            return factors
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting confidence factors: {e}")
            return ["Faktor confidence sedang dianalisis"]
    
    def _extract_risk_factors(self, trade_plan: Dict, execution_signal: Dict) -> List[str]:
        """Extract risk factors from analysis"""
        factors = []
        
        try:
            # Plan quality risks
            plan_quality = trade_plan.get('plan_quality', 'average')
            if plan_quality == 'poor':
                factors.append("Kualitas rencana trading rendah")
            
            # R/R risks
            rr_ratio = trade_plan.get('risk_reward_ratio', 0)
            if rr_ratio < 1.5:
                factors.append("Risk/Reward ratio tidak optimal")
            
            # Execution risks
            rejection_reasons = execution_signal.get('rejection_reasons', [])
            factors.extend(rejection_reasons[:2])  # Top 2 reasons
            
            return factors
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error extracting risk factors: {e}")
            return ["Faktor risiko sedang dievaluasi"]
    
    def _generate_concise_narrative(self, symbol: str, direction: str, 
                                  market_context: str, signal_reasoning: str, 
                                  trade_rationale: str) -> str:
        """Generate concise narrative (< 200 words)"""
        try:
            narrative = f"🎯 **{direction} {symbol}**\n\n"
            narrative += f"{market_context[:100]}...\n\n"
            narrative += f"{signal_reasoning[:100]}...\n\n"
            narrative += f"{trade_rationale[:80]}..."
            
            return narrative
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generating concise narrative: {e}")
            return f"📊 {direction} signal untuk {symbol} berdasarkan analisis SMC komprehensif."
    
    def _generate_detailed_narrative(self, symbol: str, direction: str,
                                   market_context: str, signal_reasoning: str,
                                   smc_analysis: str, risk_assessment: str,
                                   trade_rationale: str) -> str:
        """Generate detailed narrative (400-600 words)"""
        try:
            narrative = f"🚀 **ANALISIS TRADING {direction} - {symbol}**\n\n"
            narrative += f"📊 **KONTEKS MARKET:**\n{market_context}\n\n"
            narrative += f"🎯 **REASONING SIGNAL:**\n{signal_reasoning}\n\n"
            narrative += f"🧠 **ANALISIS SMC:**\n{smc_analysis}\n\n"
            narrative += f"⚠️ **MANAJEMEN RISIKO:**\n{risk_assessment}\n\n"
            narrative += f"💡 **RASIONAL TRADING:**\n{trade_rationale}\n\n"
            narrative += f"⏰ **Waktu Analisis:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB"
            
            return narrative
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generating detailed narrative: {e}")
            return f"Analisis detailed untuk {direction} {symbol} sedang diproses."
    
    def _generate_technical_narrative(self, symbol: str, direction: str,
                                    smc_components: Dict, execution_signal: Dict,
                                    trade_plan: Dict) -> str:
        """Generate technical narrative for advanced users"""
        try:
            narrative = f"⚙️ **TECHNICAL ANALYSIS - {direction} {symbol}**\n\n"
            
            # SMC Technical Details
            narrative += "📈 **SMC COMPONENTS:**\n"
            narrative += f"• CHoCH Patterns: {smc_components.get('choch_count', 0)}\n"
            narrative += f"• BOS Signals: {smc_components.get('bos_count', 0)}\n"
            narrative += f"• Order Blocks: {smc_components.get('order_blocks_count', 0)}\n"
            narrative += f"• FVG Zones: {smc_components.get('fvg_count', 0)}\n"
            narrative += f"• Liquidity Sweeps: {smc_components.get('liquidity_sweeps_count', 0)}\n\n"
            
            # Validation Matrix
            narrative += "✅ **VALIDATION MATRIX:**\n"
            confirmations = execution_signal.get('confirmations', {})
            for comp, status in confirmations.items():
                status_icon = "✅" if status else "❌"
                narrative += f"• {comp.upper()}: {status_icon}\n"
            
            narrative += f"\n📊 **Validation Score:** {execution_signal.get('validation_score', 0):.2f}\n"
            narrative += f"🎯 **R/R Ratio:** {trade_plan.get('risk_reward_ratio', 0):.2f}:1\n"
            
            return narrative
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generating technical narrative: {e}")
            return f"Technical analysis untuk {direction} {symbol} dalam proses."
    
    def _generate_educational_narrative(self, symbol: str, direction: str,
                                      smc_components: Dict, bias_signal: Dict,
                                      execution_signal: Dict) -> str:
        """Generate educational narrative for learning"""
        try:
            narrative = f"🎓 **EDUKASI SMC - {direction} {symbol}**\n\n"
            
            narrative += "📚 **KONSEP YANG DITERAPKAN:**\n"
            narrative += "• **Smart Money Concept (SMC):** Analisis berdasarkan perilaku institutional traders\n"
            narrative += "• **CHoCH:** Change of Character - perubahan struktur market\n"
            narrative += "• **BOS:** Break of Structure - konfirmasi continuasi trend\n"
            narrative += "• **Order Blocks:** Area dimana institusi menempatkan order besar\n"
            narrative += "• **FVG:** Fair Value Gap - area ketidakseimbangan harga\n\n"
            
            narrative += "🔍 **PROSES ANALISIS:**\n"
            narrative += "1. Identifikasi market bias melalui struktur trend\n"
            narrative += "2. Validasi entry menggunakan confluence SMC\n"
            narrative += "3. Penentuan level entry, SL, TP berdasarkan liquidity\n"
            narrative += "4. Manajemen risiko dengan R/R ratio optimal\n\n"
            
            narrative += f"💡 **LESSON LEARNED:**\n"
            bias_confidence = bias_signal.get('confidence', 0.5)
            if bias_confidence > 0.7:
                narrative += "• High confidence setup mengindikasikan alignment multi-indikator\n"
            else:
                narrative += "• Medium/low confidence memerlukan konfirmasi tambahan\n"
            
            return narrative
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error generating educational narrative: {e}")
            return f"Materi edukasi SMC untuk {direction} {symbol} sedang disiapkan."
    
    def _get_confidence_descriptor(self, confidence: float) -> str:
        """Get Indonesian confidence descriptor"""
        for threshold in sorted(self.confidence_descriptors.keys(), reverse=True):
            if confidence >= threshold:
                return self.confidence_descriptors[threshold]
        return "sangat rendah"
    
    def _calculate_narrative_confidence(self, bias_signal: Dict, execution_signal: Dict) -> float:
        """Calculate overall narrative confidence"""
        try:
            bias_conf = bias_signal.get('confidence', 0.5)
            exec_conf = execution_signal.get('confidence', 0.5)
            validation_score = execution_signal.get('validation_score', 0.5)
            
            # Weighted average
            narrative_conf = (bias_conf * 0.4) + (exec_conf * 0.4) + (validation_score * 0.2)
            
            return min(narrative_conf, 1.0)
            
        except Exception:
            return 0.5
    
    def _calculate_complexity_score(self, smc_components: Dict, execution_signal: Dict) -> float:
        """Calculate narrative complexity score"""
        try:
            # Count SMC components
            smc_count = sum([
                smc_components.get('choch_count', 0),
                smc_components.get('bos_count', 0),
                smc_components.get('order_blocks_count', 0),
                smc_components.get('fvg_count', 0),
                smc_components.get('liquidity_sweeps_count', 0)
            ])
            
            # Count confirmations
            confirmed_count = sum(execution_signal.get('confirmations', {}).values())
            
            # Normalize to 0-1 scale
            complexity = min((smc_count + confirmed_count) / 20, 1.0)
            
            return complexity
            
        except Exception:
            return 0.5
    
    def _calculate_readability_score(self, text: str) -> float:
        """Calculate text readability score (simplified)"""
        try:
            if not text:
                return 0.0
            
            # Simple readability metrics
            word_count = len(text.split())
            sentence_count = text.count('.') + text.count('!') + text.count('?')
            
            if sentence_count == 0:
                return 0.5
            
            avg_words_per_sentence = word_count / sentence_count
            
            # Score based on sentence length (optimal: 15-20 words)
            if 15 <= avg_words_per_sentence <= 20:
                readability = 1.0
            elif 10 <= avg_words_per_sentence <= 25:
                readability = 0.8
            elif 8 <= avg_words_per_sentence <= 30:
                readability = 0.6
            else:
                readability = 0.4
            
            return readability
            
        except Exception:
            return 0.5
    
    def _get_default_narrative(self, symbol: str, direction: str, timeframe: str) -> TradingNarrative:
        """Get default narrative for error cases"""
        return TradingNarrative(
            symbol=symbol,
            direction=direction,
            timeframe=timeframe,
            timestamp=int(datetime.now().timestamp() * 1000),
            market_context="Market sedang dalam analisis untuk menentukan struktur dan bias yang tepat.",
            signal_reasoning="Signal sedang divalidasi menggunakan kriteria Smart Money Concept.",
            smc_analysis="Analisis SMC menunjukkan pola yang sedang berkembang dan memerlukan konfirmasi.",
            risk_assessment="Manajemen risiko mengikuti protokol standar dengan R/R ratio konservatif.",
            trade_rationale="Setup trading memerlukan analisis lebih lanjut sebelum eksekusi.",
            key_levels=["Level kunci sedang diidentifikasi"],
            indicators_summary=["Indikator dalam proses validasi"],
            confidence_factors=["Faktor confidence sedang dievaluasi"],
            risk_factors=["Faktor risiko sedang dinilai"],
            concise_narrative=f"Analisis {direction} {symbol} sedang diproses dengan pendekatan SMC.",
            detailed_narrative=f"Analisis komprehensif untuk {direction} {symbol} menggunakan Smart Money Concept sedang berlangsung.",
            technical_narrative=f"Technical analysis {direction} {symbol} dalam tahap pemrosesan data.",
            educational_narrative=f"Pembelajaran SMC untuk {direction} {symbol} sedang disiapkan.",
            narrative_confidence=0.3,
            complexity_score=0.5,
            readability_score=0.7
        )
    
    def get_narrative_by_style(self, narrative: TradingNarrative, style: NarrativeStyle) -> str:
        """
        Get narrative by specific style
        
        Returns:
            Formatted narrative string
        """
        style_map = {
            NarrativeStyle.CONCISE: narrative.concise_narrative,
            NarrativeStyle.DETAILED: narrative.detailed_narrative,
            NarrativeStyle.TECHNICAL: narrative.technical_narrative,
            NarrativeStyle.EDUCATIONAL: narrative.educational_narrative
        }
        
        return style_map.get(style, narrative.detailed_narrative)
    
    def get_narrative_summary(self, narrative: TradingNarrative) -> Dict[str, Any]:
        """
        Get summary of narrative for external use
        
        Returns:
            Dictionary with narrative summary
        """
        return {
            "symbol": narrative.symbol,
            "direction": narrative.direction,
            "timeframe": narrative.timeframe,
            "timestamp": narrative.timestamp,
            "narrative_confidence": narrative.narrative_confidence,
            "complexity_score": narrative.complexity_score,
            "readability_score": narrative.readability_score,
            "key_levels_count": len(narrative.key_levels),
            "indicators_count": len(narrative.indicators_summary),
            "confidence_factors_count": len(narrative.confidence_factors),
            "risk_factors_count": len(narrative.risk_factors),
            "narratives_available": {
                "concise": len(narrative.concise_narrative),
                "detailed": len(narrative.detailed_narrative),
                "technical": len(narrative.technical_narrative),
                "educational": len(narrative.educational_narrative)
            }
        }