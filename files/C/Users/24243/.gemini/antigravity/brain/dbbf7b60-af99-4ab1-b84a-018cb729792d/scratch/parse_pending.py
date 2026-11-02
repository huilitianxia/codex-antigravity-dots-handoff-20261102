import json, sys, re
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

p = r'C:\Users\24243\.gemini\antigravity\brain\675d7e41-2d41-4b28-b1f5-b2ca4c6c75c7\.system_generated\steps\5749\output.txt'
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Find json
m = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text)
if not m:
    # Try finding "totalParsed"
    idx = text.find('{"totalParsed"')
    if idx != -1:
        end_idx = text.rfind('}')
        json_str = text[idx:end_idx+1]
    else:
        json_str = None
else:
    json_str = m.group(1)

if json_str:
    try:
        data = json.loads(json_str)
    except Exception as e:
        # If it was returned as a json string representation or escaped
        print('Direct loads failed:', e)
        # Maybe text was escaped
        data = json.loads(json.loads(text.split('```json\n')[1].split('\n```')[0]))

    orders = data.get('orders', [])
    print(f'Total Pending Orders Parsed: {len(orders)}')

    date_counts = Counter()
    by_date_orders = {}
    for o in orders:
        d = o.get('orderDate', 'Unknown')
        date_counts[d] += 1
        if d not in by_date_orders:
            by_date_orders[d] = []
        by_date_orders[d].append(o)

    print('\n=== PENDING ORDERS BY ORDER DATE ===')
    for d, c in sorted(date_counts.items(), reverse=True):
        rev = sum(float(x.get('subtotal', '0').replace('US$', '').replace('CA$', '').replace(',', '')) for x in by_date_orders[d] if x.get('subtotal'))
        qty = sum(x.get('qty', 1) for x in by_date_orders[d])
        print(f'{d}: {c} 单 | {qty} 件 | 待结金额: ${rev:.2f}')

    print('\n=== THURSDAY (2026/10/29) PENDING ITEMS BREAKDOWN ===')
    thu_orders = by_date_orders.get('2026/10/29', [])
    asin_counts = Counter()
    for o in thu_orders:
        asin_counts[(o.get('asin'), o.get('sku'), o.get('title', '')[:40])] += o.get('qty', 1)
    for (asin, sku, title), qty in asin_counts.most_common():
        print(f'  {asin} | {sku} | {qty}件 | {title}')
