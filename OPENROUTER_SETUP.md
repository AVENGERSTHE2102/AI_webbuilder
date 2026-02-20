# OpenRouter API Setup Guide

Your Zero-Code AI App Builder now uses **OpenRouter** for AI code generation!

---

## 🌟 Why OpenRouter?

**Benefits:**
- ✅ **Pay-per-use** - Only pay for what you use
- ✅ **$5 free credits** - Start for free
- ✅ **Multiple models** - Access to Claude, GPT-4, and more
- ✅ **Better rates** - Often cheaper than direct APIs
- ✅ **No rate limits** - Same as provider limits
- ✅ **One API key** - Access multiple AI models

---

## 🚀 Get Your API Key (2 Minutes)

### Step 1: Create Account
1. Visit: **https://openrouter.ai/**
2. Click **"Sign In"** (top right)
3. Sign up with:
   - Google account, or
   - GitHub account, or
   - Email + password

### Step 2: Add Credits (Optional)
1. Click your profile (top right)
2. Go to **"Credits"**
3. **$5 free credits** automatically added! 🎉
4. Optional: Add more credits if needed
   - $10 minimum purchase
   - Pay with card

### Step 3: Get API Key
1. Go to **"Keys"** tab
2. Click **"Create Key"**
3. Name it: `Zero-Code App Builder`
4. Click **"Create"**
5. **Copy the key** (starts with `sk-or-v1-...`)

⚠️ **Important**: Save this key somewhere safe - you can't see it again!

---

## 🔧 Configure Your App

### Local Development

1. **Create .env file**:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit .env**:
   ```env
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

3. **Save and start**:
   ```bash
   python main.py
   ```

### Render Deployment

1. **Go to Render Dashboard**
2. **Select your backend service** (`ai-webbuilder-api`)
3. **Click "Environment" tab**
4. **Add variable**:
   - Key: `OPENROUTER_API_KEY`
   - Value: `sk-or-v1-your-key-here`
5. **Save** - Service will redeploy automatically

---

## 💰 Pricing

### Free Tier
- **$5 free credits** on signup
- Enough for ~50-100 app generations
- No credit card required

### Claude Sonnet 4 Pricing (via OpenRouter)
- **Input**: $3 per million tokens
- **Output**: $15 per million tokens

**Typical Usage:**
- 1 app generation ≈ 5,000 tokens
- Cost per generation: ~$0.05-0.10
- $5 = 50-100 apps generated

### Add More Credits
- Minimum: $10
- No subscription needed
- Pay only for what you use

---

## 🔄 Switch Between APIs

Your app supports **both** OpenRouter and direct Anthropic API!

### Use OpenRouter (Recommended)
```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
# ANTHROPIC_API_KEY=  # Leave commented
```

### Use Direct Anthropic
```env
# OPENROUTER_API_KEY=  # Comment out
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**Priority**: If both are set, OpenRouter is used.

---

## 📊 Monitor Usage

### OpenRouter Dashboard
1. Visit: https://openrouter.ai/
2. Click **"Activity"** tab
3. See:
   - Requests made
   - Tokens used
   - Cost per request
   - Remaining credits

### Set Spending Limits
1. Go to **"Settings"**
2. Set **monthly limit**
3. Get alerts when approaching limit

---

## 🎯 Models Available

With OpenRouter, you can easily switch models:

**Claude Models:**
- `anthropic/claude-sonnet-4-20250514` (Default - Best balance)
- `anthropic/claude-opus-4-20250514` (Most capable)
- `anthropic/claude-haiku-4-20250514` (Fastest, cheapest)

**OpenAI Models:**
- `openai/gpt-4-turbo`
- `openai/gpt-4o`
- `openai/gpt-3.5-turbo`

**Other Models:**
- Google Gemini
- Meta Llama
- Mistral
- And 100+ more!

**To change model**, edit `generator.py`:
```python
self.model = "anthropic/claude-opus-4-20250514"  # Use Opus instead
```

---

## 🔒 Security Best Practices

### Keep Your Key Safe
- ✅ Never commit `.env` to Git
- ✅ Use environment variables only
- ✅ Rotate keys periodically
- ✅ Use different keys for dev/prod

### .gitignore Already Includes
```
.env
.env.local
.env.production
```

### Render Deployment
- ✅ API key stored encrypted
- ✅ Not visible in logs
- ✅ Only accessible to your service

---

## 🐛 Troubleshooting

### Error: "API key not set"
**Fix**:
```bash
# Check .env file exists
ls backend/.env

# Check key is set
cat backend/.env | grep OPENROUTER

# Should see: OPENROUTER_API_KEY=sk-or-v1-...
```

### Error: "Insufficient credits"
**Fix**:
1. Go to https://openrouter.ai/credits
2. Add more credits ($10 minimum)
3. Wait 1-2 minutes for activation

### Error: "Invalid API key"
**Fix**:
1. Verify key starts with `sk-or-v1-`
2. No quotes in .env file
3. No extra spaces
4. Regenerate key if needed

### Requests Failing
**Check**:
1. Internet connection
2. OpenRouter status: https://status.openrouter.ai/
3. Your credits balance
4. Backend logs for detailed errors

---

## 📚 OpenRouter Resources

- **Website**: https://openrouter.ai/
- **Docs**: https://openrouter.ai/docs
- **Pricing**: https://openrouter.ai/models
- **Status**: https://status.openrouter.ai/
- **Discord**: https://discord.gg/openrouter

---

## ✨ Quick Start Recap

1. **Get API key**: https://openrouter.ai/ → Sign up → Create key
2. **Local**: Add to `backend/.env`
3. **Render**: Add to environment variables
4. **Test**: Generate an app!

**You get $5 free credits - start building now!** 🚀

---

## 🎉 Ready to Use

Your app is configured to use OpenRouter:

**Model**: Claude Sonnet 4 (via OpenRouter)
**Cost**: ~$0.05-0.10 per app generation
**Free Credits**: $5 (50-100 apps)

Get your key and start generating apps! 🎊
