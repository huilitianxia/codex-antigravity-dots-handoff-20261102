import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

MASTER_FILE = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"
REVIEW_FILE = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\4A_库存分类与合并复核_20261031.xlsx"
ALL_LISTINGS_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
FBA_INV_FILE = r"D:\下载文件\284701020757.txt"

with open(ALL_LISTINGS_FILE, "r", encoding="utf-8", errors="ignore") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))
by_asin = {}
by_sku = {}
for r in all_rows:
    by_asin.setdefault(r["asin1"], []).append(r)
    by_sku[r["seller-sku"]] = r

fba_by_sku = {}
with open(FBA_INV_FILE, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fba_by_sku[r["sku"]] = r

print("=== 1. CHECK 4A_库存分类与合并复核_20261031.xlsx '同款配对' & '库存补救' ===")
wb_rev = openpyxl.load_workbook(REVIEW_FILE, read_only=True, data_only=True)
for sname in ("同款配对", "库存补救"):
    ws = wb_rev[sname]
    print(f"\n--- Sheet: {sname} ---")
    for i, r in enumerate(ws.iter_rows(values_only=True), 1):
        if any(r) and i <= 60:
            vals = [str(v) if v is not None else "" for v in r[:14]]
            print(f"  R{i:2d}: {' | '.join(vals)}")
wb_rev.close()

print("\n=== 2. CHECK MASTER SHEET ROWS WHERE VC_ASIN != SL_ASIN OR VC_ASIN EXISTS ===")
wb_m = openpyxl.load_workbook(MASTER_FILE, read_only=True, data_only=True)
ws_m = wb_m["Sheet1"]
for i, r in enumerate(ws_m.iter_rows(min_row=2, values_only=True), 2):
    if r and any(r[:6]):
        sku_base = str(r[0] or "").strip()
        vc_asin = str(r[2] or "").strip()
        sl_asin = str(r[4] or "").strip()
        ship_code = str(r[7] or "").strip()
        price_base = r[11]
        price_2026 = r[12]
        wt = r[14]
        vc_offers = by_asin.get(vc_asin, []) if vc_asin else []
        sl_offers = by_asin.get(sl_asin, []) if sl_asin else []
        if vc_asin or sl_asin:
            vc_str = ", ".join(f"{o['seller-sku']}({'FBA' if o['fulfillment-channel']=='AMAZON_NA' else 'FBM:'+o['quantity']})" for o in vc_offers) or "NONE_IN_STORE"
            sl_str = ", ".join(f"{o['seller-sku']}({'FBA' if o['fulfillment-channel']=='AMAZON_NA' else 'FBM:'+o['quantity']})" for o in sl_offers) or "NONE_IN_STORE"
            print(f"Row {i:3d} | Model={sku_base:18s} | Price={str(price_2026 or price_base):6s} | VC={vc_asin:11s} [{vc_str}] | SL={sl_asin:11s} [{sl_str}]")
wb_m.close()
