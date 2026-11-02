import json

audit_path = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\12-processing-receipt-audit.json'
with open(audit_path, 'r', encoding='utf-8') as f:
    audit = json.load(f)

for r in audit.get('rows_detail', []):
    if r.get('sku') == '4A095':
        print("SKU 4A095 details:")
        print(json.dumps(r, ensure_ascii=False, indent=2))

for s in ['4A 039', '4A 040', '4A 037', '4A 0166']:
    for r in audit.get('rows_detail', []):
        if r.get('sku') == s:
            print(f"SKU {s} details:")
            print(json.dumps(r, ensure_ascii=False, indent=2))
