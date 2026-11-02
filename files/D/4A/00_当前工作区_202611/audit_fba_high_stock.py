import csv
import json
import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')

FBA_INV_FILE = r"D:\下载文件\284701020757.txt"
ALL_LISTINGS_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
ORDERS_FILE = r"D:\下载文件\175793876516020757.txt"
CAT_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
COUPON_FULL_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-fullscan-parsed.json"
COUPON_15_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon15-final22-product-acceptance.json"
COUPON_5_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon5-final12-live-acceptance.json"
MASTER_FILE = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"

# 1. Coupons
with open(COUPON_15_FILE, "r", encoding="utf-8") as f:
    c15_asins = set(r['asin'] for r in json.load(f).get('rows', []))
with open(COUPON_5_FILE, "r", encoding="utf-8") as f:
    c5_asins = set(json.load(f).get('asins', []))

with open(COUPON_FULL_FILE, "r", encoding="utf-8") as f:
    coupon_scan = json.load(f)
    coupon_by_sku = {}
    coupon_by_asin = {}
    for r in coupon_scan.get('rows', []):
        if r.get('sku'): coupon_by_sku[r['sku']] = r
        if r.get('asin') and r.get('channel') == 'FBA': coupon_by_asin[r['asin']] = r

# 2. October Orders
oct_by_sku = {}
with open(ORDERS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        sku = row.get('sku', '').strip()
        status = row.get('order-status', '')
        qty = int(row.get('quantity', 0) or 0)
        price = float(row.get('item-price', 0) or 0)
        channel = row.get('fulfillment-channel', '')
        if status.lower() != 'cancelled':
            if sku not in oct_by_sku:
                oct_by_sku[sku] = {'orders': 0, 'units': 0, 'fba_units': 0, 'mfn_units': 0, 'sales': 0.0}
            oct_by_sku[sku]['orders'] += 1
            oct_by_sku[sku]['units'] += qty
            oct_by_sku[sku]['sales'] += price
            if channel.lower() == 'amazon':
                oct_by_sku[sku]['fba_units'] += qty
            else:
                oct_by_sku[sku]['mfn_units'] += qty

# 3. All Listings
all_listings = {}
with open(ALL_LISTINGS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        all_listings[r.get('seller-sku', '').strip()] = r

# 4. FBA Inv
fba_24 = []
with open(FBA_INV_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        avail = int(r.get('available', 0) or 0)
        if avail >= 50:
            fba_24.append(r)

fba_24.sort(key=lambda x: int(x.get('available', 0) or 0), reverse=True)

print(f"=== DETAILED AUDIT OF {len(fba_24)} FBA HIGH-STOCK SKUS ===")
out_fba = []
for r in fba_24:
    sku = r['sku']
    asin = r['asin']
    avail = int(r.get('available', 0) or 0)
    fc_transfer = int(r.get('fc-transfer', 0) or 0)
    inbound = int(r.get('inbound-quantity', 0) or 0)
    total_supply = avail + fc_transfer
    t30_shipped = int(r.get('units-shipped-t30', 0) or 0)
    price = float(r.get('your-price', 0) or 0)
    
    # Oct orders
    oct_stat = oct_by_sku.get(sku, {'orders': 0, 'units': 0, 'sales': 0.0})
    oct_units = oct_stat['units']
    oct_sales = oct_stat['sales']
    
    # Inventory age
    age_0_90 = int(r.get('inv-age-0-to-90-days', 0) or 0)
    age_91_180 = int(r.get('inv-age-91-to-180-days', 0) or 0)
    age_181_270 = int(r.get('inv-age-181-to-270-days', 0) or 0)
    age_271_365 = int(r.get('inv-age-271-to-365-days', 0) or 0)
    age_366_455 = int(r.get('inv-age-366-to-455-days', 0) or 0)
    age_456_plus = int(r.get('inv-age-456-plus-days', 0) or 0)
    aged_181_plus = age_181_270 + age_271_365 + age_366_455 + age_456_plus
    aged_365_plus = age_366_455 + age_456_plus
    
    # Storage cost
    est_storage_next_mo = float(r.get('estimated-storage-cost-next-month', 0) or 0)
    
    # Coupon status
    c_status = 'None'
    if asin in c15_asins:
        c_status = 'Active 15%'
    elif asin in c5_asins:
        c_status = 'Active 5%'
        
    c_scan = coupon_by_sku.get(sku) or coupon_by_asin.get(asin) or {}
    selectable = c_scan.get('selectable', False)
    reasons = c_scan.get('reasons', [])
    
    # MFN sibling check
    mfn_sku = f"4A GM{sku.replace('4A ', '').replace('AAAA 4A ', '')}"
    # Also check if another MFN exists on the same ASIN
    same_asin_mfn = []
    for l_sku, l_row in all_listings.items():
        if l_row.get('asin1') == asin and l_row.get('fulfillment-channel') == 'DEFAULT':
            same_asin_mfn.append((l_sku, l_row.get('quantity', '0'), l_row.get('status', '')))

    rec = {
        'sku': sku,
        'asin': asin,
        'product_name': r.get('product-name', ''),
        'available': avail,
        'fc_transfer': fc_transfer,
        'total_fba_units': total_supply,
        'inbound': inbound,
        'price': price,
        't30_shipped': t30_shipped,
        'oct_orders': oct_stat['orders'],
        'oct_units': oct_units,
        'oct_sales': round(oct_sales, 2),
        'inv_age': {
            '0_90': age_0_90,
            '91_180': age_91_180,
            '181_270': age_181_270,
            '271_365': age_271_365,
            '366_455': age_366_455,
            '456_plus': age_456_plus,
            'aged_181_plus': aged_181_plus,
            'aged_365_plus': aged_365_plus
        },
        'est_storage_cost_next_month': est_storage_next_mo,
        'coupon_status': c_status,
        'coupon_selectable': selectable,
        'coupon_blocker_reasons': reasons,
        'same_asin_mfn': same_asin_mfn
    }
    out_fba.append(rec)
    print(f"[{c_status:10}] {sku:25} | ASIN:{asin} | Avail:{avail:4d} | OctU:{oct_units:3d} | Aged181+:{aged_181_plus:3d} | Aged365+:{aged_365_plus:3d} | SiblingMFN:{same_asin_mfn}")

with open(r"D:\4A\00_当前工作区_202611\fba_24_audit.json", "w", encoding="utf-8") as f:
    json.dump(out_fba, f, ensure_ascii=False, indent=2)

print("\nSaved fba_24_audit.json successfully!")
