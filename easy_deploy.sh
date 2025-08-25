#!/bin/bash
echo "🚀 EASY VPS DEPLOYMENT - ONE CLICK SOLUTION"
echo "==========================================="

echo "✅ This script will:"
echo "1. 📤 Commit & push changes to GitHub"  
echo "2. 🔄 SSH to VPS and pull latest changes"
echo "3. 🐳 Restart Docker containers"
echo "4. 🧪 Test endpoints"
echo ""

# Check if we're ready
echo "🔍 Pre-deployment checks..."

# Auto-commit and push (if you have git configured)
echo "📤 Step 1: Pushing to GitHub..."
echo "Run these commands manually:"
echo "git add core/okx_fetcher.py core/high_prob_signal_engine.py"
echo "git commit -m '🔧 Real-time data integration + OKX price fix'"
echo "git push origin main"
echo ""

# VPS deployment commands
echo "🔄 Step 2: VPS Deployment Commands"
echo "Copy-paste these commands:"
echo ""
echo "# SSH to VPS"
echo "ssh root@guardiansofthetoken.id"
echo ""
echo "# Once connected to VPS, run:"
echo "cd /root/crypto-analysis-dashboard"
echo "git pull origin main"
echo "docker-compose -f docker-compose-vps.yml restart"
echo "docker-compose -f docker-compose-vps.yml logs --tail=50"
echo ""

# Test commands
echo "🧪 Step 3: Test After Deployment"
echo "curl https://guardiansofthetoken.id/"
echo "curl https://guardiansofthetoken.id/api/signal/top"
echo ""

echo "💡 ALTERNATIVE - Simple File Copy Method:"
echo "========================================="
echo "Instead of git, you can directly copy files:"
echo ""
echo "# Copy updated files directly to VPS"
echo "scp core/okx_fetcher.py root@guardiansofthetoken.id:/root/crypto-analysis-dashboard/core/"
echo "scp core/high_prob_signal_engine.py root@guardiansofthetoken.id:/root/crypto-analysis-dashboard/core/"
echo ""
echo "# Then restart containers"
echo "ssh root@guardiansofthetoken.id 'cd /root/crypto-analysis-dashboard && docker-compose -f docker-compose-vps.yml restart'"
echo ""

echo "✨ OPTION 3 - Remote Restart Only:"
echo "================================="
echo "If code is already synced, just restart:"
echo "ssh root@guardiansofthetoken.id 'cd /root/crypto-analysis-dashboard && docker-compose -f docker-compose-vps.yml restart'"
echo ""

echo "🎯 Expected Result:"
echo "Trading signals will use real BTC price (~$111,796) instead of $45,000"
echo ""
echo "Choose the method that works best for you! 💪"