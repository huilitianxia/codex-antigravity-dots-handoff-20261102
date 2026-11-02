import openpyxl

wb = openpyxl.load_workbook(r'D:\下载文件\Add_new_variant.xlsm', data_only=True)
ws = wb['Template']

print("Row 1 col 1..10:", [ws.cell(1, c).value for c in range(1, 11)])
print("Row 2 col 1..10:", [ws.cell(2, c).value for c in range(1, 11)])
print("Row 3 col 1..10:", [ws.cell(3, c).value for c in range(1, 11)])
print("Row 4 col 1..10:", [ws.cell(4, c).value for c in range(1, 11)])
print("Row 5 col 1..10:", [ws.cell(5, c).value for c in range(1, 11)])
