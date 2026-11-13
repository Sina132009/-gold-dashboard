import os
import json
import requests
import time

# API نوبیتکس برای دریافت تاریخچه (فرمت استاندارد TradingView)
API_URL = "https://api.nobitex.ir/market/udf/history"

def main():
    print("Fetching 3 years USDT history from Nobitex...")
    
    # زمان حال و ۳ سال پیش
    to_ts = int(time.time())
    from_ts = to_ts - (3 * 365 * 24 * 60 * 60)
    
    url = f"{API_URL}?symbol=USDTIRT&resolution=1D&from={from_ts}&to={to_ts}"
    
    try:
        res = requests.get(url, timeout=15)
        res.raise_for_status()
        data = res.json()
        
        if data.get("s") != "ok":
            print(f"❌ Error from Nobitex: {data}")
            return
            
        times = data.get("t", [])
        closes = data.get("c", [])
        highs = data.get("h", [])
        lows = data.get("l", [])
        
        if not times:
            print("❌ No data received.")
            return
            
        formatted = []
        for i in range(len(times)):
            formatted.append({
                "time": int(times[i] * 1000), # تبدیل ثانیه به میلی‌ثانیه
                "close": float(closes[i]),
                "low": float(lows[i]),
                "high": float(highs[i])
            })
            
        # ذخیره در فایل USDT
        HISTORY_DIR = "data/history"
        os.makedirs(HISTORY_DIR, exist_ok=True)
        
        file_path = os.path.join(HISTORY_DIR, "USDT.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(formatted, f, ensure_ascii=False)
            
        print(f"✅ Saved {len(formatted)} points for USDT from Nobitex.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
