import openpyxl

file_path = r'd:\下载文件\4A_全店21大家族精细化变体清洗_终极纯净版-processing-summary (1).xlsm'
wb = openpyxl.load_workbook(file_path, data_only=True)
print("Sheet names:", wb.sheetnames)

for sname in wb.sheetnames:
    ws = wb[sname]
    print(f"Sheet '{sname}' max_row={ws.max_row}, max_col={ws.max_column}")

# Let's inspect 'Processing Summary' or similar sheet
ws_sum = wb[wb.sheetnames[0]]
for r in range(1, min(ws_sum.max_row + 1, 30)):
    row_vals = [ws_sum.cell(r, c).value for c in range(1, min(ws_sum.max_column + 1, 10))]
    if any(row_vals):
        print(f"Row {r}: {row_vals}")
