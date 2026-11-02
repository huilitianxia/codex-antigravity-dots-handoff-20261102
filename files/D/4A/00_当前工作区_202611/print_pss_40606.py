import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_当前工作区_202611\residual_mfn16_evidence_audit.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if item['sku'] in ['4A PSS 9-5 NB', '4A 40606']:
        print(f"=== {item['sku']} ===")
        print(json.dumps(item, ensure_ascii=False, indent=2))
