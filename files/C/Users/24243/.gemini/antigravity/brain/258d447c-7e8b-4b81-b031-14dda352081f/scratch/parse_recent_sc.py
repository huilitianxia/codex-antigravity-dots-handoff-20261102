import os
import sys
import json
import re

sys.stdout.reconfigure(encoding='utf-8')

steps_dir = r"C:\Users\24243\.gemini\antigravity\brain\f1367eb9-fa19-4a11-abf4-4dc63e32dd4b\.system_generated\steps"

recent_sc_items = {}

def extract_items_from_text(txt):
    items = []
    # match json blocks
    m = re.findall(r'```json\s*([\s\S]*?)\s*```', txt)
    for block in m:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                items.extend(data)
            elif isinstance(data, dict):
                if 'items' in data and isinstance(data['items'], list):
                    items.extend(data['items'])
                elif 'asin' in data or 'sku' in data:
                    items.append(data)
        except Exception:
            pass
    return items

for step in ['570', '581', '588', '638']:
    p = os.path.join(steps_dir, step, "output.txt")
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            t = f.read()
            extracted = extract_items_from_text(t)
            print(f"Step {step}: extracted {len(extracted)} items")
            for it in extracted:
                sku = it.get('sku', '').strip()
                asin = it.get('asin', '').strip()
                if sku or asin:
                    key = sku if sku else asin
                    recent_sc_items[key] = it

print(f"Total unique recent SC items parsed: {len(recent_sc_items)}")
for k, v in list(recent_sc_items.items())[:5]:
    print(" ", k, "->", v.get('asin'), v.get('sku'), v.get('avail'), v.get('status'), (v.get('title') or '')[:50])
