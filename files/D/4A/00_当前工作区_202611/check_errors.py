import json

path = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\residual62-closeout.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

mfn_rows = [r for r in data['rows'] if r.get('inventory_group') == '仅MFN有申报库存']

for i, r in enumerate(mfn_rows):
    print(f"Index {i+1}: SKU={r['sku']}, ASIN={r['asin']}")
    print(f"  All codes: {r.get('all_codes')}")
    print(f"  Errors:")
    for err in r.get('errors', []):
        print(f"    Code: {err.get('code')}, Severity: {err.get('severity')}")
        print(f"    Msg: {err.get('message')[:160]}...")
