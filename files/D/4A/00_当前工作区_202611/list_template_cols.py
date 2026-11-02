import openpyxl

cat_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb['Template']
rows = list(ws.iter_rows(min_row=1, max_row=5, values_only=True))
wb.close()

row4 = rows[3]
row5 = rows[4]
for idx, (r4, r5) in enumerate(zip(row4, row5)):
    if r4 is not None or r5 is not None:
        print(f"Col {idx:3d}: {str(r4):<35} | {str(r5)}")
