import openpyxl
import csv
import sys

sys.stdout.reconfigure(encoding="utf-8")

# Let's check all Excel files in D:\4A to see where factory/warehouse inventory is recorded!
import glob
for path in glob.glob(r"D:\4A\**\*.xlsx", recursive=True):
    if "~$" in path: continue
    try:
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        print(f"File: {path} -> Sheets: {wb.sheetnames}")
        wb.close()
    except Exception as e:
        pass
