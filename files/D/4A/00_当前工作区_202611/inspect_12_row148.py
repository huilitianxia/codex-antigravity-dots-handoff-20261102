import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\12-catalog-text-repairs-only.xlsm", data_only=True)
ws = wb['Template']

print("Row 148 in 12-catalog-text-repairs-only.xlsm:")
for c in range(1, ws.max_column + 1):
    v = ws.cell(148, c).value
    if v is not None:
        print(f"Col {c} ({openpyxl.utils.get_column_letter(c)}): Header='{ws.cell(4, c).value}' | Attr='{ws.cell(5, c).value}' | Val='{v}'")
