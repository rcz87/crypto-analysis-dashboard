"""
Async Helpers - Convert async functions untuk Flask compatibility
Flask tidak support async langsung, jadi kita convert dengan asyncio.run()
"""

import asyncio
import logging
from functools import wraps
from typing import Any, Callable

logger = logging.getLogger(__name__)

def async_to_sync(async_func: Callable) -> Callable:
    """
    Decorator untuk convert async function ke sync untuk Flask compatibility
    """
    @wraps(async_func)
    def sync_wrapper(*args, **kwargs):
        try:
            # Run async function dalam event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(async_func(*args, **kwargs))
                return result
            finally:
                loop.close()
        except Exception as e:
            logger.error(f"Async function execution failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    return sync_wrapper

def run_async_safely(coro, timeout: int = 30):
    """
    Run async coroutine safely dengan timeout
    """
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
            return {"success": True, "result": result}
        except asyncio.TimeoutError:
            logger.error(f"Async operation timeout after {timeout}s")
            return {"success": False, "error": f"Operation timeout after {timeout}s"}
        finally:
            loop.close()
    except Exception as e:
        logger.error(f"Async operation failed: {e}", exc_info=True)
        return {"success": False, "error": str(e)}

# Async route helpers
def create_async_route(async_func: Callable, timeout: int = 30):
    """
    Create Flask-compatible route dari async function
    """
    def sync_route(*args, **kwargs):
        from flask import jsonify
        
        try:
            result = run_async_safely(async_func(*args, **kwargs), timeout)
            
            if result["success"]:
                return jsonify({"success": True, "data": result["result"]})
            else:
                return jsonify({"success": False, "error": result["error"]}), 500
                
        except Exception as e:
            logger.error(f"Route execution failed: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500
    
    return sync_route