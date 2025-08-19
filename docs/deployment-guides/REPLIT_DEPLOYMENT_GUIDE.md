# REPLIT DEPLOYMENT GUIDE - Fixed Configuration

## MASALAH DEPLOYMENT REPLIT YANG UMUM:

### 1. Multiple Ports Issue (FIXED)
**Problem**: .replit file memiliki multiple ports yang menyebabkan deployment failure
**Solution**: Hanya gunakan satu external port (port 80) untuk web access

### 2. Incorrect Build/Run Commands
**Problem**: Commands tidak sesuai dengan Replit requirements
**Solution**: Use proper WSGI configuration

### 3. Environment Variables Missing
**Problem**: API keys tidak tersedia di deployment
**Solution**: Set di Replit Secrets tab

## REPLIT DEPLOYMENT CONFIGURATION:

### Step 1: Deployment Settings
```
Deployment Type: Reserved VM (Recommended for your app)
Build Command: pip install -r requirements-prod.txt
Run Command: gunicorn --bind 0.0.0.0:$PORT wsgi_production:application --workers 2
```

### Step 2: Environment Variables (Secrets Tab)
```
OKX_API_KEY=your_okx_api_key
OKX_SECRET_KEY=your_okx_secret  
OKX_PASSPHRASE=your_okx_passphrase
OPENAI_API_KEY=your_openai_key
FLASK_SECRET_KEY=your_secret_key
```

### Step 3: Port Configuration
- **Internal Port**: 5000 (Flask default)
- **External Port**: 80 (HTTP access)
- **Access URL**: `https://your-app-name.username.repl.co`

## FIXED FILES CREATED:

### 1. wsgi_production.py
- Proper WSGI entry point for Replit
- Uses $PORT environment variable
- Production-ready configuration

### 2. gunicorn.conf.py (Already exists)
- Optimized for Replit deployment
- Proper worker configuration

## DEPLOYMENT STEPS:

### 1. Set Environment Variables:
```
1. Go to Replit project
2. Click "Secrets" tab (🔒 icon)
3. Add required API keys:
   - OKX_API_KEY
   - OKX_SECRET_KEY
   - OKX_PASSPHRASE
   - OPENAI_API_KEY
   - FLASK_SECRET_KEY
```

### 2. Configure Deployment:
```
1. Click "Deploy" button
2. Choose "Reserved VM" (not Autoscale)
3. Build Command: pip install -r requirements-prod.txt
4. Run Command: gunicorn --bind 0.0.0.0:$PORT wsgi_production:application --workers 2
5. Click "Deploy"
```

### 3. Test Deployment:
```
1. Wait for deployment to complete
2. Get deployment URL (e.g., https://crypto-gpts.username.repl.co)
3. Test endpoints:
   - /api/gpts/status
   - /api/gpts/sinyal/tajam?format=narrative
```

## EXPECTED DEPLOYMENT URL:
```
https://your-replit-app.username.repl.co/api/gpts/sinyal/tajam?format=narrative
```

## TROUBLESHOOTING:

### Common Issues & Solutions:

#### ❌ "No traffic getting through"
**Cause**: Wrong port configuration
**Fix**: Ensure using $PORT variable in run command

#### ❌ "Background activities detected"
**Cause**: App has background processes
**Fix**: Use Reserved VM instead of Autoscale

#### ❌ "Build failed"
**Cause**: Missing dependencies
**Fix**: Check requirements-prod.txt contains all packages

#### ❌ "Environment variables not found"
**Cause**: Secrets not set properly
**Fix**: Add all required API keys in Secrets tab

### Debug Commands:
```bash
# Check if app starts locally
python wsgi_production.py

# Test endpoints locally
curl "http://localhost:5000/api/gpts/status"
curl "http://localhost:5000/api/gpts/sinyal/tajam?format=narrative"
```

## ADVANTAGES OF REPLIT DEPLOYMENT:

1. **Auto-scaling**: Handles traffic spikes automatically
2. **HTTPS**: Automatic SSL certificate
3. **Custom Domain**: Can add custom domain
4. **Zero Config**: No server management needed
5. **Global CDN**: Fast access worldwide

## FINAL REPLIT URL STRUCTURE:
```
Production: https://crypto-gpts.username.repl.co/api/gpts/sinyal/tajam?format=narrative
Status: https://crypto-gpts.username.repl.co/api/gpts/status
```

**Ready for ChatGPT Custom GPTs integration dengan Replit URL!**