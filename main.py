import os
import re
import requests
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

URLS = {
    "dollar": "https://call1.tgju.org/ajax.json?rev=2&q=price_dollar_rl",
    "gold": "https://call1.tgju.org/ajax.json?rev=2&q=geram18",
    "silver": "https://call1.tgju.org/ajax.json?rev=2&q=silver",
    "tether": "https://api.nobitex.ir/market/stats?src=usdt&dst=rls",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.tgju.org/",
    "Origin": "https://www.tgju.org",
}


def extract_number(text):
    if text is None:
        return None
    s = str(text)
    m = re.search(r"[\d][\d,]*", s)
    if not m:
        return None
    return m.group(0)


def walk_find_price(obj):
    """
    به صورت بازگشتی در کل JSON می‌گردد و اولین مقدار عددی معقول را برمی‌گرداند.
    """
    preferred_keys = [
        "p", "price", "current", "last", "latest", "value", "close",
        "sell", "buy", "now", "amount", "rate", "price_now"
    ]

    if isinstance(obj, dict):
        # اول کلیدهای مهم
        for k in preferred_keys:
            if k in obj:
                found = walk_find_price(obj[k])
                if found is not None:
                    return found

        # بعد همه اعضا
        for v in obj.values():
            found = walk_find_price(v)
            if found is not None:
                return found

    elif isinstance(obj, list):
        for item in obj:
            found = walk_find_price(item)
            if found is not None:
                return found

    elif isinstance(obj, (int, float)):
        return f"{int(obj):,}"

    elif isinstance(obj, str):
        num = extract_number(obj)
        if num:
            try:
                return f"{int(num.replace(',', '')):,}"
            except:
                return num

    return None


def fetch_json(url):
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json()


def get_tgju_value(url):
    try:
        data = fetch_json(url)

        # لاگ برای دیباگ
        print("TGJU RAW:", data)

        # اول تلاش مستقیم
        price = walk_find_price(data)

        # اگر هنوز پیدا نشد، چند مسیر رایج دیگر را امتحان کن
        if price is None and isinstance(data, dict):
            for key in ["current", "data", "result", "value", "response", "stats"]:
                if key in data:
                    price = walk_find_price(data[key])
                    if price is not None:
                        break

        return price or "دریافت نشد"

    except Exception as e:
        print(f"TGJU ERROR: {url} => {e}")
        return "دریافت نشد"


def get_tether_value():
    try:
        data = fetch_json(URLS["tether"])

        # لاگ برای دیباگ
        print("NOBITEX RAW:", data)

        price = None

        if isinstance(data, dict):
            # مسیرهای رایج در Nobitex
            if "stats" in data and isinstance(data["stats"], dict):
                for key in ["usdt-rls", "USDT-RLS", "usdt_rls"]:
                    if key in data["stats"]:
                        price = walk_find_price(data["stats"][key])
                        if price is not None:
                            break

            if price is None:
                price = walk_find_price(data)

        return price or "دریافت نشد"

    except Exception as e:
        print(f"NOBITEX ERROR: {e}")
        return "دریافت نشد"


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
    }
    r = requests.post(url, data=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    dollar = get_tgju_value(URLS["dollar"])
    gold = get_tgju_value(URLS["gold"])
    silver = get_tgju_value(URLS["silver"])
    tether = get_tether_value()

    # اگر خواستی تاریخ شمسی دقیق هم اضافه کنیم، بعداً می‌تونم نسخه شمسی‌شده بدم
    time_str = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

    message = f"""📈 بروزرسانی بازار

💵 دلار: {dollar}
₮ تتر: {tether}
🥇 طلای 18 عیار: {gold}
🥈 نقره: {silver}

🕒 {time_str}"""

    print(message)
    send_telegram(message)


if __name__ == "__main__":
    main()
