import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\samepage-stocked-fba-execution.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print("Keys in samepage-stocked-fba-execution:", list(data.keys()) if isinstance(data, dict) else len(data))
    if isinstance(data, list):
        print("First item:", json.dumps(data[0], indent=2, ensure_ascii=False))
    elif isinstance(data, dict):
        for k in list(data.keys())[:5]:
            print(k, "->", str(data[k])[:100])
