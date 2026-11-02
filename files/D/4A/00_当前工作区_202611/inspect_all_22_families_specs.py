import csv
import openpyxl
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
all_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
fba_path = r"D:\下载文件\284701020757.txt"
master_path = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"

with open(all_path, "r", encoding="utf-8", errors="ignore") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))
all_by_sku = {r["seller-sku"]: r for r in all_rows}

fba_by_sku = {}
with open(fba_path, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fba_by_sku[r["sku"]] = int(r.get("available") or 0) + int(r.get("fc-transfer") or 0)

# Load Master Pricing Sheet titles by ASIN and by Model so even generic-titled SKUs have their exact spec!
master_title_by_asin = {}
wb_m = openpyxl.load_workbook(master_path, read_only=True, data_only=True)
ws_m = wb_m["Sheet1"]
for r in ws_m.iter_rows(min_row=2, values_only=True):
    if r and any(r[:6]):
        t = str(r[6] or "").strip()
        for a_col in (2, 4):
            for a in str(r[a_col] or "").split():
                a = a.replace("√", "").strip()
                if a.startswith("B0"):
                    master_title_by_asin[a] = t
wb_m.close()

wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
cat_rows = list(ws.iter_rows(min_row=7, values_only=True))

by_asin = {}
for r in cat_rows:
    if r and len(r) > 59 and r[12] and r[5] != "Parent":
        by_asin.setdefault(str(r[12]).strip(), []).append(r)

from test_clean_21_classifier import classify_asin_v3

# Let's inspect all ASINs per family (especially active/in-stock ones and all siblings) to design clean Color & Size!
fam_asins = {}
for asin, rlist in sorted(by_asin.items()):
    p = classify_asin_v3(asin, rlist)
    fam_asins.setdefault(p, []).append((asin, rlist))

for p, alist in sorted(fam_asins.items()):
    print(f"\n==================== {p} ({len(alist)} ASINs) ====================")
    for asin, rlist in alist:
        skus = [str(r[2]) for r in rlist]
        fba_q = sum(fba_by_sku.get(s, 0) for s in skus)
        mfn_q = sum(int(all_by_sku.get(s, {}).get("quantity") or 0) for s in skus if all_by_sku.get(s, {}).get("fulfillment-channel") == "DEFAULT")
        titles = [str(r[8] or "") for r in rlist if r[8] and not str(r[8]).startswith("4A Self-Stick Notes")]
        if asin in master_title_by_asin:
            titles.append(master_title_by_asin[asin])
        best_t = max(titles, key=len) if titles else str(rlist[0][8] or "")
        cur_c = rlist[0][58]
        cur_s = rlist[0][59]
        if fba_q > 0 or mfn_q > 0 or len(rlist) > 1 or "(Pack" in str(cur_s) or str(rlist[0][6]) != p:
            print(f"  ASIN={asin} | FBA={fba_q:4d} | MFN={mfn_q:5d} | SKUs={skus} | CurC={str(cur_c):18s} | CurS={str(cur_s):28s} | BestT={best_t[:75]}")
