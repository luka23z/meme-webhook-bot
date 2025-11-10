import os
import logging
from flask import Flask, request
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "8386709935:AAHyDsPJs5hSYNDDeYPTPOKf3gam3RB_LDU"
TELEGRAM_CHAT_ID = -1003184454690
PORT = int(os.environ.get('PORT', 5000))

app = Flask(__name__)

def send_telegram_message(text):
    """Send message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, data=data, timeout=10)
        logger.info(f"Telegram response: {response.status_code}")
        return response.json()
    except Exception as e:
        logger.error(f"Telegram error: {e}")
        return None

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.data.decode('utf-8')
        logger.info(f"Webhook received: {data}")

        lines = data.strip().split('\n')

        assets_list = []
        for line in lines:
            if line.strip():
                parts = line.split('|')
                if len(parts) == 3:
                    rank, asset, sum_val = parts
                    try:
                        sum_int = int(sum_val)
                        assets_list.append({
                            'asset': asset.strip(),
                            'sum': sum_int
                        })
                    except Exception as e:
                        logger.error(f"Parse error: {e}")
                        continue

        if not assets_list:
            logger.info("No assets received.")
            return {"status": "ok"}, 200

        # Sort by sum (score) descending
        sorted_assets = sorted(assets_list, key=lambda x: x['sum'], reverse=True)
        
        # Take top 5
        top_5 = sorted_assets[:5]
        
        # Get max sum for bar scaling
        max_sum = max([item['sum'] for item in top_5])
        
        # Build premium message
        message = "╔═══════════════════════════════════════╗\n"
        message += "║ 🎯 <b>TOP 5 MEMES</b>  |  📊 <b>QUANT SYSTEM</b> ║\n"
        message += "╚═══════════════════════════════════════╝\n\n"
        
        for item in top_5:
            # Create green bar
            bar_length = int((item['sum'] / max_sum) * 10)
            bar = "🟩" * bar_length + "⬜" * (10 - bar_length)
            
            message += f"<b>{item['asset']}</b>\n"
            message += f"Score: <b><u>{item['sum']}</u></b>  {bar}\n\n"
        
        send_telegram_message(message)
        logger.info(f"Message sent with top 5 assets")

        return {"status": "ok"}, 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}, 500

@app.route('/')
def home():
    return {"status": "Bot running"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
