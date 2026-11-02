import openpyxl

cat_report_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb = openpyxl.load_workbook(cat_report_path, data_only=True)
ws = wb['Template']

cols_to_check = [
    3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 20, 57, 58, 59, 60, 61
]

print("=== Template Header Rows 1, 2, 3 ===")
for c in range(1, 70):
    c_letter = openpyxl.utils.get_column_letter(c)
    val1 = ws.cell(1, c).value
    val2 = ws.cell(2, c).value
    val3 = ws.cell(3, c).value
    if val2 is not None or val3 is not None:
        print(f"Col {c_letter} ({c}): Row1='{val1}', Row2='{val2}', Row3='{val3}'")

wb.close()
