import os
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

p1 = r"E:\OpenAI-Codex\Workspaces\C-Documents\2026-08-28\new-task-handoff-2026-08-28\work\vc_sc_audit_data.json"
p2 = r"E:\OpenAI-Codex\Workspaces\C-Documents\2026-08-28\new-task-handoff-2026-08-28\work\vc_sales_audit_results.json"

for p in [p1, p2]:
    if os.path.exists(p):
        print(f"=== {p} ({os.path.getsize(p)} bytes) ===")
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print("Type:", type(data))
            if isinstance(data, dict):
                print("Keys:", list(data.keys()))
                for k in list(data.keys())[:3]:
                    val = data[k]
                    if isinstance(val, list):
                        print(f"  {k}: len={len(val)}, item[0]={val[0] if len(val)>0 else None}")
                    else:
                        print(f"  {k}: {type(val)}")
            elif isinstance(data, list):
                print(f"List len={len(data)}, item[0]={data[0] if len(data)>0 else None}")
