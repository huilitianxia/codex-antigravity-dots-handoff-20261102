import csv
import openpyxl
import sys
import re

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

# Map ASIN -> all rows in CLR (including non-Child rows that share the ASIN!)
by_asin = {}
for r in cat_rows:
    if r and len(r) > 59 and r[12] and r[5] != "Parent":
        by_asin.setdefault(str(r[12]).strip(), []).append(r)

print(f"Total distinct non-Parent ASINs in CLR: {len(by_asin)}")

# Let's inspect all non-Child non-Parent rows (orphans in CLR)
orphans = [r for r in cat_rows if r and len(r) > 59 and r[5] not in ("Child", "Parent") and r[2]]
print(f"Orphan rows in CLR: {len(orphans)}")
for r in orphans:
    sku = r[2]
    asin = r[12]
    al = all_by_sku.get(sku, {})
    mfn_q = int(al.get("quantity") or 0) if al.get("fulfillment-channel") == "DEFAULT" else 0
    fba_q = fba_by_sku.get(sku, 0)
    if fba_q > 0 or mfn_q > 0 or asin in by_asin and len(by_asin[asin]) > 1:
        print(f"  Orphan SKU={sku:26s} | ASIN={str(asin):11s} | FBA={fba_q:4d} | MFN={mfn_q:4d} | SiblingCount={len(by_asin.get(str(asin),[]))} | Title={str(r[8])[:55]}")
