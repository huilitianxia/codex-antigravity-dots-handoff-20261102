import openpyxl
import json
import os
import hashlib
import sys

sys.stdout.reconfigure(encoding='utf-8')

tpl_path = r"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\13-0146-office-only.xlsm"
cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
out_path = r"D:\4A\00_当前工作区_202611\14-proven-catalog-conflicts-only.xlsm"
audit_path = r"D:\4A\00_当前工作区_202611\batch14_cell_audit.json"

wb_cat = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws_cat = wb_cat['Template']
cat_rows = list(ws_cat.iter_rows(values_only=True))
h4 = cat_rows[3]
h5 = cat_rows[4]
cat_by_sku = {r[2]: r for r in cat_rows[6:] if r and len(r) > 2 and r[2]}
wb_cat.close()

# Specification of the 19 SKUs to be fixed in Batch 14:
# 5 FBA in-stock SKUs verified by Main Brain:
#   4A 039 (B01N1T23HH, FBA 12): color -> Orange&pink
#   4A 040 (B01N7IT411, FBA 5): color -> Red&pink
#   4A 037 (B01M617ZTH, FBA 2): color -> Green&yellow
#   4A 0166 (B0784GHSVJ, FBA 3): color -> White-atlantic Ocean
#   4A095 (B01M2UDADZ, MFN 719, sibling FBA 2): manufacturer -> 4A（USA）LIMITED
# 13 MFN in-stock SKUs proven SAFE_CATALOG_MATCH_PROVEN:
#   4A092, 4A PSS 9-5 NB, 4A 0153, 4A 0154, 4A 0155, 4A 0168, 4A 0169, 4A 0171, 4A 40606, 4A 5036, 4A 60238, 4A SF-60238, 4A093
# 1 MFN in-stock SKU with 99022:
#   4A GM40624*2 (color_map -> White, keeping existing color White)

# Note on column 1-based indices in Template:
# Col 3 (C): SKU
# Col 4 (D): Product Type
# Col 5 (E): Listing Action = 'Edit (Partial Update)'
# Col 12 (L): Product Id Type
# Col 13 (M): Product Id
# Col 20 (T): Manufacturer
# Col 59 (BG): Color
# Col 255 (IU): Color Map

batch14_items = [
    # 5 FBA SKUs
    {
        "sku": "4A 039",
        "reason": "FBA 12 units: align Color attribute with verified Amazon catalog value 'Orange&pink'",
        "target_updates": {59: "Orange&pink"} # Col BG
    },
    {
        "sku": "4A 040",
        "reason": "FBA 5 units: align Color attribute with verified Amazon catalog value 'Red&pink'",
        "target_updates": {59: "Red&pink"} # Col BG
    },
    {
        "sku": "4A 037",
        "reason": "FBA 2 units: align Color attribute with verified Amazon catalog value 'Green&yellow'",
        "target_updates": {59: "Green&yellow"} # Col BG
    },
    {
        "sku": "4A 0166",
        "reason": "FBA 3 units: align Color attribute with verified Amazon catalog value 'White-atlantic Ocean'",
        "target_updates": {59: "White-atlantic Ocean"} # Col BG
    },
    {
        "sku": "4A095",
        "reason": "MFN 719 units (sibling FBA 2 units): align Manufacturer with authentic company name '4A（USA）LIMITED'",
        "target_updates": {20: "4A（USA）LIMITED"} # Col T
    },
    # 13 MFN SAFE_CATALOG_MATCH_PROVEN SKUs
    {
        "sku": "4A092",
        "reason": "MFN 6 units: align Color attribute with verified Amazon catalog variation value 'Colors-s434' (SMC 434 model)",
        "target_updates": {59: "Colors-s434"} # Col BG
    },
    {
        "sku": "4A PSS 9-5 NB",
        "reason": "MFN 45 units: align standard_product_id with packaging barcode UPC 702877123140 (catalog value 00702877123140)",
        "override_id": {"id_type": "UPC", "id_val": "702877123140"},
        "target_updates": {}
    },
    {
        "sku": "4A 0153",
        "reason": "MFN 3 units: align Color attribute with verified Amazon catalog variation value 'White-tiger' (Tiger 3D note)",
        "target_updates": {59: "White-tiger"} # Col BG
    },
    {
        "sku": "4A 0154",
        "reason": "MFN 12 units: align Color attribute with verified Amazon catalog variation value 'White-havana Dog' (Havana Dog 3D note)",
        "target_updates": {59: "White-havana Dog"} # Col BG
    },
    {
        "sku": "4A 0155",
        "reason": "MFN 12 units: align Color attribute with verified Amazon catalog variation value 'White-berman Cat' (Berman Cat 3D note)",
        "target_updates": {59: "White-berman Cat"} # Col BG
    },
    {
        "sku": "4A 0168",
        "reason": "MFN 9 units: align Color attribute with verified Amazon catalog variation value \"White-risso's Dolphin\" (Risso's Dolphin 3D note)",
        "target_updates": {59: "White-risso's Dolphin"} # Col BG
    },
    {
        "sku": "4A 0169",
        "reason": "MFN 12 units: align Color attribute with verified Amazon catalog variation value 'White-japanese Bobtail' (Japanese Bobtail 3D note)",
        "target_updates": {59: "White-japanese Bobtail"} # Col BG
    },
    {
        "sku": "4A 0171",
        "reason": "MFN 9 units: align Color attribute with verified Amazon catalog variation value 'White-polar Bear' (Polar Bear 3D note)",
        "target_updates": {59: "White-polar Bear"} # Col BG
    },
    {
        "sku": "4A 40606",
        "reason": "MFN 278 units: align standard_product_id with VC packaging barcode UPC 702877120040 (catalog value 00702877120040)",
        "override_id": {"id_type": "UPC", "id_val": "702877120040"},
        "target_updates": {}
    },
    {
        "sku": "4A 5036",
        "reason": "MFN 1404 units: align Color attribute with verified Amazon catalog variation value 'Colors-heart' (Heart shape model 5036)",
        "target_updates": {59: "Colors-heart"} # Col BG
    },
    {
        "sku": "4A 60238",
        "reason": "MFN Inactive (revival candidate): align Manufacturer with authentic company name '4A（USA）LIMITED'",
        "target_updates": {20: "4A（USA）LIMITED"} # Col T
    },
    {
        "sku": "4A SF-60238",
        "reason": "MFN 381 units: align Manufacturer with authentic company name '4A（USA）LIMITED'",
        "target_updates": {20: "4A（USA）LIMITED"} # Col T
    },
    {
        "sku": "4A093",
        "reason": "MFN 419 units: align Color attribute with verified Amazon catalog variation value 'Wave' (MC 434 wave cube)",
        "target_updates": {59: "Wave"} # Col BG
    },
    # 1 MFN 99022 SKU
    {
        "sku": "4A GM40624*2",
        "reason": "MFN 747 units: resolve error 99022 by providing Color Map 'White' matching existing Color 'White'",
        "target_updates": {
            59: "White",  # Col BG (Color)
            255: "White"  # Col IU (Color Map)
        }
    }
]

print(f"Loading template workbook from {tpl_path} ...")
wb_out = openpyxl.load_workbook(tpl_path, keep_vba=True)
ws_out = wb_out['Template']

# Clear existing data rows starting from row 7 down to max_row
print(f"Clearing rows 7 to {ws_out.max_row} in Template sheet...")
for r_idx in range(7, ws_out.max_row + 1):
    for c_idx in range(1, ws_out.max_column + 1):
        ws_out.cell(r_idx, c_idx).value = None

audit_rows = []

for idx, item in enumerate(batch14_items, start=7):
    sku = item['sku']
    cr = cat_by_sku[sku]
    pt = cr[3] # Product Type from cat report
    
    # ID type and value
    if "override_id" in item:
        id_type = item["override_id"]["id_type"]
        id_val = item["override_id"]["id_val"]
    else:
        id_type = cr[11]
        id_val = cr[12]
        
    action = "Edit (Partial Update)"
    
    ws_out.cell(idx, 3).value = sku
    ws_out.cell(idx, 4).value = pt
    ws_out.cell(idx, 5).value = action
    ws_out.cell(idx, 12).value = id_type
    ws_out.cell(idx, 13).value = id_val
    
    populated = {
        "C (SKU)": sku,
        "D (Product Type)": pt,
        "E (Listing Action)": action,
        "L (Product Id Type)": id_type,
        "M (Product Id)": id_val
    }
    
    for col_1based, val in item["target_updates"].items():
        ws_out.cell(idx, col_1based).value = val
        col_letter = openpyxl.utils.get_column_letter(col_1based)
        header_name = h4[col_1based - 1]
        populated[f"{col_letter} ({header_name})"] = val
        
    audit_rows.append({
        "excel_row": idx,
        "sku": sku,
        "product_type": pt,
        "id_type": id_type,
        "product_id": id_val,
        "reason": item["reason"],
        "populated_cells": populated,
        "cell_count": len(populated)
    })

print(f"Saving new workbook to {out_path} ...")
wb_out.save(out_path)
wb_out.close()

# Step 4 verification: Re-read saved .xlsm to ensure 100% minimal cell integrity
print("Re-reading saved .xlsm for cell-by-cell verification...")
wb_ver = openpyxl.load_workbook(out_path, data_only=True)
ws_ver = wb_ver['Template']

verification_results = []
total_populated_cells = 0

for idx, expected_item in enumerate(audit_rows, start=7):
    actual_cells = {}
    for c in range(1, ws_ver.max_column + 1):
        v = ws_ver.cell(idx, c).value
        if v is not None:
            col_letter = openpyxl.utils.get_column_letter(c)
            actual_cells[f"{col_letter} ({h4[c-1]})"] = v
            
    expected_cells = expected_item["populated_cells"]
    assert actual_cells == expected_cells, f"Row {idx} mismatch: expected {expected_cells}, got {actual_cells}"
    total_populated_cells += len(actual_cells)
    verification_results.append({
        "excel_row": idx,
        "sku": expected_item["sku"],
        "expected_cell_count": len(expected_cells),
        "actual_cell_count": len(actual_cells),
        "verified": True,
        "populated_cells": actual_cells
    })

# Check that rows beyond 25 are completely empty
for r_idx in range(7 + len(batch14_items), ws_ver.max_row + 1):
    for c_idx in range(1, ws_ver.max_column + 1):
        val = ws_ver.cell(r_idx, c_idx).value
        assert val is None, f"Unexpected non-empty cell at {openpyxl.utils.get_column_letter(c_idx)}{r_idx}: {val}"

wb_ver.close()

file_bytes = open(out_path, "rb").read()
sha256_hash = hashlib.sha256(file_bytes).hexdigest()

final_audit = {
    "file_path": out_path,
    "sha256": sha256_hash,
    "file_size_bytes": len(file_bytes),
    "total_rows": len(batch14_items),
    "total_populated_cells": total_populated_cells,
    "start_row": 7,
    "end_row": 7 + len(batch14_items) - 1,
    "audit_timestamp": "2026-11-01T21:30:00Z",
    "verification_status": "PASSED_100%_MINIMAL_CELL_INTEGRITY",
    "rows": audit_rows
}

with open(audit_path, "w", encoding="utf-8") as f:
    json.dump(final_audit, f, ensure_ascii=False, indent=2)

print(f"SUCCESS: Batch 14 built and verified!")
print(f"File: {out_path}")
print(f"Rows: {len(batch14_items)} (Rows 7 to 25)")
print(f"Total populated cells: {total_populated_cells}")
print(f"SHA256: {sha256_hash}")
print(f"Audit saved to: {audit_path}")
