import os
import json
import requests
import time
from datetime import datetime, timedelta

# کلید API از Secrets گیت‌هاب خوانده می‌شود
API_KEY = os.environ.get("TALASANJ_API_KEY")

# آدرس پایه API طلاسنج
BASE_URL = "https://talasanj.info/api/v1"

# نقشه نمادها: نام در سایت ما -> نام در طلاسنج
SYMBOL_MAP = {
    "usd": "usd",           # دلار تهران
    "usdt": "usdt",         # تتر (در OpenAPI ذکر شده)
    "eur": "usd",           # یورو در طلاسنج موجود نیست، از دلار استفاده می‌کنیم (یا حذف کنید)
    "g18": "gram18",        # طلای ۱۸ عیار
    "g24": "gram24",        # طلای ۲۴ عیار
    "silver": "gram18",     # نقره در طلاسنج نیست، از طلا استفاده می‌کنیم (یا حذف کنید)
    "emami": "coin_full",   # سکه امامی
    "bahar": "coin_bahar",  # سکه بهار آزادی
    "half": "coin_half",    # نیم سکه
    "quarter": "coin_quarter", # ربع سکه
    "btc": "usd",           # بیت‌کوین در طلاسنج نیست
    "oil": "usd"            # نفت در طلاسنج نیست
}

HISTORY_DIR = "data/history"

def main():
    os.makedirs(HISTORY_DIR, exist_ok=True)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Client-Name": "PulseMarket",
        "X-Client-Url": "https://sina132009.github.io/"
    } if API_KEY else {}

    # بازه زمانی: ۱ سال پیش تا الان
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # فرمت تاریخ برای API (معمولاً YYYY-MM-DD)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")

    for our_id, ts_id in SYMBOL_MAP.items():
        # از تکرار استفاده از یک نماد برای چند دارایی جلوگیری می‌کنیم
        if list(SYMBOL_MAP.values()).count(ts_id) > 1 and our_id not in ["usd", "usdt", "g18", "g24", "emami", "bahar", "half", "quarter"]:
            continue

        print(f"Fetching 1 year history for {our_id} ({ts_id})...")
        try:
            # فرض بر این است که Endpoint قیمت‌ها پارامترهای start و end را می‌پذیرد
            # اگر طلاسنج Endpoint جداگانه‌ای برای تاریخچه دارد، آدرس را اینجا تغییر دهید
            url = f"{BASE_URL}/prices/{ts_id}"
            params = {
                "start": start_str,
                "end": end_str,
                "unit": "toman"
            }
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            raw_data = response.json()
            
            # استخراج داده‌های تاریخی (ساختار ممکن است لیستی از آبجکت‌ها باشد)
            # اگر ساختار متفاوت است، این بخش را بر اساس خروجی واقعی تنظیم کنید
            data_points = []
            if isinstance(raw_data, list):
                data_points = raw_data
            elif isinstance(raw_data, dict) and "history" in raw_data:
                data_points = raw_data["history"]
            elif isinstance(raw_data, dict) and "prices" in raw_data:
                # اگر فقط قیمت لحظه‌ای برگرداند، یک نقطه ثبت می‌کنیم
                price = raw_data.get("prices", {}).get("price")
                if price:
                    data_points = [{"time": int(datetime.now().timestamp() * 1000), "close": price}]

            formatted_history = []
            for item in data_points:
                # تلاش برای خواندن زمان و قیمت با کلیدهای مختلف
                t = item.get("time") or item.get("timestamp") or item.get("date")
                if isinstance(t, str):
                    try:
                        t = int(datetime.strptime(t, "%Y-%m-%d").timestamp() * 1000)
                    except:
                        t = int(datetime.now().timestamp() * 1000)
                elif not isinstance(t, int):
                    t = int(datetime.now().timestamp() * 1000)

                p = item.get("price") or item.get("close") or item.get("value")
                if p:
                    formatted_history.append({
                        "time": t,
                        "close": float(p),
                        "low": float(item.get("low", p)),
                        "high": float(item.get("high", p)),
                        "date": item.get("date", "")
                    })
            
            # مرتب‌سازی و حذف تکراری‌ها
            formatted_history.sort(key=lambda x: x["time"])
            
            file_path = os.path.join(HISTORY_DIR, f"{our_id.upper()}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(formatted_history, f, ensure_ascii=False)
                
            print(f"Saved {len(formatted_history)} points for {our_id}.")
            time.sleep(2) # تاخیر برای جلوگیری از محدودیت نرخ
            
        except Exception as e:
            print(f"Error fetching {our_id}: {e}")

if __name__ == "__main__":
    main()
