import csv
import glob
import json
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

# Find all excel/csv/json files in D:\4A that might have factory/FBM inventory
for p in glob.glob(r"D:\4A\**\*", recursive=True):
    if any(k in p.lower() for k in ("库存", "pricing", "master", "cashflow", "stock", "盘点", "底表")):
        print("Found file:", p)
