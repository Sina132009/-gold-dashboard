import os
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# کلید API به صورت خودکار از تنظیمات گیت‌هاب (Secrets) خوانده می‌شود
API_KEY = os.environ.get("TALASANJ_API_KEY")

# آدرس API طلا سنج (اگر ربات آدرس دقیق دیگری بهت داده، اینجا جایگزین کن)
API_URL = "https://api.talasnj.com/v1/prices" 

# نقشه ارتباطی: اسم در سایت ما -> اسم در طلا سنج
# ⚠️ توجه: اگر طلا سنج از کلمات دیگری استفاده می‌کند، باید سمت راستِ هر خط را اصلاح کنی
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
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"خطا در دریافت داده: {e}")
        return

    now = datetime.now(ZoneInfo("Asia/Tehran"))
    timestamp = int(now.timestamp() * 1000)
    date_str = now.strftime("%Y-%m-%d")
    
    prices_file = os.path.join(DATA_DIR, "latest-prices.json")
    
    # خواندن فایل قبلی برای اینکه دیتای بقیه دارایی‌ها پاک نشود
    try:
        with open(prices_file, "r", encoding="utf-8") as f:
            latest = json.load(f)
    except:
        latest = {"prices": {}, "sources": {}}

    updated_count = 0
    for our_id, ts_id in SYMBOL_MAP.items():
        try:
            item = data.get(ts_id) or data.get("data", {}).get(ts_id)
            
            if item:
                price = float(item.get("price") or item.get("close") or 0)
                if price <= 0: continue
                
                latest["prices"][our_id] = price
                updated_count += 1
                
                hist_file = os.path.join(HISTORY_DIR, f"{our_id.upper()}.json")
                history = []
                if os.path.exists(hist_file):
                    try:
                        with open(hist_file, "r", encoding="utf-8") as f:
                            history = json.load(f)
                    except:
                        pass
                
                if history and (timestamp - history[-1]["time"]) < 60000:
                    continue

                history.append({
                    "time": timestamp,
                    "date": date_str,
                    "close": price,
                    "low": price,
                    "high": price
                })
                
                history = history[-10000:]
                
                with open(hist_file, "w", encoding="utf-8") as f:
                    json.dump(history, f, ensure_ascii=False)
        except Exception as e:
            print(f"خطا در پردازش {our_id}: {e}")

    with open(prices_file, "w", encoding="utf-8") as f:
        json.dump(latest, f, ensure_ascii=False)
    
    print(f"تعداد {updated_count} دارایی با موفقیت آپدیت شد.")

if __name__ == "__main__":
    main()
