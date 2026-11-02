import json
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

m1 = r"C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx"
wb1 = openpyxl.load_workbook(m1, read_only=True, data_only=True)
print("Master 1 sheets:", wb1.sheetnames)
for s in wb1.sheetnames:
    ws = wb1[s]
    rows = list(ws.iter_rows(min_row=1, max_row=8, values_only=True))
    print(f"  Sheet {s}: max_row={ws.max_row}, headers={rows[0][:18] if rows else []}")
wb1.close()

m2 = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\4A_库存分类与合并复核_20261031.xlsx"
wb2 = openpyxl.load_workbook(m2, read_only=True, data_only=True)
print("Master 2 sheets:", wb2.sheetnames)
for s in wb2.sheetnames:
    ws = wb2[s]
    rows = list(ws.iter_rows(min_row=1, max_row=5, values_only=True))
    print(f"  Sheet {s}: max_row={ws.max_row}, headers={rows[0][:18] if rows else []}")
wb2.close()
