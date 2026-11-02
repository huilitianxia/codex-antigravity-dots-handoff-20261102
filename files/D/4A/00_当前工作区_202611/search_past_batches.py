import openpyxl
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

bdir = r"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传"
for fname in sorted(os.listdir(bdir)):
    if fname.endswith(".xlsm"):
        wb = openpyxl.load_workbook(os.path.join(bdir, fname), data_only=True)
        ws = wb['Template']
        for r in range(7, ws.max_row + 1):
            sku = ws.cell(r, 3).value
            if sku in ['4A PSS 9-5 NB', '4A 40606']:
                cells = [(openpyxl.utils.get_column_letter(c), ws.cell(4, c).value, ws.cell(r, c).value) for c in range(1, ws.max_column+1) if ws.cell(r, c).value is not None]
                print(f"File {fname} Row {r} SKU={sku}: {cells}")
