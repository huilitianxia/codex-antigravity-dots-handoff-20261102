import openpyxl, sys
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\24243\Downloads'
names = ['亚马逊供应商和开店总表-2026.xlsx', '亚马逊供应商和开店总表-2026 (1).xlsx', '亚马逊供应商和开店总表-2026 (2).xlsx', '亚马逊供应商和开店总表-2026 (3).xlsx']
tags = ['v0', 'v1', 'v2', 'v3']
data = {}
for n, t in zip(names, tags):
    wb = openpyxl.load_workbook(D + '\\' + n, read_only=True, data_only=True)
    ws = wb['Sheet1']
    data[t] = [list(r) for r in ws.iter_rows(values_only=True)]
for t in tags:
    print('==', t, 'header:', [str(c)[:14] if c is not None else '' for c in data[t][0]])
for t in tags:
    print(t, 'row2:', [str(c)[:16] if c is not None else '' for c in data[t][1]][:34])
