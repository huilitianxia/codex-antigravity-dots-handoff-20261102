import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\12-final-processing-summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data.get('skus', []):
    if item.get('sku') in ['4A 40606', '4A PSS 9-5 NB']:
        print(f"=== {item.get('sku')} in 12-final-summary ===")
        print(json.dumps(item, indent=2, ensure_ascii=False))
