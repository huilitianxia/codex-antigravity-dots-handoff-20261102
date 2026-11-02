import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

parent_dir = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d"
scratch = os.path.join(parent_dir, "scratch")

for jf in ["oos_items.json", "enriched_oos.json", "oos_matched_analysis.json"]:
    jp = os.path.join(scratch, jf)
    if os.path.exists(jp):
        with open(jp, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"=== {jf} ===")
            print(f"type: {type(data)}, len: {len(data)}")
            if len(data) > 0:
                print("sample item 0:", json.dumps(data[0], ensure_ascii=False)[:300])

inv_md = os.path.join(parent_dir, "inventory_first_3_pages_audit.md")
if os.path.exists(inv_md):
    with open(inv_md, 'r', encoding='utf-8') as f:
        print("=== inventory_first_3_pages_audit.md ===")
        print(f.read()[:1000])
