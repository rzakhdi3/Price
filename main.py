import os
import re
import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
}

TGJU_URLS = {
    "dollar": "https://www.tgju.org/profile/price_dollar_rl",
    "gold": "https://www.tgju.org/profile/geram18",
    "silver": "https://www.tgju.org/profile/silver",
}

TETHER_URLS = [
    "https://www.tgju.org/profile/crypto-tether",
    "https://www.tgju.org/profile/tether",
    "https://www.tgju.org/profile/usdt",
    "https://www.tgju.org/profile/USDT",
]


def english_digits(text):
    if text is None:
        return ""

    fa_digits = "۰۱۲۳۴۵۶۷۸۹"
    ar_digits = "٠١٢٣٤٥٦٧٨٩"
    en_digits = "0123456789"

    for i in range(10):
        text = text.replace(fa_digits[i], en_digits[i])
        text = text.replace(ar_digits[i], en_digits[i])

    return text


def to_persian_digits(text):
    text = str(text)

    en_digits = "0123456789"
    fa_digits = "۰۱۲۳۴۵۶۷۸۹"

    for i in range(10):
        text = text.replace(en_digits[i], fa_digits[i])

    return text


def extract_first_price_from_html(html):
    html = english_digits(html)

    matches = re.findall(r'>([\d,]{5,})<', html)

    if not matches:
        return None

    for item in matches:
        clean = item.replace(",", "").strip()

        if not clean.isdigit():
            continue

        value = int(clean)

        if value < 10000:
            continue

        return value

    return None


def get_tgju_price_rial(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)

        print("URL:", url)
        print("Status:", response.status_code)
        print("Length:", len(response.text))

        if response.status_code != 200:
            return None

        price = extract_first_price_from_html(response.text)
        print("Extracted price:", price)

        return price

    except Exception as e:
        print("Error fetching:", url)
        print("Exception:", repr(e))
        return None


def format_toman(price_rial):
    if price_rial is None:
        return "دریافت نشد"

    toman = int(price_rial / 10)
    formatted = f"{toman:,}"

    return to_persian_digits(formatted)


def get_tether_price_rial(dollar_rial):
    for url in TETHER_URLS:
        price = get_tgju_price_rial(url)

        if price is not None:
            if price >= 100000 and price <= 5000000:
                return price, False

    if dollar_rial is not None:
        return dollar_rial, True

    return None, False


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": text,
    }

    response = requests.post(url, data=data, timeout=20)

    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)


def get_iran_time():
    iran_tz = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(iran_tz)

    date_time = now.strftime("%Y/%m/%d, %H:%M:%S")

    return to_persian_digits(date_time)


def main():
    print("Script started")

    dollar_rial = get_tgju_price_rial(TGJU_URLS["dollar"])
    gold_rial = get_tgju_price_rial(TGJU_URLS["gold"])
    silver_rial = get_tgju_price_rial(TGJU_URLS["silver"])

    tether_rial, tether_is_fallback = get_tether_price_rial(dollar_rial)

    dollar = format_toman(dollar_rial)
    tether = format_toman(tether_rial)
    gold = format_toman(gold_rial)
    silver = format_toman(silver_rial)

    now = get_iran_time()

    tether_label = "₮ تتر"

    if tether_is_fallback:
        tether_label = "₮ تتر تقریبی"

    message_lines = [
        "📈 بروزرسانی بازار - تومان",
        "",
        "💵 دلار: " + dollar,
        tether_label + ": " + tether,
        "🥇 طلای ۱۸ عیار: " + gold,
        "🥈 نقره: " + silver,
        "",
        "🕒 " + now,
    ]

    message = "\n".join(message_lines)

    print("Message:")
    print(message)

    send_telegram(message)

    print("Script finished")


if __name__ == "__main__":
    main()
