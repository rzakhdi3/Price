import os
import re
import requests
from datetime import datetime

# تنظیمات تلگرام از سکرت‌های گیت‌هاب
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

def get_price(symbol):
    """استخراج قیمت از ای‌پی‌آی‌های مستقیم سایت با هدرهای شبیه‌ساز مرورگر"""
    urls = {
        "dollar": "https://call1.tgju.org/ajax.json?rev=2&q=price_dollar_rl",
        "gold": "https://call1.tgju.org/ajax.json?rev=2&q=geram18",
        "silver": "https://call1.tgju.org/ajax.json?rev=2&q=silver",
        "tether": "https://api.nobitex.ir/market/stats?src=usdt&dst=rls"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(urls[symbol], headers=headers, timeout=15)
        data = response.json()
        
        if symbol == "tether":
            # استخراج قیمت تتر از نوبیتکس (تبدیل ریال به تومان برای رند شدن)
            price_raw = data['stats']['usdt-rls']['latest']
            return f"{int(float(price_raw)/10):,}" # تبدیل به تومان
        else:
            # استخراج قیمت از TGJU و تبدیل ریال به تومان
            price_raw = data['current']['p'].replace(',', '')
            return f"{int(int(price_raw)/10):,}" # تبدیل به تومان
    except:
        return "خطا در دریافت"

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"})

# اجرای اصلی
if __name__ == "__main__":
    d = get_price("dollar")
    t = get_price("tether")
    g = get_price("gold")
    s = get_price("silver")
    
    now = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
    
    message = f"""
📈 <b>بروزرسانی بازار (تومان)</b>

💵 دلار: <b>{d}</b>
₮ تتر: <b>{t}</b>
🥇 طلای 18 عیار: <b>{g}</b>
🥈 نقره: <b>{s}</b>

🕒 {now}
    """
    
    send_telegram(message)
