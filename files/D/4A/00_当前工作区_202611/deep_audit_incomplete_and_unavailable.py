import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

all_listings_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
with open(all_listings_path, "r", encoding="utf-8", errors="replace") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))

# 1. Analyze all 129 'Incomplete' rows in 所有商品报告_11-01-2026.txt
inc_rows = [r for r in all_rows if r.get("status") == "Incomplete"]
print(f"=== 1. INCOMPLETE ROWS IN 所有商品报告_11-01-2026.txt: {len(inc_rows)} ===")
inc_mfn_with_qty = [r for r in inc_rows if r.get("fulfillment-channel") == "DEFAULT" and int(r.get("quantity") or 0) > 0]
inc_mfn_zero_qty = [r for r in inc_rows if r.get("fulfillment-channel") == "DEFAULT" and int(r.get("quantity") or 0) == 0]
inc_fba = [r for r in inc_rows if r.get("fulfillment-channel") != "DEFAULT"]
print(f"  - MFN Incomplete with Qty > 0: {len(inc_mfn_with_qty)}")
for r in inc_mfn_with_qty:
    print(f"    SKU={r['seller-sku']:25s} | ASIN={r['asin1']:12s} | Qty={r['quantity']:6s} | Price={r['price']:7s} | OpenDate={r['open-date']}")
print(f"  - MFN Incomplete with Qty == 0: {len(inc_mfn_zero_qty)}")
print(f"  - FBA Incomplete: {len(inc_fba)}")
for r in inc_fba[:25]:
    print(f"    SKU={r['seller-sku']:25s} | ASIN={r['asin1']:12s} | Price={r['price']:7s} | OpenDate={r['open-date']}")

# 2. Check 3.8's Oct 30 TSV (4A_全店21大家族精细化变体清洗_终极纯净版_V2.tsv) vs 所有商品报告
tsv_path = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\4A_全店21大家族精细化变体清洗_终极纯净版_V2.tsv"
with open(tsv_path, "r", encoding="utf-8", errors="replace") as f:
    tsv_lines = [line.rstrip("\r\n").split("\t") for line in f]

all_skus_in_report = {r["seller-sku"] for r in all_rows}
tsv_skus_not_in_report = []
for row in tsv_lines[3:]:
    if len(row) > 1 and row[0]:
        sku = row[0]
        if sku not in all_skus_in_report and not sku.startswith("PARENT-"):
            tsv_skus_not_in_report.append((sku, row[2] if len(row) > 2 else "", row[3] if len(row) > 3 else "", row[7] if len(row) > 7 else ""))

print(f"\n=== 2. SKUs IN 3.8's OCT 30 TSV THAT ARE NOT IN 所有商品报告 (became 补全草稿 Drafts with ASIN='-'): {len(tsv_skus_not_in_report)} ===")
for sku, pid, ptype, parent in tsv_skus_not_in_report[:35]:
    print(f"  Draft SKU={sku:25s} | TSV_ProductID={pid:14s} | IDType={ptype:6s} | Parent={parent}")

# 3. Check all children of PARENT-4A-406-MEDIUM-PADS and PARENT-4A-508-LARGE-5X8
cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
cat_rows = list(ws.iter_rows(values_only=True))

report_by_sku = {r["seller-sku"]: r for r in all_rows}

print("\n=== 3. ALL CHILDREN OF PARENT-4A-406-MEDIUM-PADS & PARENT-4A-508-LARGE-5X8 ===")
for r in cat_rows[6:]:
    if not r or len(r) < 60:
        continue
    sku = str(r[2] or "")
    parent = str(r[6] or "")
    if parent in ("PARENT-4A-406-MEDIUM-PADS", "PARENT-4A-508-LARGE-5X8") or any(k in sku.lower() for k in ["406", "508"]):
        rep = report_by_sku.get(sku, {})
        print(
            f"Parent={parent:26s} | SKU={sku:22s} | ASIN={str(r[12]):12s} | RepStatus={rep.get('status','N/A'):10s} | "
            f"Chan={rep.get('fulfillment-channel','N/A'):9s} | Qty={rep.get('quantity',''):5s} | "
            f"Color={str(r[58]):20s} | Size={str(r[59]):26s} | ShipTpl={str(r[372])}"
        )
