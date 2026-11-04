import openpyxl
import csv
from collections import defaultdict

# 1. Load All Listings Report 11-01-2026
all_listings = {}
with open(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt', 'r', encoding='utf-8-sig', errors='replace') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for r in reader:
        sku = (r.get('seller-sku') or '').strip()
        all_listings[sku] = r

# 2. Load 10-31 CLR to know current Parent / Theme / Color / Size / Title / Shipping Template / Price
wb_clr = openpyxl.load_workbook(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm', read_only=True, data_only=True)
ws_clr = wb_clr['Template']
clr_rows = {}
parent_rows = {}
for idx, row in enumerate(ws_clr.iter_rows(min_row=7, values_only=True), start=7):
    sku = str(row[2] or '').strip()
    if not sku:
        continue
    plevel = str(row[5] or '').strip()
    if plevel == 'Parent':
        parent_rows[sku] = {
            'sku': sku,
            'theme': str(row[7] or '').strip(),
            'title': str(row[8] or '').strip(),
            'prod_type': str(row[0] or '').strip()
        }
    else:
        clr_rows[sku] = {
            'sku': sku,
            'asin': str(row[12] or '').strip(),
            'parent': str(row[6] or '').strip(),
            'theme': str(row[7] or '').strip(),
            'title': str(row[8] or '').strip(),
            'color': str(row[58] or '').strip(),
            'size': str(row[59] or '').strip(),
            'prod_type': str(row[0] or '').strip(),
            'list_price': row[317],
            'your_price': row[347],
            'sale_price': row[351],
            'ship_tmpl': str(row[372] or '').strip(),
            'full_row': list(row)
        }

# Apply updates from Batches 09, 10, 12, 14, 15, 16, 17, 18, 19 so we know the exact live state!
import glob, os
batch_files = sorted(glob.glob(r'D:\4A\00_Codex交接给Gemini_20261101\03_正式上传文件\*.xlsm'))
for bf in batch_files:
    bname = os.path.basename(bf)
    wb_b = openpyxl.load_workbook(bf, read_only=True, data_only=True)
    if 'Template' not in wb_b.sheetnames:
        continue
    ws_b = wb_b['Template']
    for r in ws_b.iter_rows(min_row=7, values_only=True):
        sku = str(r[2] or '').strip()
        if not sku:
            continue
        act = str(r[4] or '').strip()
        plevel = str(r[5] or '').strip()
        if plevel == 'Parent':
            if 'Delete' not in act:
                parent_rows[sku] = {
                    'sku': sku,
                    'theme': str(r[7] or '').strip(),
                    'title': str(r[8] or '').strip(),
                    'prod_type': str(r[0] or '').strip()
                }
        else:
            if sku in clr_rows and 'Delete' not in act:
                if r[6]: clr_rows[sku]['parent'] = str(r[6]).strip()
                if r[7]: clr_rows[sku]['theme'] = str(r[7]).strip()
                if r[8]: clr_rows[sku]['title'] = str(r[8]).strip()
                if r[58] is not None: clr_rows[sku]['color'] = str(r[58]).strip()
                if r[59] is not None: clr_rows[sku]['size'] = str(r[59]).strip()
                if r[347] is not None: clr_rows[sku]['your_price'] = r[347]
                if r[372] is not None: clr_rows[sku]['ship_tmpl'] = str(r[372]).strip()

print("Total parents:", len(parent_rows))
for psku, pinfo in sorted(parent_rows.items()):
    print(f"  {psku:36s} | Theme={pinfo['theme']:12s} | Type={pinfo['prod_type']}")
