
#!/usr/bin/env python3
"""
Enhanced Reasoning Engine (Patched) - Production-hardened
- Safe JSON serialization
- Indicator normalization & clamping
- Robust AI response schema guard
- Lightweight retry/backoff for OpenAI
- Prompt compaction to reduce token usage
- Zero-safe diagnostics & history ring buffer
"""

import os
import json
import time
import math
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


# =============================
# Enums & Data Models
# =============================

class ReasoningConfidence(Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class ReasoningResult:
    """Hasil reasoning dengan tingkat confidence dan evidence"""
    conclusion: str
    confidence: ReasoningConfidence
    confidence_score: float
    evidence: List[str]
    data_sources: List[str]
    reasoning_chain: List[str]
    uncertainty_factors: List[str]
    timestamp: float

    def to_dict(self) -> Dict[str, Any]:
        """JSON-serializable dictionary (Enum → value, ts → ISO8601)"""
        return {
            "conclusion": self.conclusion,
            "confidence": self.confidence.value if isinstance(self.confidence, ReasoningConfidence) else str(self.confidence),
            "confidence_score": float(self.confidence_score),
            "evidence": list(self.evidence or []),
            "data_sources": list(self.data_sources or []),
            "reasoning_chain": list(self.reasoning_chain or []),
            "uncertainty_factors": list(self.uncertainty_factors or []),
            "timestamp": datetime.utcfromtimestamp(self.timestamp).isoformat() + "Z",
        }


@dataclass
class MarketFactors:
    """Market factors yang akan dianalisis"""
    price_data: Dict[str, Any]
    volume_data: Dict[str, Any]
    technical_indicators: Dict[str, Any]
    smc_analysis: Dict[str, Any]
    market_structure: Dict[str, Any]
    orderbook_data: Optional[Dict[str, Any]] = None
    news_sentiment: Optional[Dict[str, Any]] = None


# =============================
# Core Engine
# =============================

class EnhancedReasoningEngine:
    """
    Enhanced Reasoning Engine untuk analisis trading cryptocurrency
    Fokus pada accuracy, clarity, dan menghindari halusinasi
    """

    def __init__(self, history_size: int = 100):
        self.reasoning_history: List[ReasoningResult] = []
        self.history_size = max(10, history_size)
        self.confidence_threshold = 50.0  # Minimum confidence untuk actionable signals

        # Optional OpenAI client
        self.openai_client = None
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI  # type: ignore
                self.openai_client = OpenAI(api_key=api_key)
                logger.info("🧠 OpenAI client initialized")
            except Exception as e:
                logger.warning(f"OpenAI init failed, proceeding rule-based only: {e}")
        else:
            logger.info("🧠 Running without OpenAI (rule-based only)")

    # ---------------
    # Public API
    # ---------------
    def analyze_market_factors(self, market_factors: MarketFactors, symbol: str, timeframe: str) -> ReasoningResult:
        """Comprehensive market analysis dengan fact-based reasoning"""
        try:
            vr = self._validate_market_data(market_factors)
            if not vr["valid"]:
                return self._create_low_confidence_result("Data validation failed", vr["errors"])

            evidence = self._extract_factual_evidence(market_factors)

            rule_conclusion, rule_conf, rule_chain, rule_warns = self._calculate_rule_based_analysis(market_factors)

            final_conclusion = rule_conclusion
            final_conf = rule_conf
            final_chain = list(rule_chain)
            final_warns = list(rule_warns)

            # Optional AI fusion
            if self.openai_client:
                ai_json = self._perform_ai_enhanced_reasoning(market_factors, evidence, symbol, timeframe)
                if ai_json and ai_json.get("validation_passed"):
                    ai_conf = float(ai_json.get("confidence", 50.0))
                    ai_conc = str(ai_json.get("conclusion", "NEUTRAL")).upper()

                    # Fusion logic (agreement boost, threshold guard)
                    if ai_conc == rule_conclusion:
                        final_conf = min(100.0, (final_conf * 0.6) + (ai_conf * 0.6))  # slight boost
                        final_chain.append(f"AI agrees with rule-based: {ai_conc} ({ai_conf:.1f}%)")
                    else:
                        # If disagreement, weigh by confidence
                        if ai_conf - final_conf >= 10:
                            final_conclusion = ai_conc
                            final_conf = (final_conf * 0.4) + (ai_conf * 0.7)
                            final_chain.append(f"AI overrides due to higher confidence: {ai_conc} ({ai_conf:.1f}%)")
                        else:
                            final_chain.append(f"AI disagrees but keeps rule due to low margin: AI {ai_conc} ({ai_conf:.1f}%)")

                    # Merge AI rationale
                    for s in ai_json.get("supporting_factors", [])[:5]:
                        if s not in evidence:
                            evidence.append(s)
                    for u in ai_json.get("uncertainty_factors", [])[:5]:
                        if u not in final_warns:
                            final_warns.append(u)

            conf_bucket = self._confidence_bucket(final_conf)

            result = ReasoningResult(
                conclusion=final_conclusion,
                confidence=conf_bucket,
                confidence_score=float(final_conf),
                evidence=evidence[:12],
                data_sources=["price", "volume", "indicators", "smc", "structure"],
                reasoning_chain=final_chain[:12],
                uncertainty_factors=final_warns[:8],
                timestamp=time.time(),
            )

            # Ring buffer for history
            self.reasoning_history.append(result)
            if len(self.reasoning_history) > self.history_size:
                self.reasoning_history.pop(0)

            return result

        except Exception as e:
            logger.error(f"Error in market analysis: {e}")
            return self._create_error_result(str(e))

    # ---------------
    # Validation
    # ---------------
    def _validate_market_data(self, mf: MarketFactors) -> Dict[str, Any]:
        errors: List[str] = []
        price = mf.price_data or {}
        for f in ("open", "high", "low", "close", "volume"):
            if f not in price:
                errors.append(f"Missing price field: {f}")
                continue
            v = price[f]
            if not isinstance(v, (int, float)) or (f != "volume" and v < 0) or (f == "volume" and v < 0):
                errors.append(f"Invalid {f}: {v}")

        # Relationship: high >= max(open, close) and low <= min(open, close)
        if all(k in price for k in ("open", "high", "low", "close")):
            if price["high"] < max(price["open"], price["close"]):
                errors.append("High cannot be < max(Open, Close)")
            if price["low"] > min(price["open"], price["close"]):
                errors.append("Low cannot be > min(Open, Close)")
            if price["high"] < price["low"]:
                errors.append("High cannot be < Low")

        indicators = mf.technical_indicators or {}
        # Basic type checks
        for k in ("rsi", "macd", "ema_50", "ema_200", "sma_20", "sma_50"):
            if k in indicators and not isinstance(indicators[k], (int, float)):
                errors.append(f"Indicator {k} not numeric")

        # Clamp RSI bounds if present (0..100)
        if "rsi" in indicators and not (0 <= float(indicators["rsi"]) <= 100):
            errors.append(f"RSI out of bounds: {indicators['rsi']}")

        return {"valid": len(errors) == 0, "errors": errors}

    # ---------------
    # Evidence & Rules
    # ---------------
    def _extract_factual_evidence(self, mf: MarketFactors) -> List[str]:
        ev: List[str] = []
        p = mf.price_data or {}
        ind = mf.technical_indicators or {}
        smc = mf.smc_analysis or {}

        # Price snapshot
        for k in ("open", "high", "low", "close", "volume"):
            if k in p:
                ev.append(f"{k}={p[k]}")

        # Indicators snapshot
        for k in ("rsi", "macd", "ema_50", "ema_200", "sma_20", "sma_50"):
            if k in ind:
                ev.append(f"{k}={ind[k]}")

        # SMC snapshot
        if "trend" in smc:
            ev.append(f"smc_trend={smc['trend']}")
        if "structure" in smc:
            ev.append(f"smc_structure={smc['structure']}")
        if "key_levels" in smc:
            ev.append(f"smc_levels={smc['key_levels']}")

        return ev

    def _calculate_rule_based_analysis(self, mf: MarketFactors) -> Tuple[str, float, List[str], List[str]]:
        """Return (conclusion, confidence_score, reasoning_chain, uncertainty_factors)"""
        p = mf.price_data or {}
        ind = mf.technical_indicators or {}
        smc = mf.smc_analysis or {}
        chain: List[str] = []
        warns: List[str] = []

        close = float(p.get("close", 0.0))
        ema50 = float(ind.get("ema_50", close))
        ema200 = float(ind.get("ema_200", close))
        rsi = self._clamp(float(ind.get("rsi", 50.0)), 0.0, 100.0)
        macd = float(ind.get("macd", 0.0))

        # Trend filter
        bullish_trend = ema50 > ema200 or smc.get("trend", "").lower() == "bullish"
        bearish_trend = ema50 < ema200 or smc.get("trend", "").lower() == "bearish"

        conf = 50.0
        conc = "NEUTRAL"

        if bullish_trend and 45 <= rsi <= 65 and macd >= 0:
            conc = "BUY"
            conf += 15
            chain.append("Trend bullish (EMA50>EMA200/SMC), RSI sehat 45-65, MACD ≥ 0")

        if bearish_trend and (rsi >= 65 or macd < 0):
            conc = "SELL"
            conf += 15
            chain.append("Trend bearish, RSI tinggi atau MACD < 0")

        # SMC key levels confluence
        if isinstance(smc.get("key_levels"), dict):
            levels = smc["key_levels"]
            brk = levels.get("breakout") or levels.get("bo")
            sup = levels.get("support")
            res = levels.get("resistance")
            if conc == "BUY" and brk:
                conf += 5
                chain.append("BUY confluence: breakout level detected")
            if conc == "SELL" and res:
                conf += 5
                chain.append("SELL confluence: near resistance")

        # Normalize confidence
        conf = self._clamp(conf, 0.0, 100.0)

        # Basic uncertainty factors
        if 40 <= rsi <= 60 and conc != "NEUTRAL":
            warns.append("RSI dekat tengah → momentum bisa lemah")
        if abs(ema50 - ema200) / (abs(ema200) + 1e-9) < 0.01:
            warns.append("EMA50 dan EMA200 sangat dekat → trend belum kuat")

        return conc, conf, chain, warns

    # ---------------
    # AI (Optional)
    # ---------------
    def _perform_ai_enhanced_reasoning(self, mf: MarketFactors, evidence: List[str], symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        try:
            if not self.openai_client:
                return None

            # Compact context to save tokens
            ctx = self._prepare_ai_context_compact(mf, evidence, symbol, timeframe)

            sys_msg = "You are a factual crypto analyst. Only analyze provided data, never assume."
            user_msg = (
                "Analyze the following FACTUAL data and return strict JSON with keys: "
                "conclusion ∈ {BUY,SELL,NEUTRAL}, confidence(0-100), supporting_factors[], uncertainty_factors[], summary_indonesian.\n\n"
                f"{json.dumps(ctx, ensure_ascii=False)}"
            )

            resp = self._call_openai_safe([
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg},
            ], max_attempts=3)

            if not resp:
                return None

            try:
                raw = resp.choices[0].message.content if hasattr(resp, "choices") else None
                ai_json = json.loads(raw) if raw else {}
            except Exception as e:
                logger.warning(f"AI JSON parse failed: {e}")
                return None

            return self._validate_ai_response(ai_json)
        except Exception as e:
            logger.warning(f"AI reasoning error: {e}")
            return None

    def _validate_ai_response(self, ai: Dict[str, Any]) -> Dict[str, Any]:
        out = {
            "conclusion": "NEUTRAL",
            "confidence": 50.0,
            "supporting_factors": [],
            "uncertainty_factors": [],
            "summary_indonesian": "Analisis terbatas karena data terbatas.",
            "validation_passed": False,
        }
        try:
            conc = str(ai.get("conclusion", "NEUTRAL")).upper().strip()
            if conc not in {"BUY", "SELL", "NEUTRAL"}:
                conc = "NEUTRAL"
            out["conclusion"] = conc

            conf = float(ai.get("confidence", 50.0))
            out["confidence"] = self._clamp(conf, 0.0, 100.0)

            s = ai.get("supporting_factors", [])
            u = ai.get("uncertainty_factors", [])
            if isinstance(s, list):
                out["supporting_factors"] = [str(x) for x in s][:10]
            if isinstance(u, list):
                out["uncertainty_factors"] = [str(x) for x in u][:10]

            summ = ai.get("summary_indonesian") or ai.get("summary") or ""
            out["summary_indonesian"] = str(summ)[:800] if summ else out["summary_indonesian"]

            out["validation_passed"] = True
        except Exception as e:
            logger.warning(f"AI response normalization failed: {e}")
        return out

    # ---------------
    # Utilities
    # ---------------
    def _confidence_bucket(self, score: float) -> ReasoningConfidence:
        s = float(score)
        if s >= 85: return ReasoningConfidence.VERY_HIGH
        if s >= 70: return ReasoningConfidence.HIGH
        if s >= 55: return ReasoningConfidence.MEDIUM
        if s >= 40: return ReasoningConfidence.LOW
        return ReasoningConfidence.VERY_LOW

    def _clamp(self, x: float, lo: float, hi: float) -> float:
        try:
            return max(lo, min(hi, float(x)))
        except Exception:
            return lo

    def _prepare_ai_context_compact(self, mf: MarketFactors, evidence: List[str], symbol: str, timeframe: str) -> Dict[str, Any]:
        def subset(d: Dict[str, Any], keep: Tuple[str, ...]) -> Dict[str, Any]:
            return {k: d.get(k) for k in keep if isinstance(d, dict) and k in d}

        price = subset(mf.price_data or {}, ("open", "high", "low", "close", "volume"))
        ind = {k: (mf.technical_indicators or {}).get(k) for k in ("rsi", "macd", "ema_50", "ema_200", "sma_20", "sma_50") if k in (mf.technical_indicators or {})}

        smc = {}
        if isinstance(mf.smc_analysis, dict):
            for k in ("trend", "structure", "key_levels"):
                if k in mf.smc_analysis:
                    smc[k] = mf.smc_analysis[k]

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "price": price,
            "indicators": ind,
            "smc": smc,
            "evidence": evidence[:12],
        }

    def _call_openai_safe(self, messages: List[Dict[str, str]], max_attempts: int = 3):
        if not self.openai_client:
            return None
        delay = 0.6
        for attempt in range(1, max_attempts + 1):
            try:
                return self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=800,
                    temperature=0.1,
                    response_format={"type": "json_object"},
                    timeout=20.0,
                )
            except Exception as e:
                logger.warning(f"OpenAI attempt {attempt} failed: {e}")
                time.sleep(delay)
                delay *= 1.7
        return None

    # ---------------
    # Result helpers
    # ---------------
    def _create_low_confidence_result(self, reason: str, errors: List[str]) -> ReasoningResult:
        return ReasoningResult(
            conclusion="NEUTRAL",
            confidence=ReasoningConfidence.LOW,
            confidence_score=35.0,
            evidence=[f"validation_error: {e}" for e in (errors or [])][:8],
            data_sources=[],
            reasoning_chain=[f"Validation failed: {reason}"],
            uncertainty_factors=["Data quality low"],
            timestamp=time.time(),
        )

    def _create_error_result(self, reason: str) -> ReasoningResult:
        return ReasoningResult(
            conclusion="NEUTRAL",
            confidence=ReasoningConfidence.VERY_LOW,
            confidence_score=20.0,
            evidence=[],
            data_sources=[],
            reasoning_chain=[f"Engine error: {reason}"],
            uncertainty_factors=["Exception raised during analysis"],
            timestamp=time.time(),
        )

    # ---------------
    # Diagnostics
    # ---------------
    def diagnostics(self) -> Dict[str, Any]:
        n = len(self.reasoning_history)
        if n == 0:
            return {
                "total": 0,
                "openai_enabled": bool(self.openai_client),
                "confidence_threshold": self.confidence_threshold,
                "notes": "No history yet",
            }
        den = float(n)
        hi = sum(1 for r in self.reasoning_history if r.confidence_score >= 75.0)
        lo = sum(1 for r in self.reasoning_history if r.confidence_score < 40.0)
        return {
            "total": n,
            "openai_enabled": bool(self.openai_client),
            "confidence_threshold": self.confidence_threshold,
            "high_confidence_rate_pct": round(100.0 * hi / den, 2),
            "low_confidence_rate_pct": round(100.0 * lo / den, 2),
            "last_conclusion": self.reasoning_history[-1].conclusion,
            "last_confidence": self.reasoning_history[-1].confidence_score,
        }


# =============================
# Global instance & getter
# =============================
enhanced_reasoning_engine = EnhancedReasoningEngine()

def get_enhanced_reasoning_engine() -> EnhancedReasoningEngine:
    return enhanced_reasoning_engine
