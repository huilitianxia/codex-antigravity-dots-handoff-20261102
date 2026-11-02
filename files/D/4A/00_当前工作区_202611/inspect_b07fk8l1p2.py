import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
all_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"

with open(all_path, "r", encoding="utf-8", errors="replace") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))
all_by_sku = {r["seller-sku"]: r for r in all_rows}

wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
cat_rows = list(ws.iter_rows(min_row=7, values_only=True))

print("=== ALL CHILDREN OF PARENT-4A-303-CLASSIC-SQUARE ===")
for r in cat_rows:
    if r and len(r) > 6 and (r[6] == "PARENT-4A-303-CLASSIC-SQUARE" or "4.3" in str(r[59]) or "Christmas" in str(r[8]) or "Christmas" in str(r[1])):
        sku = r[2]
        al = all_by_sku.get(sku, {})
        print(
            f"SKU={str(sku):24s} | ASIN={str(r[12]):12s} | Status={str(r[0]):10s} | Chan={str(al.get('fulfillment-channel','')):10s} | "
            f"Qty={str(al.get('quantity','')):5s} | Parent={str(r[6]):28s} | Color={str(r[58]):22s} | Size={str(r[59]):26s} | Title={str(r[8])[:55]}"
        )
