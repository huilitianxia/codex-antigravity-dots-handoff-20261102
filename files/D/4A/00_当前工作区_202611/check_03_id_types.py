import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\03-catalog-errors-consolidated.xlsm", data_only=True)
ws = wb['Template']

types = set()
for r in range(7, ws.max_row + 1):
    pid_type = ws.cell(r, 12).value
    types.add(pid_type)
    if pid_type != 'ASIN':
        print(f"Row {r} SKU={ws.cell(r,3).value}: type={pid_type}, id={ws.cell(r,13).value}")

print("All ID types in 03:", types)
