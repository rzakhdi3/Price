import requests
import os
import re

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHANNEL_ID")


def get_prices():
    url = "https://www.tgju.org/"
    r = requests.get(url, timeout=20)
    html = r.text

    def find(pattern):
        m = re.search(pattern, html)
        if m:
            return m.group(1)
        return "نامشخص"

    dollar = find(r"price_dollar_rl.*?(\d[\d,]+)")
    gold = find(r"price_geram18.*?(\d[\d,]+)")
    bitcoin = find(r"price_bitcoin.*?(\d[\d,]+)")

    return dollar, gold, bitcoin


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text
    }

    requests.post(url, data=data)


def main():

    dollar, gold, bitcoin = get_prices()

    message = f"""
📊 قیمت لحظه‌ای بازار

💵 دلار: {dollar}
🥇 طلا ۱۸: {gold}
₿ بیتکوین: {bitcoin}
"""

    send_telegram(message)


if __name__ == "__main__":
    main()
