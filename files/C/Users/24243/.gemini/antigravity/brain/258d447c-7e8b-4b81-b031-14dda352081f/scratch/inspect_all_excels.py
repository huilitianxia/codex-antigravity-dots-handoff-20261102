import os
import sys
import openpyxl
import csv

sys.stdout.reconfigure(encoding='utf-8')

def inspect_wb(path):
    print(f"\n======================================")
    print(f"FILE: {path}")
    print(f"======================================")
    wb = openpyxl.load_workbook(path, data_only=True)
    print("Sheets:", wb.sheetnames)
    for name in wb.sheetnames:
        sheet = wb[name]
        print(f"\n--- Sheet: {name} (Rows: {sheet.max_row}, Cols: {sheet.max_column}) ---")
        for r in range(1, min(6, sheet.max_row + 1)):
            vals = [sheet.cell(r, c).value for c in range(1, min(20, sheet.max_column + 1))]
            # truncate long strings
            clean_vals = [str(v)[:30] if v is not None else '' for v in vals]
            print(f"Row {r}: {clean_vals}")

inspect_wb(r"C:\Users\24243\Downloads\4A缺货_269评分已补全_被低估好款.xlsx")
inspect_wb(r"C:\Users\24243\Downloads\4A-SL缺货评分好款.xlsx")
inspect_wb(r"C:\Users\24243\Downloads\4A_2026-08-10库存.xlsx")
