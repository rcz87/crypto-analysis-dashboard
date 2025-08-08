"""
Prompt Injection Defense System - Mitigasi kerentanan LLM
Implementasi multi-layer defense untuk melindungi dari prompt injection attacks
"""

import logging
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Level ancaman prompt injection"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class InjectionDetectionResult:
    """Hasil deteksi prompt injection"""
    is_safe: bool
    threat_level: ThreatLevel
    confidence: float
    detected_patterns: List[str]
    sanitized_input: str
    risk_factors: List[str]
    metadata: Dict[str, Any]

class PromptInjectionDefense:
    """
    Multi-layer defense system untuk prompt injection
    Implementasi Secure Planner, Dynamic Validator, dan Injection Isolator
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.detection_history = []
        self.known_patterns = {}
        
        # Injection patterns yang dikenal (enhanced detection)
        self.injection_patterns = {
            'direct_commands': [
                r'ignore\s+(?:previous|all|above|prior)\s+(?:instructions|prompts|rules|commands)',
                r'forget\s+(?:everything|all|previous|prior|above)',
                r'start\s+(?:over|again|fresh|new)',
                r'new\s+(?:instructions|task|role|persona|mode)',
                r'disregard\s+(?:previous|above|all|prior)',
                r'override\s+(?:previous|system|default|all)',
                r'act\s+as\s+(?:if|though|a|an)',
                r'pretend\s+(?:you|to)\s+(?:are|be)',
                r'roleplay\s+as',
                r'simulate\s+(?:a|an|being)',
                r'behave\s+(?:as|like)',
                r'now\s+you\s+(?:are|will|must)',
            ],
            'system_manipulation': [
                r'system\s*:\s*',
                r'assistant\s*:\s*',
                r'user\s*:\s*',
                r'\[SYSTEM\]',
                r'\[ASSISTANT\]',
                r'\[USER\]',
                r'<\|system\|>',
                r'<\|assistant\|>',
                r'<\|user\|>',
                r'###\s*(?:System|Assistant|User)',
            ],
            'data_extraction': [
                r'show\s+(?:me\s+)?(?:your|the)\s+(?:instructions|prompt|system|rules|original)',
                r'what\s+(?:are\s+)?(?:your|the)\s+(?:instructions|rules|guidelines|original)',
                r'reveal\s+(?:your|the)\s+(?:prompt|instructions|system|original)',
                r'display\s+(?:your|the)\s+(?:prompt|instructions|original)',
                r'print\s+(?:your|the)\s+(?:prompt|instructions|system|original)',
                r'output\s+(?:your|the)\s+(?:prompt|instructions|original)',
                r'tell\s+me\s+(?:your|the)\s+(?:prompt|instructions|rules|original)',
                r'(?:your|the)\s+(?:original|initial)\s+(?:instructions|prompt|system)',
                r'share\s+(?:your|the)\s+(?:prompt|instructions|system)',
            ],
            'jailbreak_attempts': [
                r'developer\s+mode',
                r'god\s+mode',
                r'admin\s+mode',
                r'debug\s+mode',
                r'maintenance\s+mode',
                r'unrestricted\s+mode',
                r'bypass\s+(?:safety|restrictions|filters)',
                r'disable\s+(?:safety|restrictions|filters|guidelines)',
                r'turn\s+off\s+(?:safety|restrictions|filters)',
                r'remove\s+(?:safety|restrictions|limitations)',
            ],
            'encoding_tricks': [
                r'base64',
                r'hex\s+encoded',
                r'url\s+encoded',
                r'rot13',
                r'caesar\s+cipher',
                r'reverse\s+(?:the|this)\s+(?:string|text)',
                r'decode\s+(?:this|the)',
                r'&#\d+;',  # HTML entities
                r'%[0-9A-Fa-f]{2}',  # URL encoding
            ],
            'context_switching': [
                r'meanwhile\s+in\s+(?:another|a\s+different)',
                r'in\s+(?:another|a\s+different)\s+(?:conversation|context|scenario)',
                r'switch\s+(?:context|mode|role)',
                r'change\s+(?:context|mode|role|topic)',
                r'now\s+(?:switch|change)\s+to',
                r'continuing\s+(?:from|where)',
                r'going\s+back\s+to',
            ]
        }
        
        # Whitelist patterns untuk legitimate requests
        self.whitelist_patterns = [
            r'analyze\s+(?:this\s+)?(?:crypto|market|trading)',
            r'generate\s+(?:a\s+)?(?:signal|analysis|report)',
            r'show\s+(?:me\s+)?(?:price|market|trading)\s+data',
            r'what\s+is\s+the\s+(?:price|trend|signal)',
            r'help\s+(?:me\s+)?(?:with\s+)?(?:trading|analysis)',
        ]
        
        # Security configuration
        self.security_config = {
            'max_input_length': 2000,
            'max_repeated_chars': 10,
            'suspicious_char_threshold': 0.15,
            'injection_confidence_threshold': 0.7,
            'auto_sanitize': True,
            'log_all_attempts': True
        }
        
        logger.info("🛡️ Prompt Injection Defense System initialized")
    
    def analyze_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> InjectionDetectionResult:
        """
        Analisis comprehensive input untuk deteksi prompt injection
        """
        try:
            risk_factors = []
            detected_patterns = []
            threat_score = 0.0
            
            # 1. Basic input validation
            basic_issues = self._validate_basic_input(user_input)
            if basic_issues:
                risk_factors.extend(basic_issues)
                threat_score += 0.2
            
            # 2. Pattern matching untuk injection attempts
            pattern_results = self._detect_injection_patterns(user_input)
            detected_patterns.extend(pattern_results['patterns'])
            threat_score += pattern_results['score']
            
            # 3. Context analysis
            if context:
                context_score = self._analyze_context_manipulation(user_input, context)
                threat_score += context_score
                if context_score > 0:
                    risk_factors.append("Context manipulation detected")
            
            # 4. Encoding/obfuscation detection
            encoding_score = self._detect_encoding_tricks(user_input)
            threat_score += encoding_score
            if encoding_score > 0:
                risk_factors.append("Encoding obfuscation detected")
            
            # 5. Statistical analysis
            stats_score = self._statistical_analysis(user_input)
            threat_score += stats_score
            if stats_score > 0:
                risk_factors.append("Statistical anomalies detected")
            
            # 6. Whitelist check
            is_whitelisted = self._check_whitelist(user_input)
            if is_whitelisted:
                threat_score *= 0.5  # Reduce threat score for whitelisted patterns
                risk_factors.append("Contains whitelisted patterns")
            
            # Normalize threat score
            threat_score = min(threat_score, 1.0)
            
            # Determine threat level
            threat_level = self._determine_threat_level(threat_score)
            is_safe = threat_level in [ThreatLevel.SAFE, ThreatLevel.LOW]
            
            # Sanitize input if needed
            sanitized_input = self._sanitize_input(user_input, detected_patterns) if self.security_config['auto_sanitize'] else user_input
            
            result = InjectionDetectionResult(
                is_safe=is_safe,
                threat_level=threat_level,
                confidence=threat_score,
                detected_patterns=detected_patterns,
                sanitized_input=sanitized_input,
                risk_factors=risk_factors,
                metadata={
                    'analysis_timestamp': datetime.now().isoformat(),
                    'input_length': len(user_input),
                    'input_hash': hashlib.md5(user_input.encode()).hexdigest()[:8],
                    'whitelist_match': is_whitelisted
                }
            )
            
            # Log hasil analisis
            self._log_analysis_result(result, user_input)
            self.detection_history.append(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing input: {e}")
            return InjectionDetectionResult(
                is_safe=False,
                threat_level=ThreatLevel.CRITICAL,
                confidence=1.0,
                detected_patterns=['Analysis error'],
                sanitized_input="",
                risk_factors=[f"Analysis error: {str(e)}"],
                metadata={'error': str(e)}
            )
    
    def _validate_basic_input(self, user_input: str) -> List[str]:
        """
        Validasi basic input untuk red flags
        """
        issues = []
        
        try:
            # Length check
            if len(user_input) > self.security_config['max_input_length']:
                issues.append(f"Input too long: {len(user_input)} chars")
            
            # Repeated character check
            for char in set(user_input):
                count = user_input.count(char)
                if count > self.security_config['max_repeated_chars'] and char not in ' \n\t':
                    issues.append(f"Excessive repeated character: '{char}' ({count} times)")
            
            # Suspicious character ratio
            suspicious_chars = sum(1 for c in user_input if ord(c) > 127 or c in '<>[]{}|\\')
            suspicious_ratio = suspicious_chars / len(user_input) if user_input else 0
            if suspicious_ratio > self.security_config['suspicious_char_threshold']:
                issues.append(f"High suspicious character ratio: {suspicious_ratio:.2%}")
            
            # Multiple line breaks (potential formatting manipulation)
            line_breaks = user_input.count('\n')
            if line_breaks > 10:
                issues.append(f"Excessive line breaks: {line_breaks}")
            
            return issues
            
        except Exception as e:
            return [f"Basic validation error: {str(e)}"]
    
    def _detect_injection_patterns(self, user_input: str) -> Dict[str, Any]:
        """
        Deteksi patterns injection menggunakan regex
        """
        detected_patterns = []
        total_score = 0.0
        
        try:
            input_lower = user_input.lower()
            
            for category, patterns in self.injection_patterns.items():
                category_score = 0.0
                category_matches = []
                
                for pattern in patterns:
                    matches = re.findall(pattern, input_lower, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        match_score = len(matches) * 0.3  # Increased from 0.1 to 0.3
                        category_score += match_score
                        category_matches.extend(matches)
                        detected_patterns.append(f"{category}: {pattern}")
                    
                    # Also check with word boundaries for better detection
                    if re.search(r'\b' + pattern + r'\b', input_lower, re.IGNORECASE):
                        category_score += 0.2
                
                # Weight by category (increased for better detection)
                category_weights = {
                    'direct_commands': 1.0,
                    'system_manipulation': 1.0,
                    'data_extraction': 0.9,
                    'jailbreak_attempts': 1.0,
                    'encoding_tricks': 0.8,
                    'context_switching': 0.7
                }
                
                weight = category_weights.get(category, 0.5)
                total_score += category_score * weight
            
            return {
                'patterns': detected_patterns,
                'score': min(total_score, 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {'patterns': [], 'score': 0.0}
    
    def _analyze_context_manipulation(self, user_input: str, context: Dict[str, Any]) -> float:
        """
        Analisis context manipulation attempts
        """
        try:
            manipulation_score = 0.0
            
            # Check for attempts to change role/context
            role_changes = [
                'you are now',
                'your new role',
                'from now on',
                'starting now',
                'beginning immediately',
                'effective immediately'
            ]
            
            input_lower = user_input.lower()
            for phrase in role_changes:
                if phrase in input_lower:
                    manipulation_score += 0.3
            
            # Check for context boundary violations
            context_violations = [
                'outside of this conversation',
                'in reality',
                'in the real world',
                'actually',
                'in truth',
                'honestly',
                'secretly'
            ]
            
            for violation in context_violations:
                if violation in input_lower:
                    manipulation_score += 0.2
            
            # Check for contradictory instructions
            contradictions = [
                'but actually',
                'however',
                'on second thought',
                'wait no',
                'actually do',
                'instead do'
            ]
            
            for contradiction in contradictions:
                if contradiction in input_lower:
                    manipulation_score += 0.15
            
            return min(manipulation_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error analyzing context manipulation: {e}")
            return 0.0
    
    def _detect_encoding_tricks(self, user_input: str) -> float:
        """
        Deteksi encoding/obfuscation tricks
        """
        try:
            encoding_score = 0.0
            
            # Base64 detection
            base64_pattern = r'[A-Za-z0-9+/]{4,}={0,2}'
            base64_matches = re.findall(base64_pattern, user_input)
            if base64_matches:
                encoding_score += 0.3
            
            # Hex encoding detection
            hex_pattern = r'(?:0x|\\x)[0-9A-Fa-f]{2,}'
            hex_matches = re.findall(hex_pattern, user_input)
            if hex_matches:
                encoding_score += 0.25
            
            # Unicode escape sequences
            unicode_pattern = r'\\u[0-9A-Fa-f]{4}'
            unicode_matches = re.findall(unicode_pattern, user_input)
            if unicode_matches:
                encoding_score += 0.2
            
            # HTML entities
            html_entity_pattern = r'&#\d+;|&[a-zA-Z]+;'
            html_matches = re.findall(html_entity_pattern, user_input)
            if html_matches:
                encoding_score += 0.2
            
            # URL encoding
            url_encoding_pattern = r'%[0-9A-Fa-f]{2}'
            url_matches = re.findall(url_encoding_pattern, user_input)
            if url_matches:
                encoding_score += 0.2
            
            return min(encoding_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error detecting encoding tricks: {e}")
            return 0.0
    
    def _statistical_analysis(self, user_input: str) -> float:
        """
        Statistical analysis untuk anomaly detection
        """
        try:
            anomaly_score = 0.0
            
            if not user_input:
                return 0.0
            
            # Character frequency analysis
            char_freq = {}
            for char in user_input.lower():
                char_freq[char] = char_freq.get(char, 0) + 1
            
            # Check for unusual character distributions
            total_chars = len(user_input)
            for char, freq in char_freq.items():
                char_ratio = freq / total_chars
                
                # Very high frequency of single character (except spaces)
                if char_ratio > 0.3 and char not in ' \n\t':
                    anomaly_score += 0.2
                
                # Suspicious characters
                if char in '<>{}[]|\\`~' and char_ratio > 0.05:
                    anomaly_score += 0.15
            
            # Word length analysis
            words = user_input.split()
            if words:
                avg_word_length = sum(len(word) for word in words) / len(words)
                
                # Extremely long or short average word length
                if avg_word_length > 15 or avg_word_length < 2:
                    anomaly_score += 0.1
            
            # Punctuation density
            punctuation = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
            punct_count = sum(1 for char in user_input if char in punctuation)
            punct_ratio = punct_count / total_chars
            
            if punct_ratio > 0.3:  # High punctuation density
                anomaly_score += 0.15
            
            return min(anomaly_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error in statistical analysis: {e}")
            return 0.0
    
    def _check_whitelist(self, user_input: str) -> bool:
        """
        Check jika input mengandung whitelisted patterns
        """
        try:
            input_lower = user_input.lower()
            
            for pattern in self.whitelist_patterns:
                if re.search(pattern, input_lower, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking whitelist: {e}")
            return False
    
    def _determine_threat_level(self, threat_score: float) -> ThreatLevel:
        """
        Determine threat level berdasarkan score
        """
        if threat_score < 0.2:
            return ThreatLevel.SAFE
        elif threat_score < 0.4:
            return ThreatLevel.LOW
        elif threat_score < 0.6:
            return ThreatLevel.MEDIUM
        elif threat_score < 0.8:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL
    
    def _sanitize_input(self, user_input: str, detected_patterns: List[str]) -> str:
        """
        Sanitize input untuk menghilangkan injection attempts
        """
        try:
            sanitized = user_input
            
            # Remove detected injection patterns
            for category, patterns in self.injection_patterns.items():
                for pattern in patterns:
                    sanitized = re.sub(pattern, '[FILTERED]', sanitized, flags=re.IGNORECASE | re.MULTILINE)
            
            # Remove suspicious encodings
            sanitized = re.sub(r'[A-Za-z0-9+/]{20,}={0,2}', '[BASE64_FILTERED]', sanitized)
            sanitized = re.sub(r'(?:0x|\\x)[0-9A-Fa-f]{2,}', '[HEX_FILTERED]', sanitized)
            sanitized = re.sub(r'\\u[0-9A-Fa-f]{4}', '[UNICODE_FILTERED]', sanitized)
            
            # Remove excessive special characters
            sanitized = re.sub(r'[<>{}[\]|\\`~]{2,}', '[SPECIAL_CHARS_FILTERED]', sanitized)
            
            # Limit length
            if len(sanitized) > self.security_config['max_input_length']:
                sanitized = sanitized[:self.security_config['max_input_length']] + '[TRUNCATED]'
            
            return sanitized.strip()
            
        except Exception as e:
            logger.error(f"Error sanitizing input: {e}")
            return "[SANITIZATION_ERROR]"
    
    def _log_analysis_result(self, result: InjectionDetectionResult, original_input: str):
        """
        Log hasil analisis untuk monitoring
        """
        try:
            if self.security_config['log_all_attempts'] or result.threat_level != ThreatLevel.SAFE:
                log_data = {
                    'timestamp': result.metadata['analysis_timestamp'],
                    'threat_level': result.threat_level.value,
                    'confidence': result.confidence,
                    'patterns_detected': len(result.detected_patterns),
                    'input_hash': result.metadata['input_hash'],
                    'is_safe': result.is_safe
                }
                
                if result.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                    logger.warning(f"🚨 HIGH THREAT DETECTED: {log_data}")
                elif result.threat_level == ThreatLevel.MEDIUM:
                    logger.info(f"⚠️ MEDIUM THREAT: {log_data}")
                else:
                    logger.debug(f"✅ Safe input: {log_data}")
            
        except Exception as e:
            logger.error(f"Error logging analysis result: {e}")
    
    def get_defense_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Analytics untuk defense performance
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_detections = [
                det for det in self.detection_history 
                if datetime.fromisoformat(det.metadata['analysis_timestamp']) > cutoff_date
            ]
            
            if not recent_detections:
                return {'message': 'No detections in the specified period'}
            
            analytics = {
                'total_analyses': len(recent_detections),
                'threat_distribution': {},
                'avg_confidence': np.mean([det.confidence for det in recent_detections]),
                'attack_attempt_rate': 0,
                'top_attack_patterns': {}
            }
            
            # Threat distribution
            threats = [det.threat_level.value for det in recent_detections]
            analytics['threat_distribution'] = {threat: threats.count(threat) for threat in set(threats)}
            
            # Attack attempt rate
            attacks = sum(1 for det in recent_detections if det.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL])
            analytics['attack_attempt_rate'] = attacks / len(recent_detections)
            
            # Top attack patterns
            all_patterns = []
            for det in recent_detections:
                all_patterns.extend(det.detected_patterns)
            
            analytics['top_attack_patterns'] = {
                pattern: all_patterns.count(pattern) 
                for pattern in set(all_patterns)
            }
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating defense analytics: {e}")
            return {'error': str(e)}

# Create singleton instance
prompt_defense = PromptInjectionDefense()