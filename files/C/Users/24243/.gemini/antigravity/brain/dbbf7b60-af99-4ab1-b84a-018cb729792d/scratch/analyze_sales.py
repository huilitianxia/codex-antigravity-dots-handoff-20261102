import sys, re, os
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 1. Parse extracted_order_data.txt
with open(r'E:\Desktop\extracted_order_data.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Also check subagent_orders_step5336.txt
if os.path.exists(r'E:\Desktop\subagent_orders_step5336.txt'):
    with open(r'E:\Desktop\subagent_orders_step5336.txt', 'r', encoding='utf-8', errors='ignore') as f:
        text += '\n' + f.read()

# Let's find order snippets
# Format typically:
# 112-9915637-7582645
# ASIN: B08DKJ2K3T
# SKU: 4A SCPSS 32x6
# 数量: 1
# 商品小计: US$13.99

pattern = re.compile(r'(?:订单编号:?\s*([0-9\-]+)|([0-9]{3}-[0-9]{7}-[0-9]{7}))[\s\S]*?ASIN:\s*([A-Z0-9]{10})[\s\S]*?SKU:\s*([^\n\r\|]+)[\s\S]*?数量:\s*(\d+)[\s\S]*?商品小计:\s*[A-Z]*\$([0-9\.,]+)')

matches = pattern.findall(text)
print(f'Total regex matches: {len(matches)}')

# In case pattern misses some, let's also split by order cards
cards = re.split(r'(?=[0-9]{3}-[0-9]{7}-[0-9]{7})', text)
print(f'Total order card chunks: {len(cards)}')

orders = []
seen_order_asins = set()

for c in cards:
    order_id_m = re.search(r'([0-9]{3}-[0-9]{7}-[0-9]{7})', c)
    asin_m = re.search(r'ASIN:\s*([A-Z0-9]{10})', c)
    sku_m = re.search(r'SKU:\s*([^\n\r\|]+)', c)
    qty_m = re.search(r'数量:\s*(\d+)', c)
    price_m = re.search(r'商品小计:\s*[A-Z]*\$([0-9\.,]+)', c)
    title_m = re.search(r'(4A[^\n\r\|]{10,90})', c)
    is_biz = '企业买家' in c or 'Business Buyer' in c

    if asin_m and (order_id_m or price_m):
        oid = order_id_m.group(1) if order_id_m else 'UNKNOWN'
        asin = asin_m.group(1).strip()
        sku = sku_m.group(1).strip() if sku_m else 'UNKNOWN'
        qty = int(qty_m.group(1)) if qty_m else 1
        price = float(price_m.group(1).replace(',', '')) if price_m else 0.0
        title = title_m.group(1).strip() if title_m else ''

        key = (oid, asin)
        if key not in seen_order_asins:
            seen_order_asins.add(key)
            orders.append({
                'order_id': oid,
                'asin': asin,
                'sku': sku,
                'qty': qty,
                'price': price,
                'title': title,
                'is_biz': is_biz
            })

print(f'Unique order items: {len(orders)}')

by_asin = defaultdict(lambda: {'count': 0, 'qty': 0, 'revenue': 0.0, 'skus': set(), 'titles': set(), 'biz_count': 0})
for o in orders:
    a = o['asin']
    by_asin[a]['count'] += 1
    by_asin[a]['qty'] += o['qty']
    by_asin[a]['revenue'] += o['price']
    by_asin[a]['skus'].add(o['sku'])
    if o['title']:
        by_asin[a]['titles'].add(o['title'])
    if o['is_biz']:
        by_asin[a]['biz_count'] += 1

print('\n' + '='*80)
print(f"{'ASIN':<12} | {'分类':<10} | {'件数':<5} | {'金额($)':<8} | {'企业':<4} | {'SKU':<25}")
print('='*80)

sorted_by_qty = sorted(by_asin.items(), key=lambda x: (x[1]['qty'], x[1]['revenue']), reverse=True)

full_glue_asins = {'B07QXJYTZ7', 'B0FBG138ND', 'B0F2TKL2P5', 'B07FK975YB', 'B00SMEFFRE', 'B07QXJWDPL', 'B00SMEG5XW', 'B01LW6N0WA'}

total_revenue = sum(d['revenue'] for d in by_asin.values())
total_qty = sum(d['qty'] for d in by_asin.values())

fg_revenue = sum(d['revenue'] for a, d in by_asin.items() if a in full_glue_asins)
fg_qty = sum(d['qty'] for a, d in by_asin.items() if a in full_glue_asins)

non_fg_revenue = total_revenue - fg_revenue
non_fg_qty = total_qty - fg_qty

print(f"全店核查总件数: {total_qty} 件, 总金额: ${total_revenue:.2f}")
print(f"满胶系列: {fg_qty} 件 ({fg_qty/total_qty*100:.1f}%), 金额: ${fg_revenue:.2f} ({fg_revenue/total_revenue*100:.1f}%)")
print(f"非满胶(自主激活): {non_fg_qty} 件 ({non_fg_qty/total_qty*100:.1f}%), 金额: ${non_fg_revenue:.2f} ({non_fg_revenue/total_revenue*100:.1f}%)")
print('='*80)

rank = 1
for a, d in sorted_by_qty:
    is_fg = a in full_glue_asins
    cat = '【满胶-传统】' if is_fg else '【非满胶-自营】'
    skus_str = ', '.join(d['skus'])[:24]
    print(f"Top {rank:2d}: {a} | {cat} | {d['qty']:2d}件 | ${d['revenue']:7.2f} | {d['biz_count']}单企业 | SKU: {skus_str}")
    rank += 1
