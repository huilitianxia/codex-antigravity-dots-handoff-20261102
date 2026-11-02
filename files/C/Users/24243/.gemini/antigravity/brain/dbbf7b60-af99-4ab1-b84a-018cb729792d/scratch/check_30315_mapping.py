import openpyxl

wb = openpyxl.load_workbook(r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx', data_only=True)
ws = wb.worksheets[1]

print("--- 30315 Rows in Mapping Sheet ---")
for r in range(2, ws.max_row + 1):
    vals = [ws.cell(r, c).value for c in range(1, 13)]
    row_str = " ".join([str(v) for v in vals if v is not None])
    if '30315' in row_str:
        print(f"Row {r}: {vals}")
