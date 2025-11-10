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

# Color coding for ranks
RANK_COLORS = {
    1: "🥇",  # Gold
    2: "🥈",  # Silver
    3: "🥉",  # Bronze
    4: "4️⃣",
    5: "5️⃣"
}

# Gradient colors for sum values
def get_sum_color(sum_val, max_sum):
    """Return emoji based on sum value intensity"""
    ratio = sum_val / max_sum if max_sum > 0 else 0
    if ratio >= 0.95:
        return "🔴"  # Red - highest
    elif ratio >= 0.85:
        return "🟠"  # Orange
    elif ratio >= 0.75:
        return "🟡"  # Yellow
    else:
        return "🟢"  # Green

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
                        rank_int = int(rank)
                        sum_int = int(sum_val)
                        assets_list.append({
                            'rank': rank_int,
                            'asset': asset.strip(),
                            'sum': sum_int
                        })
                    except Exception as e:
                        logger.error(f"Parse error: {e}")
                        continue

        # Filter for ranks 1-5
        filtered = [item for item in assets_list if 1 <= item['rank'] <= 5]
        
        # Sort by rank ONLY
        filtered.sort(key=lambda x: x['rank'])

        if filtered:
            # Get max sum for color gradient
            max_sum = max([item['sum'] for item in filtered])
            
            # Build professional message
            message = "╔══════════════════════════════════╗\n"
            message += "║  <b>🎯 TOP 5 MEMES</b>               ║\n"
            message += "╚══════════════════════════════════╝\n\n"
            
            for i, item in enumerate(filtered):
                rank_emoji = RANK_COLORS.get(item['rank'], "•")
                sum_emoji = get_sum_color(item['sum'], max_sum)
                
                # Create bar representation
                bar_length = int((item['sum'] / max_sum) * 10)
                bar = "█" * bar_length + "░" * (10 - bar_length)
                
                message += f"{rank_emoji} <b>{item['asset']}</b>\n"
                message += f"   {sum_emoji} Score: <code>{item['sum']}</code>  {bar}\n"
                
                if i < len(filtered) - 1:
                    message += "\n"
            
            message += "\n" + "─" * 34 + "\n"
            message += f"📊 <i>Updated: {__import__('datetime').datetime.now().strftime('%H:%M:%S')}</i>"
            
            send_telegram_message(message)
            logger.info(f"Professional message sent with {len(filtered)} assets")
        else:
            logger.info("No assets found for rank 1-5.")

        return {"status": "ok"}, 200

    except Exception as e:
        logger.error(f"Error: {e}")
        return {"error": str(e)}, 500

@app.route('/')
def home():
    return {"status": "Bot running"}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)
