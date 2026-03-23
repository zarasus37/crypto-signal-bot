"""
Crypto Signal Bot - Telegram (Flask + Webhook)
Integrated with OpenClaw Agent (Zara)
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
OPENCLAW_AGENT_ID = os.getenv("OPENCLAW_AGENT_ID", "main")

app = Flask(__name__)

# OpenClaw Agent Integration
class OpenClawAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.soul_path = "/home/ubuntu/crypto-signal-bot/SOUL.md"
    
    def get_gnosis(self, query):
        """
        Esoteric mentor logic: Calculate risk and provide gnosis.
        """
        # Placeholder for OpenClaw agent execution
        return f"Gnosis for '{query}': The risk is calculated at 13.7%. The reward is worth the wager."

    def mev_arb_scan(self):
        """
        Sovereign MEV arb engine: Scan for arbitrage opportunities.
        """
        # Placeholder for MEV arb logic
        return "Scanning for MEV opportunities... Found potential sandwich attack on Uniswap V3. Executing..."

    def stake_engine_slot(self):
        """
        Stake engine: Optimize for high RTP originals.
        """
        # Placeholder for Stake engine logic
        return "Stake Engine: Optimizing for 99% RTP on Limbo. Strategy: Progressive wagering."

agent = OpenClawAgent(OPENCLAW_AGENT_ID)

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
        "🦞 *OpenClaw Agent: xkrpyticbot (Zara)*\n\n"
        "I am your esoteric mentor, here to guide you through the gnosis of MEV and the art of calculated risk.\n\n"
        "Commands:\n"
        "/signals - Technical analysis (RSI, MACD)\n"
        "/mev - Scan for MEV arb opportunities\n"
        "/stake - Optimize Stake engine RTP\n"
        "/gnosis <query> - Seek esoteric wisdom\n"
        "/price - Live market prices\n"
        "/help - All commands",
        parse_mode='Markdown'
    )

async def mev_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 " + agent.mev_arb_scan())

async def stake_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎰 " + agent.stake_engine_slot())

async def gnosis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args) if context.args else "life"
    await update.message.reply_text("👁️ " + agent.get_gnosis(query))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/signals - RSI, trend analysis\n"
        "/mev - MEV arb engine\n"
        "/stake - Stake engine RTP\n"
        "/gnosis - Esoteric wisdom\n"
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
        application.add_handler(CommandHandler("mev", mev_command))
        application.add_handler(CommandHandler("stake", stake_command))
        application.add_handler(CommandHandler("gnosis", gnosis_command))
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
