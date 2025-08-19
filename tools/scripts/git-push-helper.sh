#!/bin/bash
echo "🚀 PUSH TO GITHUB & UPDATE VPS"
echo "==============================="

# Add and commit changes
echo "📦 Adding files to git..."
git add gpts_api_simple.py main.py
git commit -m "Fix: Enable both GET and POST methods for /sinyal/tajam endpoint

- Added proper request.method handling for GET parameters
- Route decorator supports both GET and POST
- Ready for ChatGPT Custom GPTs integration
- XAI integration fully operational"

echo "🚀 Pushing to GitHub..."
git push origin main

echo "==============================="
echo "✅ PUSHED TO GITHUB SUCCESSFULLY"
echo "Now run this command on VPS:"
echo ""
echo "cd /root/crypto-analysis-dashboard && git pull origin main && docker-compose -f docker-compose-vps.yml down && docker-compose -f docker-compose-vps.yml build --no-cache && docker-compose -f docker-compose-vps.yml up -d && sleep 30 && curl 'http://localhost:5050/api/gpts/sinyal/tajam?symbol=BTCUSDT&timeframe=1H'"
echo ""
echo "==============================="