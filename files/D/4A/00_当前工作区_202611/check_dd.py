import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws_dd = wb['Data Definitions']

for r in range(1, ws_dd.max_row + 1):
    val = str(ws_dd.cell(r, 1).value or '') + " " + str(ws_dd.cell(r, 2).value or '')
    if any(k in val.lower() for k in ['product id type', 'product id', 'standard_product_id']):
        print(f"Row {r}:", [ws_dd.cell(r, c).value for c in range(1, 6)])
