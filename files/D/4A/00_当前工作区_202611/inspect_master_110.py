import openpyxl

wb_master = openpyxl.load_workbook(r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx', data_only=True)
ws_master = wb_master['Sheet1']
headers = [ws_master.cell(1, c).value for c in range(1, ws_master.max_column + 1)]
row_110 = [ws_master.cell(110, c).value for c in range(1, ws_master.max_column + 1)]

print('=== 2026 MASTER ROW 110 ===')
for h, v in zip(headers, row_110):
    if v is not None:
        print(f'{h}: {v}')
wb_master.close()
