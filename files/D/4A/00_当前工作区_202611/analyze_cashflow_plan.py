import csv
import json
import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

# File paths
FBA_INV_FILE = r"D:\下载文件\284701020757.txt"
ALL_LISTINGS_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
ORDERS_FILE = r"D:\下载文件\175793876516020757.txt"
CAT_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
COUPON_FULL_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-fullscan-parsed.json"
COUPON_15_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon15-final22-product-acceptance.json"
COUPON_5_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon5-final12-live-acceptance.json"
MASTER_FILE = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"
SAMEPAGE_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\samepage-stocked-fba-execution.json"

# 1. Load active coupons
with open(COUPON_15_FILE, "r", encoding="utf-8") as f:
    c15_data = json.load(f)
    active_15_asins = set(r['asin'] for r in c15_data.get('rows', []))

with open(COUPON_5_FILE, "r", encoding="utf-8") as f:
    c5_data = json.load(f)
    active_5_asins = set(c5_data.get('asins', []))

# 2. Load coupon fullscan
with open(COUPON_FULL_FILE, "r", encoding="utf-8") as f:
    coupon_scan = json.load(f)
    coupon_by_sku = {}
    coupon_by_asin = {}
    for r in coupon_scan.get('rows', []):
        if r.get('sku'): coupon_by_sku[r['sku']] = r
        if r.get('asin') and r.get('channel') == 'FBA': coupon_by_asin[r['asin']] = r

# 3. Load October Orders
oct_by_sku = {}
oct_by_asin = {}
with open(ORDERS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        sku = row.get('sku', '').strip()
        asin = row.get('asin', '').strip()
        status = row.get('order-status', '')
        qty = int(row.get('quantity', 0) or 0)
        price = float(row.get('item-price', 0) or 0)
        channel = row.get('fulfillment-channel', '')
        is_cancelled = (status.lower() == 'cancelled')
        
        def add_rec(d, k):
            if not k: return
            if k not in d:
                d[k] = {'orders': 0, 'units': 0, 'fba_units': 0, 'mfn_units': 0, 'sales': 0.0, 'cancelled_orders': 0}
            if is_cancelled:
                d[k]['cancelled_orders'] += 1
            else:
                d[k]['orders'] += 1
                d[k]['units'] += qty
                d[k]['sales'] += price
                if channel.lower() == 'amazon':
                    d[k]['fba_units'] += qty
                else:
                    d[k]['mfn_units'] += qty

        add_rec(oct_by_sku, sku)
        add_rec(oct_by_asin, asin)

# 4. Load Master sheet
wb_m = openpyxl.load_workbook(MASTER_FILE, read_only=True, data_only=True)
ws_m = wb_m['Sheet1']
master_rows = list(ws_m.iter_rows(values_only=True))
master_by_sku = {}
master_by_asin = {}
for r in master_rows[1:]:
    if r and len(r) > 12:
        sku = str(r[0]).strip() if r[0] else ''
        vc_asin = str(r[2]).strip() if r[2] else ''
        sl_asin = str(r[4]).strip() if r[4] else ''
        cost = r[9] # FOB
        amz_cost = r[10] # Amazon Cost
        base_price = r[11]
        weight_lbs = r[13]
        rec = {'sku': sku, 'vc_asin': vc_asin, 'sl_asin': sl_asin, 'fob': cost, 'amz_cost': amz_cost, 'base_price': base_price, 'weight_lbs': weight_lbs, 'title': r[6]}
        if sku: master_by_sku[sku] = rec
        if vc_asin: master_by_asin[vc_asin] = rec
        if sl_asin: master_by_asin[sl_asin] = rec

# 5. Load Category report
wb_cat = openpyxl.load_workbook(CAT_FILE, read_only=True, data_only=True)
ws_cat = wb_cat['Template']
cat_rows = list(ws_cat.iter_rows(values_only=True))
cat_by_sku = {r[2]: r for r in cat_rows[6:] if r and len(r) > 2 and r[2]}

# 6. Load All Listings
all_listings_mfn = {}
all_listings_fba = {}
all_listings_by_asin = {}
with open(ALL_LISTINGS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for r in reader:
        sku = r.get('seller-sku', '').strip()
        asin = r.get('asin1', '').strip()
        channel = r.get('fulfillment-channel', '').strip()
        if channel == 'DEFAULT':
            all_listings_mfn[sku] = r
        else:
            all_listings_fba[sku] = r
        all_listings_by_asin.setdefault(asin, []).append(r)

# 7. Load FBA Inventory
fba_inv = []
with open(FBA_INV_FILE, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for r in reader:
        fba_inv.append(r)

print(f"Loaded: FBA Inv items={len(fba_inv)}, MFN items={len(all_listings_mfn)}, Oct SKU stats={len(oct_by_sku)}")

# Test Cash Cow #1:
print("\n--- CASH COW #1 CHECK ---")
for r in fba_inv:
    if r['sku'] == '4A 303-Full Adhesive-400':
        print("FBA 4A 303-Full Adhesive-400:", {
            'avail': r['available'], 'fc_transfer': r['fc-transfer'], 'inbound': r['inbound-quantity'],
            'price': r['your-price'], 'sales_price': r['sales-price'], 't30': r['units-shipped-t30'],
            'age0_90': r['inv-age-0-to-90-days'], 'age91_180': r['inv-age-91-to-180-days'],
            'est_cost_next_month': r['estimated-storage-cost-next-month']
        })

mfn_sibling = all_listings_mfn.get('4A GM303-Full Adhesive-400')
print("MFN 4A GM303-Full Adhesive-400:", mfn_sibling)
print("Oct orders for 4A 303-Full Adhesive-400:", oct_by_sku.get('4A 303-Full Adhesive-400'))
print("Oct orders for ASIN B07QXJYTZ7:", oct_by_asin.get('B07QXJYTZ7'))
