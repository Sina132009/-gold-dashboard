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

        # استخراج لیست نقاط داده
        points = data.get("data", []) if isinstance(data, dict) else data

        if not points:
            print(f"  ⚠️ No data points found for {our_id}.")
            continue

        formatted = []
        for p in points:
            # 1. تبدیل زمان (ISO 8601 به میلی‌ثانیه)
            t_raw = p.get("t_tehran") or p.get("t")
            if not t_raw:
                continue
            
            t = None
            if isinstance(t_raw, str):
                try:
                    # جایگزینی Z با +00:00 برای سازگاری با پایتون
                    clean_t = t_raw.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(clean_t)
                    t = int(dt.timestamp() * 1000)
                except Exception:
                    continue
            
            # 2. خواندن قیمت پایانی
            close = p.get("close")
            if close is None:
                continue
                
            formatted.append({
                "time": t,
                "close": float(close),
                "low": float(p.get("low", close)),
                "high": float(p.get("high", close)),
                "date": p.get("date_jalali", "")
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
