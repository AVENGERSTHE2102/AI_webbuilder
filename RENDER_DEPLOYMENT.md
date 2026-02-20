# Deploy to Render - Blueprint Guide

Deploy your Zero-Code AI App Builder to Render using Infrastructure as Code (Blueprint).

---

## 🚀 Quick Deploy (5 Minutes)

### Prerequisites
- GitHub account
- Render account (free tier works!)
- Anthropic API key

---

## Step 1: Push to GitHub

```bash
cd zero_code_builder

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Zero-Code AI App Builder with Live Preview"

# Create GitHub repo and push
# (Replace with your GitHub username and repo name)
git remote add origin https://github.com/YOUR_USERNAME/zero-code-builder.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Render

### Option A: One-Click Deploy (Recommended)

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com/

2. **New Blueprint Instance**
   - Click **"New"** → **"Blueprint"**
   - Connect your GitHub account if not already connected
   - Select your repository: `zero-code-builder`
   - Render will detect the `render.yaml` file automatically

3. **Configure Service Group**
   - Name: `zero-code-builder`
   - Click **"Apply"**

4. **Set Environment Variables**
   - In the backend service settings, add:
     - `ANTHROPIC_API_KEY` = `your_api_key_here`
   - Click **"Save"**

5. **Deploy**
   - Render will automatically build and deploy both services
   - Backend: Python/FastAPI web service
   - Frontend: Static site (Vite build)

### Option B: Manual Blueprint Deploy

```bash
# Install Render CLI (optional)
brew install render  # macOS
# or
npm install -g @renderinc/cli

# Login to Render
render login

# Deploy blueprint
render blueprint launch
```

---

## Step 3: Verify Deployment

### Check Services

1. **Backend API**
   - URL: `https://zero-code-builder-api.onrender.com`
   - Test: Visit `https://zero-code-builder-api.onrender.com/`
   - Should return: `{"status": "online", ...}`

2. **Frontend**
   - URL: `https://zero-code-builder-frontend.onrender.com`
   - Should show the app builder UI

### Test End-to-End

1. Visit your frontend URL
2. Enter description: "A todo list app"
3. Click **Generate App**
4. Should see live preview in ~30 seconds
5. Test the generated app
6. Download ZIP if needed

---

## 📋 What Gets Deployed

### Backend Service
```yaml
Type: Web Service
Runtime: Python 3.11
Build: pip install -r requirements.txt
Start: uvicorn main:app --host 0.0.0.0 --port $PORT
Health Check: GET /
Region: Oregon (Free tier)
```

### Frontend Service
```yaml
Type: Static Site
Runtime: Node 18
Build: npm install && npm run build
Publish: ./dist
Routes: SPA (/* → /index.html)
Region: Oregon (Free tier)
```

---

## 🔧 Configuration

### Environment Variables

**Backend (`zero-code-builder-api`)**:
- `ANTHROPIC_API_KEY` - Your Claude API key (Required)
- `PORT` - Auto-set by Render
- `HOST` - `0.0.0.0`
- `PYTHON_VERSION` - `3.11.0`

**Frontend (`zero-code-builder-frontend`)**:
- `VITE_API_URL` - Auto-set from backend service URL
- `NODE_VERSION` - `18.18.0`

### Auto-Configuration

The `render.yaml` blueprint automatically:
✅ Links frontend to backend (via `VITE_API_URL`)
✅ Sets correct build commands
✅ Configures health checks
✅ Sets up SPA routing
✅ Enables CORS
✅ Uses free tier

---

## 🔄 Updates & Redeployment

### Automatic Deploys

Render automatically redeploys when you push to GitHub:

```bash
# Make changes to code
git add .
git commit -m "Update: Added new feature"
git push

# Render will automatically:
# 1. Detect the push
# 2. Rebuild both services
# 3. Deploy new version
```

### Manual Redeploy

In Render Dashboard:
1. Go to service (backend or frontend)
2. Click **"Manual Deploy"**
3. Select branch: `main`
4. Click **"Deploy"**

---

## 💰 Pricing

### Free Tier (What You Get)
- ✅ Backend: 750 hours/month (enough for 24/7)
- ✅ Frontend: Unlimited bandwidth
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Auto-deploy from Git
- ⚠️ Backend spins down after 15 min inactivity
- ⚠️ Cold start: ~30s when spinning up

### Upgrading

If you need always-on:
- **Starter Plan**: $7/month per service
  - No spin-down
  - Faster builds
  - More resources

---

## 🐛 Troubleshooting

### Backend Won't Start

**Check Logs**:
1. Go to Render Dashboard
2. Click backend service
3. Check **"Logs"** tab
4. Look for Python errors

**Common Issues**:
- ❌ Missing `ANTHROPIC_API_KEY` → Set in environment variables
- ❌ Port binding error → Ensure using `$PORT` variable
- ❌ Module not found → Check `requirements.txt`

**Fix**:
```bash
# Verify requirements.txt includes all dependencies
cat backend/requirements.txt

# Should have:
# fastapi==0.115.0
# uvicorn[standard]==0.30.6
# pydantic==2.6.4
# httpx==0.27.0
# python-dotenv==1.0.1
```

### Frontend Won't Build

**Check Logs**:
1. Go to Render Dashboard
2. Click frontend service
3. Check **"Logs"** tab

**Common Issues**:
- ❌ `npm install` fails → Check `package.json`
- ❌ Build errors → Check Vite config
- ❌ API calls fail → Check `VITE_API_URL` is set

**Fix**:
```bash
# Test build locally first
cd frontend
npm install
npm run build

# Should create dist/ folder
ls dist/
```

### API Connection Issues

**CORS Errors**:
- Ensure backend has CORS middleware enabled
- Check `main.py` has:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],  # For production, specify frontend URL
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```

**Wrong API URL**:
- Check frontend environment variable
- Should be: `https://zero-code-builder-api.onrender.com`
- Not: `http://localhost:8000`

### Cold Starts (Free Tier)

**Issue**: Backend takes 30s to respond after inactivity

**Solutions**:
1. **Upgrade to Starter plan** ($7/mo) - No spin-down
2. **Use a keep-alive service**:
   - UptimeRobot (free)
   - Ping your API every 10 minutes
3. **Add loading message**: "Waking up server... (~30s)"

---

## 🔒 Security Best Practices

### Environment Variables
- ✅ Never commit `.env` files
- ✅ Set `ANTHROPIC_API_KEY` in Render Dashboard only
- ✅ Use Render's encrypted secret storage

### CORS Configuration
For production, update `main.py`:
```python
# Instead of allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://zero-code-builder-frontend.onrender.com",
        "https://your-custom-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Rate Limiting
Add rate limiting to prevent abuse:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/generate")
@limiter.limit("10/hour")  # 10 requests per hour
async def generate_app(request: GenerateRequest):
    # ... existing code
```

---

## 📊 Monitoring

### Render Dashboard

**Metrics Available**:
- CPU usage
- Memory usage
- Request count
- Response times
- Error rates

**Logs**:
- Real-time log streaming
- Filter by service
- Search logs
- Download logs

### Health Checks

Render automatically monitors:
- Backend: `GET /` every 30s
- If fails 3 times → Service restarted
- Email notifications on failures

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain

1. **Go to Frontend Service**
   - Click **"Settings"** → **"Custom Domain"**

2. **Add Domain**
   - Enter: `app.yourdomain.com`
   - Follow DNS instructions

3. **Update CORS**
   - Add custom domain to backend CORS whitelist

4. **HTTPS**
   - Render automatically provisions SSL certificate
   - Free via Let's Encrypt

---

## 🚀 Deployment Checklist

Before deploying:

- [ ] Code pushed to GitHub
- [ ] `render.yaml` in repository root
- [ ] `.gitignore` includes `.env` and `node_modules`
- [ ] `ANTHROPIC_API_KEY` ready
- [ ] Backend builds locally: `pip install -r requirements.txt`
- [ ] Frontend builds locally: `npm run build`
- [ ] All tests pass
- [ ] README updated with deployment URLs

After deploying:

- [ ] Backend health check passes
- [ ] Frontend loads correctly
- [ ] API connection works (check browser console)
- [ ] Generate a test app end-to-end
- [ ] Live preview works
- [ ] Download ZIP works
- [ ] Debug console captures logs
- [ ] No CORS errors
- [ ] Environment variables set correctly

---

## 📝 Render.yaml Explained

```yaml
services:
  # Backend API
  - type: web                    # Web service (not static)
    name: zero-code-builder-api  # Service name in Render
    runtime: python              # Python runtime
    plan: free                   # Free tier
    buildCommand: pip install... # Install dependencies
    startCommand: uvicorn...     # Start FastAPI server
    healthCheckPath: /           # Health check endpoint
    envVars:                     # Environment variables
      - key: ANTHROPIC_API_KEY
        sync: false              # Set manually in dashboard

  # Frontend Static Site
  - type: web                    # Web service for static
    name: zero-code-builder-frontend
    runtime: node                # Node.js runtime
    buildCommand: npm install... # Build command
    staticPublishPath: ./dist    # Serve from dist/
    routes:                      # SPA routing
      - type: rewrite
        source: /*
        destination: /index.html # Redirect all to index.html
    envVars:
      - key: VITE_API_URL        # Auto-set from backend
        fromService:
          name: zero-code-builder-api
          envVarKey: RENDER_EXTERNAL_URL
```

---

## 🎉 Success!

Your Zero-Code AI App Builder is now live at:
- **Frontend**: `https://zero-code-builder-frontend.onrender.com`
- **API**: `https://zero-code-builder-api.onrender.com`

Share the frontend URL with anyone - they can generate apps instantly!

---

## 📚 Additional Resources

- [Render Blueprints Docs](https://render.com/docs/blueprint-spec)
- [Render Python Guide](https://render.com/docs/deploy-fastapi)
- [Render Static Sites](https://render.com/docs/static-sites)
- [Environment Variables](https://render.com/docs/environment-variables)
- [Custom Domains](https://render.com/docs/custom-domains)

---

## 💡 Pro Tips

1. **Use GitHub Actions** for testing before deploy
2. **Set up staging environment** using branch deploys
3. **Monitor API usage** to stay within Anthropic limits
4. **Add analytics** (Plausible, Google Analytics)
5. **Set up error tracking** (Sentry)
6. **Use Redis** for caching generated apps (upgrade needed)

---

**Need help?** Check Render's excellent documentation or community forum!

Happy deploying! 🚀
