import os
import sys
import csv
import json
import openpyxl
import re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# ==========================================================
# 1. LOAD ALL DATA SOURCES WITH PROPER ENCODING
# ==========================================================
print("=== Loading data sources ===")

# (1) All Listings Report 09-03 (754 rows)
sc_report = {}
with open(r"D:\下载文件\所有商品报告_09-03-2026.txt", 'r', encoding='utf-8-sig', errors='ignore') as f:
    reader = csv.DictReader(f, delimiter='\t')
    for r in reader:
        sku = (r.get('seller-sku') or '').strip()
        asin = (r.get('asin1') or '').strip()
        if not sku and not asin: continue
        key = sku if sku else asin
        sc_report[key] = {
            'sku': sku,
            'asin': asin,
            'title': (r.get('item-name') or '').strip(),
            'price': (r.get('price') or '').strip(),
            'qty': (r.get('quantity') or '').strip(),
            'status': (r.get('status') or '').strip(),
            'fc': (r.get('fulfillment-channel') or '').strip(),
            'open_date': (r.get('open-date') or '').strip()
        }
print(f"Loaded {len(sc_report)} from 所有商品报告_09-03 (with utf-8-sig BOM stripped)")

# (2) Recent SC items from f1367eb9 steps
recent_sc = {}
steps_dir = r"C:\Users\24243\.gemini\antigravity\brain\f1367eb9-fa19-4a11-abf4-4dc63e32dd4b\.system_generated\steps"
for step in ['54', '57', '537', '570', '581', '588', '599']:
    p = os.path.join(steps_dir, step, "output.txt")
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.read()
            blocks = re.findall(r'```json\s*([\s\S]*?)\s*```', txt)
            for b in blocks:
                try:
                    data = json.loads(b)
                    if isinstance(data, list):
                        for it in data:
                            sku = it.get('sku', '').strip()
                            asin = it.get('asin', '').strip()
                            if sku or asin:
                                recent_sc[sku or asin] = it
                except Exception:
                    pass
print(f"Loaded {len(recent_sc)} from recent SC inventory crawls")

# (3) WooCommerce 163 SKUs
woo_items = {}
with open(r"E:\Desktop\WooCommerce_完整改价_163_SKUs_复核后上传_2026-08-20.csv", 'r', encoding='utf-8-sig', errors='ignore') as f:
    reader = csv.DictReader(f)
    for r in reader:
        sku = (r.get('SKU') or '').strip()
        if sku:
            woo_items[sku] = {
                'id': r.get('ID', ''),
                'regular_price': r.get('Regular price', ''),
                'sale_price': r.get('Sale price', '')
            }
print(f"Loaded {len(woo_items)} from WooCommerce 163")

# (4) 269 Out of Stock Excels
oos_items = {}
wb1 = openpyxl.load_workbook(r"C:\Users\24243\Downloads\4A缺货_269评分已补全_被低估好款.xlsx", data_only=True)
ws1 = wb1['全部269(已补评分)']
for r in ws1.iter_rows(min_row=2, values_only=True):
    if not r or not r[0]: continue
    asin = str(r[0]).strip()
    oos_items[asin] = {
        'asin': asin,
        'title': str(r[1]).strip() if r[1] else '',
        'status': str(r[2]).strip() if r[2] else '',
        'price': str(r[3]).strip() if r[3] else '',
        'stars': r[4] if r[4] is not None else '',
        'reviews': r[5] if isinstance(r[5], (int, float)) else 0,
        'category': str(r[8]).strip() if len(r) > 8 and r[8] else ''
    }

wb2 = openpyxl.load_workbook(r"C:\Users\24243\Downloads\4A-SL缺货评分好款.xlsx", data_only=True)
ws2 = wb2['全部269(父子过滤)']
for r in ws2.iter_rows(min_row=2, values_only=True):
    if not r or not r[0]: continue
    asin = str(r[0]).strip()
    if asin not in oos_items:
        oos_items[asin] = {'asin': asin, 'title': str(r[1] or r[2] or ''), 'reviews': 0, 'stars': ''}
    oos_items[asin]['parent_asin'] = str(r[14]).strip() if len(r) > 14 and r[14] else ''
    oos_items[asin]['brothers'] = str(r[15]).strip() if len(r) > 15 and r[15] else ''
    rev = r[6] if len(r) > 6 and isinstance(r[6], (int, float)) else 0
    if rev > oos_items[asin].get('reviews', 0):
        oos_items[asin]['reviews'] = rev
        oos_items[asin]['stars'] = r[5] if len(r) > 5 else ''
print(f"Loaded {len(oos_items)} from 269 OOS Excels")

# (5) 供应商与开店总表 (200 rows)
store_master = {}
wb3 = openpyxl.load_workbook(r"C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx", data_only=True)
ws3 = wb3['Sheet1']
for r in ws3.iter_rows(min_row=2, values_only=True):
    if not r or not r[0]: continue
    sku = str(r[0]).strip()
    store_master[sku] = {
        'sku': sku,
        'vc_upc': str(r[1]).strip() if r[1] else '',
        'vc_asin': str(r[2]).strip() if r[2] else '',
        'sl_upc': str(r[3]).strip() if r[3] else '',
        'sl_asin': str(r[4]).strip() if r[4] else '',
        'title': str(r[6]).strip() if len(r) > 6 and r[6] else '',
        'sale_price': str(r[12]).strip() if len(r) > 12 and r[12] else ''
    }
print(f"Loaded {len(store_master)} from 供应商与店铺总表")

# (6) VC SC Audit Data (309 items)
vc_audit = {}
with open(r"E:\OpenAI-Codex\Workspaces\C-Documents\2026-08-28\new-task-handoff-2026-08-28\work\vc_sc_audit_data.json", 'r', encoding='utf-8') as f:
    vcd = json.load(f)
    for it in vcd.get('vc_all', []):
        asin = (it.get('vc_asin') or '').strip()
        sku = (it.get('vc_sku') or '').strip()
        vc_audit[asin or sku] = it
print(f"Loaded {len(vc_audit)} from VC Audit Data")

# (7) SellerSprite Live Reviews (256 items)
ss_ratings = {}
wb_ss = openpyxl.load_workbook(r"D:\下载文件\Competitor-US-Last-30-days-217940.xlsx", data_only=True)
ws_ss = wb_ss['Competitor-US-Last-30-days']
for r in ws_ss.iter_rows(min_row=2, values_only=True):
    if not r or not r[0]: continue
    asin = str(r[0]).strip()
    revs = r[27] if len(r) > 27 and isinstance(r[27], (int, float)) else 0
    stars = r[29] if len(r) > 29 and r[29] is not None else ''
    ss_ratings[asin] = {'reviews': int(revs), 'stars': stars}
print(f"Loaded {len(ss_ratings)} from SellerSprite")

# (8) Factory Warehouse Inventory (212 items)
wh_stock = {}
wb_wh = openpyxl.load_workbook(r"C:\Users\24243\Downloads\4A_2026-08-10库存.xlsx", data_only=True)
for sn in wb_wh.sheetnames:
    ws = wb_wh[sn]
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or not r[1]: continue
        sku = str(r[1]).strip()
        qty = r[3] if len(r) > 3 and r[3] is not None else 0
        wh_stock[sku] = qty
print(f"Loaded {len(wh_stock)} from 工厂实物库存表")

# ==========================================================
# 2. MASTER UNIFIED PRODUCT REGISTRY
# ==========================================================
print("\n=== Building Master Unified Registry ===")

all_entities = {}

def get_or_create(sku, asin, title=''):
    key = sku if sku else asin
    if key not in all_entities:
        all_entities[key] = {
            'sku': sku,
            'asin': asin,
            'title': title,
            'price': '',
            'woo_price': '',
            'fba_qty': 0,
            'wh_qty': 0,
            'status': '',
            'fc': '',
            'reviews': 0,
            'stars': '',
            'parent_asin': '',
            'vc_asin': '',
            'vc_sku': '',
            'is_historical_oos': False,
            'is_woo_163': False,
            'sources': set()
        }
    ent = all_entities[key]
    if sku and not ent['sku']: ent['sku'] = sku
    if asin and not ent['asin']: ent['asin'] = asin
    if title and len(title) > len(ent['title']): ent['title'] = title
    return ent

# Ingest SC report (754)
for k, v in sc_report.items():
    ent = get_or_create(v['sku'], v['asin'], v['title'])
    ent['price'] = v['price']
    ent['status'] = v['status']
    ent['fc'] = v['fc']
    try:
        ent['fba_qty'] = int(v['qty']) if v['qty'] else 0
    except:
        pass
    ent['sources'].add('SC_0903_Report')

# Ingest Recent SC crawled (77)
for k, v in recent_sc.items():
    ent = get_or_create(v.get('sku', ''), v.get('asin', ''), v.get('title', ''))
    if v.get('price'): ent['price'] = v.get('price')
    if v.get('status'): ent['status'] = v.get('status')
    try:
        avail = int(v.get('avail', '0') or 0)
        if avail > ent['fba_qty']: ent['fba_qty'] = avail
    except:
        pass
    ent['sources'].add('SC_Recent_Crawl')

# Ingest WooCommerce 163
for sku, v in woo_items.items():
    ent = get_or_create(sku, '')
    ent['is_woo_163'] = True
    ent['woo_price'] = v['sale_price'] or v['regular_price']
    ent['sources'].add('WooCommerce_163')

# Ingest 269 OOS
for asin, v in oos_items.items():
    found = False
    for ent in all_entities.values():
        if ent['asin'] == asin:
            ent['is_historical_oos'] = True
            if v['reviews'] > ent['reviews']:
                ent['reviews'] = v['reviews']
                ent['stars'] = v['stars']
            if v['title'] and len(v['title']) > len(ent['title']):
                ent['title'] = v['title']
            if v.get('parent_asin'): ent['parent_asin'] = v['parent_asin']
            ent['sources'].add('269_OOS')
            found = True
            break
    if not found:
        ent = get_or_create('', asin, v['title'])
        ent['is_historical_oos'] = True
        ent['reviews'] = v['reviews']
        ent['stars'] = v['stars']
        ent['status'] = v['status']
        ent['price'] = v['price']
        ent['parent_asin'] = v.get('parent_asin', '')
        ent['sources'].add('269_OOS')

# Ingest Store Master (200)
for sku, v in store_master.items():
    ent = get_or_create(sku, v['sl_asin'], v['title'])
    ent['vc_asin'] = v['vc_asin']
    ent['vc_sku'] = sku
    if v['sale_price'] and not ent['price']: ent['price'] = v['sale_price']
    ent['sources'].add('Store_Master_2026')

# Ingest VC Audit (309)
for k, v in vc_audit.items():
    vc_asin = v.get('vc_asin', '')
    vc_sku = v.get('vc_sku', '')
    sc_asin = v.get('sc_asin', '')
    sc_sku = v.get('sc_sku', '')
    matched = False
    for ent in all_entities.values():
        if (sc_sku and ent['sku'] == sc_sku) or (sc_asin and ent['asin'] == sc_asin) or (vc_asin and ent['asin'] == vc_asin):
            ent['vc_asin'] = vc_asin
            ent['vc_sku'] = vc_sku
            ent['sources'].add('VC_Audit')
            matched = True
            break
    if not matched and (sc_sku or vc_sku or vc_asin):
        ent = get_or_create(sc_sku or vc_sku, sc_asin or vc_asin)
        ent['vc_asin'] = vc_asin
        ent['vc_sku'] = vc_sku
        ent['sources'].add('VC_Audit')

# Ingest SellerSprite reviews
for asin, v in ss_ratings.items():
    for ent in all_entities.values():
        if ent['asin'] == asin:
            if v['reviews'] > ent['reviews']:
                ent['reviews'] = v['reviews']
                ent['stars'] = v['stars']
            break

# Ingest Factory warehouse stock
for sku, qty in wh_stock.items():
    for ent in all_entities.values():
        if ent['sku'] == sku or ent['sku'].replace(' ', '') == sku.replace(' ', ''):
            ent['wh_qty'] = qty
            break

print(f"Total Unique Unified Entities in Master Registry: {len(all_entities)}")

out_path = r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\unified_entities_summary.json"
with open(out_path, 'w', encoding='utf-8') as f:
    serializable = {}
    for k, v in all_entities.items():
        c = dict(v)
        c['sources'] = list(c['sources'])
        serializable[k] = c
    json.dump(serializable, f, ensure_ascii=False, indent=2)
print("Saved refreshed unified entities summary to JSON.")
