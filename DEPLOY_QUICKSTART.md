# Deploy to Render - Quick Start

**Deploy your Zero-Code AI App Builder in 5 minutes!**

---

## 🚀 Step-by-Step

### 1. Push to GitHub (2 minutes)

```bash
cd zero_code_builder

# Initialize git
git init
git add .
git commit -m "Initial commit: Zero-Code AI App Builder"

# Create GitHub repo and push
# Go to github.com → New Repository → "zero-code-builder"
git remote add origin https://github.com/YOUR_USERNAME/zero-code-builder.git
git branch -M main
git push -u origin main
```

### 2. Deploy to Render (3 minutes)

1. **Visit**: https://dashboard.render.com/

2. **New Blueprint**:
   - Click **"New"** → **"Blueprint"**
   - Connect GitHub (if needed)
   - Select repository: `zero-code-builder`
   - Render detects `render.yaml` automatically ✅

3. **Configure**:
   - Service Group Name: `zero-code-builder`
   - Click **"Apply"**

4. **Set API Key**:
   - Go to backend service settings
   - Add environment variable:
     - Key: `ANTHROPIC_API_KEY`
     - Value: `your_api_key_here`
   - Click **"Save"**

5. **Wait for Deploy**:
   - Backend: ~2 minutes
   - Frontend: ~1 minute
   - Both should show "Live" 🟢

### 3. Test Your Deployment

1. **Visit Frontend URL**:
   - `https://zero-code-builder-frontend.onrender.com`

2. **Generate an App**:
   - Enter: "A todo list app"
   - Click **Generate App**
   - Wait ~30 seconds
   - ✨ See it running live!

3. **Verify**:
   - Live preview works
   - Debug console shows logs
   - Download ZIP works
   - **Success!** 🎉

---

## 📋 URLs You'll Get

- **Frontend**: `https://zero-code-builder-frontend.onrender.com`
- **API**: `https://zero-code-builder-api.onrender.com`
- **API Docs**: `https://zero-code-builder-api.onrender.com/docs`

---

## ⚠️ Important Notes

### Free Tier Limitations
- Backend **spins down** after 15 min of inactivity
- **Cold start**: ~30s when waking up
- First request might be slow
- After that, runs normally

### Solutions
1. **Upgrade to Starter** ($7/mo) - No spin-down
2. **Add keep-alive** ping service
3. **Show loading message** to users

---

## 🔧 After Deployment

### Update API URL Locally

If you want local frontend to use production API:

```bash
# frontend/.env.local
VITE_API_URL=https://zero-code-builder-api.onrender.com
```

### Monitor Your App

In Render Dashboard:
- Check **Logs** for errors
- Monitor **Metrics** (CPU, Memory)
- Set up **Notifications**

---

## 🔄 Making Updates

Push to GitHub to auto-deploy:

```bash
git add .
git commit -m "Update: New feature"
git push

# Render automatically rebuilds and redeploys! 🚀
```

---

## ❓ Troubleshooting

### Backend Not Starting
- Check `ANTHROPIC_API_KEY` is set
- View logs in Render Dashboard
- Ensure `requirements.txt` is complete

### Frontend Can't Connect
- Check `VITE_API_URL` is set automatically
- Verify backend is running (visit API URL)
- Check browser console for CORS errors

### Slow First Load
- **Normal on free tier!** (Cold start)
- Backend wakes up in ~30s
- Consider upgrade for always-on

---

## 📚 Full Documentation

For detailed docs, see: **[RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md)**

Topics covered:
- Custom domains
- Environment variables
- Security best practices
- Monitoring
- Troubleshooting
- Production tips

---

## 🎉 That's It!

Your Zero-Code AI App Builder is now **LIVE** and accessible to anyone!

**Share your frontend URL** and let others generate apps instantly! 🚀

---

**Need help?**
- [Render Docs](https://render.com/docs)
- [Full Deployment Guide](RENDER_DEPLOYMENT.md)
- [Render Community](https://community.render.com/)
