import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
all_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
fba_path = r"D:\下载文件\284701020757.txt"

with open(all_path, "r", encoding="utf-8", errors="ignore") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))
all_by_sku = {r["seller-sku"]: r for r in all_rows}

fba_by_sku = {}
with open(fba_path, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fba_by_sku[r["sku"]] = int(r.get("available") or 0) + int(r.get("fc-transfer") or 0)

wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
cat_rows = list(ws.iter_rows(min_row=7, values_only=True))

# 1. Check all ASINs with multiple SKUs in Category Report where Parent, Color, or Size disagree!
by_asin = {}
for r in cat_rows:
    if r and len(r) > 59 and r[12]:
        by_asin.setdefault(r[12], []).append(r)

print("=== 1. ALL ASINS WHERE MULTIPLE SKUS DISAGREE ON PARENT, COLOR, OR SIZE ===")
disagree_count = 0
for asin, rlist in sorted(by_asin.items()):
    if len(rlist) > 1:
        parents = {r[6] for r in rlist}
        colors = {r[58] for r in rlist}
        sizes = {r[59] for r in rlist}
        if len(parents) > 1 or len(colors) > 1 or len(sizes) > 1:
            disagree_count += 1
            desc = " || ".join(
                f"{r[2]}[P={r[6]}, C={r[58]}, S={r[59]}]"
                for r in rlist
            )
            print(f"  {asin}: {desc}")
print(f"Total multi-SKU ASINs with Parent/Color/Size disagreement: {disagree_count}")

# 2. Print all 21 families and all their ACTIVE (or in-stock FBA/FBM) children + their current Color/Size/Title
print("\n=== 2. ALL 21 FAMILIES: ACTIVE / IN-STOCK CHILDREN AUDIT ===")
by_parent = {}
for r in cat_rows:
    if r and len(r) > 59 and r[5] == "Child":
        by_parent.setdefault(str(r[6]), []).append(r)

for parent, rlist in sorted(by_parent.items(), key=lambda x: -len(x[1])):
    print(f"\n==================== {parent} (Total rows: {len(rlist)}) ====================")
    for r in rlist:
        sku = r[2]
        asin = r[12]
        al = all_by_sku.get(sku, {})
        ch = al.get("fulfillment-channel", "")
        mfn_q = int(al.get("quantity") or 0) if ch == "DEFAULT" else 0
        fba_q = fba_by_sku.get(sku, 0)
        st = al.get("status", r[0])
        if st == "Active" or mfn_q > 0 or fba_q > 0:
            print(
                f"  SKU={str(sku):26s} | ASIN={str(asin):11s} | {ch:9s} | FBA={fba_q:4d} | MFN={mfn_q:4d} | "
                f"Color={str(r[58]):20s} | Size={str(r[59]):32s} | Title={str(r[8])[:55]}"
            )
