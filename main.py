import requests
import json
import os
import re

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHANNEL_ID")

PRICE_FILE = "previous_prices.json"


def extract_price(html, key):
    pattern = rf'data-market-names="{key}".*?data-last-price="([\d,]+)"'
    m = re.search(pattern, html)
    if m:
        return m.group(1)
    return None


def get_prices():
    url = "https://www.tgju.org/"
    r = requests.get(url, timeout=20)
    html = r.text

    prices = {}

    markets = {
        "price_dollar_rl": "dollar",
        "price_geram18": "gold18",
        "price_bitcoin": "bitcoin",
        "price_tether": "tether"
    }

    for key, name in markets.items():
        p = extract_price(html, key)
        if p:
            prices[name] = p

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
        "text": text
    }

    requests.post(url, data=data)


def build_message(new, old):
    names = {
        "dollar": "💵 دلار",
        "gold18": "🥇 طلا ۱۸",
        "bitcoin": "₿ بیتکوین",
        "tether": "💲 تتر"
    }

    msg = "📊 بروزرسانی قیمت بازار\n\n"
    changed = False

    for k, v in new.items():

        if k not in old:
            msg += f"{names[k]} : {v} 🆕\n"
            changed = True

        elif old[k] != v:
            msg += f"{names[k]} : {v} 🔄\n"
            changed = True

    if changed:
        return msg

    return None


def main():

    new_prices = get_prices()
    old_prices = load_previous()

    message = build_message(new_prices, old_prices)

    if message:
        send_telegram(message)

    save_prices(new_prices)


if __name__ == "__main__":
    main()
