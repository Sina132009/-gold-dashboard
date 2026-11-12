import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib as mpl

# تنظیمات برای تم تیره و شفاف
mpl.rcParams['text.color'] = '#94a3b8'
mpl.rcParams['axes.labelcolor'] = '#94a3b8'
mpl.rcParams['xtick.color'] = '#94a3b8'
mpl.rcParams['ytick.color'] = '#94a3b8'

ASSETS = ['usd', 'usdt', 'eur', 'g18', 'g24', 'silver', 'emami', 'bahar', 'half', 'quarter', 'btc']
RANGES = ['daily', 'weekly', 'monthly', 'yearly', 'all']
SYMBOLS = {
    'usd': 'USD_IRR_FREE', 'usdt': 'USDT_IRR', 'eur': 'EUR_IRR_FREE',
    'g18': 'GOLD_18K_IRR', 'g24': 'GOLD_24K_IRR', 'silver': 'SILVER_999',
    'emami': 'COIN_EMAMI_IRR', 'bahar': 'COIN_BAHAR_IRR', 
    'half': 'COIN_HALF_IRR', 'quarter': 'COIN_QUARTER_IRR', 'btc': 'BTC_USD'
}

os.makedirs('data/charts', exist_ok=True)

def parse_time(t_str):
    try:
        if isinstance(t_str, (int, float)): return datetime.fromtimestamp(t_str / 1000)
        return datetime.strptime(str(t_str)[:10], '%Y-%m-%d')
    except:
        return datetime.now()

def generate_chart(asset_id, symbol, days=None):
    file_path = f'data/history/{symbol}.json'
    if not os.path.exists(file_path):
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    rows = data if isinstance(data, list) else data.get('data', [])
    dates = []
    prices = []
    
    for r in rows:
        d = parse_time(r.get('date') or r.get('t') or r.get('t_tehran'))
        p = float(r.get('close') or r.get('price') or 0)
        if p > 0:
            dates.append(d)
            prices.append(p)
            
    if not dates: return

    # فیلتر بازه زمانی
    if days:
        cutoff = datetime.now().timestamp() - (days * 86400)
        filtered = [(d, p) for d, p in zip(dates, prices) if d.timestamp() >= cutoff]
        if not filtered: return
        dates, prices = zip(*filtered)

    # رسم نمودار
    fig, ax = plt.subplots(figsize=(4, 2), dpi=150)
    fig.patch.set_alpha(0) # پس‌زمینه شفاف
    ax.patch.set_alpha(0)
    
    # رنگ گرادیانت
    color = '#38bdf8' # آبی
    ax.plot(dates, prices, color=color, linewidth=2)
    ax.fill_between(dates, prices, min(prices), color=color, alpha=0.15)
    
    # حذف حاشیه‌ها
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#333')
    
    ax.grid(axis='y', color='#333', linestyle='--', alpha=0.5)
    ax.tick_params(axis='both', which='both', length=0)
    
    # فرمت تاریخ
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=0, fontsize=8)
    plt.yticks(fontsize=8)
    
    plt.tight_layout()
    
    range_name = 'all'
    if days == 7: range_name = 'weekly'
    elif days == 30: range_name = 'monthly'
    elif days == 365: range_name = 'yearly'
    elif days is None: range_name = 'daily'

    # ذخیره عکس
    save_path = f'data/charts/{asset_id}_{range_name}.png'
    plt.savefig(save_path, transparent=True, bbox_inches='tight', pad_inches=0.1)
    plt.close()

print("Generating charts...")
for asset_id, symbol in SYMBOLS.items():
    generate_chart(asset_id, symbol, 1)     # daily (1 day)
    generate_chart(asset_id, symbol, 7)     # weekly
    generate_chart(asset_id, symbol, 30)    # monthly
    generate_chart(asset_id, symbol, 365)   # yearly
    generate_chart(asset_id, symbol, 3650)  # all

print("Done!")
