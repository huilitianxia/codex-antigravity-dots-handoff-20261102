import json, openpyxl

with open(r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\samepage-stocked-fba-execution.json', encoding='utf-8') as f:
    sp = json.load(f)

key_models = ['303x12', '30315', '354818', '406x6', '5088', '5084', '5082', '301', '2028', '608', 'PSS 32', '1801', '305x6']
print("=== VC Classic Models in Stocked FBA (129 rows) ===")
for r in sp.get('rows', []):
    s = str(r.get('sku', '')) + ' ' + str(r.get('title', ''))
    if any(k.lower() in s.lower() for k in key_models):
        print(f"{r.get('sku'):<24} | {r.get('asin')} | FBA={r.get('fba_stock_saved_scan')} | 30d_units={r.get('units30_fba_saved')} | route={r.get('route')} | cross={r.get('cross_asin_candidates')}")

# Also check all 303x12, 30315, 354818 SKUs in 11-01 All Listings Report
import csv
print("\n=== All 303x12 / 30315 / 354818 in 11-01 Report ===")
with open(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt', encoding='utf-8', errors='replace') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for row in reader:
        sku = row.get('seller-sku', '')
        title = row.get('item-name', '')
        if any(k in (sku + ' ' + title).lower() for k in ['303x12', '30315', '354818']):
            print(f"{sku:<26} | {row.get('asin1')} | status={row.get('status'):<10} | ch={row.get('fulfillment-channel'):<10} | price={row.get('price'):<6} | qty={row.get('quantity')}")
