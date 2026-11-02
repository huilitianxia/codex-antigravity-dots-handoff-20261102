import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-expanded-execution-ledger.json", "r", encoding="utf-8") as f:
    ledger = json.load(f)

print("final15_running_asins:", len(ledger.get("final15_running_asins", [])), ledger.get("final15_running_asins", []))
print("final5_running_asins:", len(ledger.get("final5_running_asins", [])), ledger.get("final5_running_asins", []))

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-fullscan-parsed.json", "r", encoding="utf-8") as f:
    scan = json.load(f)

print("\n=== SCAN ITEMS ===")
items = scan if isinstance(scan, list) else scan.get("rows", scan.get("items", []))
for k, v in (scan.items() if isinstance(scan, dict) else []):
    if not isinstance(v, list):
        print(f"  {k}: {v}")
    else:
        print(f"  {k} (list len={len(v)}):")
        for x in v[:40]:
            print("   ", x)
