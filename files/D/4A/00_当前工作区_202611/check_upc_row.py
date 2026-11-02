import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

for r in range(7, ws.max_row + 1):
    t = ws.cell(r, 12).value
    if t == 'UPC':
        print(f"Row {r}: SKU={ws.cell(r,3).value}, Type={t}, ID={ws.cell(r,13).value}")
