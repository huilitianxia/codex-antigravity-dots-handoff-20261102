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

# Let's see how each ASIN's product type / model number / title maps to the 21 families!
# First let's list all ASINs where the current parent in CLR looks wrong or where multiple SKUs disagree on parent.
by_asin = {}
for r in cat_rows:
    if r and len(r) > 59 and r[12] and r[5] != "Parent":
        by_asin.setdefault(str(r[12]).strip(), []).append(r)

print("=== ASINS WITH MULTIPLE DIFFERENT PARENTS IN CLR ===")
for asin, rlist in sorted(by_asin.items()):
    ps = {r[6] for r in rlist if r[6]}
    if len(ps) > 1:
        print(f"  {asin}: " + " || ".join(f"{r[2]} -> {r[6]} ({r[8]})" for r in rlist))
