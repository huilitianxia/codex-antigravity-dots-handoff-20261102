import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

print("Searching column headers...")
terms = ['color', 'colour', 'manufacturer', 'standard_product_id', 'product_id', 'upc', 'product id']

for col in range(1, ws.max_column + 1):
    h4 = str(ws.cell(4, col).value or '').lower()
    h5 = str(ws.cell(5, col).value or '').lower()
    for t in terms:
        if t in h4 or t in h5:
            print(f"Col {col:3d} ({openpyxl.utils.get_column_letter(col):4s}): Row 4='{ws.cell(4, col).value}' | Row 5='{ws.cell(5, col).value}'")
            break
