import os
import json
import requests
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

API_KEY = os.environ.get("TALASANJ_API_KEY")

# ⚠️ آدرس API تاریخچه طلا سنج را اینجا قرار دهید 
# (بر اساس مستنداتی که از ربات گرفتید. معمولاً شامل پارامترهای start و end است)
API_URL = "https://api.talasnj.com/v1/history" 

SYMBOL_MAP = {
    "usd": "dollar",
    "usdt": "tether",
    "eur": "euro",
    "g18": "gold_18k",
    "g24": "gold_24k",
    "silver": "silver",
    "emami": "coin_emami",
    "bahar": "coin_bahar",
    "half": "coin_half",
    "quarter": "coin_quarter",
    "btc": "bitcoin",
    "oil": "oil"
}

DATA_DIR = "data"
HISTORY_DIR = os.path.join(DATA_DIR, "history")

def main():
    os.makedirs(HISTORY_DIR, exist_ok=True)
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    
    # تاریخ ۱ سال پیش تا الان
    end_time = int(datetime.now().timestamp() * 1000)
    start_time = int((datetime.now() - timedelta(days=365)).timestamp() * 1000)

    for our_id, ts_id in SYMBOL_MAP.items():
        print(f"Fetching 1 year history for {our_id}...")
        try:
            # ⚠️ پارامترها را بر اساس مستندات طلا سنج تنظیم کنید
            params = {
                "symbol": ts_id,
                "start_time": start_time,
                "end_time": end_time,
                "interval": "1d" 
            }
            response = requests.get(API_URL, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            raw_data = response.json()
            
            # ⚠️ ساختار خواندن خروجی را بر اساس طلا سنج تنظیم کنید
            formatted_history = []
            for item in raw_data:
                formatted_history.append({
                    "time": int(item.get("timestamp", 0)), 
                    "close": float(item.get("price", 0)),
                    "low": float(item.get("low", item.get("price", 0))),
                    "high": float(item.get("high", item.get("price", 0))),
                    "date": item.get("date", "")
                })
            
            # مرتب سازی و حذف تکراری‌ها
            formatted_history.sort(key=lambda x: x["time"])
            
            file_path = os.path.join(HISTORY_DIR, f"{our_id.upper()}.json")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(formatted_history, f, ensure_ascii=False)
                
            print(f"Saved {len(formatted_history)} points for {our_id}.")
            time.sleep(2) # تاخیر برای جلوگیری از بلاک شدن
            
        except Exception as e:
            print(f"Error fetching {our_id}: {e}")

if __name__ == "__main__":
    main()
