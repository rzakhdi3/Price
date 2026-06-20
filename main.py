import os
import requests
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

def send_telegram(text):
    if not TOKEN:
        print("ERROR: TELEGRAM_TOKEN is empty or not available")
        return

    if not CHAT_ID:
        print("ERROR: CHANNEL_ID is empty or not available")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
    }

    try:
        response = requests.post(url, data=payload, timeout=20)
        print("Telegram status:", response.status_code)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Telegram exception:", repr(e))

if __name__ == "__main__":
    now = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S UTC")

    print("Script started")
    print("TOKEN exists:", bool(TOKEN))
    print("CHAT_ID exists:", bool(CHAT_ID))
    print("CHAT_ID value:", CHAT_ID)

    send_telegram(f"Test message from GitHub Actions\nTime: {now}")

    print("Script finished")
