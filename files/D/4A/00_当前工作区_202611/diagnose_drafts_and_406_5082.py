import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 1. Inspect 所有商品报告_11-01-2026.txt for Incomplete / Drafts and for 406x6, 5082, 303x12, 301x12
all_listings_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
with open(all_listings_path, "r", encoding="utf-8", errors="replace") as f:
    reader = csv.DictReader(f, delimiter="\t")
    rows = list(reader)

print(f"Total rows in 所有商品报告_11-01-2026.txt: {len(rows)}")
status_counts = {}
for r in rows:
    st = r.get("status", "")
    status_counts[st] = status_counts.get(st, 0) + 1
print("Status counts in 所有商品报告:", status_counts)

# Check 406x6, 5082, 303x12-N-Z, 301x12 in 所有商品报告
print("\n=== TARGET SKUS IN 所有商品报告_11-01-2026.txt ===")
for r in rows:
    sku = r.get("seller-sku", "")
    if any(k in sku.lower() for k in ["406x6", "5082", "303x12", "301x12"]):
        print(
            f"SKU={sku:24s} | ASIN={r.get('asin1',''):12s} | Status={r.get('status',''):10s} | "
            f"Channel={r.get('fulfillment-channel',''):10s} | Qty={r.get('quantity',''):6s} | "
            f"Price={r.get('price',''):7s} | ShipGroup={r.get('merchant-shipping-group','')}"
        )

# 2. Check 分类商品报告_10-31-2026.xlsm for 4A 301x12-Y, 4A 301x12, 4A 303x12-N-Z, 406x6, 5082
cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
cat_rows = list(ws.iter_rows(values_only=True))
h4 = cat_rows[3]
h5 = cat_rows[4]

print("\n=== TARGET SKUS IN 分类商品报告_10-31-2026.xlsm ===")
for idx, r in enumerate(cat_rows[6:], 7):
    if not r or len(r) < 15:
        continue
    sku = str(r[2] or "")
    if any(k in sku.lower() for k in ["406x6", "5082", "303x12", "301x12"]):
        print(
            f"Row {idx:3d} | SKU={sku:24s} | Status={str(r[0]):12s} | Role={str(r[5]):6s} | Parent={str(r[6]):28s} | "
            f"IDType={str(r[11]):6s} | ID={str(r[12]):14s} | Qty(346)={str(r[346]):6s} | Price(348)={str(r[348]):7s} | "
            f"Stop(355)={str(r[355]):24s} | ShipTpl(372)={str(r[372])}"
        )
