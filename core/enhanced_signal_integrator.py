"""
Enhanced Signal Integrator - Integration antara existing signals dengan Stateful AI Engine
Menghubungkan semua signal generators dengan tracking system
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from core.stateful_signal_helper import (
    track_signal_generation, 
    track_gpt_query,
    log_user_interaction,
    get_signal_analytics_summary
)
from services.state_manager import get_state_manager
from core.redis_manager import redis_manager

logger = logging.getLogger(__name__)


class EnhancedSignalIntegrator:
    """
    Integrator yang menghubungkan existing signal engines dengan Stateful AI Engine
    """
    
    def __init__(self):
        self.state_manager = get_state_manager(redis_manager.redis_client)
        logger.info("🔗 Enhanced Signal Integrator initialized")
    
    def track_signal_from_engine(self, signal_data: Dict[str, Any], 
                               source_engine: str, request_context: Optional[Dict] = None) -> str:
        """
        Track signal yang dihasilkan dari engine manapun
        
        Args:
            signal_data: Data signal yang dihasilkan
            source_engine: Nama engine yang generate (sharp_signal, multi_timeframe, dll)
            request_context: Context dari request
            
        Returns:
            signal_id: Unique identifier untuk signal
        """
        try:
            # Standardize signal data format
            standardized_signal = self._standardize_signal_data(signal_data, source_engine)
            
            # Save ke database
            signal_id = self.state_manager.save_signal_history(standardized_signal, request_context)
            
            # Track generation event
            generation_data = {
                'type': 'SIGNAL_GENERATED',
                'source': source_engine.upper(),
                'data': {'engine': source_engine, 'confidence': signal_data.get('confidence', 0)}
            }
            
            self.state_manager.track_user_interaction(signal_id, generation_data, request_context)
            
            logger.info(f"✅ Signal tracked from {source_engine}: {signal_id}")
            return signal_id
            
        except Exception as e:
            logger.error(f"❌ Failed to track signal from {source_engine}: {e}")
            raise
    
    def track_telegram_interaction(self, signal_id: str, interaction_type: str, 
                                 telegram_data: Dict[str, Any]) -> Optional[str]:
        """
        Track interaction dari Telegram bot
        
        Args:
            signal_id: ID signal yang di-interact
            interaction_type: Type interaction (CLICK, EXECUTE, SHARE)
            telegram_data: Data dari Telegram (chat_id, username, dll)
            
        Returns:
            interaction_id atau None jika gagal
        """
        try:
            interaction_data = {
                'type': interaction_type.upper(),
                'source': 'TELEGRAM',
                'data': telegram_data,
                'user_id': telegram_data.get('chat_id')
            }
            
            interaction_id = self.state_manager.track_user_interaction(
                signal_id, interaction_data
            )
            
            logger.info(f"✅ Telegram interaction tracked: {interaction_id}")
            return interaction_id
            
        except Exception as e:
            logger.error(f"❌ Failed to track Telegram interaction: {e}")
            return None
    
    def track_chatgpt_query(self, endpoint: str, query_data: Dict, 
                          response_data: Dict, processing_time_ms: int) -> Optional[str]:
        """
        Track query dari ChatGPT
        
        Args:
            endpoint: Endpoint yang dipanggil
            query_data: Data query
            response_data: Data response
            processing_time_ms: Waktu processing
            
        Returns:
            query_id atau None jika gagal
        """
        try:
            # Prepare query log data
            query_log_data = {
                'endpoint': endpoint,
                'method': 'POST',
                'params': query_data,
                'user_query': query_data.get('user_query', '')
            }
            
            response_log_data = {
                'status_code': 200,
                'data': response_data,
                'processing_time_ms': processing_time_ms,
                'ai_model': 'GPT-4o',
                'confidence_score': response_data.get('confidence')
            }
            
            query_id = self.state_manager.log_gpt_query(
                query_log_data, response_log_data
            )
            
            logger.info(f"✅ ChatGPT query tracked: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"❌ Failed to track ChatGPT query: {e}")
            return None
    
    def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """
        Get comprehensive analytics untuk dashboard
        
        Returns:
            Dictionary dengan semua analytics data
        """
        try:
            return get_signal_analytics_summary()
        except Exception as e:
            logger.error(f"❌ Failed to get comprehensive analytics: {e}")
            return {}
    
    def _standardize_signal_data(self, signal_data: Dict[str, Any], source_engine: str) -> Dict[str, Any]:
        """
        Standardize signal data dari berbagai engine ke format yang konsisten
        
        Args:
            signal_data: Raw signal data
            source_engine: Source engine name
            
        Returns:
            Standardized signal data
        """
        # Map common field names
        field_mapping = {
            'direction': 'action',
            'signal_type': 'action',
            'type': 'action',
            'signal': 'action'
        }
        
        standardized = {}
        
        # Basic fields
        standardized['symbol'] = signal_data.get('symbol', '').upper()
        standardized['timeframe'] = signal_data.get('timeframe', '1H')
        standardized['confidence'] = float(signal_data.get('confidence', 0.0))
        standardized['entry_price'] = float(signal_data.get('entry_price', 0.0))
        standardized['take_profit'] = signal_data.get('take_profit')
        standardized['stop_loss'] = signal_data.get('stop_loss')
        standardized['risk_reward_ratio'] = signal_data.get('risk_reward_ratio')
        
        # Action/direction mapping
        action = signal_data.get('action')
        if not action:
            for old_field, new_field in field_mapping.items():
                if old_field in signal_data:
                    action = signal_data[old_field]
                    break
        
        standardized['action'] = str(action).upper() if action else 'HOLD'
        
        # AI reasoning
        standardized['ai_reasoning'] = signal_data.get('ai_reasoning', '')
        
        # SMC analysis (jika ada)
        if 'smc_analysis' in signal_data:
            standardized['smc_analysis'] = signal_data['smc_analysis']
        
        # Technical indicators (jika ada)
        if 'technical_indicators' in signal_data:
            standardized['technical_indicators'] = signal_data['technical_indicators']
        
        # Market conditions
        standardized['market_conditions'] = signal_data.get('market_conditions', 'UNKNOWN')
        
        # Source engine info
        standardized['source_engine'] = source_engine
        
        return standardized
    
    def update_signal_performance(self, signal_id: str, outcome: str, 
                                pnl_percentage: Optional[float] = None) -> bool:
        """
        Update performance signal setelah close position
        
        Args:
            signal_id: ID signal
            outcome: WIN, LOSS, BREAKEVEN
            pnl_percentage: Profit/Loss percentage
            
        Returns:
            True jika berhasil update
        """
        try:
            from core.stateful_signal_helper import update_signal_outcome
            return update_signal_outcome(signal_id, outcome, pnl_percentage)
        except Exception as e:
            logger.error(f"❌ Failed to update signal performance: {e}")
            return False
    
    def get_signal_by_id(self, signal_id: str) -> Optional[Dict[str, Any]]:
        """
        Get signal by ID untuk reference
        
        Args:
            signal_id: ID signal
            
        Returns:
            Signal data atau None
        """
        try:
            signals = self.state_manager.get_signal_history(limit=1)
            # Filter by signal_id (simplified implementation)
            for signal in signals:
                if signal.get('signal_id') == signal_id:
                    return signal
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get signal by ID: {e}")
            return None
    
    def cleanup_old_signals(self, days_to_keep: int = 90) -> Dict[str, int]:
        """
        Cleanup signal data yang sudah lama
        
        Args:
            days_to_keep: Jumlah hari data yang dipertahankan
            
        Returns:
            Cleanup result
        """
        try:
            return self.state_manager.cleanup_old_data(days_to_keep)
        except Exception as e:
            logger.error(f"❌ Failed to cleanup old signals: {e}")
            return {}


# Singleton instance
enhanced_integrator = None


def get_enhanced_integrator() -> EnhancedSignalIntegrator:
    """
    Get singleton instance of EnhancedSignalIntegrator
    
    Returns:
        EnhancedSignalIntegrator instance
    """
    global enhanced_integrator
    if enhanced_integrator is None:
        enhanced_integrator = EnhancedSignalIntegrator()
    return enhanced_integrator


# Convenience functions untuk easy integration
def track_signal(signal_data: Dict[str, Any], source_engine: str = 'API') -> str:
    """Convenience function untuk track signal"""
    integrator = get_enhanced_integrator()
    return integrator.track_signal_from_engine(signal_data, source_engine)


def track_telegram_click(signal_id: str, chat_id: str, username: str = None) -> Optional[str]:
    """Convenience function untuk track Telegram click"""
    integrator = get_enhanced_integrator()
    telegram_data = {'chat_id': chat_id, 'username': username}
    return integrator.track_telegram_interaction(signal_id, 'CLICK', telegram_data)


def track_signal_execution(signal_id: str, execution_price: float, source: str = 'MANUAL') -> Optional[str]:
    """Convenience function untuk track signal execution"""
    integrator = get_enhanced_integrator()
    execution_data = {'execution_price': execution_price}
    return integrator.track_telegram_interaction(signal_id, 'EXECUTE', execution_data)


logger.info("🔗 Enhanced Signal Integrator module loaded")