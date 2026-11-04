import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent
bulk = json.loads((ROOT / 'ad-cleanup-20261103/bulk-source-allrows.json').read_text(encoding='utf-8-sig'))
inventory = json.loads((ROOT / 'full-coverage/source-sc-current-20261103.json').read_text(encoding='utf-8-sig'))
cohort = [
    ('30315', 'B07FKG29KB', ['B07F295DPC']),
    ('PSS32x6', 'B08CVLH794', ['B08DKJ2K3T']),
    ('404AC-holder', 'B07Z2555TN', ['B07WK3JX6K']),
    ('2028-N', 'B07DJXC4PJ', ['B07F295V3S']),
    ('5082-Y-L', 'B07F2BHFJH', ['B07DJKB2S9']),
    ('304FullGlue', 'B00SMEFFRE', []),
    ('4012', 'B01M3N310M', []),
]
metrics = {'impressions': '展示量', 'clicks': '点击量', 'spend': '花费', 'attributed_sales': '销量', 'attributed_orders': '订单数量', 'attributed_units': '商品数量'}
ads = [r for r in bulk['rows'] if r.get('实体层级') == '商品广告']
out = {'source': bulk['source'], 'period': bulk['period'], 'metric_grain': 'Sponsored Products product-ad rows; never sum with campaign/keyword rows',
       'limitations': ['Current export metrics may differ slightly between entity levels due to processing; use SKU rows consistently.',
                       'Ad-attributed orders are not all orders and do not alone establish actual purchased fulfillment channel.',
                       'New FBM SKUs were created today; historical zero metrics for these new SKUs do not measure prior performance.',
                       'Inventory export predates the new FBM creation and stock consolidation; use live readbacks for current quantities.'], 'products': []}
for code, asin, previous in cohort:
    asins = [asin] + previous
    product = {'code': code, 'selected_asin': asin, 'previous_or_alternate_asins': previous, 'asins': []}
    for a in asins:
        rows = [r for r in ads if r.get('ASIN（仅供参考）') == a]
        inv = [r for r in inventory if r.get('asin1') == a]
        skus = sorted(set([r['SKU'] for r in rows if r.get('SKU')] + [r['seller-sku'] for r in inv]))
        per_sku = []
        for sku in skus:
            sr = [r for r in rows if r.get('SKU') == sku]
            ir = next((r for r in inv if r['seller-sku'] == sku), {})
            stats = {k: round(sum(float(r.get(v) or 0) for r in sr), 2) for k, v in metrics.items()}
            per_sku.append({'sku': sku, 'fulfillment_export': ir.get('fulfillment-channel'), 'export_price': ir.get('price'),
                            'export_quantity': ir.get('quantity'), 'export_status': ir.get('status'), 'ad_rows': len(sr), **stats,
                            'nonzero_ad_records': [{'campaign': r.get('广告活动名称（仅供参考）'), 'campaign_id': r.get('广告活动编号'),
                                                    **{k:r.get(v) for k,v in metrics.items()}} for r in sr if r.get('展示量') or r.get('花费')]})
        totals = {k: round(sum(float(r.get(v) or 0) for r in rows), 2) for k,v in metrics.items()}
        product['asins'].append({'asin': a, 'ad_rows': len(rows), 'sku_stats': per_sku, **totals})
    out['products'].append(product)
(ROOT / 'fbm-funnel-historical-ad-evidence.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps([{'code': p['code'], 'asins': [{k:a[k] for k in ['asin','ad_rows','impressions','clicks','spend','attributed_sales','attributed_orders']} for a in p['asins']]} for p in out['products']], ensure_ascii=True))
