#!/usr/bin/env python3
"""
🧠 GPTs Reasoning Logger - Track AI Decision Making Process
Sistem untuk mencatat dan menganalisis reasoning GPT dalam setiap keputusan
"""

import os
import logging
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import threading
from queue import Queue, Empty

logger = logging.getLogger(__name__)

@dataclass
class GPTReasoningLog:
    """Data class untuk GPT reasoning tracking"""
    reasoning_id: str
    query_id: str
    endpoint: str
    user_query: str
    gpt_model: str
    prompt_template: str
    reasoning_steps: List[Dict[str, Any]]
    final_decision: Dict[str, Any]
    confidence_factors: Dict[str, Any]
    market_context: Dict[str, Any]
    processing_time_ms: float
    token_usage: Dict[str, int]
    created_at: str
    ip_address: Optional[str]
    user_agent: Optional[str]

class GPTReasoningLogger:
    """
    🧠 GPT Reasoning Logger untuk comprehensive AI decision tracking
    
    Features:
    - Track setiap reasoning step dari GPT
    - Analyze decision quality dan consistency
    - Pattern recognition dalam AI decision making
    - Performance monitoring untuk different prompts
    - Audit trail untuk AI transparency
    """
    
    def __init__(self, db_session=None, redis_manager=None):
        """Initialize GPT Reasoning Logger"""
        self.db_session = db_session
        self.redis_manager = redis_manager
        self.reasoning_queue = Queue()
        self.processing_thread = None
        self.is_running = False
        
        # Start background processing
        self._start_background_processor()
        
        logger.info("🧠 GPT Reasoning Logger initialized")
    
    def log_reasoning_process(self, reasoning_data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """
        Log GPT reasoning process dengan detailed tracking
        
        Args:
            reasoning_data: Complete reasoning information
            context: Additional context (user, request info)
            
        Returns:
            reasoning_id: Unique reasoning tracking ID
        """
        try:
            # Generate unique reasoning ID
            reasoning_id = self._generate_reasoning_id(reasoning_data)
            
            # Extract reasoning steps
            reasoning_steps = self._extract_reasoning_steps(reasoning_data)
            
            # Create reasoning log
            reasoning_log = GPTReasoningLog(
                reasoning_id=reasoning_id,
                query_id=reasoning_data.get('query_id', ''),
                endpoint=reasoning_data.get('endpoint', ''),
                user_query=reasoning_data.get('user_query', ''),
                gpt_model=reasoning_data.get('model', 'gpt-4o'),
                prompt_template=reasoning_data.get('prompt_template', ''),
                reasoning_steps=reasoning_steps,
                final_decision=reasoning_data.get('final_decision', {}),
                confidence_factors=reasoning_data.get('confidence_factors', {}),
                market_context=reasoning_data.get('market_context', {}),
                processing_time_ms=reasoning_data.get('processing_time_ms', 0.0),
                token_usage=reasoning_data.get('token_usage', {}),
                created_at=datetime.now(timezone.utc).isoformat(),
                ip_address=context.get('ip_address') if context else None,
                user_agent=context.get('user_agent') if context else None
            )
            
            # Queue for background processing
            self.reasoning_queue.put({
                'type': 'REASONING_LOG',
                'data': reasoning_log,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Immediate cache for quick access
            if self.redis_manager:
                cache_key = f"gpt_reasoning:{reasoning_id}"
                self.redis_manager.set_cache(cache_key, asdict(reasoning_log), expire_seconds=86400)
            
            logger.info(f"🧠 GPT reasoning logged: {reasoning_id} - {reasoning_data.get('endpoint', 'unknown')}")
            return reasoning_id
            
        except Exception as e:
            logger.error(f"Failed to log GPT reasoning: {e}")
            # Emergency backup
            self._emergency_reasoning_log(reasoning_data, str(e))
            raise
    
    def analyze_reasoning_quality(self, reasoning_id: str) -> Dict[str, Any]:
        """
        Analyze quality of GPT reasoning untuk specific decision
        
        Args:
            reasoning_id: ID of reasoning to analyze
            
        Returns:
            analysis: Quality analysis results
        """
        try:
            # Get reasoning data
            reasoning_data = self._get_reasoning_data(reasoning_id)
            if not reasoning_data:
                return {'error': 'Reasoning not found'}
            
            # Perform quality analysis
            analysis = {
                'reasoning_id': reasoning_id,
                'quality_score': self._calculate_quality_score(reasoning_data),
                'consistency_check': self._check_reasoning_consistency(reasoning_data),
                'logical_flow': self._analyze_logical_flow(reasoning_data['reasoning_steps']),
                'confidence_validation': self._validate_confidence_factors(reasoning_data),
                'market_alignment': self._check_market_context_alignment(reasoning_data),
                'improvement_suggestions': self._generate_improvement_suggestions(reasoning_data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze reasoning quality: {e}")
            return {'error': str(e)}
    
    def get_reasoning_patterns(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Identify patterns dalam GPT reasoning over time
        
        Args:
            days_back: Days to look back for pattern analysis
            
        Returns:
            patterns: Identified reasoning patterns
        """
        try:
            if not self.db_session:
                return {'error': 'Database not available'}
            
            from models import GPTQueryLog
            from datetime import timedelta
            
            since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
            
            # Get recent reasoning logs
            logs = self.db_session.query(GPTQueryLog).filter(
                GPTQueryLog.created_at >= since_date
            ).all()
            
            if not logs:
                return {'total_queries': 0, 'period_days': days_back}
            
            # Analyze patterns
            patterns = {
                'total_queries': len(logs),
                'period_days': days_back,
                'endpoint_patterns': self._analyze_endpoint_patterns(logs),
                'confidence_patterns': self._analyze_confidence_patterns(logs),
                'decision_consistency': self._analyze_decision_consistency(logs),
                'performance_trends': self._analyze_performance_trends(logs),
                'common_reasoning_flows': self._identify_common_flows(logs),
                'error_patterns': self._analyze_error_patterns(logs)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Failed to get reasoning patterns: {e}")
            return {'error': str(e)}
    
    def compare_reasoning_approaches(self, approach_a: str, approach_b: str) -> Dict[str, Any]:
        """
        Compare different reasoning approaches untuk A/B testing
        
        Args:
            approach_a: First approach identifier
            approach_b: Second approach identifier
            
        Returns:
            comparison: Detailed comparison results
        """
        try:
            # Get reasoning data for both approaches
            logs_a = self._get_reasoning_by_approach(approach_a)
            logs_b = self._get_reasoning_by_approach(approach_b)
            
            comparison = {
                'approach_a': {
                    'identifier': approach_a,
                    'sample_size': len(logs_a),
                    'avg_quality_score': self._calculate_avg_quality(logs_a),
                    'avg_processing_time': self._calculate_avg_processing_time(logs_a),
                    'success_rate': self._calculate_success_rate(logs_a),
                    'common_patterns': self._extract_common_patterns(logs_a)
                },
                'approach_b': {
                    'identifier': approach_b,
                    'sample_size': len(logs_b),
                    'avg_quality_score': self._calculate_avg_quality(logs_b),
                    'avg_processing_time': self._calculate_avg_processing_time(logs_b),
                    'success_rate': self._calculate_success_rate(logs_b),
                    'common_patterns': self._extract_common_patterns(logs_b)
                },
                'statistical_significance': self._calculate_statistical_significance(logs_a, logs_b),
                'recommendation': self._generate_approach_recommendation(logs_a, logs_b)
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare reasoning approaches: {e}")
            return {'error': str(e)}
    
    def get_reasoning_insights(self, symbol: str = None, timeframe: str = None) -> Dict[str, Any]:
        """Get insights tentang GPT reasoning untuk specific conditions"""
        try:
            # Build filter conditions
            filters = {}
            if symbol:
                filters['symbol'] = symbol.upper()
            if timeframe:
                filters['timeframe'] = timeframe
            
            # Get relevant reasoning logs
            reasoning_logs = self._get_filtered_reasoning_logs(filters)
            
            if not reasoning_logs:
                return {'message': 'No reasoning logs found for specified criteria'}
            
            insights = {
                'total_logs': len(reasoning_logs),
                'filters_applied': filters,
                'reasoning_quality': {
                    'avg_quality_score': self._calculate_avg_quality(reasoning_logs),
                    'quality_distribution': self._analyze_quality_distribution(reasoning_logs),
                    'top_quality_factors': self._identify_top_quality_factors(reasoning_logs)
                },
                'decision_patterns': {
                    'most_common_decisions': self._analyze_decision_frequency(reasoning_logs),
                    'confidence_correlation': self._analyze_confidence_correlation(reasoning_logs),
                    'market_condition_impact': self._analyze_market_impact(reasoning_logs)
                },
                'performance_metrics': {
                    'avg_processing_time': self._calculate_avg_processing_time(reasoning_logs),
                    'token_efficiency': self._analyze_token_efficiency(reasoning_logs),
                    'consistency_score': self._calculate_consistency_score(reasoning_logs)
                },
                'improvement_opportunities': self._identify_improvement_opportunities(reasoning_logs)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get reasoning insights: {e}")
            return {'error': str(e)}
    
    def _start_background_processor(self):
        """Start background thread untuk processing reasoning logs"""
        if self.processing_thread and self.processing_thread.is_alive():
            return
        
        self.is_running = True
        self.processing_thread = threading.Thread(target=self._process_reasoning_queue, daemon=True)
        self.processing_thread.start()
        logger.info("🧠 Background reasoning processor started")
    
    def _process_reasoning_queue(self):
        """Background processor untuk reasoning queue"""
        while self.is_running:
            try:
                # Get item from queue dengan timeout
                item = self.reasoning_queue.get(timeout=1.0)
                
                if item['type'] == 'REASONING_LOG':
                    self._save_reasoning_to_db(item['data'])
                
                self.reasoning_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing reasoning queue: {e}")
    
    def _save_reasoning_to_db(self, reasoning_log: GPTReasoningLog):
        """Save reasoning log to database"""
        if not self.db_session:
            return
        
        try:
            from models import GPTQueryLog
            
            # Convert to database model
            query_log = GPTQueryLog(
                query_id=reasoning_log.reasoning_id,
                endpoint=reasoning_log.endpoint,
                user_query=reasoning_log.user_query,
                response_data=json.dumps({
                    'reasoning_steps': reasoning_log.reasoning_steps,
                    'final_decision': reasoning_log.final_decision,
                    'confidence_factors': reasoning_log.confidence_factors
                }),
                processing_time_ms=reasoning_log.processing_time_ms,
                tokens_used=reasoning_log.token_usage.get('total', 0),
                prompt_tokens=reasoning_log.token_usage.get('prompt', 0),
                completion_tokens=reasoning_log.token_usage.get('completion', 0),
                model_used=reasoning_log.gpt_model,
                user_agent=reasoning_log.user_agent,
                ip_address=reasoning_log.ip_address
            )
            
            self.db_session.add(query_log)
            self.db_session.commit()
            
            logger.debug(f"🧠 Reasoning saved to database: {reasoning_log.reasoning_id}")
            
        except Exception as e:
            logger.error(f"Failed to save reasoning to database: {e}")
            if self.db_session:
                self.db_session.rollback()
    
    def _generate_reasoning_id(self, reasoning_data: Dict[str, Any]) -> str:
        """Generate unique reasoning ID"""
        data_str = f"{reasoning_data.get('endpoint', '')}{reasoning_data.get('user_query', '')}{datetime.now(timezone.utc).isoformat()}"
        hash_obj = hashlib.md5(data_str.encode())
        return f"RSN_{hash_obj.hexdigest()[:12].upper()}"
    
    def _extract_reasoning_steps(self, reasoning_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract structured reasoning steps dari GPT response"""
        raw_reasoning = reasoning_data.get('ai_reasoning', '')
        
        # Parse reasoning steps (this would be more sophisticated in practice)
        steps = []
        
        # Look for numbered steps or bullet points
        lines = raw_reasoning.split('\n')
        current_step = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for step indicators
            if any(line.startswith(prefix) for prefix in ['1.', '2.', '3.', '•', '-', '*']):
                if current_step:
                    steps.append(current_step)
                
                current_step = {
                    'step_number': len(steps) + 1,
                    'description': line,
                    'type': self._classify_reasoning_step(line),
                    'confidence_keywords': self._extract_confidence_keywords(line)
                }
            elif current_step:
                current_step['description'] += ' ' + line
        
        if current_step:
            steps.append(current_step)
        
        return steps
    
    def _classify_reasoning_step(self, step_text: str) -> str:
        """Classify type of reasoning step"""
        step_lower = step_text.lower()
        
        if any(keyword in step_lower for keyword in ['technical', 'indicator', 'sma', 'rsi', 'macd']):
            return 'TECHNICAL_ANALYSIS'
        elif any(keyword in step_lower for keyword in ['trend', 'breakout', 'support', 'resistance']):
            return 'TREND_ANALYSIS'
        elif any(keyword in step_lower for keyword in ['volume', 'liquidity']):
            return 'VOLUME_ANALYSIS'
        elif any(keyword in step_lower for keyword in ['risk', 'stop', 'loss']):
            return 'RISK_ASSESSMENT'
        elif any(keyword in step_lower for keyword in ['confidence', 'probability']):
            return 'CONFIDENCE_EVALUATION'
        else:
            return 'GENERAL_REASONING'
    
    def _extract_confidence_keywords(self, text: str) -> List[str]:
        """Extract confidence-related keywords"""
        confidence_keywords = [
            'strong', 'weak', 'high', 'low', 'confident', 'uncertain',
            'likely', 'unlikely', 'probable', 'possible', 'confirmed', 'potential'
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in confidence_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_quality_score(self, reasoning_data: Dict[str, Any]) -> float:
        """Calculate quality score untuk reasoning"""
        score = 0.0
        
        # Check for structured reasoning
        reasoning_steps = reasoning_data.get('reasoning_steps', [])
        if len(reasoning_steps) >= 3:
            score += 25  # Good structure
        
        # Check for different types of analysis
        step_types = set(step.get('type', '') for step in reasoning_steps)
        score += len(step_types) * 10  # Diversity bonus
        
        # Check for confidence factors
        confidence_factors = reasoning_data.get('confidence_factors', {})
        if confidence_factors:
            score += 20  # Has confidence assessment
        
        # Check for market context
        market_context = reasoning_data.get('market_context', {})
        if market_context:
            score += 15  # Considers market context
        
        # Processing efficiency
        processing_time = reasoning_data.get('processing_time_ms', 0)
        if processing_time < 5000:  # Under 5 seconds
            score += 10
        
        return min(score, 100.0)  # Cap at 100
    
    def _check_reasoning_consistency(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check consistency dalam reasoning process"""
        consistency_check = {
            'status': 'CONSISTENT',
            'issues': [],
            'score': 100.0
        }
        
        reasoning_steps = reasoning_data.get('reasoning_steps', [])
        final_decision = reasoning_data.get('final_decision', {})
        
        # Check if final decision aligns with reasoning steps
        decision_sentiment = final_decision.get('action', '').upper()
        
        positive_keywords = ['bullish', 'buy', 'long', 'upward', 'positive']
        negative_keywords = ['bearish', 'sell', 'short', 'downward', 'negative']
        
        step_sentiments = []
        for step in reasoning_steps:
            step_text = step.get('description', '').lower()
            if any(keyword in step_text for keyword in positive_keywords):
                step_sentiments.append('POSITIVE')
            elif any(keyword in step_text for keyword in negative_keywords):
                step_sentiments.append('NEGATIVE')
            else:
                step_sentiments.append('NEUTRAL')
        
        # Check consistency
        if decision_sentiment in ['BUY', 'LONG'] and 'NEGATIVE' in step_sentiments:
            consistency_check['issues'].append("Bullish decision with bearish reasoning steps")
            consistency_check['score'] -= 30
        elif decision_sentiment in ['SELL', 'SHORT'] and 'POSITIVE' in step_sentiments:
            consistency_check['issues'].append("Bearish decision with bullish reasoning steps")
            consistency_check['score'] -= 30
        
        if consistency_check['issues']:
            consistency_check['status'] = 'INCONSISTENT'
        
        return consistency_check
    
    def _analyze_logical_flow(self, reasoning_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze logical flow of reasoning steps"""
        flow_analysis = {
            'flow_quality': 'GOOD',
            'step_progression': [],
            'logical_gaps': [],
            'flow_score': 0.0
        }
        
        if not reasoning_steps:
            flow_analysis['flow_quality'] = 'POOR'
            flow_analysis['logical_gaps'].append("No reasoning steps provided")
            return flow_analysis
        
        # Analyze step progression
        for i, step in enumerate(reasoning_steps):
            step_analysis = {
                'step_number': i + 1,
                'type': step.get('type', 'UNKNOWN'),
                'has_supporting_evidence': len(step.get('confidence_keywords', [])) > 0,
                'connects_to_previous': i == 0 or self._check_step_connection(reasoning_steps[i-1], step)
            }
            flow_analysis['step_progression'].append(step_analysis)
        
        # Calculate flow score
        connected_steps = sum(1 for step in flow_analysis['step_progression'] if step['connects_to_previous'])
        evidence_steps = sum(1 for step in flow_analysis['step_progression'] if step['has_supporting_evidence'])
        
        flow_analysis['flow_score'] = ((connected_steps + evidence_steps) / (len(reasoning_steps) * 2)) * 100
        
        if flow_analysis['flow_score'] < 50:
            flow_analysis['flow_quality'] = 'POOR'
        elif flow_analysis['flow_score'] < 75:
            flow_analysis['flow_quality'] = 'FAIR'
        
        return flow_analysis
    
    def _check_step_connection(self, prev_step: Dict[str, Any], current_step: Dict[str, Any]) -> bool:
        """Check if current step logically connects to previous step"""
        # Simple heuristic - check if they're related types or have common keywords
        prev_type = prev_step.get('type', '')
        current_type = current_step.get('type', '')
        
        # Related types
        related_types = {
            'TECHNICAL_ANALYSIS': ['TREND_ANALYSIS', 'VOLUME_ANALYSIS'],
            'TREND_ANALYSIS': ['TECHNICAL_ANALYSIS', 'RISK_ASSESSMENT'],
            'VOLUME_ANALYSIS': ['TECHNICAL_ANALYSIS', 'CONFIDENCE_EVALUATION'],
            'RISK_ASSESSMENT': ['CONFIDENCE_EVALUATION'],
        }
        
        if current_type in related_types.get(prev_type, []):
            return True
        
        # Check for keyword overlap (simplified)
        prev_keywords = set(prev_step.get('confidence_keywords', []))
        current_keywords = set(current_step.get('confidence_keywords', []))
        
        return len(prev_keywords.intersection(current_keywords)) > 0
    
    def _validate_confidence_factors(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate confidence factors dalam reasoning"""
        validation = {
            'status': 'VALID',
            'confidence_score': 0.0,
            'factors_analyzed': 0,
            'issues': []
        }
        
        confidence_factors = reasoning_data.get('confidence_factors', {})
        
        if not confidence_factors:
            validation['status'] = 'MISSING'
            validation['issues'].append("No confidence factors provided")
            return validation
        
        # Analyze each confidence factor
        total_confidence = 0
        valid_factors = 0
        
        for factor, value in confidence_factors.items():
            if isinstance(value, (int, float)) and 0 <= value <= 100:
                total_confidence += value
                valid_factors += 1
            else:
                validation['issues'].append(f"Invalid confidence value for {factor}: {value}")
        
        if valid_factors > 0:
            validation['confidence_score'] = total_confidence / valid_factors
            validation['factors_analyzed'] = valid_factors
        
        if validation['issues']:
            validation['status'] = 'INVALID'
        
        return validation
    
    def _check_market_context_alignment(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if reasoning aligns dengan market context"""
        alignment = {
            'status': 'ALIGNED',
            'context_factors': 0,
            'alignment_score': 0.0,
            'misalignments': []
        }
        
        market_context = reasoning_data.get('market_context', {})
        final_decision = reasoning_data.get('final_decision', {})
        
        if not market_context:
            alignment['status'] = 'NO_CONTEXT'
            return alignment
        
        # Check alignment between market conditions and decision
        market_trend = market_context.get('trend', '').upper()
        decision_action = final_decision.get('action', '').upper()
        
        if market_trend == 'BULLISH' and decision_action in ['SELL', 'SHORT']:
            alignment['misalignments'].append("Bearish decision in bullish market")
        elif market_trend == 'BEARISH' and decision_action in ['BUY', 'LONG']:
            alignment['misalignments'].append("Bullish decision in bearish market")
        
        # Calculate alignment score
        alignment['context_factors'] = len(market_context)
        alignment['alignment_score'] = max(0, 100 - (len(alignment['misalignments']) * 25))
        
        if alignment['misalignments']:
            alignment['status'] = 'MISALIGNED'
        
        return alignment
    
    def _generate_improvement_suggestions(self, reasoning_data: Dict[str, Any]) -> List[str]:
        """Generate suggestions untuk improving reasoning quality"""
        suggestions = []
        
        reasoning_steps = reasoning_data.get('reasoning_steps', [])
        
        # Check structure
        if len(reasoning_steps) < 3:
            suggestions.append("Add more detailed reasoning steps for better analysis")
        
        # Check diversity
        step_types = set(step.get('type', '') for step in reasoning_steps)
        if len(step_types) < 3:
            suggestions.append("Include diverse analysis types (technical, trend, volume, risk)")
        
        # Check confidence factors
        confidence_factors = reasoning_data.get('confidence_factors', {})
        if not confidence_factors:
            suggestions.append("Include confidence factors for better decision transparency")
        
        # Check market context
        market_context = reasoning_data.get('market_context', {})
        if not market_context:
            suggestions.append("Consider market context in reasoning process")
        
        # Check processing efficiency
        processing_time = reasoning_data.get('processing_time_ms', 0)
        if processing_time > 10000:  # Over 10 seconds
            suggestions.append("Optimize reasoning process for better performance")
        
        return suggestions if suggestions else ["Reasoning quality is excellent - no improvements needed"]
    
    def _get_reasoning_data(self, reasoning_id: str) -> Optional[Dict[str, Any]]:
        """Get reasoning data from cache or database"""
        # Try cache first
        if self.redis_manager:
            cache_key = f"gpt_reasoning:{reasoning_id}"
            cached_data = self.redis_manager.get_cache(cache_key)
            if cached_data:
                return cached_data
        
        # Fallback to database
        if self.db_session:
            try:
                from models import GPTQueryLog
                query_log = self.db_session.query(GPTQueryLog).filter_by(query_id=reasoning_id).first()
                if query_log:
                    return {
                        'reasoning_id': query_log.query_id,
                        'endpoint': query_log.endpoint,
                        'user_query': query_log.user_query,
                        'reasoning_steps': json.loads(query_log.response_data or '{}').get('reasoning_steps', []),
                        'final_decision': json.loads(query_log.response_data or '{}').get('final_decision', {}),
                        'confidence_factors': json.loads(query_log.response_data or '{}').get('confidence_factors', {}),
                        'processing_time_ms': query_log.processing_time_ms,
                        'token_usage': {
                            'total': query_log.tokens_used,
                            'prompt': query_log.prompt_tokens,
                            'completion': query_log.completion_tokens
                        }
                    }
            except Exception as e:
                logger.error(f"Database query error: {e}")
        
        return None
    
    def _emergency_reasoning_log(self, reasoning_data: Dict[str, Any], error: str):
        """Emergency logging kalau database fail"""
        try:
            emergency_file = 'logs/emergency_reasoning.log'
            os.makedirs(os.path.dirname(emergency_file), exist_ok=True)
            
            with open(emergency_file, 'a') as f:
                emergency_record = {
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'reasoning_data': reasoning_data,
                    'error': error
                }
                f.write(json.dumps(emergency_record) + '\n')
                
        except Exception as e:
            logger.critical(f"Emergency reasoning logging failed: {e}")
    
    def shutdown(self):
        """Gracefully shutdown background processor"""
        self.is_running = False
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=5.0)
        logger.info("🧠 GPT Reasoning Logger shutdown completed")

# Global logger instance
reasoning_logger = None

def get_reasoning_logger():
    """Get global reasoning logger instance"""
    global reasoning_logger
    if reasoning_logger is None:
        try:
            from models import db
            from core.redis_manager import RedisManager
            
            redis_manager = RedisManager()
            reasoning_logger = GPTReasoningLogger(
                db_session=db.session,
                redis_manager=redis_manager
            )
        except Exception as e:
            logger.error(f"Failed to initialize reasoning logger: {e}")
            reasoning_logger = GPTReasoningLogger()  # Fallback without dependencies
    
    return reasoning_logger

def log_gpt_reasoning(reasoning_data: Dict[str, Any], context: Dict[str, Any] = None) -> str:
    """Convenience function untuk logging GPT reasoning"""
    return get_reasoning_logger().log_reasoning_process(reasoning_data, context)

# Export
__all__ = [
    'GPTReasoningLogger', 'GPTReasoningLog', 'get_reasoning_logger',
    'log_gpt_reasoning'
]