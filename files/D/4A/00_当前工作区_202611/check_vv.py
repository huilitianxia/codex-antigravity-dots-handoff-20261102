import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws_vv = wb['Valid Values']
print("Valid values sheet rows:", ws_vv.max_row, "cols:", ws_vv.max_column)

for r in range(1, 50):
    for c in range(1, ws_vv.max_column + 1):
        v = ws_vv.cell(r, c).value
        if v and any(x in str(v).lower() for x in ['product id type', 'asin', 'upc', 'ean', 'gtin']):
            print(f"Row {r}, Col {c}: {v}")
            # print column header
            print(f"  Header at row 1, col {c}: {ws_vv.cell(1, c).value}")
