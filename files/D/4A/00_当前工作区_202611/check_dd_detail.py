import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws_dd = wb['Data Definitions']

# Find row 18 (amzn1.volt.ca.product_id_type) and row 19 (amzn1.volt.ca.product_id_value)
for col in range(1, 10):
    print(f"Col {col}: R18={ws_dd.cell(18, col).value!r} | R19={ws_dd.cell(19, col).value!r}")
