import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

parent_dir = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch"
for jf in ["ss_217940.json", "ss_863796.json", "ss_863876.json"]:
    jp = os.path.join(parent_dir, jf)
    if os.path.exists(jp):
        with open(jp, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"=== {jf} ===")
            print(f"source: {data.get('source')}")
            sheets = data.get('sheets', [])
            for s in sheets:
                name = s.get('name')
                rows = s.get('rows', [])
                print(f"  Sheet: {name}, rows: {len(rows)}")
                if len(rows) > 0:
                    print(f"    Row 0: {rows[0]}")
