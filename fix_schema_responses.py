#!/usr/bin/env python3
"""
Quick fix untuk memperbaiki semua schema responses yang menggunakan bare {"type": "object"}
"""

def fix_schema_file():
    # Read the file
    with open('gpts_openapi_ultra_complete.py', 'r') as f:
        content = f.read()
    
    # Define replacement mappings for different endpoints
    fixes = [
        # Top signals
        ('"/api/signal/top"', '"schema": {"type": "object"}', 
         '"schema": {"type": "object", "properties": {"signals": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "status": {"type": "string", "example": "success"}}, "additionalProperties": True}'),
        
        # Market data 
        ('"/api/gpts/market-data"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"data": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "symbol": {"type": "string"}, "timeframe": {"type": "string"}}, "additionalProperties": True}'),
        
        # Ticker data
        ('"/api/gpts/ticker/{symbol}"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"ticker": {"type": "object", "additionalProperties": True}, "symbol": {"type": "string"}, "price": {"type": "number"}}, "additionalProperties": True}'),
         
        # Order book
        ('"/api/gpts/orderbook/{symbol}"', '"schema": {"type": "object"}', 
         '"schema": {"type": "object", "properties": {"orderbook": {"type": "object", "additionalProperties": True}, "symbol": {"type": "string"}, "depth": {"type": "integer"}}, "additionalProperties": True}'),
         
        # SMC Analysis
        ('"/api/gpts/smc-analysis"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"smc_analysis": {"type": "object", "additionalProperties": True}, "patterns": {"type": "array", "items": {"type": "object", "additionalProperties": True}}}, "additionalProperties": True}'),
         
        # SMC Zones  
        ('"/api/gpts/smc-zones/{symbol}"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"zones": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "symbol": {"type": "string"}}, "additionalProperties": True}'),
         
        # Analysis deep
        ('"/api/gpts/analysis/deep"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"analysis": {"type": "object", "additionalProperties": True}, "insights": {"type": "array", "items": {"type": "object", "additionalProperties": True}}}, "additionalProperties": True}'),
         
        # Enhanced signals
        ('"/api/gpts/sinyal/enhanced"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"signal": {"type": "object", "additionalProperties": True}, "enhanced_analysis": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Alerts status
        ('"/api/gpts/alerts/status"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"alerts": {"type": "object", "additionalProperties": True}, "status": {"type": "string", "example": "active"}}, "additionalProperties": True}'),
         
        # News status
        ('"/api/news/status"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"news_service": {"type": "object", "additionalProperties": True}, "status": {"type": "string", "example": "operational"}}, "additionalProperties": True}'),
         
        # Backtest
        ('"/api/backtest"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"backtest_results": {"type": "object", "additionalProperties": True}, "performance": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Quick backtest
        ('"/api/backtest/quick"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"quick_results": {"type": "object", "additionalProperties": True}, "summary": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Strategies
        ('"/api/backtest/strategies"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"strategies": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "count": {"type": "integer"}}, "additionalProperties": True}'),
         
        # Context live
        ('"/api/gpts/context/live"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"context": {"type": "object", "additionalProperties": True}, "live_data": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Promptbook
        ('"/api/promptbook/"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"prompts": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "templates": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Performance
        ('"/api/performance/stats"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"performance": {"type": "object", "additionalProperties": True}, "stats": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # SMC zones (alternate)
        ('"/api/smc/zones"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"smc_zones": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "analysis": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Order blocks
        ('"/api/smc/orderblocks"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"orderblocks": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "timeframe": {"type": "string"}}, "additionalProperties": True}'),
         
        # Pattern recognition
        ('"/api/smc/patterns/recognize"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"patterns": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "recognition_result": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Signals history
        ('"/api/signals/history"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"history": {"type": "array", "items": {"type": "object", "additionalProperties": True}}, "pagination": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Widget
        ('"/widget"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"widget_data": {"type": "object", "additionalProperties": True}, "config": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}'),
         
        # Dashboard
        ('"/dashboard"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"dashboard": {"type": "object", "additionalProperties": True}, "widgets": {"type": "array", "items": {"type": "object", "additionalProperties": True}}}, "additionalProperties": True}'),
         
        # Data
        ('"/data"', '"schema": {"type": "object"}',
         '"schema": {"type": "object", "properties": {"data": {"type": "object", "additionalProperties": True}, "metadata": {"type": "object", "additionalProperties": True}}, "additionalProperties": True}')
    ]
    
    # Apply fixes one by one
    for endpoint_pattern, old_schema, new_schema in fixes:
        # Find the endpoint and replace the first occurrence of bare schema after it
        import re
        
        # Find endpoint position
        endpoint_pos = content.find(endpoint_pattern)
        if endpoint_pos != -1:
            # Find the next occurrence of bare object schema after this endpoint
            search_start = endpoint_pos
            schema_pos = content.find(old_schema, search_start)
            if schema_pos != -1:
                # Replace this specific occurrence
                content = content[:schema_pos] + new_schema + content[schema_pos + len(old_schema):]
                print(f"Fixed schema for {endpoint_pattern}")
    
    # Write back
    with open('gpts_openapi_ultra_complete.py', 'w') as f:
        f.write(content)
    
    print("✅ All schema responses have been fixed!")

if __name__ == "__main__":
    fix_schema_file()