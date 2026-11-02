import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

wb = openpyxl.load_workbook(r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx", read_only=True, data_only=True)
ws = wb["Sheet1"]
headers = [str(c) if c is not None else '' for c in next(ws.iter_rows(min_row=1, max_row=1, values_only=True))]
print("Headers:", list(enumerate(headers)))
for i, r in enumerate(ws.iter_rows(min_row=40, max_row=65, values_only=True), 40):
    if any(r):
        print(f"Row {i:2d}: {[(idx, str(c)) for idx, c in enumerate(r) if c is not None]}")
wb.close()
