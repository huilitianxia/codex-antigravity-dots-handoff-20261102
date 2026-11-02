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

# Let's check every Child row in 10-31 CLR and see if its Parent is one of the 21 parents or something else
children = [r for r in cat_rows if r and len(r) > 59 and r[5] == "Child"]
print(f"Total Child rows in 10-31 CLR: {len(children)}")

# Group by ASIN to ensure same-ASIN SKUs ALWAYS get identical (Parent, Theme, Color, Size)!
by_asin = {}
for r in children:
    asin = str(r[12] or "").strip()
    by_asin.setdefault(asin, []).append(r)

print(f"Total distinct Child ASINs: {len(by_asin)}")
