import openpyxl, sys
sys.stdout.reconfigure(encoding='utf-8')
base = r'C:\Users\24243\Documents\Codex\2026-08-11\7-30-slack-plugin-slack-openai\outputs\019ff179-ce00-7621-9ae6-13daf0989ce8'
files = ['4A_PriceAndQuantity_100_SKUs_2026-08-17.xlsx', '4A_PriceAndQuantity_SC核验版_23_SKUs_2026-08-17.xlsx', '4Ausa_163_SKUs_改价实时核对_2026-08-21.xlsx']
for f in files:
    wb = openpyxl.load_workbook(base + '\\' + f, data_only=True)
    print('=====', f)
    for ws in wb.worksheets:
        print('  sheet', ws.title, ws.max_row, 'x', ws.max_column)
        for r in ws.iter_rows(min_row=1, max_row=4, values_only=True):
            print('    ', [str(c)[:28] if c is not None else '' for c in r[:12]])
