import os
import json
import requests
import time
from datetime import datetime, timedelta

API_KEY = os.environ.get("TALASANJ_API_KEY")
BASE = "https://talasanj.info/api/v1"

# ساخت پوشه
HISTORY_DIR = "data/history"
os.makedirs(HISTORY_DIR, exist_ok=True)

# نقشه نمادها
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

def get_urls(sym):
    return [
        f"{BASE}/history?symbol={sym}",
        f"{BASE}/history/{sym}",
        f"{BASE}/prices/{sym}/history"
    ]

for our_id, ts_id in SYMBOL_MAP.items():
    print(f"Fetching history for {our_id} ({ts_id})...")
    success = False
    
    for url in get_urls(ts_id):
        try:
            print(f"  Trying: {url}")
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                raw = res.json()
                rows = raw if isinstance(raw, list) else raw.get("data", [])
                
                if rows and len(rows) > 0:
                    out = []
                    for r in rows:
                        out.append({
                            "time": r.get("time") or r.get("timestamp") or int(time.time()*1000),
                            "close": float(r.get("price") or r.get("close") or 0),
                            "low": float(r.get("low") or r.get("price") or 0),
                            "high": float(r.get("high") or r.get("price") or 0)
                        })
                    with open(f"{HISTORY_DIR}/{our_id.upper()}.json", "w", encoding="utf-8") as f:
                        json.dump(out, f, ensure_ascii=False)
                    print(f"  ✅ Success! Saved {len(out)} points.")
                    success = True
                    break
        except Exception as e:
            print(f"  Error: {e}")
            
    if not success:
        print(f"  ❌ Could not fetch history for {our_id}")
        # ساخت فایل خالی برای جلوگیری از خطای گیت‌هاب
        with open(f"{HISTORY_DIR}/{our_id.upper()}.json", "w") as f:
            json.dump([], f)

print("Backfill process completed.")
