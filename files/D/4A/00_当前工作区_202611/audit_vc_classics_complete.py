import openpyxl
import os
import json

# Load All Listings 11-01-2026
with open(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt', 'r', encoding='utf-8', errors='replace') as f:
    all_lines = [l.rstrip('\n').split('\t') for l in f]

# Load FBA Inventory
fba_inv = {}
for root, dirs, files in os.walk(r'D:\4A'):
    for fn in files:
        if '亚马逊物流库存' in fn and fn.endswith('.txt'):
            p = os.path.join(root, fn)
            with open(p, 'r', encoding='utf-8', errors='replace') as f:
                flines = [l.rstrip('\n').split('\t') for l in f]
            fh = flines[0]
            for r in flines[1:]:
                if len(r) > 10 and r[9] == 'US':
                    fba_inv[r[0]] = {
                        'asin': r[2],
                        'afn_fulfillable': int(r[12]) if r[12].isdigit() else 0,
                        'afn_inbound': (int(r[15]) if r[15].isdigit() else 0) + (int(r[16]) if r[16].isdigit() else 0) + (int(r[17]) if r[17].isdigit() else 0),
                        'afn_reserved': int(r[13]) if r[13].isdigit() else 0
                    }
            break

# Load 分类商品报告_10-31-2026.xlsm
wb_cat = openpyxl.load_workbook(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm', read_only=True, data_only=True)
ws_cat = wb_cat['Template']
cat_rows = list(ws_cat.iter_rows(values_only=True))
cat_by_sku = {r[2]: r for r in cat_rows[6:] if r and len(r) > 2 and r[2]}

# Father's core VC best-seller models
vc_models = [
    ('303x12 (Pop-up & Flat)', ['303x12', '303X12']),
    ('30315 (15-Pad Rainbow)', ['30315']),
    ('354818 (1.38x1.88 Mini 18/36/72)', ['354818']),
    ('406x6 (4x6 Pastel/Neon/Yellow)', ['406x6', '406X6']),
    ('5088-N-L (5x8 Lined 8-Pad)', ['5088']),
    ('5084-N-L (5x8 Lined 4-Pad)', ['5084']),
    ('5082-Y-L (5x8 Yellow Lined 2-Pad)', ['5082']),
    ('608 Series (6x8 Lined)', ['608']),
    ('PSS 32x6 (6-Roll Dispenser)', ['PSS 32', 'PSS32']),
    ('301 Series (1.5x2 Mini)', ['301']),
    ('2028 Series (2x2 Mini)', ['2028']),
    ('BS 1801 & Refill (Desktop Organizer)', ['1801']),
    ('4012 / 4013 (PP Box Set)', ['4012', '4013']),
    ('5020x3 (Shaped Notes)', ['5020']),
    ('PSS 7 (Roll Notes Set)', ['PSS 7', 'PSS7']),
    ('406SL-10 / 40612 / 40612-L (4x6 Bulk)', ['406SL', '40612']),
]

print("=== FATHER'S VC CLASSICS LIVE AUDIT ===")
for label, keys in vc_models:
    print(f"\n>>> {label} <<<")
    for r in all_lines[1:]:
        if len(r) > 28 and any(k.lower() in r[3].lower() for k in keys):
            sku = r[3]
            asin = r[16]
            ch = 'FBA' if r[26] == 'AMAZON_NA' else 'MFN'
            st = r[28]
            price = r[4]
            mfn_q = int(r[5]) if r[5].isdigit() else 0
            fba_q = fba_inv.get(sku, {}).get('afn_fulfillable', 0)
            tpl = r[27]
            cr = cat_by_sku.get(sku)
            parent = cr[6] if cr and len(cr) > 6 else ''
            color = cr[80] if cr and len(cr) > 80 else ''
            size = cr[86] if cr and len(cr) > 86 else ''
            stop_dt = cr[355] if cr and len(cr) > 355 else ''
            if st == 'Active' or fba_q > 0 or mfn_q > 0 or '303x12' in sku.lower() or '354818' in sku.lower() or 'pss 32' in sku.lower():
                print(f"  SKU={sku:24s} | ASIN={asin} | {ch} | St={st:8s} | FBA={fba_q:4d} | MFN={mfn_q:4d} | ${price:6s} | Tpl={tpl:20s} | Parent={str(parent):28s} | Size={size} | Stop={stop_dt}")
