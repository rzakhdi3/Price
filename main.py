import os
import re
import requests
from datetime import datetime, timezone, timedelta

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
}

TGJU_URLS = {
    "dollar": "https://www.tgju.org/profile/price_dollar_rl",
    "gold": "https://www.tgju.org/profile/geram18",
    "silver": "https://www.tgju.org/profile/silver",
}

# چون نوبیتکس روی GitHub resolve نمی‌شود، برای تتر چند مسیر جایگزین تست می‌کنیم.
# اگر هیچ‌کدام جواب نداد، تتر را برابر دلار آزاد می‌گذاریم.
TETHER_URLS = [
    "https://www.tgju.org/profile/crypto-tether",
    "https://www.tgju.org/profile/tether",
    "https://www.tgju.org/profile/usdt",
    "https://www.tgju.org/profile/USDT",
]


def english_digits(text):
    """
    تبدیل اعداد فارسی/عربی به انگلیسی برای پردازش راحت‌تر
    """
    if text is None:
        return ""

    fa = "۰۱۲۳۴۵۶۷۸۹"
    ar = "٠١٢٣٤٥٦٧٨٩"
    en = "0123456789"

    for f, e in zip(fa, en):
        text = text.replace(f, e)

    for a, e in zip(ar, en):
        text = text.replace(a, e)

    return text


def to_persian_digits(text):
    """
    تبدیل اعداد انگلیسی به فارسی برای نمایش زیباتر در تلگرام
    """
    text = str(text)
    en = "0123456789"
    fa = "۰۱۲۳۴۵۶۷۸۹"

    for e, f in zip(en, fa):
        text = text.replace(e, f)

    return text


def extract_first_price_from_html(html):
    """
    طبق دیباگی که از GitHub گرفتی، عدد اول با الگوی زیر قیمت فعلی است.
    مثال:
    1,620,000
    161,478,000
    """
    html = english_digits(html)

    matches = re.findall(r'>([\d,]{5,})<', html)

    if not matches:
        return None

    for item in matches:
        clean = item.replace(",", "").strip()

        if not clean.isdigit():
            continue

        value = int(clean)

        # حذف عددهای خیلی کوچک یا بی‌ربط
        if value < 10000:
            continue

        return value

    return None


def get_tgju_price_rial(url):
    """
    دریافت قیمت ریالی از صفحه HTML سایت TGJU
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)

        print("URL:", url)
        print("Status:", response.status_code)
        print("Length:", len(response.text))

        if response.status_code != 200:
            return None

        return extract_first_price_from_html(response.text)

    except Exception as e:
        print("Error fetching:", url)
        print("Exception:", repr(e))
        return None


def format_toman(price_rial):
    """
    تبدیل ریال به تومان و فرمت سه‌رقمی
    """
    if price_rial is None:
        return "دریافت نشد"

    toman = int(price_rial / 10)
    formatted = f"{toman:,}"
    return to_persian_digits(formatted)


def get_tether_price_rial(dollar_rial=None):
    """
    تلاش برای دریافت تتر از صفحات احتمالی TGJU.
    اگر نشد، چون نوبیتکس از GitHub قابل resolve نیست، تتر را تقریباً برابر دلار آزاد می‌گذاریم.
    """
    for url in TETHER_URLS:
        price = get_tgju_price_rial(url)

        if price:
            # فیلتر تقریبی برای جلوگیری از گرفتن عددهای پرت
            # تتر/دلار معمولاً در محدوده چندصد هزار تا چند میلیون ریال است.
            if 100000 <= price <= 5000000:
                return price, False

    # fallback
    if dollar_rial:
        return dollar_rial, True

    return None, False


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
        },
        timeout=20
    )

    print("Telegram status:", response.status_code)
    print("Telegram response:", response.text)


def get_iran_time():
    """
    زمان ایران: UTC+3:30
