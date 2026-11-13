import os
import json
import requests
import time
from datetime import datetime, timedelta

API_KEY = os.environ.get("TALASANJ_API_KEY")

# آدرس پایه
BASE = "https://talasanj.info/api/v1"

# تاریخ‌ها به فرمت‌های مختلف
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
end_date = datetime.now().strftime("%Y-%m-%d")
start_ts = int((datetime.now() - timedelta(days=365)).timestamp() * 1000)
end_ts = int(datetime.now().timestamp() * 1000)

# لیست حالت‌های مختلف برای تست
# (نام حالت، آدرس کامل، پارامترها)
tests = [
    ("GET /prices/usd (start/end)", f"{BASE}/prices/usd", {"start": start_date, "end": end_date}),
    ("GET /prices/usd (from/to)", f"{BASE}/prices/usd", {"from": start_date, "to": end_date}),
    ("GET /prices?symbol=usd (start/end)", f"{BASE}/prices", {"symbol": "usd", "start": start_date, "end": end_date}),
    ("GET /prices?symbol=usd (from/to)", f"{BASE}/prices", {"symbol": "usd", "from": start_date, "to": end_date}),
    ("GET /history?symbol=usd (start/end)", f"{BASE}/history", {"symbol": "usd", "start": start_date, "end": end_date}),
    ("GET /history?symbol=usd (from/to)", f"{BASE}/history", {"symbol": "usd", "from": start_date, "to": end_date}),
    ("GET /history/usd (start/end)", f"{BASE}/history/usd", {"start": start_date, "end": end_date}),
    ("GET /prices/usd (timestamp)", f"{BASE}/prices/usd", {"start": start_ts, "end": end_ts}),
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "X-Client-Name": "PulseMarket",
    "X-Client-Url": "https://sina132009.github.io/"
} if API_KEY else {}

print("--- شروع تست API تاریخچه طلاسنج ---")

for name, url, params in tests:
    print(f"\n🔍 تست: {name}")
    print(f"   URL: {url}")
    print(f"   Params: {params}")
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"   Status Code: {res.status_code}")
        # فقط 200 کاراکتر اول پاسخ را چاپ می‌کنیم تا لاگ شلوغ نشود
        print(f"   Response (بخش اول): {res.text[:200]}")
    except Exception as e:
        print(f"   ❌ خطا در اتصال: {e}")
    time.sleep(1) # تاخیر بین تست‌ها

print("\n--- پایان تست ---")
