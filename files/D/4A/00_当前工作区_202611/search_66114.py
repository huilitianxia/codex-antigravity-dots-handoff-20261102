import json

audit_path = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\12-processing-receipt-audit.json'
with open(audit_path, 'r', encoding='utf-8') as f:
    audit = json.load(f)

print("Searching for 66114 in 12-processing-receipt-audit.json:")
for r in audit.get('rows_detail', []):
    if '66114' in str(r):
        print("rows_detail:", r)

for err in audit.get('sku_errors', []):
    if '66114' in str(err):
        print("sku_errors:", err)
