import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\1801-orders-live-summary.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print("Keys in 1801-orders-live-summary:", list(data.keys()) if isinstance(data, dict) else len(data))
    if isinstance(data, dict):
        for k in list(data.keys())[:10]:
            print(k, "->", str(data[k])[:100])
