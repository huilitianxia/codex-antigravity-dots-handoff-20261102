import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

r = 39 # 4A093
for c in range(1, ws.max_column + 1):
    val = ws.cell(r, c).value
    if val is not None:
        print(f"Col {c-1:3d} (1-based {c:3d}, {openpyxl.utils.get_column_letter(c):3s}) | {ws.cell(4, c).value} | {ws.cell(5, c).value} => {val!r}")
