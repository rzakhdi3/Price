import os
import re
import requests
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7",
}

URLS = {
    "dollar": "https://www.tgju.org/profile/price_dollar_rl",
    "gold": "https://www.tgju.org/profile/geram18",
    "silver": "https://www.tgju.org/profile/silver",
}

PATTERNS = [
    r'<span[^>]*class="value"[^>]*>([\d,]+)</span>',
    r'"last_price":"?([\d,]+)"?',
    r'"p":"?([\d,]+)"?',
    r'"price":"?([\d,]+)"?',
    r'>([\d,]{5,})<',
]

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    resp = requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=20)
    print("Telegram status:", resp.status_code)
    print("Telegram response:", resp.text)

def inspect_page(name, url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        text = r.text

        lines = [
            f"{name}",
            f"Status: {r.status_code}",
            f"Length: {len(text)}",
        ]

        found_any = False
        for i, pattern in enumerate(PATTERNS, start=1):
            matches = re.findall(pattern, text)
            uniq = []
            for m in matches:
                if m not in uniq:
                    uniq.append(m)
            uniq = uniq[:5]
            if uniq:
                found_any = True
                lines.append(f"Pattern {i}: {uniq}")

        # چند کلمه کلیدی مهم را هم چک می‌کنیم
        keywords = ["value", "price", "current", "last", "geram18", "price_dollar_rl", "silver"]
        present = [k for k in keywords if k in text]
        lines.append(f"Keywords: {present[:10]}")

        if not found_any:
            lines.append("No numeric matches found with current patterns")

        return "\n".join(lines)

    except Exception as e:
        return f"{name}\nERROR: {repr(e)}"

if __name__ == "__main__":
    now = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S UTC")
    report = [f"TGJU HTML Inspect\nTime: {now}\n"]

    for name, url in URLS.items():
        report.append(inspect_page(name, url))
        report.append("-" * 20)

    send_telegram("\n".join(report)[:3900])
