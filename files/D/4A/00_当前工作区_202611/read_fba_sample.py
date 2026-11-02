import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\samepage-stocked-fba-execution.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print("Total rows:", len(data['rows']))
    print("First 3 rows:")
    for r in data['rows'][:3]:
        print(json.dumps(r, indent=2, ensure_ascii=False))
