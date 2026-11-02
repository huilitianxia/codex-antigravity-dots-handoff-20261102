import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

for col in range(1, ws.max_column + 1):
    h4 = str(ws.cell(4, col).value or '')
    h5 = str(ws.cell(5, col).value or '')
    if 'product_id' in h4.lower() or 'product_id' in h5.lower() or 'standard' in h4.lower() or 'standard' in h5.lower():
        print(f"Col {col} ({openpyxl.utils.get_column_letter(col)}): Row 4='{h4}' | Row 5='{h5}'")
