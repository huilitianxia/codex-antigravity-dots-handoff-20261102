import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

found = []
for c in range(1, ws.max_column + 1):
    h4 = str(ws.cell(4, c).value or '')
    h5 = str(ws.cell(5, c).value or '')
    if any(k in h4.lower() or k in h5.lower() for k in ['upc', 'ean', 'gtin', 'barcode', 'standard_product_id', 'product id', 'external_product_id']):
        found.append((c, openpyxl.utils.get_column_letter(c), h4, h5))

print(f"Total matching columns: {len(found)}")
for x in found:
    print(x)
