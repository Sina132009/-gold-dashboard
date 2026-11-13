import os
import json
import requests
import time
from datetime import datetime

API_KEY = os.environ.get("TALASANJ_API_KEY")
BASE = "https://talasanj.info/api/v1"

HISTORY_DIR = "data/history"
os.makedirs(HISTORY_DIR, exist_ok=True)

# طبق مستندات، فقط این سه دارایی تاریخچه دارند
ALLOWED_SYMBOLS = {
    "usd": "usd",
    "g18": "gram18",
    "mazaneh": "mazaneh"
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "X-Client-Name": "PulseMarket",
    "X-Client-Url": "https://sina132009.github.io/"
} if API_KEY else {}

for our_id, ts_id in ALLOWED_SYMBOLS.items():
    print(f"Fetching 1 year history for {our_id} ({ts_id})...")
    try:
        url = f"{BASE}/history"
        params = {
            "symbol": ts_id,
            "range": "1y",
            "unit": "toman"
        }
        res = requests.get(url, headers=headers, params=params, timeout=15)
        res.raise_for_status()
        data = res.json()

        # استخراج لیست نقاط
        if isinstance(data, list):
            points = data
        elif isinstance(data, dict):
            points = data.get("data") or data.get("points") or data.get("history") or []
        else:
            points = []

        if not points:
            print(f"⚠️ No data points returned for {our_id}.")
            continue
            
        # چاپ اولین نقطه برای اینکه ساختار خروجی رو ببینیم
        print(f"    Sample data point: {points[0]}")

        formatted = []
        for p in points:
            t, price, low, high = None, None, None, None

            # حالت اول: اگر داده یک دیکشنری باشد
            if isinstance(p, dict):
                t = p.get("time") or p.get("timestamp") or p.get("date")
                price = p.get("price") or p.get("close") or p.get("value")
                low = p.get("low", price)
                high = p.get("high", price)
            
            # حالت دوم: اگر داده یک لیست باشد (مثلا [timestamp, price] یا [timestamp, open, high, low, close])
            elif isinstance(p, list) or isinstance(p, tuple):
                if len(p) >= 2:
                    t = p[0]
                    if len(p) >= 5:
                        high, low, price = p[2], p[3], p[4]
                    else:
                        price = p[1]
                        low = high = price

            # اگر زمان و قیمت پیدا شد
            if t is not None and price is not None:
                # تبدیل زمان به میلی‌ثانیه
                if isinstance(t, str):
                    try: t = int(datetime.strptime(t, "%Y-%m-%d").timestamp() * 1000)
                    except: t = int(datetime.now().timestamp() * 1000)
                else:
                    t = int(t)
                    if t < 1e11: t *= 1000 # اگر ثانیه بود به میلی‌ثانیه تبدیل کن

                formatted.append({
                    "time": t,
                    "close": float(price),
                    "low": float(low) if low else float(price),
                    "high": float(high) if high else float(price)
                })

        if formatted:
            formatted.sort(key=lambda x: x["time"])
            file_path = os.path.join(HISTORY_DIR, f"{our_id.upper()}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(formatted, f, ensure_ascii=False)
            print(f"✅ Saved {len(formatted)} points for {our_id}.")
        else:
            print(f"⚠️ Failed to parse points for {our_id}.")

    except Exception as e:
        print(f"❌ Error fetching {our_id}: {e}")

print("Backfill process completed.")
