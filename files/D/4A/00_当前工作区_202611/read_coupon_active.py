import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

for fname in ['coupon15-final22-product-acceptance.json', 'coupon5-final12-live-acceptance.json', 'coupon-expanded-execution-ledger.json']:
    fp = rf"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\{fname}"
    with open(fp, "r", encoding="utf-8") as f:
        d = json.load(f)
        print(f"=== {fname} ===")
        print("Keys:", list(d.keys()) if isinstance(d, dict) else len(d))
        if isinstance(d, dict):
            if 'asins' in d:
                print("ASINs count:", len(d['asins']), d['asins'])
            elif 'rows' in d:
                print("Rows count:", len(d['rows']))
