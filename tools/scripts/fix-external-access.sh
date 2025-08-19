#!/bin/bash
echo "🔧 FIXING VPS EXTERNAL ACCESS - Port 5050"
echo "=========================================="

echo "Creating VPS external access fix script..."

cat > /tmp/fix_external_access.sh << 'SCRIPT_END'
#!/bin/bash
echo "🔧 VPS EXTERNAL ACCESS FIX"
echo "=========================="

echo "1. Checking current firewall status..."
ufw status || echo "UFW not active"

echo "2. Opening port 5050 for external access..."
ufw allow 5050/tcp
ufw allow 5000/tcp

echo "3. Checking if ports are listening..."
netstat -tlnp | grep ":5050"
netstat -tlnp | grep ":5000"

echo "4. Checking Docker port mapping..."
docker-compose -f docker-compose-vps.yml ps

echo "5. Testing internal access..."
curl -s "http://localhost:5050/api/gpts/status" | head -3 || echo "Internal access failed"

echo "6. Checking nginx configuration..."
docker exec crypto_nginx nginx -t 2>/dev/null || echo "Nginx config issue"

echo "7. Restarting nginx for good measure..."
docker-compose -f docker-compose-vps.yml restart crypto_nginx

echo "8. Final external test from VPS..."
timeout 10 curl -s "http://212.26.36.253:5050/api/gpts/status" | head -3 || echo "External access still blocked"

echo ""
echo "9. FIREWALL RULES CHECK:"
iptables -L INPUT | grep 5050 || echo "No iptables rule for 5050"

echo ""
echo "10. ALTERNATIVE: Use port 80 if 5050 blocked..."
echo "If port 5050 is blocked by hosting provider, try:"
echo "- Use port 80: http://212.26.36.253/api/gpts/sinyal/tajam?format=narrative"
echo "- Check hosting provider firewall settings"
echo "- Contact hosting provider to open port 5050"

echo ""
echo "=========================="
echo "EXTERNAL ACCESS FIX COMPLETE"
echo "If still blocked, hosting provider may restrict port 5050"
echo "=========================="
SCRIPT_END

chmod +x /tmp/fix_external_access.sh
echo "Script created at /tmp/fix_external_access.sh"