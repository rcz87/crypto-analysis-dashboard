# Development Workflow

## Flask + Gunicorn Deployment Workflow

### Development Environment (Replit)
1. **Code Development**: Edit `app.py`, `routes/`, `models/` files
2. **Local Testing**: Use Replit workflow to test endpoints
3. **Health Check**: Verify `/health` and `/api/gpts/status` endpoints
4. **Database Testing**: Ensure SQLAlchemy connection works

### GitHub Integration
1. **Commit Changes**: `git add .` → `git commit -m "feat: description"`
2. **Push to GitHub**: `git push origin main`
3. **Version Control**: Track all changes with descriptive commits

### VPS Production Deployment
1. **Pull Latest**: `cd /root/crypto-analysis-dashboard && git reset --hard origin/main`
2. **Restart Service**: `systemctl restart cryptoapi.service`
3. **Verify Deployment**: `curl -s http://127.0.0.1:5050/health | jq`

### Quick Commands

#### Development (Replit)
```bash
# Test local endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/gpts/status

# Run tests
python -m pytest tests/
```

#### GitHub (Replit Terminal)
```bash
git add .
git commit -m "feat: add new functionality"  
git push origin main
```

#### VPS Production
```bash
# Deploy latest changes
cd /root/crypto-analysis-dashboard
bash scripts/deploy-vps.sh

# Manual deployment steps
git reset --hard origin/main
systemctl restart cryptoapi.service
curl -s http://127.0.0.1:5050/health | jq
```

### Project Structure
```
/app.py                 # Flask application factory
/main.py               # Entry point (main:app)
/routes/               # Blueprint routes
  ├── __init__.py      # init_routes() function
  └── health.py        # Health check endpoints
/models/               # SQLAlchemy models
  ├── __init__.py
  └── base.py          # Basic models
/scripts/              # Deployment scripts
  └── deploy-vps.sh    # VPS deployment automation
/tests/                # Test suite
  ├── __init__.py
  └── test_health.py   # Health endpoint tests
/.env.example          # Environment template
/requirements.txt      # Dependencies
/.github/workflows/    # GitHub Actions (optional)
  └── deploy.yml       # Auto-deployment
```

### Environment Configuration
- **Development**: Uses `sqlite:///dev.db` as fallback
- **Production**: Uses Neon PostgreSQL via `DATABASE_URL`
- **Secrets**: Managed via Replit Secrets or VPS environment files

### Monitoring
- **Health Endpoint**: `/health` - Full system check with database
- **Status Endpoint**: `/api/gpts/status` - Lightweight status check
- **Service Status**: `systemctl status cryptoapi.service`
- **Logs**: `journalctl -u cryptoapi.service -f`