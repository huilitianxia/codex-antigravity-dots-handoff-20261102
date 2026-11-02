import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-fullscan-parsed.json", "r", encoding="utf-8") as f:
    scan = json.load(f)

target_asins = {'B00SMEFFRE', 'B07QXJWDPL', 'B0FBG138ND', 'B0F2TKL2P5', 'B07FK975YB', 'B07QXJZKHC', 'B07FK9BYHW', 'B07RN7WQ81', 'B07F2BHFJH'}
print("=== IN COUPON-FULLSCAN-PARSED ===")
for r in scan['rows']:
    if r['asin'] in target_asins or '304' in str(r['sku']) or '305' in str(r['sku']) or '302' in str(r['sku']) or '5020' in str(r['sku']) or '5082' in str(r['sku']):
        print(f"SKU={r['sku']:24} | ASIN={r['asin']} | Ch={r['channel']} | Qty={r['units_current']:4} | Selectable={r['selectable']} | Selected={r['selected']} | Reasons={r['reasons']}")

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-expansion-77-complete-readonly-audit.json", "r", encoding="utf-8") as f:
    c77 = json.load(f)
print("\n=== IN COUPON-EXPANSION-77 ===")
for r in (c77 if isinstance(c77, list) else c77.get('rows', [])):
    print(r)
