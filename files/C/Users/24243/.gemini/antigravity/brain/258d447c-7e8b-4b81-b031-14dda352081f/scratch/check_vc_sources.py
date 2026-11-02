import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

p1 = r"E:\OpenAI-Codex\Workspaces\C-Documents\2026-08-28\new-task-handoff-2026-08-28\work\vc_sc_audit_data.json"
with open(p1, 'r', encoding='utf-8') as f:
    d = json.load(f)
    print("Sources:", json.dumps(d.get("sources"), indent=2, ensure_ascii=False))
    print("Summary:", json.dumps(d.get("summary"), indent=2, ensure_ascii=False))
    print("sc_missing count:", len(d.get("sc_missing", [])))
    print("vc_all count:", len(d.get("vc_all", [])))
    print("same_sku_diff_asin count:", len(d.get("same_sku_diff_asin", [])))
