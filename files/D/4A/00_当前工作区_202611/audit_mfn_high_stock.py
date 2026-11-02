import csv
import json
import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

ALL_LISTINGS_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
ORDERS_FILE = r"D:\下载文件\175793876516020757.txt"
CAT_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
MASTER_FILE = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"
BATCH14_AUDIT = r"D:\4A\00_当前工作区_202611\batch14_cell_audit.json"
BATCH15_AUDIT = r"D:\4A\00_当前工作区_202611\batch15_cell_audit.json"

# Load Batch 14 & 15 targets
b14_skus = set()
try:
    with open(BATCH14_AUDIT, "r", encoding="utf-8") as f:
        b14_data = json.load(f)
        b14_skus = set(b14_data.keys())
except Exception as e:
    print("Could not load batch 14 audit:", e)

b15_skus = set()
try:
    with open(BATCH15_AUDIT, "r", encoding="utf-8") as f:
        b15_data = json.load(f)
        b15_skus = set(b15_data.keys())
except Exception as e:
    print("Could not load batch 15 audit:", e)

# Oct Orders
oct_by_sku = {}
with open(ORDERS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        sku = r.get('sku', '').strip()
        status = r.get('order-status', '')
        qty = int(r.get('quantity', 0) or 0)
        price = float(r.get('item-price', 0) or 0)
        channel = r.get('fulfillment-channel', '')
        if status.lower() != 'cancelled':
            if sku not in oct_by_sku:
                oct_by_sku[sku] = {'orders': 0, 'units': 0, 'sales': 0.0}
            oct_by_sku[sku]['orders'] += 1
            oct_by_sku[sku]['units'] += qty
            oct_by_sku[sku]['sales'] += price

# Category Report
wb_cat = openpyxl.load_workbook(CAT_FILE, read_only=True, data_only=True)
ws_cat = wb_cat['Template']
cat_rows = list(ws_cat.iter_rows(values_only=True))
cat_by_sku = {r[2]: r for r in cat_rows[6:] if r and len(r) > 2 and r[2]}

# All Listings
mfn_rows = []
all_listings_by_asin = {}
with open(ALL_LISTINGS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        asin = r.get('asin1', '').strip()
        all_listings_by_asin.setdefault(asin, []).append(r)
        if r.get('fulfillment-channel') == 'DEFAULT':
            try:
                qty = int(r.get('quantity', 0) or 0)
            except:
                qty = 0
            if qty >= 300:
                mfn_rows.append(r)

mfn_rows.sort(key=lambda x: int(x.get('quantity', 0) or 0), reverse=True)

out_mfn = []
tpl_counts = {}

for r in mfn_rows:
    sku = r.get('seller-sku', '').strip()
    asin = r.get('asin1', '').strip()
    qty = int(r.get('quantity', 0) or 0)
    price = float(r.get('price', 0) or 0)
    status = r.get('status', '').strip()
    tpl = r.get('merchant-shipping-group', '').strip()
    tpl_counts[tpl] = tpl_counts.get(tpl, 0) + 1
    
    oct_stat = oct_by_sku.get(sku, {'orders': 0, 'units': 0, 'sales': 0.0})
    oct_units = oct_stat['units']
    oct_sales = round(oct_stat['sales'], 2)
    
    cr = cat_by_sku.get(sku)
    stop_dt = cr[355] if cr and len(cr) > 355 else None
    pkg_wt = cr[385] if cr and len(cr) > 385 else None
    
    # Check if there is an FBA sibling on this ASIN
    fba_sibling = None
    for sib in all_listings_by_asin.get(asin, []):
        if sib.get('fulfillment-channel') != 'DEFAULT':
            fba_sibling = {'sku': sib.get('seller-sku'), 'status': sib.get('status'), 'price': sib.get('price')}
            break
            
    # Blocking factors
    blockers = []
    if stop_dt and '2025' in str(stop_dt):
        blockers.append(f"Expired Stop Selling Date: {stop_dt}")
    if tpl in ['Heavy delivery', 'Big size delivery', 'Cube delivery', '4A Parcel 7.99 plus 2.99 per lb', 'Biger size delivery-25']:
        if not pkg_wt:
            blockers.append(f"Missing Package Weight on weight-based template ({tpl})")
        else:
            blockers.append(f"Non-migrated shipping template: {tpl} (wt={pkg_wt})")
    if sku in b14_skus:
        blockers.append("Catalog conflict addressed in Batch 14")
    if sku in b15_skus:
        blockers.append("Shipping/spec/stop-selling fix in Batch 15")
    if sku == '4A GM40624*2':
        blockers.append("Error 99022 unbrandable listing addressed in Batch 14")
        
    rec = {
        'sku': sku,
        'asin': asin,
        'declared_quantity': qty,
        'price': price,
        'status': status,
        'shipping_template': tpl,
        'oct_orders': oct_stat['orders'],
        'oct_units': oct_units,
        'oct_sales': oct_sales,
        'stop_selling_date': str(stop_dt) if stop_dt else None,
        'package_weight': str(pkg_wt) if pkg_wt else None,
        'fba_sibling': fba_sibling,
        'blockers': blockers,
        'batch14_target': sku in b14_skus,
        'batch15_target': sku in b15_skus
    }
    out_mfn.append(rec)

print(f"Total MFN >= 300 SKUs: {len(out_mfn)}")
print(f"Shipping template breakdown among MFN >= 300:")
for tpl, cnt in sorted(tpl_counts.items(), key=lambda x: -x[1]):
    print(f"  {tpl}: {cnt} SKUs")

with open(r"D:\4A\00_当前工作区_202611\mfn_72_audit.json", "w", encoding="utf-8") as f:
    json.dump(out_mfn, f, ensure_ascii=False, indent=2)

print("\nSaved mfn_72_audit.json successfully!")
