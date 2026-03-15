"""
Crypto Signal Bot - Telegram (Flask + Webhook)
Deploy on Render with webhook
"""

import os
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext
import ccxt
import pandas as pd
import numpy as np

# Config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

app = Flask(__name__)

# Initialize exchange
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'},
})

PAIRS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT']

# Global application
application = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Crypto Signal Bot\n\n"
        "/signals - Get current signals\n"
        "/price - Quick prices\n"
        "/help - Commands"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/signals - RSI, trend analysis\n"
        "/price - Live prices\n"
        "/subscribe - Premium info"
    )

async def signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Analyzing markets...")
    
    signals = []
    
    for pair in PAIRS[:5]:
        try:
            ohlcv = exchange.fetch_ohlcv(pair, '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            sma20 = df['close'].rolling(20).mean().iloc[-1]
            sma50 = df['close'].rolling(50).mean().iloc[-1]
            
            signal = "🟢 BUY" if rsi < 30 else "🔴 SELL" if rsi > 70 else "🟡 NEUTRAL"
            trend = "📈" if sma20 > sma50 else "📉"
            
            signals.append(f"{pair}: RSI({rsi:.0f}) {signal} {trend}")
            
        except:
            signals.append(f"{pair}: Error")
    
    msg = "📊 *Crypto Signals*\n\n" + "\n".join(signals)
    await update.message.reply_text(msg, parse_mode='Markdown')

async def price_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = []
    for pair in PAIRS:
        try:
            ticker = exchange.fetch_ticker(pair)
            price = ticker['last']
            change = ticker['percentage']
            emoji = "🟢" if change > 0 else "🔴"
            prices.append(f"{pair}: ${price:,.2f} {emoji}{change:.1f}%")
        except:
            prices.append(f"{pair}: Error")
    
    await update.message.reply_text("💰 *Prices*\n\n" + "\n".join(prices[:5]), parse_mode='Markdown')

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⭐ *Premium*\n\n"
        "$5/month:\n"
        "- All pairs\n"
        "- Real-time alerts\n\n"
        "Contact @yourhandle"
    )

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Handle incoming Telegram updates"""
    global application
    
    if application is None:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("signals", signals_command))
        application.add_handler(CommandHandler("price", price_command))
        application.add_handler(CommandHandler("subscribe", subscribe_command))
        await application.initialize()
    
    try:
        update = Update.de_json(request.json(), application.bot)
        await application.process_update(update)
    except Exception as e:
        print(f"Error processing update: {e}")
    
    return jsonify({'status': 'ok'})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
