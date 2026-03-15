# Deployment Guide

## Prerequisites
- Telegram Bot Token: ✅ Configured
- GitHub Account: ✅ zarasus37

## Step 1: Push to GitHub

1. Go to https://github.com
2. Create new repository: "crypto-signal-bot"
3. Push this folder:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/zarasus37/crypto-signal-bot.git
git push -u origin main
```

## Step 2: Deploy Free on Render

1. Go to https://render.com
2. Sign up with GitHub (zarasus37)
3. Create new Web Service
4. Connect your GitHub repo
5. Settings:
   - Build Command: (leave blank)
   - Start Command: python bot.py
6. Add Environment Variable:
   - Key: TELEGRAM_BOT_TOKEN
   - Value: 8489370163:AAHej0vWX9ydoVTW4dxlxEr2pFbe8NnErNA
7. Deploy

## Step 3: Test Your Bot

Once deployed, open Telegram and message your bot:
- Send /start
- Send /signals

---

## Alternative: Run Locally

```bash
cd C:\Users\crisc\Dev\passive-income\crypto-signal-bot
pip install -r requirements.txt
python bot.py
```
