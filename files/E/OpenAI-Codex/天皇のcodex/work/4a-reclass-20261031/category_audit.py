import json, collections, re, datetime
from pathlib import Path

root = Path(__file__).parent
raw = json.loads((root / 'category-report-raw.json').read_text(encoding='utf-8'))['rows']
prior = json.loads((root / 'analysis.json').read_text(encoding='utf-8'))
old = {x['sku']: x for x in prior['master']}
now = datetime.datetime.fromisoformat('2026-10-31T11:31:00+00:00')

def get(r, prefix):
    return next((v for k, v in r.items() if k.startswith(prefix)), None)

def offer(r, audience, suffix):
    return next((v for k, v in r.items() if '[audience=' + audience + ']' in k and k.endswith(suffix)), None)

def number(value):
    try: return float(value)
    except (ValueError, TypeError): return None

def date(value):
    try:
        result = datetime.datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return result if result.tzinfo else result.replace(tzinfo=datetime.timezone.utc)
    except (ValueError, TypeError): return None

rows = []
for r in raw:
    sku = get(r, 'contribution_sku')
    p = number(offer(r, 'ALL', 'our_price#1.schedule#1.value_with_tax'))
    sale = number(offer(r, 'ALL', 'discounted_price#1.schedule#1.value_with_tax'))
    start = date(offer(r, 'ALL', 'discounted_price#1.schedule#1.start_at'))
    end = date(offer(r, 'ALL', 'discounted_price#1.schedule#1.end_at'))
    active_sale = sale is not None and start is not None and end is not None and start <= now <= end
    stop = date(offer(r, 'ALL', '#1.end_at.value'))
    x = dict(sku=sku, asin=get(r, 'amzn1.volt.ca.product_id_value'), parentage=get(r, 'parentage_level'),
             parent=get(r, 'child_parent_sku_relationship'), product_type=get(r, 'product_type'),
             brand=get(r, 'brand'), color=get(r, 'color['), size=get(r, 'size['), shape=get(r, 'item_shape'),
             title=get(r, 'item_name'), status_report=get(r, '::listing_status'), price=p, sale=sale,
             sale_active_by_dates=active_sale, effective_before_coupons=min(p, sale) if active_sale and p is not None else p,
             b2b=number(offer(r, 'B2B', 'our_price#1.schedule#1.value_with_tax')),
             minimum=number(offer(r, 'ALL', 'minimum_seller_allowed_price#1.schedule#1.value_with_tax')),
             maximum=number(offer(r, 'ALL', 'maximum_seller_allowed_price#1.schedule#1.value_with_tax')),
             offer_stop_passed=bool(stop and stop < now), shipping_template=get(r, 'merchant_shipping_group'),
             channel=get(r, 'fulfillment_availability#1.fulfillment_channel_code'),
             quantity=number(get(r, 'fulfillment_availability#1.quantity')))
    o = old.get(sku, {})
    x.update(old_fine=o.get('fine'), old_basis=o.get('basis'), available10_30=o.get('available'),
             fnsku10_30=o.get('fnsku'), sold30_10_30=o.get('sold30'))
    rows.append(x)

nonparents = [x for x in rows if x['parentage'] != 'Parent']
children = [x for x in rows if x['parentage'] == 'Child']
parents = [x for x in rows if x['parentage'] == 'Parent']
parent_by = {x['sku']: x for x in parents}

def greater(x, first, second):
    return x[first] is not None and x[second] is not None and x[first] > x[second] + 0.001

issues = {
    'b2b_higher_than_regular': [x for x in nonparents if greater(x, 'b2b', 'price')],
    'b2b_higher_than_effective': [x for x in nonparents if greater(x, 'b2b', 'effective_before_coupons')],
    'minimum_above_regular': [x for x in nonparents if greater(x, 'minimum', 'price')],
    'minimum_above_effective': [x for x in nonparents if greater(x, 'minimum', 'effective_before_coupons')],
    'inactive_sale_fields': [x for x in nonparents if x['sale'] is not None and not x['sale_active_by_dates']],
    'generic_pack_suffix': [x for x in children if re.search(r'\(Pack \d+\)', str(x['size']))],
    'child_parent_brand_mismatch': [x for x in children if x['parent'] in parent_by and x['brand'] and parent_by[x['parent']]['brand'] and x['brand'] != parent_by[x['parent']]['brand']],
    'child_parent_type_mismatch': [x for x in children if x['parent'] in parent_by and x['product_type'] != parent_by[x['parent']]['product_type']],
    'offer_stop_passed': [x for x in nonparents if x['offer_stop_passed']],
}
by_asin = collections.defaultdict(list)
families = collections.defaultdict(list)
for x in nonparents:
    if x['asin']: by_asin[x['asin']].append(x)
for x in children: families[x['parent']].append(x)
conflicts = []
for asin, xs in by_asin.items():
    if len(set((x['parent'], x['color'], x['size']) for x in xs)) > 1:
        conflicts.append(dict(asin=asin, skus=[x['sku'] for x in xs], attributes=[(x['parent'], x['color'], x['size']) for x in xs]))
family_summary = [dict(parent=p, sku_count=len(xs), asin_count=len(set(x['asin'] for x in xs)),
                       product_types=dict(collections.Counter(x['product_type'] for x in xs)),
                       brands=dict(collections.Counter(x['brand'] or '未填写' for x in xs)),
                       classified_groups=dict(collections.Counter(x['old_fine'] or '新增待分类' for x in xs)))
                  for p, xs in families.items()]
stats = dict(rows=len(rows), parent_rows=len(parents), parents_with_children=len(families),
             empty_parent_rows=sum(x['sku'] not in families for x in parents), child_rows=len(children),
             standalone_rows=sum(not x['parentage'] for x in rows), product_types=len(set(x['product_type'] for x in rows)),
             same_asin_conflicting_labels=len(conflicts), families_mixed_product_types=sum(len(x['product_types']) > 1 for x in family_summary),
             issue_counts={k: len(v) for k, v in issues.items()}, b2b_populated=sum(x['b2b'] is not None for x in nonparents),
             sale_active=sum(x['sale_active_by_dates'] for x in nonparents))
(root / 'category-report-audit.json').write_text(json.dumps(dict(asof='2026-10-31T11:31:00Z', stats=stats, rows=rows,
                issues=issues, same_asin_conflicts=conflicts, families=family_summary), ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(stats, ensure_ascii=False, indent=2))
for key in ['b2b_higher_than_effective', 'minimum_above_regular']:
    print(key, [(x['sku'], x['price'], x['effective_before_coupons'], x['b2b'], x['minimum'], x['available10_30'], x['offer_stop_passed']) for x in issues[key]])
print('TYPEMISMATCH', [(x['sku'], x['product_type'], x['parent']) for x in issues['child_parent_type_mismatch']])
