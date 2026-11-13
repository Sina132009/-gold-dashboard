import requests
import json

url = "https://raw.githubusercontent.com/iran-market/iran-market.github.io/main/data/history/USDT_IRR.json"
print(f"Fetching sample from: {url}")
try:
    res = requests.get(url, timeout=10)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        data = res.json()
        print(f"Type of raw data: {type(data)}")
        
        # اگر داده یک دیکشنری است
        if isinstance(data, dict):
            print(f"Keys in dict: {list(data.keys())}")
            if "data" in data and isinstance(data["data"], list) and len(data["data"]) > 0:
                print("First point inside 'data':")
                print(json.dumps(data["data"][0], ensure_ascii=False))
            elif "prices" in data and isinstance(data["prices"], list) and len(data["prices"]) > 0:
                print("First point inside 'prices':")
                print(json.dumps(data["prices"][0], ensure_ascii=False))
                
        # اگر داده یک لیست است
        elif isinstance(data, list):
            print(f"List length: {len(data)}")
            if len(data) > 0:
                print("First point in list:")
                print(json.dumps(data[0], ensure_ascii=False))
        else:
            print("Raw response text (first 200 chars):")
            print(res.text[:200])
            
except Exception as e:
    print(f"Error: {e}")
