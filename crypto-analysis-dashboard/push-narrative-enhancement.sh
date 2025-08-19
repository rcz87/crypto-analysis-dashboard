#!/bin/bash
echo "🚀 PUSH NATURAL LANGUAGE NARRATIVE ENHANCEMENT"
echo "=============================================="
echo ""
echo "✅ Enhanced /api/gpts/sinyal/tajam dengan:"
echo "  - Natural language narrative capabilities"  
echo "  - Format parameter support (json, narrative, both)"
echo "  - human_readable field (1600+ characters)"
echo "  - telegram_message field untuk notifications"
echo "  - Indonesian language professional formatting"
echo ""

# Clear git locks
echo "🧹 Clearing git locks..."
rm -f .git/index.lock .git/refs/heads/main.lock 2>/dev/null || true

# Add changes
echo "📦 Adding changes..."
git add .

# Check status
echo "📊 Git status:"
git status --short

# Commit
echo ""
echo "💾 Committing changes..."
git commit -m "FEATURE: Natural Language Narrative Enhancement for /api/gpts/sinyal/tajam

✅ Added comprehensive natural language narrative capabilities
✅ Implemented format parameter support (json, narrative, both)  
✅ Added human_readable field for comprehensive trading analysis
✅ Added telegram_message field for concise notifications
✅ Enhanced with Indonesian language professional formatting
✅ Perfect for ChatGPT Custom GPTs and Telegram bot integration

Features:
- Format options: json, narrative, both
- human_readable: 1600+ character comprehensive analysis  
- telegram_message: Concise Telegram-optimized messages
- Market analysis, trade setup, risk management, AI reasoning
- XAI explanations in natural language Indonesian

Production ready at:
http://212.26.36.253:5050/api/gpts/sinyal/tajam?format=narrative"

# Push
echo ""
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "=============================================="
echo "✅ NARRATIVE ENHANCEMENT PUSHED TO GITHUB"
echo ""
echo "📝 Test URLs:"
echo "  Narrative: http://212.26.36.253:5050/api/gpts/sinyal/tajam?format=narrative"
echo "  Both: http://212.26.36.253:5050/api/gpts/sinyal/tajam?format=both"
echo ""
echo "🎯 Ready for ChatGPT Custom GPTs Integration!"
echo "=============================================="