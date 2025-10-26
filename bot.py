import os
import logging
from flask import Flask, request
from telegram import Bot
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "8386709935:AAHyDsPJs5hSYNDDeYPTPOKf3gam3RB_LDU"
TELEGRAM_CHAT_ID = 5176823610
PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)
bot = Bot(token=TELEGRAM_BOT_TOKEN)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive webhook from TradingView"""
    try:
        data = request.data.decode('utf-8')
        logger.info(f"Webhook received: {data}")
        
        # Parse the alert data
        lines = data.strip().split('\n')
        
        if lines:
            # Format as Telegram message
            message = "🔔 **Top 5 Assets Update**\n\n"
            message += "```
            message += f"{'RANK':<6} {'ASSET':<15} {'SUM':<8}\n"
            message += "─" * 35 + "\n"
            
            for line in lines:
                if line.strip():
                    parts = line.split('|')
                    if len(parts) == 3:
                        rank, asset, sum_val = parts
                        message += f"{rank:<6} {asset:<15} {sum_val:<8}\n"
            
            message += "```"
            
            # Send to Telegram
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
            logger.info("✅ Message sent to Telegram")
            return {"status": "ok"}, 200
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return {"error": str(e)}, 500

@app.route('/')
def home():
    return {"status": "Bot running"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
