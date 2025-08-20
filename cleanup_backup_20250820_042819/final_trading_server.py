#!/usr/bin/env python3
from flask import Flask, jsonify, request, Blueprint
import os
import requests
import logging
import importlib
from types import ModuleType

app = Flask(__name__)
# Hindari emoji di formatter default untuk kompatibilitas Windows console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("final_server")

# =========================
# Config via Environment
# =========================
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "<TELEGRAM_BOT_TOKEN>")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "<TELEGRAM_CHAT_ID>")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
DATABASE_URL = os.getenv("DATABASE_URL", None)

# =========================
# Utils
# =========================
def send_telegram(message: str) -> dict:
    """Send Telegram message with basic error handling"""
    result = {"success": False, "error": None}
    token = BOT_TOKEN
    chat_id = CHAT_ID

    if not token or not chat_id or token.startswith("<") or chat_id.startswith("<"):
        result["error"] = "Telegram credentials not configured"
        return result

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        resp = requests.post(url, data=data, timeout=10)
        if resp.ok:
            result["success"] = True
        else:
            result["error"] = f"HTTP {resp.status_code} - {resp.text[:200]}"
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
    status = {
        "status": "ok",
        "service": "final_server",
        "openai_configured": bool(OPENAI_API_KEY),
        "telegram_configured": bool(BOT_TOKEN and CHAT_ID and not BOT_TOKEN.startswith("<")),
        "database_configured": bool(DATABASE_URL),
    }
    return jsonify(status)

@app.route("/api/signal", methods=["GET"])
def get_signal():
    signal_data = {
        "symbol": request.args.get("symbol", "BTCUSDT"),
        "signal": "BUY",
        "confidence": 75,
        "price": 114500.0,
    }
    tg = send_telegram(f"🎯 TRADING SIGNAL: {signal_data['signal']} {signal_data['symbol']} @ ${signal_data['price']:,}")
    signal_data["telegram_sent"] = tg["success"]
    if tg["error"]:
        signal_data["telegram_error"] = tg["error"]
    return jsonify(signal_data)

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
    """
    Import module dan daftar semua objek Blueprint yang ada di dalamnya.
    Return: jumlah blueprint yang berhasil didaftarkan.
    """
    try:
        module: ModuleType = importlib.import_module(module_path)
    except Exception as e:
        logger.warning(f"Skipped module import {module_path}: {e}")
        return 0

    count = 0
    for attr_name in dir(module):
        try:
            attr = getattr(module, attr_name)
            if isinstance(attr, Blueprint):
                app.register_blueprint(attr)
                logger.info(f"Registered blueprint from {module_path}.{attr_name}")
                count += 1
        except Exception as e:
            logger.warning(f"Failed to register {module_path}.{attr_name}: {e}")
            continue

    if count == 0:
        logger.warning(f"No blueprints found in {module_path}")
    return count

def safe_register(module_path: str, attr_name: str):
    """
    Mekanisme lama: register berdasarkan nama atribut blueprint.
    Tetap dipertahankan untuk kompatibilitas.
    """
    try:
        module = importlib.import_module(module_path)
        bp = getattr(module, attr_name)
        app.register_blueprint(bp)
        logger.info(f"Registered blueprint: {module_path}.{attr_name}")
    except Exception as e:
        logger.warning(f"Skipped blueprint {module_path}.{attr_name}: {e}")

# =========================
# Register Blueprints (API modules)
# =========================
# Core API blueprints (gunakan auto_register agar nama variabel blueprint fleksibel)
# Modul dalam paket api/
auto_register_module("api.chart_endpoints")
auto_register_module("api.performance_api")
auto_register_module("api.performance_endpoints")
auto_register_module("api.smc_endpoints")
auto_register_module("api.smc_zones_endpoints")
auto_register_module("api.smc_pattern_endpoints")
auto_register_module("api.signal_engine_endpoint")
auto_register_module("api.signal_top_endpoints")
auto_register_module("api.sharp_signal_endpoint")
auto_register_module("api.state_endpoints")
auto_register_module("api.missing_endpoints")
auto_register_module("api.backtest_endpoints")

# News endpoints bergantung feedparser - tetap dicoba
auto_register_module("api.news_endpoints")

# GPTs endpoints: file Anda berada di root, bukan di folder api/
auto_register_module("gpts_api_endpoints")

# Opsional/eksperimental modul:
# auto_register_module("api.enhanced_gpts_endpoints")  # hindari bentrok path enhanced

# =========================
# Entrypoint
# =========================
if __name__ == "__main__":
    print("🚀 Starting final server...")
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
