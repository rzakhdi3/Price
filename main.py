import os
import requests
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/json;q=0.8,*/*;q=0.7",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
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
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        },
        timeout=20
    )

def short_text(text, limit=700):
    if not text:
        return ""
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return text[:limit]

def test_url(name, url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=25)

        content_type = r.headers.get("content-type", "unknown")
        server = r.headers.get("server", "unknown")

        body_sample = short_text(r.text, 900)

        return f"""
<b>{name}</b>
URL: {url}
Status: <b>{r.status_code}</b>
Content-Type: {content_type}
Server: {server}
Length: {len(r.text)}

First chars:
<code>{body_sample}</code>
"""
    except Exception as e:
        return f"""
<b>{name}</b>
URL: {url}
ERROR:
<code>{str(e)}</code>
"""

if __name__ == "__main__":
    now = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S UTC")

    parts = [f"🧪 <b>Debug Report</b>\n🕒 {now}"]

    for name, url in URLS.items():
        parts.append(test_url(name, url))

    # تلگرام محدودیت طول پیام دارد؛ پیام را چند قسمت می‌کنیم
    full = "\n--------------------\n".join(parts)

    max_len = 3500
    for i in range(0, len(full), max_len):
        send_telegram(full[i:i + max_len])
