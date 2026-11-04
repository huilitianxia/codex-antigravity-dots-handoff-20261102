"""Use actual recent orders and a dated FBA inventory snapshot for product triage."""
import csv
import json
import re
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).parent
prior = json.loads((ROOT/'analysis.json').read_text(encoding='utf-8'))
clearance = json.loads((ROOT/'fba-clearance-priority.json').read_text(encoding='utf-8'))
old_good = json.loads((ROOT/'old-good-candidates-current.json').read_text(encoding='utf-8'))
with Path('D:/下载文件/175793876516020757.txt').open(encoding='utf-8-sig', newline='') as f:
    orders = list(csv.DictReader(f, delimiter='\t'))
master = defaultdict(list)
for r in prior['master']:
    if not r['parent']:
        master[r['asin']].append(r)
stocks = defaultdict(lambda: {'available': 0, 'reserved': 0, 'fnskus': []})
for r in prior['fba_unique']:
    if r.get('market') != 'US': continue
    stocks[r['asin']]['available'] += r.get('available') or 0
    stocks[r['asin']]['reserved'] += r.get('Total Reserved Quantity') or 0
    stocks[r['asin']]['fnskus'].append(r['fnsku'])
age = defaultdict(lambda: {'age365plus': 0, 'age181plus': 0, 'storage': 0, 'ais': 0})
seen = set()
for r in clearance:
    if r['fnsku'] in seen: continue
    seen.add(r['fnsku'])
    for src, dst in [('age365plus', 'age365plus'), ('age181plus', 'age181plus'),
                     ('storage_est_next_month', 'storage'), ('ais_est', 'ais')]:
        age[r['asin']][dst] += r.get(src) or 0

sales = defaultdict(lambda: {'orders': set(), 'units': 0, 'sales': Decimal(0),
                             'b2b_sales': Decimal(0), 'title': '', 'skus': set(),
                             'recent7_units': 0, 'today_units': 0})
for r in orders:
    if r['fulfillment-channel'] != 'Amazon' or r['order-status'] == 'Cancelled': continue
    if r['ship-country'] != 'US' or r['currency'] != 'USD': continue
    a = sales[r['asin']]
    a['orders'].add(r['amazon-order-id']); a['units'] += int(r['quantity'] or 0)
    a['sales'] += Decimal(r['item-price'] or 0)
    if r['is-business-order'].lower() == 'true': a['b2b_sales'] += Decimal(r['item-price'] or 0)
    if len(r['product-name']) > len(a['title']): a['title'] = r['product-name']
    a['skus'].add(r['sku'])
    if r['purchase-date'] >= '2026-10-24T15:14:01+00:00': a['recent7_units'] += int(r['quantity'] or 0)
    if r['purchase-date'] >= '2026-10-31T07:00:00+00:00': a['today_units'] += int(r['quantity'] or 0)

rows = []
for asin in set(sales) | set(stocks):
    q = sales[asin]
    candidates = master.get(asin, [])
    best = max(candidates, key=lambda x: len(x.get('basis') or '')) if candidates else {}
    title = q['title'] or best.get('basis', '')
    info = title + ' ' + best.get('basis', '')
    if re.search(r'\bPSS\s*9|\bPSS\s*32|roll sticky|sticky rolls?|roll tape', info, re.I):
        category = '满胶卷带'
    elif re.search(r'full[ -]?(?:adhesive|glue|sticky)|full stick(?:y)? back', info, re.I):
        category = '满胶平叠便签'
    else:
        category = best.get('category', '待核实')
    st = stocks[asin]
    ar = age[asin]
    historic_ratings = sorted({str(x.get('old_rating')) for x in candidates if x.get('old_rating')})
    rows.append({'asin': asin, 'title': title, 'category': category,
                 'type': best.get('type', ''), 'order_count': len(q['orders']),
                 'units30': q['units'], 'item_sales30': float(q['sales']),
                 'b2b_item_sales30': float(q['b2b_sales']), 'units_last7': q['recent7_units'],
                 'units_us_today': q['today_units'], 'available10_30': st['available'],
                 'reserved10_30': st['reserved'], 'age365plus': ar['age365plus'],
                 'age181plus': ar['age181plus'], 'estimated_month_storage': ar['storage'],
                 'estimated_aged_surcharge': ar['ais'], 'historic_ratings_unverified': historic_ratings,
                 'order_skus': sorted(q['skus']), 'fnskus': st['fnskus'],
                 'stock_days_at_recent_rate': round(st['available'] / (q['units']/30), 1) if q['units'] else None})
rows.sort(key=lambda x: -x['item_sales30'])
cat = defaultdict(lambda: {'sales': 0, 'units': 0, 'asins': 0})
for r in rows:
    c = cat[r['category']]; c['sales'] += r['item_sales30']; c['units'] += r['units30']
    if r['units30']: c['asins'] += 1
out = {'period': '2026-10-01 to 2026-10-31 08:14 PDT export; US USD non-cancelled Amazon fulfilled orders',
       'inventory_asof': '2026-10-30', 'categories': dict(cat), 'rows': rows,
       'source_orders': '175793876516020757.txt', 'source_inventory': '284701020757.txt'}
(ROOT/'fba-potential-from-orders.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print('CATEGORY', json.dumps(dict(cat), ensure_ascii=False))
print('NON-FULL-ADHESIVE TOP')
for r in [x for x in rows if not x['category'].startswith('满胶') and x['item_sales30']][:24]:
    print(json.dumps(r, ensure_ascii=False))
print('FULL ADHESIVE TOP')
for r in [x for x in rows if x['category'].startswith('满胶') and x['item_sales30']][:8]:
    print(json.dumps(r, ensure_ascii=False))
