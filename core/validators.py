#!/usr/bin/env python3
"""
Input Validation System for GPTs API
Menggunakan Pydantic untuk validasi input yang robust
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import re

class SignalRequest(BaseModel):
    """Validator untuk request trading signal"""
    symbol: str = Field(..., min_length=3, max_length=20, description="Trading pair symbol")
    timeframe: Optional[str] = Field("1H", description="Chart timeframe")
    confidence_threshold: Optional[float] = Field(0.75, ge=0.0, le=1.0, description="Minimum confidence level")
    leverage: Optional[int] = Field(1, ge=1, le=100, description="Trading leverage")
    
    @validator('symbol')
    def validate_symbol(cls, v, values):
        """Validate trading pair symbol format"""
        if not v:
            raise ValueError("Symbol tidak boleh kosong")
        
        # Clean symbol format
        v = v.upper().strip()
        
        # Accept various formats: BTCUSDT, BTC-USDT, BTC/USDT
        if not re.match(r'^[A-Z]{2,10}[-/]?USDT?$', v):
            raise ValueError(f"Format symbol tidak valid: {v}. Gunakan format seperti BTCUSDT, BTC-USDT, atau BTC/USDT")
            
        return v
    
    @validator('timeframe')
    def validate_timeframe(cls, v, values):
        """Validate timeframe format"""
        valid_timeframes = ['1m', '5m', '15m', '1H', '4H', '1D', '1W']
        if v not in valid_timeframes:
            raise ValueError(f"Timeframe tidak valid: {v}. Gunakan: {', '.join(valid_timeframes)}")
        return v

class ChartRequest(BaseModel):
    """Validator untuk request chart data"""
    symbol: str = Field(..., min_length=3, max_length=20)
    timeframe: Optional[str] = Field("1H")
    limit: Optional[int] = Field(100, ge=10, le=500, description="Number of candles")
    
    @validator('symbol')
    def validate_symbol(cls, v, values):
        # Call static method dari SignalRequest class
        if not v:
            raise ValueError("Symbol tidak boleh kosong")
        v = v.upper().strip()
        if not re.match(r'^[A-Z]{2,10}[-/]?USDT?$', v):
            raise ValueError(f"Format symbol tidak valid: {v}")
        return v
    
    @validator('timeframe') 
    def validate_timeframe(cls, v, values):
        valid_timeframes = ['1m', '5m', '15m', '1H', '4H', '1D', '1W']
        if v not in valid_timeframes:
            raise ValueError(f"Timeframe tidak valid: {v}")
        return v

class TelegramRequest(BaseModel):
    """Validator untuk Telegram requests"""
    chat_id: str = Field(..., min_length=1, description="Telegram chat ID")
    message: Optional[str] = Field(None, max_length=4000, description="Custom message")
    
    @validator('chat_id')
    def validate_chat_id(cls, v, values):
        """Validate Telegram chat ID format"""
        if not v or not str(v).strip():
            raise ValueError("Chat ID tidak boleh kosong")
        
        # Chat ID should be numeric or start with @
        v = str(v).strip()
        if not (v.isdigit() or (v.startswith('@') and len(v) > 1)):
            raise ValueError("Chat ID harus berupa angka atau username dengan @")
            
        return v

class ValidationError(Exception):
    """Custom validation error dengan format yang konsisten"""
    def __init__(self, field: str, message: str, value=None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(message)

def validate_request(data: dict, validator_class) -> dict:
    """
    Validate request data menggunakan Pydantic
    Returns: validated data atau raise ValidationError
    """
    try:
        validated = validator_class(**data)
        return validated.dict()
    except Exception as e:
        # Convert pydantic errors to our format
        try:
            if hasattr(e, 'errors') and callable(getattr(e, 'errors')):
                errors = []
                for error in e.errors():
                    field = '.'.join(str(x) for x in error['loc'])
                    errors.append({
                        'field': field,
                        'message': error['msg'],
                        'value': error.get('input', 'N/A')
                    })
                raise ValidationError("validation_failed", f"Input validation failed: {errors}")
            else:
                raise ValidationError("unknown_error", str(e))
        except:
            raise ValidationError("unknown_error", str(e))

def create_validation_error_response(error: ValidationError) -> dict:
    """Create standardized 422 error response"""
    return {
        "error": "VALIDATION_ERROR",
        "error_code": 422,
        "message": "Input validation failed",
        "details": error.message,
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0"
    }