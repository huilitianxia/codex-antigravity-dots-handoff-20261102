import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\下载文件\12-catalog-text-repairs-only-processing-summary.xlsm", data_only=True)
ws = wb['Feed Processing Summary']
for r in range(1, ws.max_row + 1):
    vals = [ws.cell(r, c).value for c in range(1, 10)]
    if any("40624" in str(v or '') for v in vals):
        print(f"Row {r:3d}: {vals}")
