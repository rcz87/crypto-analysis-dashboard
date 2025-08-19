#!/usr/bin/env python3
"""
Enhanced Error Handler - Sistem error handling yang komprehensif dan informatif
"""

import logging
import traceback
import time
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
from flask import request, jsonify, Response
import uuid

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Tingkat severity error"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class ErrorCategory(Enum):
    """Kategori error"""
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    EXTERNAL_API = "external_api"
    PROCESSING = "processing"
    NETWORK = "network"
    SYSTEM = "system"
    UNKNOWN = "unknown"

@dataclass
class ErrorContext:
    """Context information untuk error"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None

@dataclass 
class EnhancedError:
    """Enhanced error structure"""
    error_id: str
    error_code: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    context: ErrorContext
    details: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None
    related_docs: Optional[List[str]] = None
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response"""
        return {
            'error_id': self.error_id,
            'error_code': self.error_code,
            'message': self.message,
            'severity': self.severity.value,
            'category': self.category.value,
            'context': asdict(self.context),
            'details': self.details or {},
            'suggestions': self.suggestions or [],
            'related_docs': self.related_docs or [],
            'timestamp': self.timestamp or datetime.now().isoformat()
        }

class EnhancedErrorHandler:
    """Enhanced error handler dengan comprehensive logging dan user-friendly messages"""
    
    def __init__(self):
        self.error_registry = {}
        self.error_stats = {
            'total_errors': 0,
            'errors_by_category': {},
            'errors_by_severity': {},
            'recent_errors': []
        }
        self._initialize_error_registry()
        
    def _initialize_error_registry(self):
        """Initialize common error definitions"""
        self.error_registry = {
            # Validation Errors
            'INVALID_REQUEST': {
                'message': 'Request data tidak valid atau tidak lengkap',
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.VALIDATION,
                'suggestions': [
                    'Periksa format request body',
                    'Pastikan semua field required ada',
                    'Validasi tipe data setiap field'
                ]
            },
            'MISSING_PARAMETER': {
                'message': 'Parameter required tidak ditemukan',
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.VALIDATION,
                'suggestions': [
                    'Periksa dokumentasi API untuk parameter required',
                    'Pastikan parameter dikirim dalam format yang benar'
                ]
            },
            
            # Data Access Errors
            'DATA_FETCH_FAILED': {
                'message': 'Gagal mengambil data dari sumber eksternal',
                'severity': ErrorSeverity.HIGH,
                'category': ErrorCategory.DATA_ACCESS,
                'suggestions': [
                    'Coba lagi dalam beberapa saat',
                    'Periksa koneksi internet',
                    'Verifikasi API key dan kredensial'
                ]
            },
            'DATABASE_ERROR': {
                'message': 'Terjadi kesalahan pada database',
                'severity': ErrorSeverity.CRITICAL,
                'category': ErrorCategory.SYSTEM,
                'suggestions': [
                    'Tim teknis telah diberitahu',
                    'Coba lagi dalam beberapa menit'
                ]
            },
            
            # Processing Errors
            'AI_ANALYSIS_FAILED': {
                'message': 'Analisis AI gagal diproses',
                'severity': ErrorSeverity.HIGH,
                'category': ErrorCategory.PROCESSING,
                'suggestions': [
                    'Coba dengan data yang lebih sederhana',
                    'Periksa apakah semua parameter valid',
                    'Hubungi support jika masalah berlanjut'
                ]
            },
            'CALCULATION_ERROR': {
                'message': 'Terjadi kesalahan dalam perhitungan',
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.PROCESSING,
                'suggestions': [
                    'Periksa data input untuk nilai yang tidak valid',
                    'Pastikan rentang nilai dalam batas normal'
                ]
            },
            
            # External API Errors
            'EXTERNAL_API_TIMEOUT': {
                'message': 'Timeout saat mengakses layanan eksternal',
                'severity': ErrorSeverity.HIGH,
                'category': ErrorCategory.EXTERNAL_API,
                'suggestions': [
                    'Coba lagi dalam beberapa saat',
                    'Layanan eksternal mungkin sedang sibuk'
                ]
            },
            'API_RATE_LIMITED': {
                'message': 'Rate limit tercapai untuk API eksternal',
                'severity': ErrorSeverity.MEDIUM,
                'category': ErrorCategory.EXTERNAL_API,
                'suggestions': [
                    'Tunggu beberapa menit sebelum mencoba lagi',
                    'Kurangi frekuensi request'
                ]
            },
            
            # System Errors
            'SYSTEM_OVERLOAD': {
                'message': 'Sistem sedang mengalami beban tinggi',
                'severity': ErrorSeverity.HIGH,
                'category': ErrorCategory.SYSTEM,
                'suggestions': [
                    'Coba lagi dalam beberapa menit',
                    'Gunakan fitur cache jika tersedia'
                ]
            },
            'SERVICE_UNAVAILABLE': {
                'message': 'Layanan sementara tidak tersedia',
                'severity': ErrorSeverity.CRITICAL,
                'category': ErrorCategory.SYSTEM,
                'suggestions': [
                    'Tim teknis sedang menangani masalah ini',
                    'Coba lagi dalam 10-15 menit'
                ]
            }
        }
    
    def _extract_context(self) -> ErrorContext:
        """Extract context information from current request"""
        try:
            return ErrorContext(
                request_id=str(uuid.uuid4())[:8],
                endpoint=request.endpoint if request else None,
                method=request.method if request else None,
                user_agent=request.headers.get('User-Agent') if request else None,
                ip_address=request.remote_addr if request else None,
                timestamp=datetime.now().isoformat()
            )
        except:
            return ErrorContext(
                request_id=str(uuid.uuid4())[:8],
                timestamp=datetime.now().isoformat()
            )
    
    def create_error(self, 
                    error_code: str,
                    message: Optional[str] = None,
                    details: Optional[Dict[str, Any]] = None,
                    exception: Optional[Exception] = None) -> EnhancedError:
        """Create enhanced error object"""
        
        error_id = str(uuid.uuid4())
        context = self._extract_context()
        
        # Get error definition from registry
        error_def = self.error_registry.get(error_code, {
            'message': message or 'Terjadi kesalahan yang tidak diketahui',
            'severity': ErrorSeverity.MEDIUM,
            'category': ErrorCategory.UNKNOWN,
            'suggestions': ['Hubungi support untuk bantuan']
        })
        
        enhanced_error = EnhancedError(
            error_id=error_id,
            error_code=error_code,
            message=message or error_def['message'],
            severity=error_def['severity'],
            category=error_def['category'],
            context=context,
            details=details or {},
            suggestions=error_def.get('suggestions', []),
            timestamp=datetime.now().isoformat()
        )
        
        # Log error with full context
        self._log_error(enhanced_error, exception)
        
        # Update statistics
        self._update_stats(enhanced_error)
        
        return enhanced_error
    
    def _log_error(self, error: EnhancedError, exception: Optional[Exception] = None):
        """Log error with appropriate level"""
        log_message = f"[{error.error_id}] {error.error_code}: {error.message}"
        
        log_data = {
            'error_id': error.error_id,
            'error_code': error.error_code,
            'severity': error.severity.value,
            'category': error.category.value,
            'endpoint': error.context.endpoint,
            'method': error.context.method,
            'details': error.details
        }
        
        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra=log_data)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra=log_data)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra=log_data)
        else:
            logger.info(log_message, extra=log_data)
        
        # Log exception traceback if available
        if exception:
            logger.error(f"Exception traceback for {error.error_id}:", exc_info=exception)
    
    def _update_stats(self, error: EnhancedError):
        """Update error statistics"""
        self.error_stats['total_errors'] += 1
        
        # Update category stats
        category = error.category.value
        if category not in self.error_stats['errors_by_category']:
            self.error_stats['errors_by_category'][category] = 0
        self.error_stats['errors_by_category'][category] += 1
        
        # Update severity stats
        severity = error.severity.value
        if severity not in self.error_stats['errors_by_severity']:
            self.error_stats['errors_by_severity'][severity] = 0
        self.error_stats['errors_by_severity'][severity] += 1
        
        # Keep recent errors (last 50)
        self.error_stats['recent_errors'].append({
            'error_id': error.error_id,
            'error_code': error.error_code,
            'severity': error.severity.value,
            'timestamp': error.timestamp
        })
        
        if len(self.error_stats['recent_errors']) > 50:
            self.error_stats['recent_errors'] = self.error_stats['recent_errors'][-50:]
    
    def handle_error(self, 
                    error_code: str,
                    message: Optional[str] = None,
                    details: Optional[Dict[str, Any]] = None,
                    exception: Optional[Exception] = None,
                    status_code: int = 500) -> Response:
        """Handle error and return formatted response"""
        
        enhanced_error = self.create_error(error_code, message, details, exception)
        
        # Create user-friendly response
        response_data = {
            'success': False,
            'error': enhanced_error.to_dict(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Don't expose sensitive details in production
        if not self._is_debug_mode():
            # Remove sensitive information
            response_data['error']['details'] = self._sanitize_details(response_data['error']['details'])
            response_data['error']['context']['additional_data'] = None
        
        response = jsonify(response_data)
        response.status_code = status_code
        return response
    
    def _is_debug_mode(self) -> bool:
        """Check if application is in debug mode"""
        try:
            from flask import current_app
            return current_app.debug
        except:
            return False
    
    def _sanitize_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from error details"""
        if not details:
            return {}
        
        sensitive_keys = ['password', 'token', 'key', 'secret', 'credential']
        sanitized = {}
        
        for key, value in details.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = value
        
        return sanitized
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            **self.error_stats,
            'timestamp': datetime.now().isoformat()
        }

# Global error handler instance
error_handler = EnhancedErrorHandler()

def get_error_handler() -> EnhancedErrorHandler:
    """Get global error handler instance"""
    return error_handler

def handle_api_error(error_code: str, 
                    message: Optional[str] = None,
                    details: Optional[Dict[str, Any]] = None,
                    exception: Optional[Exception] = None,
                    status_code: int = 500) -> Response:
    """Quick function to handle API errors"""
    return error_handler.handle_error(error_code, message, details, exception, status_code)

logger.info("🚨 Enhanced Error Handler module initialized")