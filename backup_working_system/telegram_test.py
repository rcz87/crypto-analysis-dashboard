import os

def test_telegram():
    print("=== TELEGRAM TEST ===")
    
    # Check environment variables
    bot_token = "7659990721:AAFmX7iRu4Azxs27kNE9QkAYJA6fiwQHwpc"
    chat_id = "5899681906"
    
    print(f"Bot Token: ...{bot_token[-10:]}")
    print(f"Chat ID: {chat_id}")
    
    try:
        import requests
        
        # Simple test message
        message = "🤖 Test dari Python script - Server berhasil jalan!"
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message
        }
        
        print("\nSending test message...")
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Telegram message sent successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except ImportError:
        print("❌ 'requests' module not found. Install with: pip install requests")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_telegram()