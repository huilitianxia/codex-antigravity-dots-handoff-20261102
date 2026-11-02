import openpyxl

wb = openpyxl.load_workbook(r'E:\Desktop\全店幽灵死链接归档隔离库_待后续安全删除.xlsx', data_only=True)
print("Sheet names:", wb.sheetnames)

ws1 = wb['160个AAAA幽灵链接(隔离池)']
print(f"Sheet 1 rows: {ws1.max_row}, cols: {ws1.max_column}")
headers1 = [ws1.cell(1, c).value for c in range(1, ws1.max_column + 1)]
print("Sheet 1 headers:", headers1)

for r in range(2, min(ws1.max_row + 1, 15)):
    vals = [ws1.cell(r, c).value for c in range(1, ws1.max_column + 1)]
    print(f"Row {r}: {vals}")
