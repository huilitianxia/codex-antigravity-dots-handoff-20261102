import os
import sys
import openpyxl
import csv
import json

sys.stdout.reconfigure(encoding='utf-8')

def inspect_excel(path):
    print(f"=== {path} ===")
    if not os.path.exists(path):
        print("FILE NOT FOUND!")
        return
    wb = openpyxl.load_workbook(path, data_only=True)
    print("Sheets:", wb.sheetnames)
    for sname in wb.sheetnames:
        sheet = wb[sname]
        print(f"Sheet '{sname}': Rows={sheet.max_row}, Cols={sheet.max_column}")
        for i in range(1, min(6, sheet.max_row + 1)):
            row_vals = [sheet.cell(i, j).value for j in range(1, min(15, sheet.max_column + 1))]
            print(f"  Row {i}:", row_vals)

def inspect_csv(path):
    print(f"=== {path} ===")
    if not os.path.exists(path):
        print("FILE NOT FOUND!")
        return
    for enc in ['utf-8', 'utf-8-sig', 'gbk', 'ansi']:
        try:
            with open(path, 'r', encoding=enc) as f:
                reader = csv.reader(f)
                rows = [next(reader, None) for _ in range(5)]
                print(f"Decoded with {enc}:")
                for r in rows:
                    if r is not None:
                        print(" ", r[:10])
                break
        except Exception as e:
            continue

inspect_excel(r"C:\Users\24243\Downloads\4A缺货_269款全量_历史好款.xlsx")
inspect_excel(r"C:\Users\24243\Downloads\4A-SL缺货好款.xlsx")
inspect_csv(r"E:\Desktop\WooCommerce_完整改价_163_SKUs_复核后上传_2026-08-20.csv")
