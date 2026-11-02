import openpyxl

cat_report_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb = openpyxl.load_workbook(cat_report_path, data_only=True)
ws = wb['Template']

print("Row 4 (Labels), Row 5 (Attributes), Row 6 (Type/Req) for key columns:")
cols_to_print = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 20, 44, 56, 57, 58, 59, 60, 61
]

for c in range(1, 80):
    c_letter = openpyxl.utils.get_column_letter(c)
    val4 = ws.cell(4, c).value
    val5 = ws.cell(5, c).value
    val6 = ws.cell(6, c).value
    if val4 is not None or val5 is not None:
        print(f"Col {c_letter} ({c}): Label(R4)='{val4}', Attr(R5)='{val5}'")

wb.close()
