import json
import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

# File paths
FBA_INV_FILE = r"D:\下载文件\284701020757.txt"
ALL_LISTINGS_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
ORDERS_FILE = r"D:\下载文件\175793876516020757.txt"
COUPON_FULL_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-fullscan-parsed.json"
COUPON_15_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon15-final22-product-acceptance.json"
COUPON_5_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon5-final12-live-acceptance.json"
SAMEPAGE_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\samepage-stocked-fba-execution.json"
MASTER_FILE = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"

# 1. Load active coupon ASINs
with open(COUPON_15_FILE, "r", encoding="utf-8") as f:
    c15_data = json.load(f)
    active_15_asins = set(r['asin'] for r in c15_data.get('rows', []))

with open(COUPON_5_FILE, "r", encoding="utf-8") as f:
    c5_data = json.load(f)
    active_5_asins = set(c5_data.get('asins', []))

print(f"Active Coupons: {len(active_15_asins)} (15%) + {len(active_5_asins)} (5%) = {len(active_15_asins | active_5_asins)} unique ASINs")

# 2. Load coupon-fullscan-parsed.json to check coupon status/reasons for all offers
with open(COUPON_FULL_FILE, "r", encoding="utf-8") as f:
    coupon_scan = json.load(f)
    coupon_rows = coupon_scan.get('rows', [])
    coupon_info_by_sku = {}
    coupon_info_by_asin = {}
    for r in coupon_rows:
        sku = r.get('sku')
        asin = r.get('asin')
        if sku:
            coupon_info_by_sku[sku] = r
        if asin:
            coupon_info_by_asin[asin] = r

# 3. Load samepage-stocked-fba-execution.json
with open(SAMEPAGE_FILE, "r", encoding="utf-8") as f:
    samepage_data = json.load(f)
    samepage_by_sku = {r['sku']: r for r in samepage_data.get('rows', [])}
    samepage_by_asin = {}
    for r in samepage_data.get('rows', []):
        samepage_by_asin.setdefault(r['asin'], []).append(r)

# 4. Load Orders for October 2026
oct_orders_by_sku = {}
oct_orders_by_asin = {}
total_oct_orders = 0
total_oct_units = 0

with open(ORDERS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        total_oct_orders += 1
        sku = row.get('sku', '').strip()
        asin = row.get('asin', '').strip()
        qty = int(row.get('quantity', 0) or 0)
        status = row.get('order-status', '')
        channel = row.get('fulfillment-channel', '')
        price = float(row.get('item-price', 0) or 0)
        
        # We track non-cancelled units
        is_cancelled = (status.lower() == 'cancelled')
        
        if not is_cancelled:
            total_oct_units += qty
            
        def record_order(d, key):
            if not key: return
            if key not in d:
                d[key] = {
                    'total_orders': 0, 'valid_orders': 0, 'cancelled_orders': 0,
                    'total_units': 0, 'valid_units': 0, 'fba_units': 0, 'mfn_units': 0,
                    'total_sales_usd': 0.0
                }
            d[key]['total_orders'] += 1
            if is_cancelled:
                d[key]['cancelled_orders'] += 1
            else:
                d[key]['valid_orders'] += 1
                d[key]['valid_units'] += qty
                d[key]['total_sales_usd'] += price
                if channel.lower() == 'amazon':
                    d[key]['fba_units'] += qty
                else:
                    d[key]['mfn_units'] += qty
                    
        record_order(oct_orders_by_sku, sku)
        record_order(oct_orders_by_asin, asin)

print(f"October Orders loaded: {total_oct_orders} order lines, {total_oct_units} valid units.")

# 5. Load FBA Inventory (284701020757.txt)
fba_inventory = []
with open(FBA_INV_FILE, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        avail = int(row.get('available', 0) or 0)
        fc_transfer = int(row.get('fc-transfer', 0) or 0)
        fba_inventory.append(row)

print(f"FBA Inventory loaded: {len(fba_inventory)} items.")

# 6. Load All Listings Report (所有商品报告_11-01-2026.txt)
all_listings = []
with open(ALL_LISTINGS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        all_listings.append(row)

print(f"All Listings loaded: {len(all_listings)} listings.")

# Save preliminary counts
print("Data sources successfully connected!")
