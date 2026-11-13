import os
import json
import requests
import time
from datetime import datetime, timedelta

API_KEY = os.environ.get("TALASANJ_API_KEY")
BASE = "https://talasanj.info/api/v1"

HISTORY_DIR = "data/history"
os.makedirs(HISTORY_DIR, exist_ok=True)

SYMBOL_MAP = {
    "usd": "usd",
    "usdt": "usdt",
    "g18": "gram18",
    "g24": "gram24",
    "emami": "coin_full",
    "bahar": "coin_bahar",
    "half": "coin_half",
    "quarter": "coin_quarter"
}

headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

# لیست کامل حالت‌های ممکن برای دریافت تاریخچه
def get_endpoints(sym):
    return [
        # حالت ۱: از همان آدرس prices با پارامتر symbol و بازه زمانی
        (f"{BASE}/prices", {"symbol": sym, "start": "2023-01-01", "end": "2023-12-31"}),
        # حالت ۲: از آدرس prices با پارامتر symbol و بازه به صورت تاریخ شمسی (احتمال کم)
        (f"{BASE}/prices", {"symbol": sym, "from": "2023-01-01", "to": "2023-12-31"}),
        # حالت ۳: از آدرس history با پارامتر symbol
        (f"{BASE}/history", {"symbol": sym}),
        # حالت ۴: از آدرس history با پارامتر symbol و بازه
        (f"{BASE}/history", {"symbol": sym, "start": "2023-01-01", "end": "2023-12-31"}),
        # حالت ۵: از آدرس prices/{symbol}/history
        (f"{BASE}/prices/{sym}/history", {}),
        # حالت ۶: از آدرس history/{symbol}
        (f"{BASE}/history/{sym}", {}),
    ]

for our_id, ts_id in SYMBOL_MAP.items():
    print(f"\nFetching history for {our_id} ({ts_id})...")
    success = False
    
    for url, params in get_endpoints(ts_id):
        try:
            print(f"  Trying: {url} with params {params}")
            res = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"    Status Code: {res.status_code}")
            
            if res.status_code == 200:
                raw = res.json()
                # تلاش برای استخراج لیست نقاط داده
                rows = []
                if isinstance(raw, list):
                    rows = raw
                elif isinstance(raw, dict):
                    if "data" in raw: rows = raw["data"]
                    elif "history" in raw: rows = raw["history"]
                    elif "prices" in raw and isinstance(raw["prices"], list): rows = raw["prices"]
                
                if rows and len(rows) > 0:
                    out = []
                    for r in rows:
                        # خواندن زمان و قیمت با کلیدهای مختلف
                        t = r.get("time") or r.get("timestamp") or r.get("date")
                        if isinstance(t, str):
                            try:
                                t = int(datetime.strptime(t, "%Y-%m-%d").timestamp() * 1000)
                            except:
                                t = int(datetime.now().timestamp() * 1000)
                        elif not isinstance(t, int):
                            t = int(datetime.now().timestamp() * 1000)
                        
                        p = r.get("price") or r.get("close") or r.get("value")
                        if p:
                            out.append({
                                "time": t,
                                "close": float(p),
                                "low": float(r.get("low", p)),
                                "high": float(r.get("high", p))
                            })
                    
                    if out:
                        with open(f"{HISTORY_DIR}/{our_id.upper()}.json", "w", encoding="utf-8") as f:
                            json.dump(out, f, ensure_ascii=False)
                        print(f"    ✅ Success! Saved {len(out)} points.")
                        success = True
                        break
                    else:
                        print("    ⚠️ Response was 200 but no valid price points found.")
                else:
                    print("    ⚠️ Response was 200 but rows were empty or invalid.")
            else:
                # چاپ بخشی از پاسخ برای دیباگ
                print(f"    Response snippet: {res.text[:200]}")
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
        time.sleep(1)  # تاخیر بین تلاش‌ها
        
    if not success:
        print(f"  ❌ Could not fetch history for {our_id}. Creating empty file.")
        # ساخت فایل خالی برای جلوگیری از خطای گیت‌هاب
        with open(f"{HISTORY_DIR}/{our_id.upper()}.json", "w") as f:
            json.dump([], f)

print("\nBackfill process completed.")
