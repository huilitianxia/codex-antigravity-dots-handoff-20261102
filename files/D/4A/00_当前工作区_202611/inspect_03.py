import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\03-catalog-errors-consolidated.xlsm", data_only=True)
ws = wb['Template']

print("Max rows in 03:", ws.max_row)
for r in range(7, ws.max_row + 1):
    sku = ws.cell(r, 3).value
    non_empty = []
    for c in range(1, ws.max_column + 1):
        v = ws.cell(r, c).value
        if v is not None:
            non_empty.append((openpyxl.utils.get_column_letter(c), ws.cell(4, c).value, ws.cell(5, c).value, v))
    print(f"Row {r} (SKU={sku}):")
    for cell in non_empty:
        print("  ", cell)
