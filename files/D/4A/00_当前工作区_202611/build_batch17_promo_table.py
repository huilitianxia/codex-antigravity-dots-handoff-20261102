import openpyxl
import shutil
import hashlib
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-fullscan-parsed.json", "r", encoding="utf-8") as f:
    scan = json.load(f)

for r in scan['rows']:
    if r['sku'] == 'AAAA 4A 305-Full Glue' or r['asin'] == 'B07FK9BYHW':
        print("In coupon scan:", r)

# Build 17-remaining-high-stock-5pct-promo-and-b2b.xlsm using 10-four-noncoupon-promotions.xlsm as base template
SRC_TPL = r"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\10-four-noncoupon-promotions.xlsm"
WORK_DIR = r"D:\4A\00_当前工作区_202611"
DESKTOP_DIR = r"E:\Desktop"

wb = openpyxl.load_workbook(SRC_TPL, keep_vba=True)
ws = wb['Template']
max_col = ws.max_column

# Clear rows 7..max_row
for r in range(7, ws.max_row + 1):
    for c in range(1, max_col + 1):
        ws.cell(r, c).value = None

# Exact 5% gentle Sale Price (2026-11-02 to 2026-11-16) + B2B Price + B2B Quantity Tiers (3->2%, 5->3%, 10->5%)
# Columns in PriceAndQuantity.xlsm (1-based):
# Col 1 (A): SKU
# Col 11 (K): Sale Price (discounted_price#1.schedule#1.value_with_tax)
# Col 12 (L): Sale Start Date (2026-11-02)
# Col 13 (M): Sale End Date (2026-11-16)
# Col 16 (P): B2B Price (audience=B2B our_price)
# Col 21 (U): Quantity Discount Type ('Percent')
# Col 22 (V): Tier 1 Lower Bound (3)
# Col 23 (W): Tier 1 Value (2)
# Col 24 (X): Tier 2 Lower Bound (5)
# Col 25 (Y): Tier 2 Value (3)
# Col 26 (Z): Tier 3 Lower Bound (10)
# Col 27 (AA): Tier 3 Value (5)

promo_rows = [
    {"sku": "4A 304 Full Glue",         "asin": "B00SMEFFRE", "qty": 333, "reg_price": 9.99,  "sale_price": 9.49,  "b2b_price": 9.49,  "note": "333 FBA units: mild 5% Sale ($9.49) + B2B $9.49 + 3/5/10 tiers (no $0.60 coupon fee!)"},
    {"sku": "4A 304-Full Adhesive-400", "asin": "B07QXJWDPL", "qty": 533, "reg_price": 21.99, "sale_price": 20.89, "b2b_price": 20.49, "note": "533 FBA units (rating 2.8 blocked from coupon): 5% Sale ($20.89) + B2B $20.49 + 3/5/10 tiers"},
    {"sku": "AAAA 4A 304-Full Glue",    "asin": "B07FK975YB", "qty": 372, "reg_price": 12.99, "sale_price": 12.34, "b2b_price": 12.19, "note": "372 FBA units (rating 2.2 blocked from coupon): 5% Sale ($12.34) + B2B $12.19 + 3/5/10 tiers"},
    {"sku": "4A 305-Full Adhesive-300", "asin": "B07QXJZKHC", "qty": 174, "reg_price": 21.99, "sale_price": 20.89, "b2b_price": 20.49, "note": "174 FBA units (rating 2.6 blocked from coupon): 5% Sale ($20.89) + B2B $20.49 + 3/5/10 tiers"},
    {"sku": "AAAA 4A 305-Full Glue",    "asin": "B07FK9BYHW", "qty": 60,  "reg_price": 14.99, "sale_price": 14.24, "b2b_price": 13.99, "note": "60 FBA units (56 aged >365d, rating 2.6 blocked): 5% Sale ($14.24) + B2B $13.99 + 3/5/10 tiers"},
    {"sku": "4A 5082-Y-L-GM",           "asin": "B07F2BHFJH", "qty": 65,  "reg_price": 11.99, "sale_price": 11.39, "b2b_price": 11.19, "note": "65 FBA units (24 aged): 5% Sale ($11.39) + B2B $11.19 + 3/5/10 tiers"},
    {"sku": "4A 5020x3",                "asin": "B07RN7WQ81", "qty": 50,  "reg_price": 25.99, "sale_price": 24.69, "b2b_price": 24.49, "note": "50 FBA units (VC classic 5020x3): 5% Sale ($24.69) + B2B $24.49 + 3/5/10 tiers"},
]

for idx, item in enumerate(promo_rows):
    r = 7 + idx
    ws.cell(r, 1).value = item["sku"]
    ws.cell(r, 11).value = item["sale_price"]
    ws.cell(r, 12).value = "2026-11-02"
    ws.cell(r, 13).value = "2026-11-16"
    ws.cell(r, 16).value = item["b2b_price"]
    ws.cell(r, 21).value = "Percent"
    ws.cell(r, 22).value = 3
    ws.cell(r, 23).value = 2
    ws.cell(r, 24).value = 5
    ws.cell(r, 25).value = 3
    ws.cell(r, 26).value = 10
    ws.cell(r, 27).value = 5

out_work = os.path.join(WORK_DIR, "17-remaining-high-stock-5pct-promo-and-b2b.xlsm")
out_desk = os.path.join(DESKTOP_DIR, "17-remaining-high-stock-5pct-promo-and-b2b.xlsm")
out_audit = os.path.join(WORK_DIR, "batch17_cell_audit.json")

wb.save(out_work)
shutil.copy2(out_work, out_desk)
with open(out_audit, "w", encoding="utf-8") as f:
    json.dump(promo_rows, f, ensure_ascii=False, indent=2)

sha = hashlib.sha256(open(out_work, "rb").read()).hexdigest()
print(f"Batch 17 built & copied to E:\\Desktop! Rows={len(promo_rows)}, SHA256={sha}")
