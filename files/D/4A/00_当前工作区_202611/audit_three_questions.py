import csv
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 1. Load All Listings Report (所有商品报告_11-01-2026.txt)
all_listings_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
with open(all_listings_path, "r", encoding="utf-8", errors="replace") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))

all_skus = {r["seller-sku"]: r for r in all_rows}

# 2. Load FBA Inventory Report
import glob
fba_files = sorted(glob.glob(r"D:\4A\**\*亚马逊物流库存*.csv", recursive=True) + glob.glob(r"D:\4A\**\*亚马逊物流库存*.txt", recursive=True))
fba_path = fba_files[-1] if fba_files else ""
fba_by_sku = {}
if fba_path:
    with open(fba_path, "r", encoding="utf-8-sig", errors="replace") as f:
        first_line = f.readline()
        f.seek(0)
        delim = "\t" if "\t" in first_line else ","
        fba_rows = list(csv.DictReader(f, delimiter=delim))
    fba_by_sku = {r.get("sku", ""): r for r in fba_rows}

# 3. Load 3.8's Oct 30 TSV (4A_全店21大家族精细化变体清洗_终极纯净版_V2.tsv)
tsv_path = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\4A_全店21大家族精细化变体清洗_终极纯净版_V2.tsv"
with open(tsv_path, "r", encoding="utf-8", errors="replace") as f:
    tsv_rows = [l.rstrip("\r\n").split("\t") for l in f][6:]

drafts = []
fake_titles = []
for r in tsv_rows:
    if len(r) > 12 and r[1]:
        sku = r[1]
        title = r[7]
        asin = r[11]
        parent = r[5]
        if title.startswith("4A Self-Stick Notes,"):
            fake_titles.append((sku, asin, parent, title, sku in all_skus))
        if not sku.startswith("PARENT-") and sku not in all_skus:
            drafts.append((sku, asin, parent, title))

print(f"=== Q2: 3.8 OCT 30 TSV DRAFTS (补全草稿 101 / 缺少的信息) ===")
print(f"Total non-parent SKUs in 3.8 TSV that are NOT in All Listings Report (became 补全草稿 Drafts): {len(drafts)}")
print(f"Total rows in 3.8 TSV with 3.8's fake title '4A Self-Stick Notes, ...': {len(fake_titles)}")
in_fba_drafts = [d for d in drafts if d[0] in fba_by_sku and int(fba_by_sku[d[0]].get("afn-fulfillable-quantity") or 0) > 0]
print(f"Drafts that actually have FBA Fulfillable > 0: {len(in_fba_drafts)}")
for d in drafts:
    print(f"  Draft SKU={d[0]:25s} | ASIN={d[1]:12s} | Parent={d[2]:30s} | Title={d[3][:55]}")

# 4. Check Q1: MFN Shipping Template distribution across all active MFN SKUs (Qty > 0)
print("\n=== Q1: ALL ACTIVE MFN SKUS (Qty > 0) BY SHIPPING TEMPLATE ===")
mfn_active = [r for r in all_rows if r.get("fulfillment-channel") == "DEFAULT" and int(r.get("quantity") or 0) > 0]
tpl_groups = {}
for r in mfn_active:
    tpl = r.get("merchant-shipping-group") or "Migrated Template"
    tpl_groups.setdefault(tpl, []).append(r)

print(f"Total MFN SKUs with Qty > 0: {len(mfn_active)} (Total Units: {sum(int(r['quantity']) for r in mfn_active):,})")
for tpl, items in sorted(tpl_groups.items(), key=lambda x: -len(x[1])):
    units = sum(int(i["quantity"]) for i in items)
    print(f"  - Template '{tpl}': {len(items)} SKUs | {units:,} units")
    for i in items[:8]:
        print(f"      {i['seller-sku']:24s} | ASIN={i['asin1']:12s} | Qty={i['quantity']:6s} | Price=${i['price']}")

# 5. Check Q3: Why 406x6 and 5082 look 'unavailable' on the front-end
print("\n=== Q3: EXACT STATUS & INVENTORY OF ALL 406x6 AND 5082 ASINS/SKUS ===")
for kw in ["406x6", "5082", "303x12", "301x12"]:
    print(f"\n--- Keyword: {kw} ---")
    for r in all_rows:
        sku = r["seller-sku"]
        if kw in sku.lower():
            fba_info = fba_by_sku.get(sku, {})
            fba_qty = fba_info.get("afn-fulfillable-quantity", "N/A")
            fba_tot = fba_info.get("afn-total-quantity", "N/A")
            print(
                f"  SKU={sku:24s} | ASIN={r['asin1']:12s} | Status={r['status']:10s} | "
                f"Chan={r['fulfillment-channel']:10s} | MFN_Qty={r['quantity']:6s} | "
                f"FBA_Fulfill={str(fba_qty):5s} (Total={str(fba_tot):5s}) | Price=${r['price']}"
            )
