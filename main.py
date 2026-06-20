import os
import requests
import re
from datetime import datetime

TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

def get_data():
    results = {
        "dollar": "دریافت نشد",
        "tether": "دریافت نشد",
        "gold": "دریافت نشد",
        "silver": "دریافت نشد"
    }
    
    # استفاده از هدرهای پیشرفته برای دور زدن ربات‌نمایی
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fa-IR,fa;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    # ۱. دریافت تتر (از منبع جایگزین برای اطمینان)
    try:
        tether_resp = requests.get("https://api.coinbase.com/v2/prices/USDT-USD/spot", timeout=10).json()
        # چون قیمت دلاری تتر نزدیک ۱ است، از نوبیتکس با متد جدید امتحان میکنیم
        nobitex = requests.get("https://api.nobitex.ir/market/stats?src=usdt&dst=rls", headers=headers, timeout=10).json()
        tether_val = int(float(nobitex['stats']['usdt-rls']['latest']) / 10)
        results["tether"] = f"{tether_val:,}"
    except:
        results["tether"] = "خطای سرور"

    # ۲. دریافت سایر قیمت‌ها از TGJU با متد شبیه‌ساز مرورگر
    keys = {
        "dollar": "https://www.tgju.org/profile/price_dollar_rl",
        "gold": "https://www.tgju.org/profile/geram18",
        "silver": "https://www.tgju.org/profile/silver"
    }

    for key, url in keys.items():
        try:
            response = requests.get(url, headers=headers, timeout=15)
            # استخراج قیمت از داخل کدهای HTML صفحه (چون API بلاک میکند)
            match = re.search(r'<span class="value">([\d,]+)</span>', response.text)
            if match:
                price_rial = match.group(1).replace(',', '')
                price_toman = int(int(price_rial) / 10)
                results[key] = f"{price_toman:,}"
        except Exception as e:
            print(f"Error fetching {key}: {e}")
            results[key] = "عدم دسترسی"

    return results

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except:
        pass

if __name__ == "__main__":
    data = get_data()
    now = datetime.now().strftime("%Y/%m/%d - %H:%M")
    
    message = f"""
📈 <b>بروزرسانی بازار (تومان)</b>

💵 دلار: <b>{data['dollar']}</b>
₮ تتر: <b>{data['tether']}</b>
🥇 طلای 18 عیار: <b>{data['gold']}</b>
🥈 نقره: <b>{data['silver']}</b>

🕒 {now}
    """
    
    send_telegram(message)
