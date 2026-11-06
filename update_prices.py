import json
import os
import time
import urllib.request

NA = 'https://nerkhara.com/api/v1'
IM_CDN = 'https://cdn.jsdelivr.net/gh/iran-market/iran-market.github.io@main/data'

ASSETS = [
    {"id": "usd",     "symbol": "USD_IRR_FREE",    "nid": "usd"},
    {"id": "usdt",    "symbol": "USDT_IRR",        "nid": "tether"},
    {"id": "eur",     "symbol": "EUR_IRR_FREE",    "nid": "eur"},
    {"id": "g18",     "symbol": "GOLD_18K_IRR",    "nid": "gold-18k"},
    {"id": "g24",     "symbol": "GOLD_24K_IRR",    "nid": "gold-24k"},
    {"id": "silver",  "symbol": "SILVER_999",      "nid": "silver"},
    {"id": "emami",   "symbol": "COIN_EMAMI_IRR",  "nid": "coin-emami"},
    {"id": "bahar",   "symbol": "COIN_BAHAR_IRR",  "nid": "coin-bahar-azadi"},
    {"id": "half",    "symbol": "COIN_HALF_IRR",   "nid": "coin-half"},
    {"id": "quarter", "symbol": "COIN_QUARTER_IRR","nid": "coin-quarter"},
    {"id": "btc",     "symbol": "BTC_USD",         "nid": "bitcoin"},
    {"id": "oil",     "symbol": "OIL",             "nid": "oil", "currency": "USD"},
]


def fetch_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (prices-bot)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def iran_rows(p):
    c = (p or {}).get("data", {}).get("categories")
    if not isinstance(c, dict):
        return []
    out = []
    for arr in c.values():
        if isinstance(arr, list):
            out.extend(arr)
    return out


def main():
    n_items, i_items = [], []
    try:
        n = fetch_json(NA + "/latest.json")
        if isinstance(n, dict) and isinstance(n.get("items"), list):
            n_items = n["items"]
    except Exception as e:
        print("NerkhAra failed:", e)

    try:
        i = fetch_json(IM_CDN + "/latest-toman.json")
        i_items = iran_rows(i)
    except Exception as e:
        print("Iran Market failed:", e)

    prices, sources = {}, {}

    for a in ASSETS:
        p, s = None, ""

        ni = next(
            (x for x in n_items
             if x.get("id") == a["nid"]
             and float(x.get("price") or 0) > 0
             and (not x.get("unit") or x.get("unit") == "IRT")),
            None,
        )
        if ni:
            p = float(ni["price"])
            s = "n"
            lo = float(ni.get("low_24h") or ni.get("low24h") or ni.get("24h_low")
                       or ni.get("min_24h") or (ni.get("24hour") or {}).get("low") or 0)
            hi = float(ni.get("high_24h") or ni.get("high24h") or ni.get("24h_high")
                       or ni.get("max_24h") or (ni.get("24hour") or {}).get("high") or 0)
            if lo > 0 and hi > 0:
                prices["_low_" + a["id"]] = lo
                prices["_high_" + a["id"]] = hi

        if not (p and p > 0):
            ii = next(
                (x for x in i_items
                 if x.get("symbol") == a["symbol"]
                 and float(x.get("price") or 0) > 0),
                None,
            )
            if ii:
                p = float(ii["price"])
                s = "i"

        if a["id"] == "btc" and p and p > 0 and s == "i":
            u = prices.get("usd", 0)
            if u and u > 0:
                p = p * u
            else:
                p = None

        if p and p > 0:
            prices[a["id"]] = p
            sources[a["id"]] = s

    data = {
        "updated_at": int(time.time() * 1000),
        "prices": prices,
        "sources": sources,
    }

    os.makedirs("data", exist_ok=True)
    with open("data/latest-prices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Updated", len([k for k in prices if not k.startswith("_")]), "prices")


if __name__ == "__main__":
    main()
