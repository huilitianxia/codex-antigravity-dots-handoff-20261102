import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\12-final-processing-summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Keys:", list(data.keys()))
for k, v in data.items():
    if isinstance(v, list):
        print(f"Key {k} has {len(v)} items")
        for x in v:
            if isinstance(x, dict) and x.get('sku') in ['4A 40606', '4A PSS 9-5 NB']:
                print(x)
