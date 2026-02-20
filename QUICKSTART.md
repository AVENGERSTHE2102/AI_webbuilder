# Zero-Code AI App Builder - Quick Start Guide

Get your app builder running in **3 minutes**. ⚡

---

## Step 1: Get Your API Key (1 minute)

1. Visit https://console.anthropic.com/
2. Sign up or log in
3. Go to **API Keys** section
4. Click **Create Key**
5. Copy your API key

---

## Step 2: Configure Environment (30 seconds)

```bash
cd zero_code_builder/backend
cp .env.example .env
```

Edit `backend/.env` and add your API key:
```env
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
```

Save and close.

---

## Step 3: Start Backend (1 minute)

**Terminal 1**:
```bash
cd zero_code_builder/backend
pip install -r requirements.txt
python main.py
```

You should see:
```
🚀 Zero-Code AI App Builder - Backend Server
🌐 Server: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
```

Leave this terminal running.

---

## Step 4: Start Frontend (1 minute)

**Terminal 2** (new terminal):
```bash
cd zero_code_builder/frontend
npm install
npm run dev
```

You should see:
```
  VITE ready in XXX ms

  ➜  Local:   http://localhost:5173/
```

Your browser should open automatically to http://localhost:5173

---

## Step 5: Generate Your First App (30 seconds)

1. In the browser at http://localhost:5173
2. In the text box, enter:
   ```
   A recipe manager with ingredients and cooking steps
   ```
3. Click **✨ Generate App**
4. Wait ~20-30 seconds
5. Click **📥 Download ZIP**
6. Extract the ZIP file

---

## Step 6: Test Your Generated App (2 minutes)

**Terminal 3**:
```bash
cd recipe_manager_xxxxx/backend
pip install -r requirements.txt
python main.py
```

**Terminal 4**:
```bash
cd recipe_manager_xxxxx/frontend
npm install
npm run dev
```

Open http://localhost:5173 and:
- Add a recipe with ingredients
- See it appear in the list
- Click delete to remove it

**✅ SUCCESS! You've generated a working full-stack app!**

---

## 🎯 Try More Examples

Go back to http://localhost:5173 and try:

- "A todo list app with tasks and priorities"
- "A contact manager with names, emails, and phone numbers"
- "A book tracker with title, author, and reading status"
- "A workout log with exercises, sets, and reps"

Each one generates a complete, working app in ~30 seconds.

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version (needs 3.8+)
python --version

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version (needs 18+)
node --version

# Clear and reinstall
rm -rf node_modules
npm install
```

### "API key not found" error
- Check `backend/.env` file exists
- Verify API key starts with `sk-ant-`
- No quotes around the key in .env

### Generation fails
- Check backend terminal for error logs
- Verify API key is valid
- Try a simpler description
- Check internet connection

---

## 📚 What Next?

- Read [README.md](README.md) for full documentation
- Check [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) for architecture details
- Review [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) before submission
- Explore the code in `backend/` and `frontend/`

---

## 💡 Tips

- Keep descriptions short (10-100 words)
- Be specific about fields you want
- Mention data types if important
- Try the example prompts first

---

## ⚡ That's It!

You now have:
- ✅ A working AI app builder
- ✅ A generated full-stack app
- ✅ Understanding of the workflow

**Total time: < 10 minutes** from zero to working app.

Happy building! 🚀
