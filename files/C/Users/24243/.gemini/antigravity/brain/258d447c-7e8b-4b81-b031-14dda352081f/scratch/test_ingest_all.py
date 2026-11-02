import os
import sys
import csv
import json
import openpyxl
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# 1. Ingest All Listings Report (754 rows)
all_listings_file = r"D:\下载文件\所有商品报告_09-03-2026.txt"
sc_report_items = {}
with open(all_listings_file, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for r in reader:
        sku = (r.get('seller-sku') or '').strip()
        asin = (r.get('asin1') or '').strip()
        if not sku and not asin:
            continue
        key = sku if sku else asin
        sc_report_items[key] = {
            'sku': sku,
            'asin': asin,
            'title': (r.get('item-name') or '').strip(),
            'price': (r.get('price') or '').strip(),
            'qty': (r.get('quantity') or '').strip(),
            'open_date': (r.get('open-date') or '').strip(),
            'status': (r.get('status') or '').strip(),
            'fc': (r.get('fulfillment-channel') or '').strip(),
            'source': '所有商品报告_09-03'
        }
print(f"Loaded {len(sc_report_items)} items from 所有商品报告_09-03")

# 2. Ingest WooCommerce 163 SKUs
woo_file = r"E:\Desktop\WooCommerce_完整改价_163_SKUs_复核后上传_2026-08-20.csv"
woo_items = {}
with open(woo_file, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f)
    for r in reader:
        sku = (r.get('SKU') or '').strip()
        if sku:
            woo_items[sku] = {
                'woo_id': r.get('ID', ''),
                'regular_price': r.get('Regular price', ''),
                'sale_price': r.get('Sale price', '')
            }
print(f"Loaded {len(woo_items)} items from WooCommerce 163")

# 3. Ingest 269 Out of Stock Excels
oos_file_1 = r"C:\Users\24243\Downloads\4A缺货_269评分已补全_被低估好款.xlsx"
oos_items = {}
wb1 = openpyxl.load_workbook(oos_file_1, data_only=True)
ws1 = wb1['全部269(已补评分)']
for r in ws1.iter_rows(min_row=2, values_only=True):
    if not r or not r[0]: continue
    asin = str(r[0]).strip()
    title = str(r[1]).strip() if r[1] else ''
    status = str(r[2]).strip() if r[2] else ''
    price = str(r[3]).strip() if r[3] else ''
    stars = r[4] if r[4] is not None else ''
    reviews = r[5] if r[5] is not None else 0
    oos_items[asin] = {
        'asin': asin,
        'title': title,
        'status': status,
        'price': price,
        'stars': stars,
        'reviews': reviews if isinstance(reviews, (int, float)) else 0
    }

oos_file_2 = r"C:\Users\24243\Downloads\4A-SL缺货评分好款.xlsx"
wb2 = openpyxl.load_workbook(oos_file_2, data_only=True)
ws2 = wb2['全部269(父子过滤)']
for r in ws2.iter_rows(min_row=2, values_only=True):
    if not r or not r[0]: continue
    asin = str(r[0]).strip()
    title_official = str(r[1]).strip() if r[1] else ''
    title_batch = str(r[2]).strip() if r[2] else ''
    parent_asin = str(r[14]).strip() if len(r) > 14 and r[14] else ''
    brothers = str(r[15]).strip() if len(r) > 15 and r[15] else ''
    stars = r[5] if len(r) > 5 and r[5] is not None else ''
    reviews = r[6] if len(r) > 6 and r[6] is not None else 0
    if asin not in oos_items:
        oos_items[asin] = {'asin': asin, 'title': title_official or title_batch, 'reviews': 0, 'stars': ''}
    oos_items[asin]['parent_asin'] = parent_asin
    oos_items[asin]['brothers'] = brothers
    if isinstance(reviews, (int, float)) and reviews > oos_items[asin].get('reviews', 0):
        oos_items[asin]['reviews'] = reviews
        oos_items[asin]['stars'] = stars
print(f"Loaded {len(oos_items)} items from 269 OOS Excels")

# 4. Ingest 亚马逊供应商和开店总表-2026 (3).xlsx
store_master_file = r"C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx"
wb3 = openpyxl.load_workbook(store_master_file, data_only=True)
ws3 = wb3['Sheet1']
store_master = {}
for r in ws3.iter_rows(min_row=2, values_only=True):
    if not r or not r[0]: continue
    sku = str(r[0]).strip()
    vc_upc = str(r[1]).strip() if r[1] else ''
    vc_asin = str(r[2]).strip() if r[2] else ''
    sl_upc = str(r[3]).strip() if r[3] else ''
    sl_asin = str(r[4]).strip() if r[4] else ''
    title = str(r[6]).strip() if len(r) > 6 and r[6] else ''
    fob = r[9] if len(r) > 9 else ''
    cost = r[10] if len(r) > 10 else ''
    list_price = r[11] if len(r) > 11 else ''
    sale_price = r[12] if len(r) > 12 else ''
    store_master[sku] = {
        'sku': sku,
        'vc_upc': vc_upc,
        'vc_asin': vc_asin,
        'sl_upc': sl_upc,
        'sl_asin': sl_asin,
        'title': title,
        'cost': cost,
        'sale_price': sale_price
    }
print(f"Loaded {len(store_master)} items from 供应商与店铺总表")

# 5. Ingest VC audit data
vc_file = r"E:\OpenAI-Codex\Workspaces\C-Documents\2026-08-28\new-task-handoff-2026-08-28\work\vc_sc_audit_data.json"
vc_data = {}
with open(vc_file, 'r', encoding='utf-8') as f:
    vcd = json.load(f)
    for item in vcd.get('vc_all', []):
        asin = item.get('vc_asin', '').strip()
        sku = item.get('vc_sku', '').strip()
        if asin or sku:
            vc_data[asin or sku] = item
print(f"Loaded {len(vc_data)} items from VC SC Audit Data")

# 6. Ingest SellerSprite Competitor reviews
ss_file = r"D:\下载文件\Competitor-US-Last-30-days-217940.xlsx"
ss_ratings = {}
wb_ss = openpyxl.load_workbook(ss_file, data_only=True)
ws_ss = wb_ss['Competitor-US-Last-30-days']
for r in ws_ss.iter_rows(min_row=2, values_only=True):
    if not r or not r[0]: continue
    asin = str(r[0]).strip()
    sku = str(r[1]).strip() if len(r) > 1 and r[1] else ''
    title = str(r[5]).strip() if len(r) > 5 and r[5] else ''
    revs = r[27] if len(r) > 27 and r[27] is not None else 0
    rating = r[29] if len(r) > 29 and r[29] is not None else ''
    try:
        revs = int(revs)
    except:
        revs = 0
    ss_ratings[asin] = {
        'asin': asin,
        'sku': sku,
        'title': title,
        'reviews': revs,
        'rating': rating
    }
print(f"Loaded {len(ss_ratings)} items from SellerSprite")

# 7. Ingest First 3 Pages SC Inventory
sc_3pages_file = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\inventory_first_3_pages_audit.md"
# We can also parse from the steps directly
print("All initial datasets successfully inspected and ready to merge!")
