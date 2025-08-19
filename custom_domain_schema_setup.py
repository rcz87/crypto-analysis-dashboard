#!/usr/bin/env python3
"""
Custom Domain Schema Setup Guide
Panduan untuk setup schema OpenAPI di domain VPS sendiri
"""

import os

def generate_custom_domain_setup():
    """Generate setup guide untuk custom domain"""
    
    # Ambil informasi dari environment atau config
    custom_domain = input("Masukkan domain VPS Anda (contoh: api.tradingbot.com): ").strip()
    if not custom_domain:
        custom_domain = "your-domain.com"
    
    print("=" * 80)
    print("🚀 PANDUAN SETUP SCHEMA OPENAPI DI DOMAIN VPS SENDIRI")
    print("=" * 80)
    
    print(f"""
📋 LANGKAH-LANGKAH SETUP:

1. 📂 COPY FILES KE VPS:
   Pastikan file-file ini ada di VPS Anda:
   
   ✅ gpts_openapi_ultra_complete.py
   ✅ routes.py (dengan blueprint registration)
   ✅ Semua blueprint files di folder api/
   ✅ Core system files

2. 🔧 UPDATE DOMAIN DI SCHEMA:
   Edit file gpts_openapi_ultra_complete.py, ganti:
   
   DARI:
   "servers": [
       {{
           "url": "https://workspace.ricozap87.replit.dev",
           "description": "Production API Server"
       }}
   ]
   
   MENJADI:
   "servers": [
       {{
           "url": "https://{custom_domain}",
           "description": "Custom VPS Production Server"
       }}
   ]

3. 🌐 NGINX CONFIGURATION:
   Tambahkan ke nginx config Anda:
   
   server {{
       listen 80;
       listen 443 ssl;
       server_name {custom_domain};
       
       # SSL configuration
       ssl_certificate /path/to/your/cert.pem;
       ssl_certificate_key /path/to/your/key.pem;
       
       location / {{
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }}
       
       # Khusus untuk schema endpoints
       location /openapi.json {{
           proxy_pass http://localhost:5000/openapi.json;
           add_header Access-Control-Allow-Origin *;
           add_header Content-Type application/json;
       }}
       
       location /.well-known/openapi.json {{
           proxy_pass http://localhost:5000/.well-known/openapi.json;
           add_header Access-Control-Allow-Origin *;
           add_header Content-Type application/json;
       }}
   }}

4. 🔑 SSL CERTIFICATE:
   Setup SSL dengan Let's Encrypt:
   
   sudo apt update
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d {custom_domain}

5. 🚀 START APPLICATION:
   Di VPS Anda:
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Start dengan gunicorn
   gunicorn --bind 0.0.0.0:5000 --workers 2 main:app
   
   # Atau dengan screen untuk background
   screen -S trading-api
   gunicorn --bind 0.0.0.0:5000 --workers 2 main:app

6. ✅ TEST SCHEMA ACCESS:
   Test endpoints ini:
   
   https://{custom_domain}/openapi.json
   https://{custom_domain}/.well-known/openapi.json  
   https://{custom_domain}/api/docs
   https://{custom_domain}/health

7. 🤖 CHATGPT CUSTOM GPT SETUP:
   Di ChatGPT Actions, gunakan URL:
   
   https://{custom_domain}/openapi.json
   
   Atau alternatif:
   https://{custom_domain}/.well-known/openapi.json

8. 🔄 AUTOMATIC UPDATES:
   Setup script untuk update otomatis:
   
   #!/bin/bash
   # update_schema.sh
   cd /path/to/your/app
   git pull origin main
   systemctl restart your-app-service
   
   # Jalankan setiap deploy:
   chmod +x update_schema.sh
   ./update_schema.sh

🎯 KEUNTUNGAN CUSTOM DOMAIN:

✅ Full control atas schema URL
✅ Custom branding (api.yourdomain.com)
✅ Tidak bergantung pada Replit uptime
✅ Bisa setup CDN untuk performance
✅ Custom SSL certificate
✅ Rate limiting sesuai kebutuhan
✅ Monitoring dan logging lengkap

⚠️ YANG PERLU DIPERHATIKAN:

🔧 Pastikan semua environment variables tersedia
🔧 Database connection string sesuai VPS
🔧 API keys (OKX, OpenAI, Telegram) sudah di-set
🔧 Firewall rules untuk port 80/443
🔧 Backup schema file secara berkala

📊 MONITORING SCHEMA:

Buat script untuk monitoring:

#!/bin/bash
# monitor_schema.sh
response=$(curl -s -o /dev/null -w "%{{http_code}}" https://{custom_domain}/openapi.json)
if [ $response != "200" ]; then
    echo "Schema endpoint down! Status: $response"
    # Send alert (email, telegram, etc)
fi
""")

    print(f"\n💾 Schema URL untuk ChatGPT Custom GPT:")
    print(f"   https://{custom_domain}/openapi.json")
    
    print(f"\n🔗 API Documentation URL:")
    print(f"   https://{custom_domain}/api/docs")
    
    return custom_domain

if __name__ == "__main__":
    domain = generate_custom_domain_setup()
    print(f"\n✅ Setup guide generated for domain: {domain}")
    print(f"📋 Simpan panduan ini dan ikuti langkah-langkahnya di VPS Anda")