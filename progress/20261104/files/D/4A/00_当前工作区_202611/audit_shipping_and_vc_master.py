import openpyxl
import os
import json

# 1. Load All Listings Report 11-01-2026
with open(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt', 'r', encoding='utf-8', errors='replace') as f:
    lines = [l.rstrip('\n').split('\t') for l in f]
h = lines[0]

# 2. Load 分类商品报告_10-31-2026.xlsm for Stop Selling Date, Package Weight, Parent SKU, etc.
wb_cat = openpyxl.load_workbook(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm', read_only=True, data_only=True)
ws_cat = wb_cat['Template']
cat_rows = list(ws_cat.iter_rows(values_only=True))
cat_by_sku = {r[2]: r for r in cat_rows[6:] if r and len(r) > 2 and r[2]}

# 3. Load Official Master Sheet (亚马逊供应商和开店总表-2026(3).xlsx)
wb_m = openpyxl.load_workbook(r'D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx', read_only=True, data_only=True)
ws_m = wb_m['Sheet1']
master_rows = list(ws_m.iter_rows(values_only=True))

print("=== MASTER SHEET HEADERS ===")
for idx, r in enumerate(master_rows[:5]):
    print(idx+1, [x for x in r[:20] if x is not None])

# Check all non-Migrated MFN SKUs with inventory > 0 and compare with Master Sheet
print("\n=== ALL NON-MIGRATED MFN IN-STOCK SKUS (43 SKUS) ===")
for r in sorted(lines[1:], key=lambda x: -(int(x[5]) if len(x)>5 and x[5].isdigit() else 0)):
    if len(r) > 28 and r[26] == 'DEFAULT':
        q = int(r[5]) if r[5].isdigit() else 0
        if q > 0 and r[27] != 'Migrated Template':
            sku = r[3]
            asin = r[16]
            price = r[4]
            tpl = r[27]
            st = r[28]
            cr = cat_by_sku.get(sku)
            stop_dt = cr[355] if cr and len(cr) > 355 else None
            pkg_wt = cr[385] if cr and len(cr) > 385 else None
            parent = cr[6] if cr and len(cr) > 6 else None
            print(f"SKU={sku:22s} | ASIN={asin} | Qty={q:4d} | Price=${price:6s} | Tpl={tpl:31s} | StopDt={str(stop_dt):24s} | SellerPkgWt={str(pkg_wt):5s} | Parent={parent}")

# Check where 4A 000 and BP2222 are in All Listings Report
print("\n=== CHECK 4A 000 AND BP2222 AND 354818 AND 2028 IN ALL LISTINGS ===")
for r in lines[1:]:
    if len(r) > 28 and any(k in r[3] for k in ['000', 'BP2222', '354818', '2028', '303x12', '303X12', '30315', '406x6', '5088', '5084', '5082', 'PSS 32']):
        print(f"SKU={r[3]:24s} | ASIN={r[16]} | Ch={r[26]:9s} | St={r[28]:10s} | Qty={r[5]:5s} | Price=${r[4]:6s} | Tpl={r[27]}")
