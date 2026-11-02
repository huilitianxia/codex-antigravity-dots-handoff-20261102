import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

id_types = {}
for r in range(7, ws.max_row + 1):
    t = ws.cell(r, 12).value
    id_types[t] = id_types.get(t, 0) + 1

print("ID types in 分类商品报告:", id_types)
