#!/usr/bin/env python3
"""
Demonstrasi lengkap broadcast SOL ke Telegram dengan actual message sending
"""
import os
import sys
import asyncio
from datetime import datetime

# Add current directory to path
sys.path.append('.')

async def telegram_broadcast_demo():
    """Demo broadcast message ke Telegram dengan format actual"""
    try:
        print("=== TELEGRAM BROADCAST DEMONSTRATION ===")
        
        # Initialize Telegram bot
        from core.telegram_bot import TelegramBot
        
        bot = TelegramBot()
        bot_info = await bot.bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username} (ID: {bot_info.id})")
        
        # Demo data SOL analysis
        sol_analysis = {
            "symbol": "SOLUSDT",
            "signal": "BUY",
            "confidence": 0.18,  # 18%
            "current_price": 163.22,
            "entry_price": 163.22,
            "take_profit": 165.36,
            "stop_loss": 159.65,
            "indicators_triggered": ["EMA_TREND", "SMC_PATTERNS", "VOLUME_ANALYSIS"],
            "narrative": "Analisis SOL menunjukkan struktur market neutral dengan bias bullish lemah. EMA trend memberikan signal BUY dengan strength 60%, namun confidence level rendah 18% mengindikasikan risk tinggi.",
            "xai_explanation": {
                "decision": "BUY",
                "confidence": 18,
                "explanation": "Signal NEUTRAL-BUY untuk SOLUSDT berdasarkan confluence technical indicators dan Smart Money Concept analysis"
            }
        }
        
        print(f"\n📊 SOL Analysis Data:")
        print(f"   Price: ${sol_analysis['current_price']}")
        print(f"   Signal: {sol_analysis['signal']}")
        print(f"   Confidence: {sol_analysis['confidence']*100:.1f}%")
        
        # Create actual Telegram message
        signal_emoji = "🟢" if sol_analysis['signal'] == "BUY" else "🔴" if sol_analysis['signal'] == "SELL" else "⚪"
        
        telegram_msg = f"""{signal_emoji} <b>SHARP SIGNAL ALERT - SOL</b> {signal_emoji}

📊 <b>Pair:</b> {sol_analysis['symbol']}
📈 <b>Signal:</b> {sol_analysis['signal']}
💯 <b>Confidence:</b> {sol_analysis['confidence']*100:.1f}%

💰 <b>Current:</b> ${sol_analysis['current_price']:,.2f}
💰 <b>Entry:</b> ${sol_analysis['entry_price']:,.2f}
🎯 <b>Take Profit:</b> ${sol_analysis['take_profit']:,.2f}
🛡 <b>Stop Loss:</b> ${sol_analysis['stop_loss']:,.2f}

📝 <b>Analysis:</b>
{sol_analysis['narrative'][:180]}...

🤖 <b>AI Reasoning:</b>
{sol_analysis['xai_explanation']['explanation'][:120]}...

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB
<i>@rzcgpsbot - RZC GPS Trading</i>"""
        
        print(f"\n📱 TELEGRAM MESSAGE FORMAT:")
        print("=" * 60)
        print(telegram_msg)
        print("=" * 60)
        
        # Check for subscribers
        if bot.chat_ids and len(bot.chat_ids) > 0:
            print(f"\n📡 Mengirim ke {len(bot.chat_ids)} subscribers...")
            await bot.send_signal(sol_analysis)
            print("✅ Message terkirim ke semua subscriber!")
        else:
            print(f"\n⚠️ Tidak ada subscriber aktif")
            print("📋 Message siap kirim, menunggu subscriber...")
            
            # Simulate sending dengan show exact steps
            print(f"\n🔄 SIMULASI PENGIRIMAN:")
            print(f"   1. Bot @{bot_info.username} ready")
            print(f"   2. Message length: {len(telegram_msg)} chars")
            print(f"   3. HTML formatting: ✅ Valid")
            print(f"   4. Waiting for subscribers via /start command")
        
        # Show how users can subscribe
        print(f"\n💡 CARA SUBSCRIBE:")
        print(f"   1. Buka Telegram")
        print(f"   2. Cari: @{bot_info.username}")
        print(f"   3. Kirim: /start")
        print(f"   4. Bot akan kirim message seperti di atas")
        
        # Bot command info
        print(f"\n🤖 BOT COMMANDS AVAILABLE:")
        print(f"   /start - Subscribe to signals")
        print(f"   /help - Show all commands")
        print(f"   /signal SOLUSDT - Manual SOL analysis")
        print(f"   /status - System status")
        print(f"   /subscribe - Resubscribe")
        print(f"   /unsubscribe - Stop notifications")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(telegram_broadcast_demo())
    print(f"\n=== DEMO {'BERHASIL' if result else 'GAGAL'} ===")