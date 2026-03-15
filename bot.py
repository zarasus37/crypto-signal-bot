"""
Crypto Signal Bot - Telegram
Deploy free on render.com / railway.app
"""

import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import ccxt
import pandas as pd
import numpy as np

# Config - Set these in your deployment platform
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Initialize exchange
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'spot'},
})

PAIRS = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'DOGE/USDT']

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Crypto Signal Bot\n\n"
        "/signals - Get current signals\n"
        "/price - Quick prices\n"
        "/help - Commands\n\n"
        "Premium: /upgrade for VIP signals"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/signals - RSI, MACD, Volume analysis\n"
        "/price - Live prices\n"
        "/alerts - Set price alerts\n"
        "/subscribe - Premium"
    )

async def signals_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Analyzing markets...")
    
    signals = []
    
    for pair in PAIRS[:5]:  # Free tier: 5 pairs
        try:
            ohlcv = exchange.fetch_ohlcv(pair, '1h', limit=100)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # RSI
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            # Simple Moving Averages
            sma20 = df['close'].rolling(20).mean().iloc[-1]
            sma50 = df['close'].rolling(50).mean().iloc[-1]
            current = df['close'].iloc[-1]
            
            signal = "🟢 BUY" if rsi < 30 else "🔴 SELL" if rsi > 70 else "🟡 NEUTRAL"
            trend = "📈" if sma20 > sma50 else "📉"
            
            signals.append(f"{pair}: RSI({rsi:.0f}) {signal} {trend}")
            
        except Exception as e:
            signals.append(f"{pair}: Error")
    
    msg = "📊 *Crypto Signals*\n\n" + "\n".join(signals)
    msg += "\n\n_Upgrade to Premium for all pairs + alerts_"
    
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
        "- All 50+ pairs\n"
        "- Real-time alerts\n"
        "- MACD, RSI, Bollinger\n"
        "- VIP channel\n\n"
        "Contact @yourhandle to subscribe"
    )

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("signals", signals_command))
    app.add_handler(CommandHandler("price", price_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    
    print("🤖 Bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
