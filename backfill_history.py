import os
import json
import requests
import time
from datetime import datetime

API_KEY = os.environ.get("TALASANJ_API_KEY")
BASE = "https://talasanj.info/api/v1"

HISTORY_DIR = "data/history"
os.makedirs(HISTORY_DIR, exist_ok=True)

# فقط این سه دارایی در طلاسنج تاریخچه دارند
ALLOWED_SYMBOLS = {
    "usd": "usd",
    "g18": "gram18",
    "mazaneh": "mazaneh"  # اگر در سایت شما دارایی به نام mazaneh وجود دارد
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

        # ساختار پاسخ احتمالاً یک لیست از نقاط است. اگر داخل کلیدی بود، آن را استخراج می‌کنیم.
        if isinstance(data, list):
            points = data
        elif isinstance(data, dict):
            points = data.get("data") or data.get("points") or data.get("history") or []
        else:
            points = []

        formatted = []
        for p in points:
            # تلاش برای خواندن زمان و قیمت با کلیدهای مختلف
            t = p.get("time") or p.get("timestamp")
            if isinstance(t, str):
                try:
                    t = int(datetime.strptime(t, "%Y-%m-%d").timestamp() * 1000)
                except:
                    t = int(datetime.now().timestamp() * 1000)
            elif not isinstance(t, int):
                t = int(datetime.now().timestamp() * 1000)

            price = p.get("price") or p.get("close") or p.get("value")
            if price:
                formatted.append({
                    "time": t,
                    "close": float(price),
                    "low": float(p.get("low", price)),
                    "high": float(p.get("high", price))
                })

        if formatted:
            formatted.sort(key=lambda x: x["time"])
            file_path = os.path.join(HISTORY_DIR, f"{our_id.upper()}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(formatted, f, ensure_ascii=False)
            print(f"✅ Saved {len(formatted)} points for {our_id}.")
        else:
            print(f"⚠️ No valid points found for {our_id}.")

    except Exception as e:
        print(f"❌ Error fetching {our_id}: {e}")

print("Backfill process completed.")
