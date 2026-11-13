import os
import json
import requests
import time

API_KEY = os.environ.get("TALASANJ_API_KEY")
BASE = "https://talasanj.info/api/v1"

headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

# لیست تست‌های جدید برای کشف ساختار درست
tests = [
    # تست ۱: آیا پارامتر symbol برای قیمت لحظه‌ای کار میکنه؟
    ("Prices with symbol only", f"{BASE}/prices", {"symbol": "usd"}),
    
    # تست ۲: تست History با symbol و limit
    ("History with symbol & limit", f"{BASE}/history", {"symbol": "usd", "limit": 10}),
    
    # تست ۳: تست History با symbol و interval
    ("History with symbol & interval", f"{BASE}/history", {"symbol": "usd", "interval": "1d"}),
    
    # تست ۴: تست History با پارامترهای جایگزین (asset)
    ("History with asset", f"{BASE}/history", {"asset": "usd"}),
    
    # تست ۵: تست History با symbol و period
    ("History with symbol & period", f"{BASE}/history", {"symbol": "usd", "period": "1d"}),
]

print("--- شروع تست دقیق ساختار API ---")

for name, url, params in tests:
    print(f"\n🔍 تست: {name}")
    print(f"   URL: {url} | Params: {params}")
    try:
        res = requests.get(url, headers=headers, params=params, timeout=10)
        print(f"   Status Code: {res.status_code}")
        if res.status_code == 200:
            # چاپ متن خام پاسخ (فقط ۵۰۰ کاراکتر اول) برای دیدن کلیدها
            print(f"   ✅ RAW Response: {res.text[:500]}")
        else:
            print(f"   ❌ Error Response: {res.text[:200]}")
    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
    time.sleep(1)

print("\n--- پایان تست ---")
