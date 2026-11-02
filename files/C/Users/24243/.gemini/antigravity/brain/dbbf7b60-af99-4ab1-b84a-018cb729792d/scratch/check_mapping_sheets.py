import openpyxl

wb = openpyxl.load_workbook(r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx', data_only=True)
print("Sheet names:", wb.sheetnames)

for sname in wb.sheetnames:
    ws = wb[sname]
    print(f"\nSheet '{sname}' max_row={ws.max_row}, max_col={ws.max_column}")
    headers = [ws.cell(1, c).value for c in range(1, min(ws.max_column + 1, 20))]
    print("Headers:", headers)
