import os
import re
import json
import requests
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

TGJU_URLS = {
    "dollar": "https://call1.tgju.org/ajax.json?rev=2&q=price_dollar_rl",
    "gold": "https://call1.tgju.org/ajax.json?rev=2&q=geram18",
    "silver": "https://call1.tgju.org/ajax.json?rev=2&q=silver",
}

NOBITEX_URL = "https://api.nobitex.ir/market/stats?src=usdt&dst=rls"


def extract_price_from_anywhere(data):
    """
    تلاش می‌کند از هر ساختار JSON، اولین قیمت معتبر را پیدا کند.
    """
    if isinstance(data, dict):
        # کلیدهای محتمل
        for key in ["price", "current", "last", "latest", "value", "p", "close", "sell", "buy"]:
            if key in data:
                val = data[key]
                extracted = extract_price_from_anywhere(val)
                if extracted is not None:
                    return extracted

        # پیمایش همه مقادیر
        for v in data.values():
            extracted = extract_price_from_anywhere(v)
            if extracted is not None:
                return extracted

    elif isinstance(data, list):
        for item in data:
            extracted = extract_price_from_anywhere(item)
            if extracted is not None:
                return extracted

    elif isinstance(data, (str, int, float)):
        s = str(data)
        # عدد داخل رشته
        m = re.search(r"[\d,]+", s)
        if m:
            return m.group(0)

    return None


def format_number(value):
    if value is None:
        return "دریافت نشد"
    s = str(value).replace(",", "").strip()
    try:
        n = int(float(s))
        return f"{n:,}"
    except:
        return value


def get_tgju_price(url):
    try:
        r = requests.get(url, timeout=20, headers={
            "User-Agent": "Mozilla/5.0"
        })
        r.raise_for_status()
        data = r.json()
        price = extract_price_from_anywhere(data)
        return format_number(price)
    except Exception as e:
        print(f"TGJU error for {url}: {e}")
        return "دریافت نشد"


def get_nobitex_price():
    try:
        r = requests.get(NOBITEX_URL, timeout=20, headers={
            "User-Agent": "Mozilla/5.0"
        })
        r.raise_for_status()
        data = r.json()

        # ساختار معمول nobitex
        price = None
        if isinstance(data, dict):
            if "stats" in data and isinstance(data["stats"], dict):
                # معمولاً کلید usdt-rls
                for key in ["usdt-rls", "USDT-RLS", "usdt_rls"]:
                    if key in data["stats"]:
                        price = extract_price_from_anywhere(data["stats"][key])
                        break

            if price is None:
                price = extract_price_from_anywhere(data)

        return format_number(price)
    except Exception as e:
        print(f"Nobitex error: {e}")
        return "دریافت نشد"


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }
    r = requests.post(url, data=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    dollar = get_tgju_price(TGJU_URLS["dollar"])
    tether = get_nobitex_price()
    gold = get_tgju_price(TGJU_URLS["gold"])
    silver = get_tgju_price(TGJU_URLS["silver"])

    time_str = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

    message = f"""📈 بروزرسانی بازار

💵 دلار: {dollar}
₮ تتر: {tether}
🥇 طلای 18 عیار: {gold}
🥈 نقره: {silver}

🕒 {time_str}"""

    print(message)
    send_message(message)


if __name__ == "__main__":
    main()
