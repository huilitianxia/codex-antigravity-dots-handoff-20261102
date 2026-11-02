import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

print("=== 1. CURRENT CHILDREN OF PARENT-4A-BIGPAD-MEETING-EASEL ===")
for r in range(7, ws.max_row + 1):
    sku = str(ws.cell(r, 3).value or '')
    parent = ws.cell(r, 7).value
    if parent == 'PARENT-4A-BIGPAD-MEETING-EASEL' or sku == 'PARENT-4A-BIGPAD-MEETING-EASEL' or any(k in sku for k in ['1111', '1515', '2222', 'BP']):
        print(f"Row {r:3d} | {sku:24} | Parent={str(parent):32} | Theme={ws.cell(r,8).value} | ASIN={ws.cell(r,13).value} | Color={ws.cell(r,59).value!r} | Size={ws.cell(r,60).value!r}")

print("\n=== 2. ORPHANED IN-STOCK / CLASSIC FBA SKUS WITH PARENT=NONE ===")
for r in range(7, ws.max_row + 1):
    sku = str(ws.cell(r, 3).value or '')
    parent = ws.cell(r, 7).value
    plevel = ws.cell(r, 6).value
    asin = str(ws.cell(r, 13).value or '')
    if parent is None and plevel != 'Parent':
        print(f"Row {r:3d} | {sku:24} | ASIN={asin:12} | PLevel={str(plevel):8} | Color={ws.cell(r,59).value!r:20} | Size={ws.cell(r,60).value!r:25} | Title={str(ws.cell(r,10).value or '')[:55]}")
