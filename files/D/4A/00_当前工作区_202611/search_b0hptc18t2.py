import os
import openpyxl

target = 'B0HPTC18T2'

def search_text_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f, 1):
                if target.lower() in line.lower():
                    print(f"[TXT MATCH] {path} Line {idx}: {line.strip()[:200]}")
    except Exception as e:
        pass

def search_excel_file(path):
    try:
        wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
        for s in wb.sheetnames:
            ws = wb[s]
            for r_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
                r_str = ' '.join([str(c) for c in row if c is not None])
                if target.lower() in r_str.lower():
                    print(f"[XLSX MATCH] {path} Sheet '{s}' Row {r_idx}: {r_str[:200]}")
        wb.close()
    except Exception as e:
        pass

# Check specific files first
search_text_file(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt')
search_excel_file(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm')
search_excel_file(r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx')

# Search entire D:\4A\00_Codex交接给Gemini_20261101\
for root, dirs, files in os.walk(r'D:\4A\00_Codex交接给Gemini_20261101'):
    for f in files:
        fp = os.path.join(root, f)
        if f.endswith(('.txt', '.json', '.md', '.csv')):
            search_text_file(fp)

# Search D:\4A\02_老资料_表格与订单\
for root, dirs, files in os.walk(r'D:\4A\02_老资料_表格与订单'):
    for f in files:
        fp = os.path.join(root, f)
        if f.endswith(('.xlsx', '.xlsm')):
            search_excel_file(fp)
        elif f.endswith(('.txt', '.json', '.md', '.csv')):
            search_text_file(fp)
