import os
import requests
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/json,*/*",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
}

URLS = {
    "tgju_dollar_api": "https://call1.tgju.org/ajax.json?rev=2&q=price_dollar_rl",
    "tgju_gold_api": "https://call1.tgju.org/ajax.json?rev=2&q=geram18",
    "tgju_silver_api": "https://call1.tgju.org/ajax.json?rev=2&q=silver",
    "tgju_dollar_page": "https://www.tgju.org/profile/price_dollar_rl",
    "tgju_gold_page": "https://www.tgju.org/profile/geram18",
    "tgju_silver_page": "https://www.tgju.org/profile/silver",
    "nobitex": "https://api.nobitex.ir/market/stats?src=usdt&dst=rls",
}

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

def detect_blocked(text):
    lower = text.lower()

    blocked_words = [
        "forbidden",
        "access denied",
        "cloudflare",
        "captcha",
        "attention required",
        "blocked",
        "403",
        "not available",
    ]

    for word in blocked_words:
        if word in lower:
            return True

    return False

def test_url(name, url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)

        content_type = r.headers.get("content-type", "unknown")
        server = r.headers.get("server", "unknown")
        length = len(r.text)

        sample = r.text[:180]
        sample = sample.replace("\n", " ").replace("\r", " ").strip()

        blocked = "YES" if detect_blocked(r.text) or r.status_code in [403, 429, 503] else "NO"

        return (
            f"{name}\n"
            f"Status: {r.status_code}\n"
            f"Type: {content_type}\n"
            f"Server: {server}\n"
            f"Length: {length}\n"
            f"Blocked: {blocked}\n"
            f"Sample: {sample[:180]}\n"
        )

    except Exception as e:
        return (
            f"{name}\n"
            f"ERROR: {repr(e)}\n"
        )

if __name__ == "__main__":
    now = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S UTC")

    report = f"Debug Price Sources\nTime: {now}\n\n"

    for name, url in URLS.items():
        report += test_url(name, url)
        report += "\n----------------\n"

    # برای جلوگیری از خطای طول پیام تلگرام
    report = report[:3800]

    send_telegram(report)
