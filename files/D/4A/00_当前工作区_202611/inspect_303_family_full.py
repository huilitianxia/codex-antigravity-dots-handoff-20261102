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

print("=== 1. ALL CHILDREN OF PARENT-4A-303-CLASSIC-SQUARE WITH INVENTORY OR ACTIVE STATUS ===")
children = [r for r in cat_rows if r and len(r) > 6 and r[6] == "PARENT-4A-303-CLASSIC-SQUARE"]
print(f"Total rows in PARENT-4A-303-CLASSIC-SQUARE: {len(children)}")
for r in children:
    sku = r[2]
    al = all_by_sku.get(sku, {})
    qty = al.get("quantity", "")
    chan = al.get("fulfillment-channel", "")
    status = al.get("status", r[0])
    print(
        f"  SKU={str(sku):28s} | ASIN={str(r[12]):11s} | St={str(status):9s} | Ch={str(chan):9s} | Qty={str(qty):5s} | "
        f"Color={str(r[58]):20s} | Size={str(r[59]):28s} | Title={str(r[8])[:55]}"
    )

print("\n=== 2. FIND WHERE '6\" x 4.3\"' OR '4\" x 2.5\"' OR '6\" x 3\"' COME FROM ===")
for r in cat_rows:
    if r and len(r) > 59 and any(x in str(r[59]) for x in ("4.3", "2.5", "6\" x 3\"")):
        print(f"  SKU={r[2]} | ASIN={r[12]} | Parent={r[6]} | Color={r[58]} | Size={r[59]} | Title={str(r[8])[:60]}")
