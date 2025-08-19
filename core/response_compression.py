#!/usr/bin/env python3
"""
Response Compression Middleware - Kompresi response untuk efisiensi bandwidth
"""

import gzip
import json
import logging
from typing import Any, Dict, Optional, Union
from functools import wraps
from flask import request, Response, jsonify, current_app
import time

logger = logging.getLogger(__name__)

class ResponseCompressor:
    """Response compression handler dengan intelligent compression"""
    
    def __init__(self, 
                 min_size: int = 500,
                 compression_level: int = 6,
                 mime_types: Optional[set] = None):
        self.min_size = min_size
        self.compression_level = compression_level
        self.mime_types = mime_types or {
            'application/json',
            'text/plain',
            'text/html',
            'text/css',
            'text/javascript',
            'application/javascript'
        }
        self.stats = {
            'total_requests': 0,
            'compressed_requests': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'compression_time_ms': 0
        }
        
    def should_compress(self, response: Response) -> bool:
        """Determine if response should be compressed"""
        # Check if client accepts gzip
        accept_encoding = request.headers.get('Accept-Encoding', '')
        if 'gzip' not in accept_encoding:
            return False
        
        # Check content type
        content_type = response.content_type
        if content_type:
            mime_type = content_type.split(';')[0].strip()
            if mime_type not in self.mime_types:
                return False
        
        # Check response size
        if hasattr(response, 'data'):
            content_length = len(response.data)
        else:
            content_length = int(response.headers.get('Content-Length', 0))
        
        if content_length < self.min_size:
            return False
        
        # Check if already compressed
        if response.headers.get('Content-Encoding'):
            return False
        
        return True
    
    def compress_response(self, response: Response) -> Response:
        """Compress response data"""
        start_time = time.time()
        
        try:
            if not self.should_compress(response):
                self.stats['total_requests'] += 1
                return response
            
            # Get original data
            if hasattr(response, 'data'):
                original_data = response.data
            else:
                original_data = response.get_data()
            
            original_size = len(original_data)
            
            # Compress data
            compressed_data = gzip.compress(original_data, compresslevel=self.compression_level)
            compressed_size = len(compressed_data)
            
            # Only use compression if it actually saves space
            compression_ratio = compressed_size / original_size
            if compression_ratio > 0.9:  # Less than 10% savings, skip compression
                self.stats['total_requests'] += 1
                return response
            
            # Update response with compressed data
            response.data = compressed_data
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Length'] = str(compressed_size)
            response.headers['X-Compression-Ratio'] = f"{compression_ratio:.2f}"
            response.headers['X-Original-Size'] = str(original_size)
            
            # Update stats
            compression_time = (time.time() - start_time) * 1000
            self.stats['total_requests'] += 1
            self.stats['compressed_requests'] += 1
            self.stats['total_original_size'] += original_size
            self.stats['total_compressed_size'] += compressed_size
            self.stats['compression_time_ms'] += compression_time
            
            logger.debug(f"Response compressed: {original_size} -> {compressed_size} bytes ({compression_ratio:.2%})")
            
            return response
            
        except Exception as e:
            logger.error(f"Compression error: {e}")
            self.stats['total_requests'] += 1
            return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get compression statistics"""
        total_requests = self.stats['total_requests']
        if total_requests == 0:
            return {
                'total_requests': 0,
                'compression_rate': '0.00%',
                'space_saved': '0.00%',
                'avg_compression_time_ms': 0
            }
        
        compression_rate = self.stats['compressed_requests'] / total_requests
        
        if self.stats['total_original_size'] > 0:
            space_saved = 1 - (self.stats['total_compressed_size'] / self.stats['total_original_size'])
        else:
            space_saved = 0
        
        avg_compression_time = self.stats['compression_time_ms'] / max(1, self.stats['compressed_requests'])
        
        return {
            'total_requests': total_requests,
            'compressed_requests': self.stats['compressed_requests'],
            'compression_rate': f"{compression_rate:.2%}",
            'total_original_size_kb': f"{self.stats['total_original_size'] / 1024:.2f}",
            'total_compressed_size_kb': f"{self.stats['total_compressed_size'] / 1024:.2f}",
            'space_saved': f"{space_saved:.2%}",
            'avg_compression_time_ms': f"{avg_compression_time:.2f}",
            'compression_level': self.compression_level,
            'min_size_bytes': self.min_size
        }

# Global compressor instance
response_compressor = ResponseCompressor()

def compress_json_response(data: Any, status_code: int = 200, headers: Optional[Dict] = None) -> Response:
    """Create compressed JSON response"""
    try:
        # Create JSON response
        response = jsonify(data)
        response.status_code = status_code
        
        if headers:
            for key, value in headers.items():
                response.headers[key] = value
        
        # Add performance headers
        response.headers['X-Response-Time'] = str(time.time())
        response.headers['X-API-Version'] = '2.0'
        
        # Compress if beneficial
        return response_compressor.compress_response(response)
        
    except Exception as e:
        logger.error(f"Error creating compressed response: {e}")
        error_response = jsonify({'error': 'Response generation failed'})
        error_response.status_code = 500
        return error_response

def compression_middleware(app):
    """Flask middleware for automatic response compression"""
    
    @app.after_request
    def compress_response(response):
        """Automatically compress all responses"""
        try:
            return response_compressor.compress_response(response)
        except Exception as e:
            logger.error(f"Compression middleware error: {e}")
            return response
    
    return app

def compress_large_response(func):
    """Decorator for compressing large responses"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If result is a tuple (response, status_code)
            if isinstance(result, tuple):
                if len(result) == 2:
                    return compress_json_response(result[0], result[1])
                elif len(result) == 3:
                    return compress_json_response(result[0], result[1], result[2])
            
            # If result is a Response object
            if isinstance(result, Response):
                return response_compressor.compress_response(result)
            
            # If result is data to be JSONified
            return compress_json_response(result)
            
        except Exception as e:
            logger.error(f"Compression decorator error: {e}")
            return jsonify({'error': 'Response processing failed'}), 500
    
    return wrapper

def get_compression_stats() -> Dict[str, Any]:
    """Get global compression statistics"""
    return response_compressor.get_stats()

logger.info("📦 Response Compression module initialized")