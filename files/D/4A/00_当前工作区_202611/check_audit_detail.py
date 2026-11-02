import json

audit_path = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\12-processing-receipt-audit.json'
with open(audit_path, 'r', encoding='utf-8') as f:
    audit = json.load(f)

targets = ['4A 039', '4A 040', '4A 037', '4A 0166', '4A095', '4A 66114', '4A 095',
           'B01N1T23HH', 'B01N7IT411', 'B01M617ZTH', 'B0784GHSVJ', 'B01M2UDADZ']

print("=== 1. Checking rows_detail ===")
for r in audit.get('rows_detail', []):
    sku = r.get('sku', '')
    asin = r.get('asin', '')
    if sku in targets or asin in targets:
        print(f"rows_detail match -> SKU: {sku}, ASIN: {asin}, Status: {r.get('status')}")
        for issue in r.get('issues', []):
            print(f"   Issue cell={issue.get('cell')}, sem_key={issue.get('semantic_key')}")
            print(f"   Message: {issue.get('message')}")

print("\n=== 2. Checking sku_errors ===")
for err in audit.get('sku_errors', []):
    count_or_sku = err.get('count_or_sku', '')
    msg = err.get('message', '')
    for t in targets:
        if t in count_or_sku or t in msg:
            print(f"sku_errors match for '{t}' -> code={err.get('code')}, severity={err.get('severity')}, field={err.get('field')}, count_or_sku={count_or_sku}")
            print(f"   Message: {msg[:200]}")

print("\n=== 3. Checking error_overview ===")
for err in audit.get('error_overview', []):
    msg = err.get('message', '')
    for t in targets:
        if t in msg:
            print(f"error_overview match for '{t}' -> code={err.get('code')}, field={err.get('field')}")
            print(f"   Message: {msg[:200]}")
