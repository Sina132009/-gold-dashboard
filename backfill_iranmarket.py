import os
import json
import requests
import time
from datetime import datetime

BASE_URL = "https://raw.githubusercontent.com/iran-market/iran-market.github.io/main/data/history/"

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

        # ساختار ایران مارکت معمولا یک لیست داخل کلید data است
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
            # خواندن زمان با کلیدهایی که در کد HTML استفاده کردیم
            t_raw = p.get("t_tehran") or p.get("t") or p.get("timestamp") or p.get("date")
            close_raw = p.get("close") or p.get("price") or p.get("value")
            
            if not t_raw or not close_raw:
                continue

            # تبدیل زمان
            if isinstance(t_raw, (int, float)):
                t = int(t_raw)
                if t < 1e11: t *= 1000 # اگر ثانیه بود به میلی‌ثانیه تبدیل کن
            elif isinstance(t_raw, str):
                try:
                    t = int(t_raw)
                    if t < 1e11: t *= 1000
                except ValueError:
                    try: t = int(datetime.strptime(t_raw, "%Y-%m-%d").timestamp() * 1000)
                    except: continue
            else:
                continue

            formatted.append({
                "time": t,
                "close": float(close_raw),
                "low": float(p.get("low") or p.get("min") or close_raw),
                "high": float(p.get("high") or p.get("max") or close_raw)
            })

        if formatted:
            formatted.sort(key=lambda x: x["time"])
            file_path = os.path.join(HISTORY_DIR, f"{our_id.upper()}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(formatted, f, ensure_ascii=False)
            print(f"  ✅ Saved {len(formatted)} points for {our_id}.")
        else:
            print(f"  ⚠️ No valid points after formatting for {our_id}.")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
             print(f"  ❌ File not found for {our_id} (Symbol: {symbol}). Skipping.")
        else:
             print(f"  ❌ Error fetching {our_id}: {e}")
    except Exception as e:
        print(f"  ❌ Error fetching {our_id}: {e}")
    time.sleep(1)

print("Iran Market backfill process completed.")
