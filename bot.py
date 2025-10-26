import os
import logging
from flask import Flask, request
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = "8386709935:AAHyDsPJs5hSYNDDeYPTPOKf3gam3RB_LDU"
TELEGRAM_CHAT_ID = -1003184454690  # Your group chat ID
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
        
        if lines:
            # Parse and sort by rank
            assets_list = []
            for line in lines:
                if line.strip():
                    parts = line.split('|')
                    if len(parts) == 3:
                        rank, asset, sum_val = parts
                        assets_list.append({
                            'rank': int(rank),
                            'asset': asset,
                            'sum': sum_val
                        })
            
            # Sort by rank (1-5)
            assets_list.sort(key=lambda x: x['rank'])
            
            # Format message
            message = "<b>🔔 Top 5 Assets Update</b>\n\n"
            message += "<pre>RANK  ASSET           SUM\n"
            message += "-----------------------------------\n"
            
            for item in assets_list:
                message += f"{item['rank']:<6}{item['asset']:<15}{item['sum']:<8}\n"
            
            message += "</pre>"
            
            result = send_telegram_message(message)
            logger.info(f"Message sent: {result}")
            return {"status": "ok"}, 200
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}, 500

@app.route('/')
def home():
    return {"status": "Bot running"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)


