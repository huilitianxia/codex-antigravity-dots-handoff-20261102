import openpyxl, sys, time
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\24243\Downloads'
names = ['亚马逊供应商和开店总表-2026.xlsx', '亚马逊供应商和开店总表-2026 (1).xlsx', '亚马逊供应商和开店总表-2026 (2).xlsx', '亚马逊供应商和开店总表-2026 (3).xlsx']
for n in names:
    t0 = time.time()
    wb = openpyxl.load_workbook(D + '\\' + n, read_only=True, data_only=True)
    print('=====', n)
    for ws in wb.worksheets:
        print('  sheet %-28s rows=%s cols=%s' % (ws.title, ws.max_row, ws.max_column))
    print('  (%.1fs)' % (time.time() - t0))
