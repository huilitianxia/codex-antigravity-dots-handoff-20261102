"""Aggregate supplied order export locally; never export customer identities."""
import csv
import json
import re
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).parent
SOURCE = Path('D:/下载文件/175793876516020757.txt')
ZIP_SOURCE = ROOT / 'us-zip-timezones.csv'

def money(value):
    return Decimal(value or '0')

def region(tz):
    if tz in {'America/New_York', 'America/Detroit', 'America/Indiana/Indianapolis',
              'America/Indiana/Marengo', 'America/Indiana/Petersburg',
              'America/Indiana/Vevay', 'America/Indiana/Vincennes',
              'America/Indiana/Winamac', 'America/Kentucky/Louisville',
              'America/Kentucky/Monticello'}:
        return '东部时区'
    if tz in {'America/Chicago', 'America/Indiana/Knox', 'America/Indiana/Tell_City',
              'America/Menominee', 'America/North_Dakota/Beulah',
              'America/North_Dakota/Center', 'America/North_Dakota/New_Salem'}:
        return '中部时区'
    if tz in {'America/Denver', 'America/Boise'}:
        return '山地时区（夏令）'
    if tz == 'America/Phoenix':
        return '亚利桑那（不实行夏令时）'
    if tz == 'America/Los_Angeles':
        return '太平洋时区（美西）'
    if tz in {'America/Anchorage', 'America/Juneau', 'America/Nome',
              'America/Sitka', 'America/Yakutat', 'America/Metlakatla', 'America/Adak'}:
        return '阿拉斯加'
    if tz == 'Pacific/Honolulu':
        return '夏威夷'
    if tz in {'America/Puerto_Rico', 'America/St_Thomas'}:
        return '波多黎各及其他属地'
    return '时区未匹配'

with ZIP_SOURCE.open(encoding='utf-8-sig', newline='') as f:
    zip_rows = list(csv.DictReader(f))
zip_map = {x['zip'].zfill(5): x for x in zip_rows}
with SOURCE.open(encoding='utf-8-sig', newline='') as f:
    raw = list(csv.DictReader(f, delimiter='\t'))

rows = [r for r in raw if r['ship-country'] == 'US' and r['currency'] == 'USD'
        and r['order-status'] != 'Cancelled']
groups = defaultdict(lambda: {'orders': set(), 'lines': 0, 'units': 0,
                             'amount': Decimal(0), 'promotion': Decimal(0),
                             'zones': Counter(), 'states': Counter()})
order_groups = defaultdict(set)
unmatched = Counter()
mapped = 0
for r in rows:
    z = re.match(r'\d{5}', r['ship-postal-code'].strip())
    entry = zip_map.get(z[0]) if z else None
    tz = entry.get('timezone') if entry else None
    bucket = region(tz)
    if bucket == '时区未匹配':
        unmatched[(r['ship-state'], tz or 'missing')] += 1
    else:
        mapped += 1
    g = groups[bucket]
    g['orders'].add(r['amazon-order-id'])
    order_groups[r['amazon-order-id']].add(bucket)
    g['lines'] += 1
    g['units'] += int(r['quantity'] or 0)
    g['amount'] += money(r['item-price'])
    g['promotion'] += money(r['item-promotion-discount'])
    g['zones'][tz or 'missing'] += 1
    g['states'][(entry or {}).get('state') or r['ship-state']] += 1
total = sum(money(r['item-price']) for r in rows)
total_orders = len(order_groups)
data = []
for label, g in groups.items():
    data.append({'region': label, 'orders': len(g['orders']), 'lines': g['lines'],
                 'units': g['units'], 'item_amount': float(g['amount']),
                 'after_item_promotion': float(g['amount'] - g['promotion']),
                 'order_share': len(g['orders']) / total_orders,
                 'amount_share': float(g['amount'] / total),
                 'zones': dict(g['zones']), 'states': dict(g['states'])})
data.sort(key=lambda g: -g['item_amount'])
out = {'source': SOURCE.name, 'date_min': min(r['purchase-date'] for r in rows),
       'date_max': max(r['purchase-date'] for r in rows),
       'definition': 'US / USD / not Cancelled; pending included; item-price before promotions, refunds, shipping and tax',
       'source_rows': len(raw), 'included_rows': len(rows), 'orders': total_orders,
       'item_amount': float(total), 'zip_matched_rows': mapped,
       'zip_database': 'https://github.com/seanpianka/Zipcodes/blob/master/scripts/data/zip_code_database.csv',
       'unmatched_summary': [{'state': s, 'timezone': t, 'lines': n} for (s, t), n in unmatched.items()],
       'orders_in_multiple_regions': sum(len(x) > 1 for x in order_groups.values()),
       'regions': data}
assert sum(g['lines'] for g in data) == len(rows)
assert sum(Decimal(str(g['item_amount'])) for g in data) == total
(ROOT / 'order-timezone-summary.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(out, ensure_ascii=False, indent=2))
