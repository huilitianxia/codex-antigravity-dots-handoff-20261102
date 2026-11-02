import openpyxl

path_13 = r'D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\13-0146-office-only.xlsm'
wb = openpyxl.load_workbook(path_13, data_only=True)
ws = wb['Template']

print("=== Checking populated rows in 13-0146-office-only.xlsm Template ===")
populated_data_rows = []

for r in range(7, ws.max_row + 1):
    non_empty = []
    for c in range(1, ws.max_column + 1):
        v = ws.cell(r, c).value
        if v is not None:
            c_letter = openpyxl.utils.get_column_letter(c)
            non_empty.append((c_letter, c, v))
    if non_empty:
        populated_data_rows.append((r, non_empty))

print(f"Total populated data rows (r >= 7): {len(populated_data_rows)}")
for r, cells in populated_data_rows:
    cell_desc = [f"{col}: '{val}'" for col, idx, val in cells]
    print(f"Row {r:3d}: {', '.join(cell_desc)}")

wb.close()
