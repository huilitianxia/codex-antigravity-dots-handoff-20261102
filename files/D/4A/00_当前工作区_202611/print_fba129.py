import json

with open(r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\samepage-stocked-fba-execution.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print("=== TOP FBA IN-STOCK SKUS FROM samepage-stocked-fba-execution.json ===")
for r in sorted(d['rows'], key=lambda x: -x['fba_units_scan']):
    mfn_info = [(m['sku'], m.get('quantity'), m.get('shipping_template')) for m in r.get('active_same_asin_mfn', [])]
    c_reason = r['coupon_reasons'][0] if r.get('coupon_reasons') else 'OK'
    print(f"FBA={r['fba_units_scan']:4d} | 30d={r['units30_fba']:3d} | Price=${r['price_snapshot']:6.2f} | Rating={str(r.get('historical_ratings_unverified')):8s} | Coupon={str(r['coupon_selectable']):5s} | SKU={r['sku']:26s} | ASIN={r['asin']} | MFN={mfn_info} | {c_reason[:30]}")
