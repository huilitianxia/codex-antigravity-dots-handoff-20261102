import openpyxl

wb = openpyxl.load_workbook(r'D:\下载文件\Add_new_variant.xlsm', data_only=True)
ws = wb['Template']

for c in range(1, 16):
    print(f"Col {c}: Row 4='{ws.cell(4, c).value}', Row 5='{ws.cell(5, c).value}'")
