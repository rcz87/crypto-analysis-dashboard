#!/usr/bin/env python3
from flask import Flask, jsonify, request, Blueprint
import os
import requests
import logging
import importlib
from types import ModuleType

app = Flask(__name__)
# Formatter tanpa emoji agar aman di Windows console (cp1252)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("final_server")

# =========================
# Config via Environment
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "<TELEGRAM_BOT_TOKEN>")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "<TELEGRAM_CHAT_ID>")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# Utils
# =========================
def send_telegram(message: str) -> dict:
    result = {"success": False, "error": None}
    if not BOT_TOKEN or not CHAT_ID or BOT_TOKEN.startswith("<") or CHAT_ID.startswith("<"):
        result["error"] = "Telegram credentials not configured"
        return result
    try:
        resp = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
        result["success"] = resp.ok
        if not resp.ok:
            result["error"] = f"HTTP {resp.status_code}: {resp.text[:200]}"
    except requests.RequestException as e:
        result["error"] = str(e)
    return result

# =========================
# Basic Routes
# =========================
@app.route("/")
def home():
    return "🚀 Final Trading Server Ready!"

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "final_server",
        "openai_configured": bool(OPENAI_API_KEY),
        "telegram_configured": bool(BOT_TOKEN and CHAT_ID and not BOT_TOKEN.startswith("<")),
        "database_configured": bool(DATABASE_URL),
    })

@app.route("/api/signal", methods=["GET"])
def get_signal():
    data = {
        "symbol": request.args.get("symbol", "BTCUSDT"),
        "signal": "BUY",
        "confidence": 75,
        "price": 114500.0,
    }
    tg = send_telegram(f"🎯 TRADING SIGNAL: {data['signal']} {data['symbol']} @ ${data['price']:,}")
    data["telegram_sent"] = tg["success"]
    if tg["error"]:
        data["telegram_error"] = tg["error"]
    return jsonify(data)

@app.route("/openapi.json")
def openapi_schema():
    base_url = os.getenv("PUBLIC_BASE_URL", "http://localhost:5000")
    return jsonify({
        "openapi": "3.0.0",
        "info": {"title": "Crypto Trading API", "version": "1.0.0"},
        "servers": [{"url": base_url}],
        "paths": {
            "/api/signal": {"get": {"summary": "Get trading signal"}},
            "/health": {"get": {"summary": "Health check"}},
        },
    })

# =========================
# Blueprint auto-register
# =========================
def auto_register_module(module_path: str) -> int:
    """Import module lalu register semua Blueprint di dalamnya."""
    try:
        module: ModuleType = importlib.import_module(module_path)
    except Exception as e:
        logger.warning(f"Skipped module import {module_path}: {e}")
        return 0

    count = 0
    for name in dir(module):
        try:
            obj = getattr(module, name)
            if isinstance(obj, Blueprint):
                app.register_blueprint(obj)
                logger.info(f"Registered blueprint from {module_path}.{name}")
                count += 1
        except Exception as e:
            logger.warning(f"Failed to register {module_path}.{name}: {e}")
    if count == 0:
        logger.warning(f"No blueprints found in {module_path}")
    return count

# Register blueprints
# Paket api/
for mod in [
    "api.chart_endpoints",
    "api.performance_api",
    "api.performance_endpoints",
    "api.smc_endpoints",
    "api.smc_zones_endpoints",
    "api.smc_pattern_endpoints",
    "api.signal_engine_endpoint",
    "api.signal_top_endpoints",
    "api.sharp_signal_endpoint",
    "api.state_endpoints",
    "api.missing_endpoints",
    "api.backtest_endpoints",
    "api.news_endpoints",  # butuh feedparser
]:
    auto_register_module(mod)

# GPTs endpoints file di root (bukan dalam paket api)
auto_register_module("gpts_api_endpoints")

# =========================
# Entrypoint (non-reloader agar stabil di Windows)
# =========================
if __name__ == "__main__":
    print("🚀 Starting final server...")
    port = int(os.getenv("PORT", "5000"))
    # Matikan reloader & debug untuk menghindari WinError 10038
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)