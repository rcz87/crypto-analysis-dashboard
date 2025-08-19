#!/usr/bin/env python3
"""
Test script untuk mengecek dan mengirim test signal via Telegram
"""
import os
import sys
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append('.')

async def test_telegram_signal():
    """Test sending signal via Telegram bot"""
    try:
        print("=== TELEGRAM SIGNAL TEST ===")
        
        # Check token
        token = os.environ.get('TELEGRAM_BOT_TOKEN')
        if not token:
            print("❌ TELEGRAM_BOT_TOKEN not found")
            return
        
        print(f"✅ Token configured: ...{token[-10:]}")
        
        # Import and initialize bot
        from core.telegram_bot import TelegramBot
        bot = TelegramBot()
        
        print(f"✅ Bot initialized successfully")
        print(f"Chat IDs: {len(bot.chat_ids)}")
        
        # Test signal data
        test_signal = {
            "symbol": "BTCUSDT",
            "signal": "BUY", 
            "confidence": 0.75,
            "entry_price": 114500.0,
            "take_profit": 116735.0,
            "stop_loss": 112265.0,
            "indicators_triggered": ["SMC_BREAK", "HIGH_VOLUME"],
            "narrative": "Strong bullish signal detected with Smart Money Concept break and high volume confirmation"
        }
        
        print("\n=== TEST SIGNAL DATA ===")
        for key, value in test_signal.items():
            print(f"{key}: {value}")
        
        # Send test signal
        print("\n=== SENDING TEST SIGNAL ===")
        if bot.chat_ids:
            await bot.send_signal(test_signal)
            print("✅ Signal sent to registered chats")
        else:
            print("⚠️ No chat IDs registered - signal not sent")
            print("To register, send /start to your bot first")
        
        # Test bot info
        bot_info = await bot.bot.get_me()
        print(f"\n=== BOT INFO ===")
        print(f"Bot Name: {bot_info.first_name}")
        print(f"Bot Username: @{bot_info.username}")
        print(f"Bot ID: {bot_info.id}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_telegram_signal())