import os
import openpyxl

upcs = ['702877126561', '702877126578']

def search_upcs():
    print("Searching for UPCs across D:\\4A...")
    for root, dirs, files in os.walk(r'D:\4A'):
        # Skip current workspace to avoid self-matches
        if '00_当前工作区_202611' in root:
            continue
        for f in files:
            fp = os.path.join(root, f)
            fl = f.lower()
            if fl.endswith(('.txt', '.json', '.md', '.csv')):
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                        for line_no, line in enumerate(file, 1):
                            for u in upcs:
                                if u in line:
                                    print(f"[TXT] {fp}:{line_no} found {u} -> {line.strip()[:150]}")
                except:
                    pass
            elif fl.endswith(('.xlsx', '.xlsm')):
                try:
                    wb = openpyxl.load_workbook(fp, data_only=True, read_only=True)
                    for s in wb.sheetnames:
                        ws = wb[s]
                        for r_no, row in enumerate(ws.iter_rows(values_only=True), 1):
                            r_str = ' '.join([str(c) for c in row if c is not None])
                            for u in upcs:
                                if u in r_str:
                                    print(f"[XLSX] {fp} Sheet '{s}' Row {r_no} found {u} -> {r_str[:150]}")
                    wb.close()
                except:
                    pass

search_upcs()
