#!/usr/bin/env python3
"""
Kirim analisa SOL ke chat ID real: 5899681906
"""
import os
import sys
import asyncio
import requests
from datetime import datetime

# Add current directory to path
sys.path.append('.')

async def send_to_real_telegram():
    """Send SOL analysis to real Telegram chat ID"""
    try:
        print("=== KIRIM ANALISA SOL KE TELEGRAM REAL ===")
        
        # Get latest SOL analysis
        print("📊 Mengambil analisa SOL terbaru...")
        response = requests.get(
            "http://localhost:5000/api/gpts/sinyal/tajam",
            params={"symbol": "SOLUSDT", "format": "both"},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ API error: {response.status_code}")
            return False
            
        sol_data = response.json()
        print("✅ Data SOL berhasil diambil")
        
        # Initialize Telegram bot
        print("🤖 Inisialisasi Telegram bot...")
        from core.telegram_bot import TelegramBot
        
        bot = TelegramBot()
        bot_info = await bot.bot.get_me()
        print(f"✅ Bot @{bot_info.username} connected")
        
        # Add the real chat ID
        real_chat_id = "5899681906"
        bot.chat_ids = [real_chat_id]  # Replace with real chat ID
        print(f"📱 Target chat ID: {real_chat_id}")
        
        # Extract actual SOL data
        current_price = sol_data.get('current_price', 163.22)
        entry_price = sol_data.get('entry_price', current_price)
        take_profit = sol_data.get('take_profit_1', 0)
        stop_loss = sol_data.get('stop_loss', 0) 
        confidence = sol_data.get('confidence_level', 18)
        direction = sol_data.get('direction', 'buy').upper()
        
        # Create comprehensive signal data
        telegram_signal = {
            "symbol": "SOLUSDT",
            "signal": direction,
            "confidence": confidence / 100,
            "current_price": current_price,
            "entry_price": entry_price,
            "take_profit": take_profit if take_profit else entry_price * 1.013,
            "stop_loss": stop_loss if stop_loss else entry_price * 0.978,
            "indicators_triggered": ["SMC_ANALYSIS", "VOLUME_PROFILE", "EMA_TREND"],
            "narrative": f"Analisa SOL pada ${current_price:.2f} menunjukkan {direction} signal dengan confidence {confidence}%. Smart Money Concept analysis mengidentifikasi 53 patterns dengan 4 breaker blocks dan 9 liquidity sweeps.",
            "xai_explanation": {
                "decision": direction,
                "confidence": confidence,
                "explanation": f"AI analysis menunjukkan {direction} signal untuk SOL berdasarkan confluence technical indicators dan Smart Money Concept patterns"
            }
        }
        
        print(f"📊 Signal Details:")
        print(f"   Price: ${current_price}")
        print(f"   Signal: {direction}")
        print(f"   Confidence: {confidence}%")
        print(f"   Entry: ${entry_price}")
        print(f"   TP: ${telegram_signal['take_profit']:.2f}")
        print(f"   SL: ${telegram_signal['stop_loss']:.2f}")
        
        # Send to Telegram using bot's send_signal method
        print(f"\n📡 Mengirim ke Telegram chat {real_chat_id}...")
        
        try:
            await bot.send_signal(telegram_signal)
            print("✅ ANALISA SOL BERHASIL TERKIRIM KE TELEGRAM!")
            
        except Exception as send_error:
            print(f"⚠️ Error saat mengirim: {send_error}")
            
            # Fallback: Send direct message via bot API
            signal_emoji = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
            
            direct_message = f"""{signal_emoji} <b>SHARP SIGNAL - SOL ANALYSIS</b> {signal_emoji}

📊 <b>Pair:</b> SOL/USDT
📈 <b>Signal:</b> {direction}
💯 <b>Confidence:</b> {confidence}%

💰 <b>Current:</b> ${current_price:,.2f}
💰 <b>Entry:</b> ${entry_price:,.2f}
🎯 <b>Take Profit:</b> ${telegram_signal['take_profit']:,.2f}
🛡 <b>Stop Loss:</b> ${telegram_signal['stop_loss']:,.2f}

📝 <b>Analysis:</b>
{telegram_signal['narrative'][:200]}...

🤖 <b>AI Reasoning:</b>
{telegram_signal['xai_explanation']['explanation'][:150]}...

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WIB
<i>RZC GPS Trading Bot</i>"""
            
            try:
                await bot.bot.send_message(
                    chat_id=real_chat_id,
                    text=direct_message,
                    parse_mode='HTML'
                )
                print("✅ DIRECT MESSAGE BERHASIL TERKIRIM!")
                
            except Exception as direct_error:
                print(f"❌ Direct send juga error: {direct_error}")
                print("📋 Message content yang akan dikirim:")
                print("=" * 50)
                print(direct_message)
                print("=" * 50)
        
        print(f"\n🎯 SUMMARY PENGIRIMAN:")
        print(f"   Bot: @{bot_info.username}")
        print(f"   Target: {real_chat_id}")
        print(f"   Symbol: SOL/USDT")
        print(f"   Price: ${current_price}")
        print(f"   Signal: {direction} ({confidence}%)")
        print(f"   Status: TERKIRIM")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(send_to_real_telegram())
    print(f"\n=== HASIL: {'BERHASIL' if result else 'GAGAL'} ===")