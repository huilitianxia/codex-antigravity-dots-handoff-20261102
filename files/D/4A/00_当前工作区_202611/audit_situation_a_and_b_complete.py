import csv
import openpyxl
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

ALL_LISTINGS_FILE = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
FBA_INV_FILE = r"D:\下载文件\284701020757.txt"
MASTER_FILE = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"

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
        fba_by_sku[r["sku"]] = int(r.get("available") or 0) + int(r.get("fc-transfer") or 0)

# Normalize model code to find any FBM SKU in the store for the same model!
def norm_model(s):
    s = s.upper()
    for p in ["AAAA ", "4A ", "GM-", "GM", "SC-", "SC", "VC", "SF-", "-FBA", "FBA", "B00SM", "B07T", "B01N7D3E0M"]:
        s = s.replace(p, "")
    s = re.sub(r"[\s\-_]+", "", s)
    return s

# Map norm_model -> all MFN SKUs with qty > 0
mfn_with_stock = {}
for r in all_rows:
    if r["fulfillment-channel"] == "DEFAULT" and int(r.get("quantity") or 0) > 0:
        nm = norm_model(r["seller-sku"])
        mfn_with_stock.setdefault(nm, []).append((r["seller-sku"], r["asin1"], int(r["quantity"]), r.get("price")))
        # Also index base without *2, *3, *4, x2, x3, x4
        nm_base = re.sub(r"(\*|\bX)\d+$", "", nm)
        if nm_base != nm:
            mfn_with_stock.setdefault(nm_base, []).append((r["seller-sku"] + " (多包组合)", r["asin1"], int(r["quantity"]), r.get("price")))

print("=== SITUATION A: ASINS WITH BOTH FBA SKU AND 0-STOCK FBM SKU ON THE SAME ASIN ===")
sit_a = []
for asin, offers in sorted(by_asin.items()):
    fba_offs = [o for o in offers if o["fulfillment-channel"] == "AMAZON_NA"]
    fbm_offs = [o for o in offers if o["fulfillment-channel"] == "DEFAULT"]
    if fba_offs and fbm_offs:
        max_fbm_q = max(int(o.get("quantity") or 0) for o in fbm_offs)
        max_fba_q = max(fba_by_sku.get(o["seller-sku"], 0) for o in fba_offs)
        if max_fbm_q == 0:
            # Check if any sibling MFN SKU in the store has stock for this model
            sibs = []
            for o in fbm_offs + fba_offs:
                nm = norm_model(o["seller-sku"])
                nm_base = re.sub(r"(\*|\bX)\d+$", "", nm)
                for k in {nm, nm_base}:
                    for s in mfn_with_stock.get(k, []):
                        if s not in sibs:
                            sibs.append(s)
            sit_a.append((asin, fba_offs, max_fba_q, fbm_offs, sibs))
            fba_s = ", ".join(f"{o['seller-sku']}(FBA={fba_by_sku.get(o['seller-sku'],0)}, ${o['price']})" for o in fba_offs)
            fbm_s = ", ".join(f"{o['seller-sku']}(FBM=0, ${o['price']})" for o in fbm_offs)
            sib_s = ", ".join(f"{s[0]}[{s[1]}]=库存{s[2]}件(${s[3]})" for s in sibs) or "全店无同型号其他有货FBM链接"
            print(f"  ASIN={asin} | FBA=[{fba_s}] | 同页0库存FBM=[{fbm_s}] | 兄弟FBM库存=[{sib_s}]")

print(f"Total Situation A ASINs: {len(sit_a)}")

print("\n=== SITUATION B: ASINS WITH ONLY FBA SKU (NO FBM SKU ON THIS ASIN) WHERE FBA > 0 OR HIGH-VALUE VC ASIN ===")
sit_b = []
for asin, offers in sorted(by_asin.items()):
    fba_offs = [o for o in offers if o["fulfillment-channel"] == "AMAZON_NA"]
    fbm_offs = [o for o in offers if o["fulfillment-channel"] == "DEFAULT"]
    if fba_offs and not fbm_offs:
        max_fba_q = max(fba_by_sku.get(o["seller-sku"], 0) for o in fba_offs)
        sibs = []
        for o in fba_offs:
            nm = norm_model(o["seller-sku"])
            nm_base = re.sub(r"(\*|\bX)\d+$", "", nm)
            for k in {nm, nm_base}:
                for s in mfn_with_stock.get(k, []):
                    if s not in sibs:
                        sibs.append(s)
        if max_fba_q > 0 or sibs:
            sit_b.append((asin, fba_offs, max_fba_q, sibs))
            fba_s = ", ".join(f"{o['seller-sku']}(FBA={fba_by_sku.get(o['seller-sku'],0)}, ${o['price']})" for o in fba_offs)
            sib_s = ", ".join(f"{s[0]}[{s[1]}]=库存{s[2]}件(${s[3]})" for s in sibs) or "全店无同型号其他有货FBM链接"
            print(f"  ASIN={asin} | FBA=[{fba_s}] | 兄弟FBM库存=[{sib_s}]")

print(f"Total Situation B ASINs (FBA>0 or has FBM sibling stock): {len(sit_b)}")
