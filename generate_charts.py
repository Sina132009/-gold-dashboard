import json
import os
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib as mpl
import warnings

warnings.filterwarnings("ignore")
mpl.rcParams['text.color'] = '#94a3b8'
mpl.rcParams['axes.labelcolor'] = '#94a3b8'
mpl.rcParams['xtick.color'] = '#94a3b8'
mpl.rcParams['ytick.color'] = '#94a3b8'

ASSETS = ['usd', 'usdt', 'eur', 'g18', 'g24', 'silver', 'emami', 'bahar', 'half', 'quarter', 'btc']
SYMBOLS = {
    'usd': 'USD_IRR_FREE', 'usdt': 'USDT_IRR', 'eur': 'EUR_IRR_FREE',
    'g18': 'GOLD_18K_IRR', 'g24': 'GOLD_24K_IRR', 'silver': 'SILVER_999',
    'emami': 'COIN_EMAMI_IRR', 'bahar': 'COIN_BAHAR_IRR', 
    'half': 'COIN_HALF_IRR', 'quarter': 'COIN_QUARTER_IRR', 'btc': 'BTC_USD'
}

os.makedirs('data/charts', exist_ok=True)
os.makedirs('data/history', exist_ok=True)

def parse_time(t_str):
    try:
        if isinstance(t_str, (int, float)): return datetime.fromtimestamp(t_str / 1000)
        return datetime.strptime(str(t_str)[:10], '%Y-%m-%d')
    except:
        return None

def generate_chart(asset_id, symbol, range_name, days=None):
    url = f"https://cdn.jsdelivr.net/gh/iran-market/iran-market.github.io@main/data/history/{symbol}.json"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code != 200: return
        data = res.json()
    except:
        return
    
    rows = data if isinstance(data, list) else data.get('data', [])
    dates = []
    prices = []
    
    for r in rows:
        d = parse_time(r.get('date') or r.get('t') or r.get('t_tehran'))
        p = float(r.get('close') or r.get('price') or 0)
        if d and p > 0:
            dates.append(d)
            prices.append(p)
            
    if not dates: return

    if days:
        cutoff = datetime.now().timestamp() - (days * 86400)
        filtered = [(d, p) for d, p in zip(dates, prices) if d.timestamp() >= cutoff]
        if not filtered: return
        dates, prices = zip(*filtered)

    fig, ax = plt.subplots(figsize=(4, 2), dpi=120)
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    
    color = '#38bdf8'
    ax.plot(dates, prices, color=color, linewidth=2)
    ax.fill_between(dates, prices, min(prices), color=color, alpha=0.15)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#333')
    
    ax.grid(axis='y', color='#333', linestyle='--', alpha=0.5)
    ax.tick_params(axis='both', which='both', length=0)
    
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
    plt.xticks(rotation=0, fontsize=7)
    plt.yticks(fontsize=7)
    
    plt.tight_layout()
    save_path = f'data/charts/{asset_id}_{range_name}.png'
    plt.savefig(save_path, transparent=True, bbox_inches='tight', pad_inches=0.1)
    plt.close()

for asset_id, symbol in SYMBOLS.items():
    generate_chart(asset_id, symbol, 'daily', 1)
    generate_chart(asset_id, symbol, 'weekly', 7)
    generate_chart(asset_id, symbol, 'monthly', 30)
    generate_chart(asset_id, symbol, 'yearly', 365)
    generate_chart(asset_id, symbol, 'all', 3650)

print("Charts generated successfully!")
