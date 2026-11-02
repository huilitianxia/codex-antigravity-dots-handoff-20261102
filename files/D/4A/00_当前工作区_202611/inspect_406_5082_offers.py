import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
rows = list(ws.iter_rows(values_only=True))
h4 = rows[3]
h5 = rows[4]

all_listings_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
with open(all_listings_path, "r", encoding="utf-8", errors="replace") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))

by_asin = {}
for r in all_rows:
    by_asin.setdefault(r["asin1"], []).append(r)

target_asins = {
    "B01MSZS7M3",  # 406x6 Pastel
    "B01MSZSEBW",  # 406x6-N Neon
    "B01N0RJSTU",  # 406x6-Y Yellow
    "B07FKL263W",  # AAAA 4A 406x6
    "B07FKHHTY4",  # 4A GM406x6-N / AAAA 4A 406x6-N
    "B07PVWYS9T",  # 406x6-N*2
    "B07F2BHFJH",  # 5082-Y-L / 5082-Y-L-GM
    "B07DJKB2S9",  # 5082-Y-L-FBA
    "B0F9L5G6XQ",  # 5082-Y-Lx2
}

print("=== 1. ALL OFFERS ON 406x6 AND 5082 ASINS IN 所有商品报告_11-01-2026.txt ===")
for asin in sorted(target_asins):
    offers = by_asin.get(asin, [])
    print(f"\nASIN {asin}: {len(offers)} offer(s)")
    for o in offers:
        print(
            f"  SKU={o['seller-sku']:22s} | Status={o['status']:10s} | Chan={o['fulfillment-channel']:10s} | "
            f"Qty={o['quantity']:6s} | Price={o['price']:7s} | ShipGroup={o.get('merchant-shipping-group','')} | "
            f"OpenDate={o['open-date']}"
        )

print("\n=== 2. ALL NON-EMPTY OFFER/DATE/PRICE/WEIGHT COLUMNS IN 分类商品报告 FOR THESE SKUS ===")
target_skus = {o["seller-sku"] for a in target_asins for o in by_asin.get(a, [])}
for r in rows[6:]:
    if r and len(r) > 2 and r[2] in target_skus:
        sku = r[2]
        asin = r[12]
        print(f"\n--- SKU: {sku} (ASIN: {asin}, Status: {r[0]}) ---")
        for c_idx in range(len(r)):
            val = r[c_idx]
            if val is not None and (c_idx >= 310 or c_idx in (3, 4, 5, 6, 7, 11, 12, 54, 58, 59, 62, 75)):
                print(f"  Col {c_idx:3d} ({h4[c_idx]}): {val}")

# 3. Also check across ALL 207 Active MFN SKUs in 分类商品报告: how many have Stop Selling Date (Col 355), or missing Weight (Col 385), or future Release Date!
print("\n=== 3. FULL AUDIT OF ALL 207 MFN (Qty>0) SKUS IN 分类商品报告 ===")
mfn_active_skus = {r["seller-sku"]: r for r in all_rows if r.get("fulfillment-channel") == "DEFAULT" and int(r.get("quantity") or 0) > 0}
stop_date_skus = []
missing_weight_skus = []
future_release_skus = []
for r in rows[6:]:
    if r and len(r) > 386 and r[2] in mfn_active_skus:
        sku = r[2]
        if r[355] is not None or r[360] is not None:
            stop_date_skus.append((sku, r[12], mfn_active_skus[sku]["quantity"], r[355], r[360]))
        if r[385] is None:
            missing_weight_skus.append((sku, r[12], mfn_active_skus[sku]["quantity"], mfn_active_skus[sku].get("merchant-shipping-group")))
        if r[321] is not None or r[354] is not None:
            future_release_skus.append((sku, r[12], r[321], r[354]))

print(f"Active MFN SKUs with Stop Selling Date (Col 355/360): {len(stop_date_skus)}")
for x in stop_date_skus:
    print(" ", x)
print(f"Active MFN SKUs with Missing Package Weight (Col 385): {len(missing_weight_skus)}")
print(f"Active MFN SKUs with Release Date (Col 321/354): {len(future_release_skus)}")
for x in future_release_skus[:15]:
    print(" ", x)
