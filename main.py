import os
import requests
from datetime import datetime

# دریافت سکرت‌ها از محیط
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHANNEL_ID")

def get_tgju_price(url):
    try:
        response = requests.get(url).json()
        # در اکثر ای‌پی‌آی‌های tgju، قیمت در فیلد 'current' یا مشابه آن است
        # ممکن است نیاز باشد بسته به پاسخ دقیق سایت کمی آن را تغییر دهید
        return response['current']['p']
    except:
        return "دریافت نشد"

def get_nobitex_price():
    try:
        url = "https://api.nobitex.ir/market/stats?src=usdt&dst=rls"
        response = requests.get(url).json()
        return response['stats']['usdt-rls']['latest']
    except:
        return "دریافت نشد"

# دریافت قیمت‌ها
dollar = get_tgju_price("https://call1.tgju.org/ajax.json?rev=2&q=price_dollar_rl")
gold = get_tgju_price("https://call1.tgju.org/ajax.json?rev=2&q=geram18")
silver = get_tgju_price("https://call1.tgju.org/ajax.json?rev=2&q=silver")
tether = get_nobitex_price()

# ساخت زمان
time_str = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

# پیام نهایی
message = f"""📈 بروزرسانی بازار

💵 دلار: {dollar}
₮ تتر: {tether}
🥇 طلای ۱۸ عیار: {gold}
🥈 نقره: {silver}

🕒 {time_str}"""

# ارسال به تلگرام
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": message}
requests.post(url, data=payload)
