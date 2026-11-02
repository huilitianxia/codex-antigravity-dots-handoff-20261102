import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

for row_idx, sku in [(588, "4A PSS 9-5 NB"), (230, "4A 40606")]:
    print(f"=== {sku} (row {row_idx}) ===")
    for col in range(1, ws.max_column + 1):
        v = ws.cell(row_idx, col).value
        if v is not None:
            print(f"Col {col:3d} ({openpyxl.utils.get_column_letter(col):4s}) [{ws.cell(4, col).value}]: {v}")
