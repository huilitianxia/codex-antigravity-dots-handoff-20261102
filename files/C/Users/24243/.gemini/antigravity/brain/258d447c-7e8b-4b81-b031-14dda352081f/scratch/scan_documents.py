import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for p in [r"C:\Users\24243\Documents", r"E:\OpenAI-Codex"]:
    print(f"=== Scanning {p} ===")
    if os.path.exists(p):
        for root, dirs, files in os.walk(p):
            for f in files:
                if f.endswith(('.json', '.csv', '.xlsx', '.txt', '.md')):
                    full = os.path.join(root, f)
                    if any(k in f.lower() for k in ['vc', 'inventory', 'sc', '4a', 'sku', 'asin', 'sales', 'audit']):
                        print(f"  {full} ({os.path.getsize(full)} bytes)")
    else:
        print("Not found")
