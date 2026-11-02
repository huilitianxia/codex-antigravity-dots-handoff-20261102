import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

wb = openpyxl.load_workbook(r"D:\4A\印刷用图片\电商\国内电商图片\新款备货-19-0710.xlsx", read_only=True, data_only=True)
ws = wb[wb.sheetnames[0]]
for i, r in enumerate(ws.iter_rows(min_row=1, max_row=40, values_only=True), 1):
    if any(r):
        print(f"Row {i:2d}: {[str(c) if c is not None else '' for c in r[:12]]}")
wb.close()
