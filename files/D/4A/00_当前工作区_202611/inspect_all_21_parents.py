import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
rows = list(ws.iter_rows(min_row=7, values_only=True))

parents = {}
for r in rows:
    if r and len(r) > 6:
        if r[5] == "Parent":
            parents.setdefault(r[2], {"theme": r[7], "children": []})
        elif r[5] == "Child" and r[6]:
            parents.setdefault(r[6], {"theme": r[7], "children": []})["children"].append(r)

for p, info in sorted(parents.items(), key=lambda x: -len(x[1]["children"])):
    active_c = [c for c in info["children"] if c[0] == "Active"]
    print(f"{p:35s} | Theme={str(info['theme']):12s} | Total={len(info['children']):3d} | Active={len(active_c):2d}")
