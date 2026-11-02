import os
import openpyxl

terms = ['PSS 32', 'PSS32', 'B08DKJ2K3T', 'B08CVLH794', '702877126561', '702877126578', 'B0HPTC18T2']

def search_excel(filepath):
    print(f'Checking {filepath}...')
    try:
        wb = openpyxl.load_workbook(filepath, data_only=True, read_only=True)
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            for row_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
                row_str = ' | '.join([str(c) for c in row if c is not None])
                for t in terms:
                    if t.lower() in row_str.lower():
                        print(f'  [{sheet_name}:Row {row_idx}] Match "{t}": {row_str[:300]}...')
                        break
        wb.close()
    except Exception as e:
        print(f'  Error reading {filepath}: {e}')

files_to_check = [
    r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx',
    r'D:\4A\02_老资料_表格与订单\亚马逊供应商和开店总表-2023.xlsx',
    r'D:\4A\02_老资料_表格与订单\Amazon Bulk order-2023总表.xlsx',
    r'D:\4A\02_老资料_表格与订单\Amazon Bulk order-2024总表.xlsx'
]

for f in files_to_check:
    if os.path.exists(f):
        search_excel(f)
    else:
        print(f'File not found: {f}')
