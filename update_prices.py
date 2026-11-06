import json
import os
import requests
import datetime
import time

# لیست دارایی‌ها دقیقا مطابق کدهای فرانت‌اند
ASSETS = {
    'usd': 'USD_IRR_FREE',
    'usdt': 'USDT_IRR',
    'eur': 'EUR_IRR_FREE',
    'g18': 'GOLD_18K_IRR',
    'g24': 'GOLD_24K_IRR',
    'silver': 'SILVER_999',
    'emami': 'COIN_EMAMI_IRR',
    'bahar': 'COIN_BAHAR_IRR',
    'half': 'COIN_HALF_IRR',
    'quarter': 'COIN_QUARTER_IRR',
    'btc': 'BTC_USD',
    'oil': 'OIL'
}

prices = {}
headers = {'User-Agent': 'Mozilla/5.0'}

print("Fetching latest prices from free sources...")
for asset_id, symbol in ASSETS.items():
    # استفاده از مخزن رایگان ایران‌مارکت برای خواندن تاریخچه و برداشتن آخرین قیمت
    url = f"https://cdn.jsdelivr.net/gh/iran-market/iran-market.github.io@main/data/history/{symbol}.json"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if 'data' in data and len(data['data']) > 0:
                last_point = data['data'][-1]
                price = last_point.get('close') or last_point.get('price') or last_point.get('value')
                if price:
                    prices[asset_id] = float(price)
    except Exception as e:
        print(f"Error fetching {asset_id}: {e}")

# اگر دیتای بیت کوین یا تتر پیدا نشد، از API رایگان نوبیتکس بگیر
try:
    nobitex_res = requests.get("https://api.nobitex.ir/market/stats", timeout=10).json()
    if 'usdt-rls' in nobitex_res.get('stats', {}):
        prices['usdt'] = float(nobitex_res['stats']['usdt-rls']['latest'])
    if 'btc-usdt' in nobitex_res.get('stats', {}):
        # تبدیل بیت کوین به دلار (چون نوبیتکس به تتر میده و باید در قیمت تتر ضرب بشه)
        btc_usdt = float(nobitex_res['stats']['btc-usdt']['latest'])
        usdt_rls = prices.get('usdt', 0)
        if usdt_rls > 0:
            prices['btc'] = btc_usdt
except Exception as e:
    print(f"Nobitex fallback error: {e}")

now = int(time.time() * 1000)
today = datetime.datetime.now().strftime("%Y-%m-%d")

os.makedirs('data', exist_ok=True)

# ۱. ذخیره در latest-prices.json
latest_prices_data = {
    "prices": prices,
    "updated_at": now
}
with open('data/latest-prices.json', 'w', encoding='utf-8') as f:
    json.dump(latest_prices_data, f, ensure_ascii=False, indent=2)

# ۲. ذخیره در intraday.json
intraday_data = {'days': {}}
if os.path.exists('data/intraday.json'):
    try:
        with open('data/intraday.json', 'r', encoding='utf-8') as f:
            intraday_data = json.load(f)
    except:
        pass

if 'days' not in intraday_data:
    intraday_data['days'] = {}
if today not in intraday_data['days']:
    intraday_data['days'][today] = {}

for asset_id, price in prices.items():
    if asset_id not in intraday_data['days'][today]:
        intraday_data['days'][today][asset_id] = []
    
    # اضافه کردن نقطه جدید به تاریخچه امروز
    intraday_data['days'][today][asset_id].append({
        "time": now,
        "price": price
    })
    # نگه داشتن ۱۰۰۰ نقطه آخر برای جلوگیری از سنگین شدن فایل
    intraday_data['days'][today][asset_id] = intraday_data['days'][today][asset_id][-1000:]

with open('data/intraday.json', 'w', encoding='utf-8') as f:
    json.dump(intraday_data, f, ensure_ascii=False, indent=2)

print(f"Successfully saved {len(prices)} assets.")
