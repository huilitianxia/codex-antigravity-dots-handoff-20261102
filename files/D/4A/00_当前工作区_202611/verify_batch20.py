import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

file_path = r"E:\Desktop\20-all-families-clean-and-complete-fixes.xlsm"
wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
ws = wb["Template"]

rows = list(ws.iter_rows(min_row=7, values_only=True))
print(f"Total rows in template: {len(rows)}")

# 1. Check parent rows
parents = [r for r in rows if r[5] == "Parent"]
print(f"Parent rows ({len(parents)}): {[p[2] for p in parents]}")
for p in parents:
    print(f"  Parent: {p[2]} | Theme={p[7]} | Title={p[8]}")

# 2. Check the 7 previously errored SKUs
failed_7 = ["4A 5082-Y-L-GM", "4A 302-Full Adhesive-400", "4A 304 Full Glue", "4A 304-Full Adhesive-400", "AAAA 4A 304-Full Glue", "4A 305-Full Adhesive", "4A 305-Full Adhesive-300"]
for r in rows:
    sku = r[2]
    if sku in failed_7:
        print(f"\nSKU={sku:26s} | Parent={r[6]} | Theme={r[7]}")
        print(f"  Color={r[58]} | Size={r[59]}")
        print(f"  Col 317 (List Price)   = {r[317]}")
        print(f"  Col 332 (Cosmetic)     = {r[332]}")
        print(f"  Col 340 (Renewed Grade)= {r[340]}")
        print(f"  Col 347 (Your Price)   = {r[347]}")
        print(f"  Col 351 (Sale Price)   = {r[351]}")
        print(f"  Col 352 (Sale Start)   = {r[352]}")
        print(f"  Col 353 (Sale End)     = {r[353]}")
        print(f"  Col 364 (B2B Qty Thres)= {r[364]}")
        print(f"  Col 8 (Title)          = {r[8]}")

# 3. Check for any same-ASIN conflicts inside Batch 20
by_asin = {}
for r in rows:
    if r[5] != "Parent" and r[12]:
        by_asin.setdefault(str(r[12]).strip(), []).append(r)

conflicts = 0
for asin, rlist in by_asin.items():
    if len(rlist) > 1:
        p_set = set(r[6] for r in rlist)
        t_set = set(r[7] for r in rlist)
        c_set = set(r[58] for r in rlist)
        s_set = set(r[59] for r in rlist)
        if len(p_set) > 1 or len(t_set) > 1 or len(c_set) > 1 or len(s_set) > 1:
            conflicts += 1
            print(f"CONFLICT on ASIN {asin}: Parents={p_set}, Themes={t_set}, Colors={c_set}, Sizes={s_set}")

if conflicts == 0:
    print("\nSUCCESS: 0 same-ASIN conflicts in Batch 20 across all multi-SKU ASINs!")
else:
    print(f"\nWARNING: Found {conflicts} same-ASIN conflicts in Batch 20!")
