import os
import json
import requests
import time
from datetime import datetime

# آدرس پایه فایل‌های تاریخچه در ریپازیتوری ایران مارکت
BASE_URL = "https://raw.githubusercontent.com/iran-market/iran-market.github.io/main/data/history/"

# لیست دارایی‌هایی که می‌خواهیم تاریخچه‌شان را از ایران مارکت بگیریم
SYMBOL_MAP = {
    "usdt": "USDT_IRR",
    "eur": "EUR_IRR_FREE",
    "g24": "GOLD_24K_IRR",
    "silver": "SILVER_999",
    "emami": "COIN_EMAMI_IRR",
    "bahar": "COIN_BAHAR_IRR",
    "half": "COIN_HALF_IRR",
    "quarter": "COIN_QUARTER_IRR",
    "btc": "BTC_USD",
    "oil": "OIL"
}

HISTORY_DIR = "data/history"
os.makedirs(HISTORY_DIR, exist_ok=True)

for our_id, symbol in SYMBOL_MAP.items():
    print(f"Fetching history for {our_id} ({symbol}) from Iran Market...")
    try:
        url = f"{BASE_URL}{symbol}.json"
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()

        # استخراج لیست نقاط داده
        if isinstance(data, dict) and "data" in data:
            points = data["data"]
        elif isinstance(data, list):
            points = data
        else:
            print(f"  ⚠️ Unexpected data structure for {our_id}. Skipping.")
            continue

        if not points:
            print(f"  ⚠️ No data points found for {our_id}.")
            continue

        formatted = []
        for p in points:
            t = p.get("timestamp") or p.get("time") or p.get("date")
            if isinstance(t, str):
                try: t = int(datetime.strptime(t, "%Y-%m-%d").timestamp() * 1000)
                except: continue
            elif not isinstance(t, int):
                continue

            close = p.get("close") or p.get("price")
            if close:
                formatted.append({
                    "time": t,
                    "close": float(close),
                    "low": float(p.get("low", close)),
                    "high": float(p.get("high", close))
                })

        if formatted:
            formatted.sort(key=lambda x: x["time"])
            file_path = os.path.join(HISTORY_DIR, f"{our_id.upper()}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(formatted, f, ensure_ascii=False)
            print(f"  ✅ Saved {len(formatted)} points for {our_id}.")
        else:
            print(f"  ⚠️ No valid points after formatting for {our_id}.")

    except Exception as e:
        print(f"  ❌ Error fetching {our_id}: {e}")
    time.sleep(1)

print("Iran Market backfill process completed.")
