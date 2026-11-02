import os
import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

def scan_conv(conv_id):
    steps_dir = rf"C:\Users\24243\.gemini\antigravity\brain\{conv_id}\.system_generated\steps"
    if not os.path.exists(steps_dir): return []
    found_items = []
    for s in os.listdir(steps_dir):
        op = os.path.join(steps_dir, s, "output.txt")
        if os.path.exists(op) and os.path.getsize(op) > 1000:
            with open(op, 'r', encoding='utf-8', errors='ignore') as f:
                txt = f.read()
                blocks = re.findall(r'```json\s*([\s\S]*?)\s*```', txt)
                for b in blocks:
                    try:
                        d = json.loads(b)
                        if isinstance(d, list) and len(d) > 0 and isinstance(d[0], dict) and ('asin' in d[0] or 'sku' in d[0]):
                            print(f"Conv {conv_id[:8]} Step {s}: found {len(d)} items")
                            found_items.extend(d)
                    except Exception:
                        pass
    return found_items

items_f1 = scan_conv("f1367eb9-fa19-4a11-abf4-4dc63e32dd4b")
items_db = scan_conv("dbbf7b60-af99-4ab1-b84a-018cb729792d")
print(f"Total from f1: {len(items_f1)}, db: {len(items_db)}")
