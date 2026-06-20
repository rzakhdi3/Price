import requests
import json
import os
import re

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHANNEL_ID")

PRICE_FILE = "previous_prices.json"


def get_prices():
    url = "https://www.tgju.org/"
    r = requests.get(url, timeout=20)
    html = r.text

    prices = {}

    patterns = {
        "dollar": r"price_dollar_rl.*?(\d[\d,]+)",
        "gold18": r"price_geram18.*?(\d[\d,]+)",
        "bitcoin": r"price_bitcoin.*?(\d[\d,]+)",
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, html)
        if m:
            prices[key] = m.group(1)

    return prices


def load_previous():
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE) as f:
            return json.load(f)
    return {}


def save_prices(prices):
    with open(PRICE_FILE, "w") as f:
        json.dump(prices, f)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)


def build_message(new, old):
    msg = "📊 بروزرسانی قیمت بازار\n\"

    names = {
        "dollar": "💵 دلار",
        "gold18": "🥇 طلا ۱۸",
        "bitcoin": "₿ بیتکوین"
    }

    for k in new:
        if k not in old:
            msg += f"{names[k]} : {new[k]} 🆕\n"
        else
