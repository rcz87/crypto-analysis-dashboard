# Deploy & Recovery (Hostinger VPS)
- App: systemd `crypto-trader.service` → 127.0.0.1:5050
- Proxy: Nginx (80/443) → 127.0.0.1:5050
- Domain: https://gpts.guardiansofthetoken.id

## Operasional
- Cek: `curl https://gpts.guardiansofthetoken.id/api/gpts/health`
- Log app: `sudo journalctl -u crypto-trader -f`
- Log nginx: `sudo tail -f /var/log/nginx/error.log`
- Restart app: `sudo systemctl restart crypto-trader`
- Update code: `git pull && pip install -r requirements_complete.txt && sudo systemctl restart crypto-trader`

## SSL
- Certbot auto-renew (crontab 03:00). Manual: `sudo certbot renew --dry-run`

## Keamanan
- `.env` chmod 600, **jangan** commit. Rotasi OpenAI/OKX/Telegram key berkala.
