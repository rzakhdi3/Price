import os
import re
import json
import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

PREVIOUS_FILE = "previous_prices.json"

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

    text = str(text)

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


def clean_html_text(html):
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def parse_number(value):
    if value is None:
        return None

    value = english_digits(value)
    value = value.replace(",", "")
    value = value.strip()

    if not value.isdigit():
        return None

    return int(value)


def extract_price_by_patterns(html):
    html = english_digits(html)

    patterns = [
        r'data-col=["\']info\.last_trade\.PDrCotVal["\'][^>]*>\s*([\d,]+)\s*<',
        r'data-col=["\']info\.last_trade\.p["\'][^>]*>\s*([\d,]+)\s*<',
        r'id=["\']main-price["\'][^>]*>\s*([\d,]+)\s*<',
        r'class=["\'][^"\']*value[^"\']*["\'][^>]*>\s*([\d,]+)\s*<',
        r'"PDrCotVal"\s*:\s*"?([\d,]+)"?',
        r'"price"\s*:\s*"?([\d,]+)"?',
    ]

    for pattern in patterns:
        match = re.search(pattern, html)
        if match:
            value = parse_number(match.group(1))
            if value is not None and value >= 10000:
                return value

    return None


def extract_price_near_current_label(html):
    text = clean_html_text(html)
    text = english_digits(text)

    keywords = [
        "نرخ فعلی",
        "قیمت فعلی",
        "آخرین قیمت",
    ]

    for keyword in keywords:
        index = text.find(keyword)

        if index == -1:
            continue

        part = text[index:index + 500]
        matches = re.findall(r"[\d,]{5,}", part)

        for item in matches:
            value = parse_number(item)

            if value is not None and value >= 10000:
                return value

    return None


def extract_first_reasonable_price(html, min_value, max_value):
    html = english_digits(html)

    matches = re.findall(r'>([\d,]{5,})<', html)

    for item in matches:
        value = parse_number(item)

        if value is None:
            continue

        if value >= min_value and value <= max_value:
            return value

    text = clean_html_text(html)
    text = english_digits(text)

    matches = re.findall(r"[\d,]{5,}", text)

    for item in matches:
        value = parse_number(item)

        if value is None:
            continue

        if value >= min_value and value <= max_value:
            return value

    return None


def extract_price_from_html(html, asset_type):
    price = extract_price_by_patterns(html)

    if price is not None:
        return price

    price = extract_price_near_current_label(html)

    if price is not None:
        return price

    if asset_type == "dollar":
        return extract_first_reasonable_price(html, 100000, 5000000)

    if asset_type == "gold":
        return extract_first_reasonable_price(html, 1000000, 500000000)

    if asset_type == "silver":
        return extract_first_reasonable_price(html, 100000, 20000000)

    if asset_type == "tether":
        return extract_first_reasonable_price(html, 100000, 5000000)

    return extract_first_reasonable_price(html, 10000, 500000000)


def get_tgju_price_rial(url, asset_type):
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)

        print("URL:", url)
        print("Status:", response.status_code)
        print("Length:", len(response.text))

        if response.status_code != 200:
            return None

        price = extract_price_from_html(response.text, asset_type)

        print("Asset:", asset_type)
        print("Extracted price rial:", price)

        return price

    except Exception as e:
        print("Error fetching:", url)
        print("Exception:", repr(e))
        return None


def rial_to_toman(price_rial):
    if price_rial is None:
        return None

    return int(price_rial / 10)


def format_toman_value(price_toman):
    if price_toman is None:
        return "دریافت نشد"

    formatted = f"{price_toman:,}"
    return to_persian_digits(formatted)


def format_change(current, previous):
    if current is None:
        return ""

    if previous is None:
        return " 🆕"

    try:
        previous = int(previous)
    except Exception:
        return " 🆕"

    diff = current - previous

    if diff == 0:
        return " ⚪ بدون تغییر"

    abs_diff = abs(diff)
    formatted_diff = to_persian_digits(f"{abs_diff:,}")

    if diff > 0:
        return " 🟢 " + formatted_diff + "+"

    return " 🔴 " + formatted_diff + "-"


def load_previous_prices():
    if not os.path.exists(PREVIOUS_FILE):
        return {}

    try:
        with open(PREVIOUS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except Exception as e:
        print("Could not load previous prices")
        print("Exception:", repr(e))
        return {}


def save_current_prices(prices):
    try:
        with open(PREVIOUS_FILE, "w", encoding="utf-8") as file:
            json.dump(prices, file, ensure_ascii=False, indent=2)

        print("Current prices saved")

    except Exception as e:
        print("Could not save current prices")
        print("Exception:", repr(e))


def get_tether_price_rial(dollar_rial):
    for url in TETHER_URLS:
        price = get_tgju_price_rial(url, "tether")

        if price is not None:
            if price >= 100000 and price <= 5000000:
                return price, False

    if dollar_rial is not None:
        return dollar_rial, True

    return None, False


def send_telegram(text):
    if not TOKEN:
        print("TELEGRAM_TOKEN is empty")
        return

    if not CHAT_ID:
        print("CHANNEL_ID is empty")
        return

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

    previous_prices = load_previous_prices()

    dollar_rial = get_tgju_price_rial(TGJU_URLS["dollar"], "dollar")
    gold_rial = get_tgju_price_rial(TGJU_URLS["gold"], "gold")
    silver_rial = get_tgju_price_rial(TGJU_URLS["silver"], "silver")

    tether_rial, tether_is_fallback = get_tether_price_rial(dollar_rial)

    current_prices = {
        "dollar": rial_to_toman(dollar_rial),
        "tether": rial_to_toman(tether_rial),
        "gold": rial_to_toman(gold_rial),
        "silver": rial_to_toman(silver_rial),
    }

    print("Previous prices:", previous_prices)
    print("Current prices:", current_prices)

    dollar_text = format_toman_value(current_prices.get("dollar"))
    tether_text = format_toman_value(current_prices.get("tether"))
    gold_text = format_toman_value(current_prices.get("gold"))
    silver_text = format_toman_value(current_prices.get("silver"))

    dollar_change = format_change(current_prices.get("dollar"), previous_prices.get("dollar"))
    tether_change = format_change(current_prices.get("tether"), previous_prices.get("tether"))
    gold_change = format_change(current_prices.get("gold"), previous_prices.get("gold"))
    silver_change = format_change(current_prices.get("silver"), previous_prices.get("silver"))

    save_current_prices(current_prices)

    now = get_iran_time()

    tether_label = "₮ تتر"

    if tether_is_fallback:
        tether_label = "₮ تتر تقریبی"

    message_lines = [
        "📈 بروزرسانی بازار - تومان",
        "",
        "💵 دلار: " + dollar_text + dollar_change,
        tether_label + ": " + tether_text + tether_change,
        "🥇 طلای ۱۸ عیار: " + gold_text + gold_change,
        "🥈 نقره ۹۹۹: " + silver_text + silver_change,
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
