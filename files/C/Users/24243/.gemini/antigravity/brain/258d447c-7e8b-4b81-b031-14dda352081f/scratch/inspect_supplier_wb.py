import os
import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

path = r"C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx"
print("Loading workbook:", path)
wb = openpyxl.load_workbook(path, read_only=True)
print("Sheet names:", wb.sheetnames)
for name in wb.sheetnames:
    sheet = wb[name]
    print(f"\nSheet '{name}':")
    row_count = 0
    for row in sheet.iter_rows(values_only=True):
        row_count += 1
        if row_count <= 3:
            clean = [str(x)[:30] if x is not None else '' for x in row[:15]]
            print(f"  Row {row_count}: {clean}")
        if row_count > 100000:
            break
    print(f"  Total read rows: {row_count}")
