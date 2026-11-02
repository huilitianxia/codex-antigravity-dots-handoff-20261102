import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')
wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", read_only=True, data_only=True)
ws = wb['Template']
rows = list(ws.iter_rows(values_only=True))
h4 = rows[3]
h5 = rows[4]
for i, (a, b) in enumerate(zip(h4, h5)):
    if any(k in str(b).lower() for k in ['item_name', 'bullet_point', 'product_description']):
        print(f"Col {i}: {a} | {b}")

targets = {
    "4A 5082-Y-Lx2",
    "4A 305-Full Adhesive",
    "4A 305-Full Adhesive-300",
    "AAAA 4A 305-Full Glue",
    "4A 304 Full Glue",
    "4A 304-Full Adhesive-400",
    "AAAA 4A 304-Full Glue",
    "4A 303-Full Adhesive-400",
    "4A 302-Full Adhesive-400",
    "4A SCPSS 32x6",
    "4A GM-SCPSS 32x6",
    "4A PSS 32x6",
}

for idx, r in enumerate(rows[6:], 7):
    if r and len(r) > 2 and r[2] in targets:
        print(f"\n=== Row {idx}: {r[2]} (ASIN={r[12]}) ===")
        print(f"  Title (Col 8): {r[8]}")
        for b_idx in range(14, 19):
            print(f"  Bullet {b_idx-13} (Col {b_idx}): {r[b_idx]}")
