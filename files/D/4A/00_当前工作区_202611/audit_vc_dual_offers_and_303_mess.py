import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
all_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"

with open(all_path, "r", encoding="utf-8", errors="replace") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))
all_by_sku = {r["seller-sku"]: r for r in all_rows}
all_by_asin = {}
for r in all_rows:
    all_by_asin.setdefault(r["asin1"], []).append(r)

wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
cat_rows = list(ws.iter_rows(min_row=7, values_only=True))
cat_by_sku = {r[2]: r for r in cat_rows if r and len(r) > 2 and r[2]}

print("=== 1. SAME-ASIN DUAL OFFERS (FBA + FBM ON THE SAME ASIN) CURRENTLY IN STORE ===")
dual_asins = []
fba_only_zero_stock_vc = []
for asin, offers in sorted(all_by_asin.items()):
    chans = {o["fulfillment-channel"] for o in offers}
    if "AMAZON_NA" in chans and "DEFAULT" in chans:
        dual_asins.append((asin, offers))
    elif "AMAZON_NA" in chans and "DEFAULT" not in chans:
        # Check if it's an old B00/B01 VC ASIN
        if asin.startswith(("B00", "B01")):
            fba_only_zero_stock_vc.append((asin, offers))

print(f"Total ASINs that ALREADY have both FBA + FBM SKUs on the exact same ASIN: {len(dual_asins)}")
for asin, offers in dual_asins[:35]:
    desc = " + ".join(
        f"{o['seller-sku']}({'FBA' if o['fulfillment-channel']=='AMAZON_NA' else 'FBM:' + str(o['quantity'])},{o['status']})"
        for o in offers
    )
    sku0 = offers[0]["seller-sku"]
    title = str(cat_by_sku.get(sku0, [None]*9)[8] or "")[:48]
    print(f"  {asin}: {desc:65s} | {title}")

print(f"\nTotal Old VC ASINs (B00/B01) that ONLY have an FBA SKU (NO FBM SKU attached yet): {len(fba_only_zero_stock_vc)}")
for asin, offers in fba_only_zero_stock_vc:
    desc = " + ".join(f"{o['seller-sku']}({o['status']},Price={o['price']})" for o in offers)
    sku0 = offers[0]["seller-sku"]
    title = str(cat_by_sku.get(sku0, [None]*9)[8] or "")[:52]
    print(f"  {asin}: {desc:45s} | {title}")

print("\n=== 2. WHY B07FK8L1P2 SHOWS 'Pastel Assorted' WITH 15 MESSY SIZES IN PARENT-4A-303-CLASSIC-SQUARE ===")
p303 = [r for r in cat_rows if r and len(r) > 6 and r[6] == "PARENT-4A-303-CLASSIC-SQUARE"]
by_color = {}
for r in p303:
    al = all_by_sku.get(r[2], {})
    st = al.get("status", r[0])
    qty = int(al.get("quantity") or 0)
    ch = al.get("fulfillment-channel", "")
    by_color.setdefault(str(r[58]), []).append((r[2], r[12], st, ch, qty, r[59], str(r[8])[:55]))

for col, items in sorted(by_color.items()):
    print(f"\nColor '{col}': {len(items)} SKUs in PARENT-4A-303-CLASSIC-SQUARE")
    for it in items:
        if it[2] == "Active" or it[4] > 0:
            print(f"  [ACTIVE] SKU={it[0]:24s} | ASIN={it[1]} | Ch={it[3]:9s} | Qty={it[4]:5d} | Size={str(it[5]):26s} | {it[6]}")
