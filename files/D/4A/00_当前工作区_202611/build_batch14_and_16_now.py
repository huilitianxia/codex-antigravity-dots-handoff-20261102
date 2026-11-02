import openpyxl
import zipfile
import xml.etree.ElementTree as ET
import shutil
import hashlib
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

SRC_XLSM = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
WORK_DIR = r"D:\4A\00_当前工作区_202611"
DESKTOP_DIR = r"E:\Desktop"

# Load source workbook once with data_only=True to read all rows
wb_src = openpyxl.load_workbook(SRC_XLSM, data_only=True)
ws_src = wb_src['Template']

max_col = ws_src.max_column
sku_to_row = {}
for r in range(7, ws_src.max_row + 1):
    s = ws_src.cell(r, 3).value
    if s:
        sku_to_row[str(s).strip()] = r

def extract_row_values(r):
    return [ws_src.cell(r, c).value for c in range(1, max_col + 1)]

# ==============================================================================
# 1. BUILD BATCH 14: 14-proven-catalog-conflicts-only.xlsm (19 SKUs)
# ==============================================================================
# 0-based indices in Template:
# Col 2 (C): SKU
# Col 3 (D): Product Type
# Col 4 (E): Listing Action -> 'Edit (Partial Update)'
# Col 11 (L): Product Id Type
# Col 12 (M): Product Id
# Col 19 (T): Manufacturer
# Col 58 (BG): Color
# Col 254 (IU): Color Map

batch14_specs = [
    # 5 FBA in-stock SKUs (3,115 units)
    {"sku": "4A 039", "mfg": "4A", "color": "5 Colors", "colormap": "Multicolor", "note": "FBA 1073u: match catalog Mfg='4A', Color='5 Colors'"},
    {"sku": "4A 040", "mfg": "4A", "color": "Bright", "colormap": "Multicolor", "note": "FBA 917u: match catalog Mfg='4A', Color='Bright'"},
    {"sku": "4A 037", "color": "Bright Colors", "colormap": "Multicolor", "note": "FBA 553u: match catalog Color='Bright Colors'"},
    {"sku": "4A 0166", "mfg": "4A", "color": "White-polar Bear", "colormap": "White", "note": "FBA 549u: match catalog Mfg='4A', Color='White-polar Bear'"},
    {"sku": "4A095", "mfg": "4A（USA）LIMITED", "color": "Assorted Colors", "colormap": "Multicolor", "note": "FBA 23u: match catalog Mfg='4A（USA）LIMITED', Color='Assorted Colors'"},
    # 13 MFN SAFE_CATALOG_MATCH_PROVEN SKUs (173 units)
    {"sku": "4A092", "color": "Colors-s434", "colormap": "Multicolor", "note": "MFN 6u: match catalog Color='Colors-s434'"},
    {"sku": "4A PSS 9-5 NB", "pid_type": "UPC", "pid": "702877123140", "colormap": "Multicolor", "note": "MFN 45u: match physical barcode & catalog UPC 702877123140 (00702877123140)"},
    {"sku": "4A 0153", "color": "White-tiger", "colormap": "White", "note": "MFN 3u: match catalog Color='White-tiger'"},
    {"sku": "4A 0154", "color": "White-havana Dog", "colormap": "White", "note": "MFN 12u: match catalog Color='White-havana Dog'"},
    {"sku": "4A 0155", "color": "White-berman Cat", "colormap": "White", "note": "MFN 12u: match catalog Color='White-berman Cat'"},
    {"sku": "4A 0168", "color": "White-risso's Dolphin", "colormap": "White", "note": "MFN 15u: match catalog Color=\"White-risso's Dolphin\""},
    {"sku": "4A 0169", "color": "White-japanese Bobtail", "colormap": "White", "note": "MFN 15u: match catalog Color='White-japanese Bobtail'"},
    {"sku": "4A 0171", "color": "White-polar Bear", "colormap": "White", "note": "MFN 10u: match catalog Color='White-polar Bear'"},
    {"sku": "4A 40606", "pid_type": "UPC", "pid": "702877120040", "colormap": "Multicolor", "note": "MFN 15u: match physical barcode & catalog UPC 702877120040 (00702877120040)"},
    {"sku": "4A 5036", "color": "Colors-heart", "colormap": "Multicolor", "note": "MFN 10u: match catalog Color='Colors-heart'"},
    {"sku": "4A 60238", "mfg": "4A（USA）LIMITED", "colormap": "Multicolor", "note": "MFN 5u: match catalog Mfg='4A（USA）LIMITED'"},
    {"sku": "4A SF-60238", "mfg": "4A（USA）LIMITED", "colormap": "Multicolor", "note": "MFN 5u: match catalog Mfg='4A（USA）LIMITED'"},
    {"sku": "4A093", "color": "Wave", "colormap": "Multicolor", "note": "MFN 20u (419 in report): match catalog Color='Wave'"},
    # 1 MFN 99022 Missing Color Map SKU (52 units)
    {"sku": "4A GM40624*2", "color": "White", "colormap": "White", "note": "MFN 52u: populate missing Color Map='White' for 99022 fix"},
]

def build_xlsm_from_rows(out_path, row_dicts, audit_json_path):
    wb = openpyxl.load_workbook(SRC_XLSM, keep_vba=True)
    ws = wb['Template']
    # Clear rows 7..max_row
    for r in range(7, ws.max_row + 1):
        for c in range(1, max_col + 1):
            ws.cell(r, c).value = None
    audit_records = []
    for idx, item in enumerate(row_dicts):
        target_r = 7 + idx
        vals = item["vals"]
        for c_idx, v in enumerate(vals):
            ws.cell(target_r, c_idx + 1).value = v
        audit_records.append(item["audit"])
    wb.save(out_path)
    with open(audit_json_path, "w", encoding="utf-8") as f:
        json.dump(audit_records, f, ensure_ascii=False, indent=2)
    return audit_records

batch14_rows = []
for spec in batch14_specs:
    sku = spec["sku"]
    src_r = sku_to_row[sku]
    vals = extract_row_values(src_r)
    before = {
        "action": vals[4],
        "pid_type": vals[11],
        "pid": vals[12],
        "mfg": vals[19],
        "color": vals[58],
        "size": vals[59],
        "colormap": vals[254],
    }
    vals[4] = "Edit (Partial Update)"
    if "pid_type" in spec:
        vals[11] = spec["pid_type"]
    if "pid" in spec:
        vals[12] = spec["pid"]
    if "mfg" in spec:
        vals[19] = spec["mfg"]
    if "color" in spec:
        vals[58] = spec["color"]
    if "colormap" in spec:
        vals[254] = spec["colormap"]
    after = {
        "action": vals[4],
        "pid_type": vals[11],
        "pid": vals[12],
        "mfg": vals[19],
        "color": vals[58],
        "size": vals[59],
        "colormap": vals[254],
    }
    batch14_rows.append({
        "vals": vals,
        "audit": {
            "sku": sku,
            "source_row": src_r,
            "product_type": vals[3],
            "note": spec["note"],
            "before": before,
            "after": after
        }
    })

b14_work = os.path.join(WORK_DIR, "14-proven-catalog-conflicts-only.xlsm")
b14_audit = os.path.join(WORK_DIR, "batch14_cell_audit.json")
b14_desk = os.path.join(DESKTOP_DIR, "14-proven-catalog-conflicts-only.xlsm")
build_xlsm_from_rows(b14_work, batch14_rows, b14_audit)
shutil.copy2(b14_work, b14_desk)
b14_sha = hashlib.sha256(open(b14_work, "rb").read()).hexdigest()
print(f"Batch 14 built & copied to Desktop! Rows={len(batch14_rows)}, SHA256={b14_sha}")

# ==============================================================================
# 2. BUILD BATCH 16: 16-family-misplaced-and-orphan-fixes.xlsm (13 SKUs)
# ==============================================================================
# Surgical family corrections:
# A) Move Giant Meeting / Easel Pads (BP 1111, BP 1515, BP 2222) out of 303 (3x3 in)
#    and 301 (1.5x2 in) into PARENT-4A-BIGPAD-MEETING-EASEL, unifying Size across FBA/MFN pairs.
# B) Unify Size on single-pad BP1111 / BP1515 / BP2222 pairs in PARENT-4A-BIGPAD-MEETING-EASEL
#    so FBA & MFN offers on the same ASIN don't conflict.

batch16_specs = [
    # 4-Pad Giant Meeting Pads moved out of 303 / 301 into PARENT-4A-BIGPAD-MEETING-EASEL
    {"sku": "4A BP 1111-Nx4",   "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Bright Ultra Colors", "colormap": "Multicolor", "size": "11 x 11 in (4 Pads)", "note": "Move 11x11 in Big Pad out of 3x3 303 family into BIGPAD family"},
    {"sku": "4A GMBP 1111-Nx4", "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Bright Ultra Colors", "colormap": "Multicolor", "size": "11 x 11 in (4 Pads)", "note": "Move 11x11 in Big Pad (839u) out of 3x3 303 family into BIGPAD family"},
    {"sku": "4A BP 1111-Px4",   "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Pastel Assorted",     "colormap": "Multicolor", "size": "11 x 11 in (4 Pads)", "note": "Move 11x11 in Pastel Big Pad out of 3x3 303 family into BIGPAD family"},
    {"sku": "4A GMBP 1111-Px4", "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Pastel Assorted",     "colormap": "Multicolor", "size": "11 x 11 in (4 Pads)", "note": "Move 11x11 in Pastel Big Pad (1010u) out of 3x3 303 family into BIGPAD family"},
    {"sku": "4A BP 1515-Nx4",   "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Bright Ultra Colors", "colormap": "Multicolor", "size": "15 x 15 in (4 Pads)", "note": "Move 15x15 in Giant Pad out of 3x3 303 family into BIGPAD family"},
    {"sku": "4A GMBP 1515-Nx4", "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Bright Ultra Colors", "colormap": "Multicolor", "size": "15 x 15 in (4 Pads)", "note": "Move 15x15 in Giant Pad (461u) out of 3x3 303 family into BIGPAD family"},
    {"sku": "4A BP 2222-Nx4",   "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Bright Ultra Colors", "colormap": "Multicolor", "size": "22 x 22 in (4 Pads)", "note": "Move 22x22 in Giant Easel Pad (19 FBA) out of 1.5x2 301 mini family into BIGPAD family"},
    {"sku": "4A GMBP 2222-Nx4", "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Bright Ultra Colors", "colormap": "Multicolor", "size": "22 x 22 in (4 Pads)", "note": "Move 22x22 in Giant Easel Pad (393 MFN) out of 1.5x2 301 mini family into BIGPAD family"},
    # 1-Pad Giant Meeting Pads already in PARENT-4A-BIGPAD-MEETING-EASEL: remove conflicting (Pack N) suffixes across same-ASIN pairs
    {"sku": "4A BP1111 BL",      "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Pastel Assorted", "colormap": "Multicolor", "size": "11 x 11 in (1 Pad)", "note": "Clean fake (Pack 4) suffix on B01N6LJNW4"},
    {"sku": "4A BP1111 BLx3",    "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Pastel Assorted", "colormap": "Multicolor", "size": "11 x 11 in (1 Pad)", "note": "Align same-ASIN B01N6LJNW4 size"},
    {"sku": "4A BP1515 NGORY",   "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Neon Assorted",   "colormap": "Multicolor", "size": "15 x 15 in (1 Pad)", "note": "Clean fake (Pack 4) suffix on B07MK2Z3VK"},
    {"sku": "4A GMBP1515 NGORY", "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Neon Assorted",   "colormap": "Multicolor", "size": "15 x 15 in (1 Pad)", "note": "Clean conflicting (Pack 5) suffix on same-ASIN B07MK2Z3VK"},
    {"sku": "4A BP2222 NGPOY",   "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Neon Assorted",   "colormap": "Multicolor", "size": "22 x 22 in (1 Pad)", "note": "Set clean 22 x 22 in (1 Pad) size on B07M854GPK"},
    {"sku": "4A GMBP2222 NGPOY", "parent": "PARENT-4A-BIGPAD-MEETING-EASEL", "theme": "COLOR/SIZE", "color": "Neon Assorted",   "colormap": "Multicolor", "size": "22 x 22 in (1 Pad)", "note": "Clean conflicting (Pack 3) suffix on same-ASIN B07M854GPK"},
]

batch16_rows = []
for spec in batch16_specs:
    sku = spec["sku"]
    src_r = sku_to_row[sku]
    vals = extract_row_values(src_r)
    before = {
        "parent": vals[6],
        "theme": vals[7],
        "color": vals[58],
        "size": vals[59],
        "colormap": vals[254],
    }
    vals[4] = "Edit (Partial Update)"
    vals[5] = "Child"
    vals[6] = spec["parent"]
    vals[7] = spec["theme"]
    vals[58] = spec["color"]
    vals[59] = spec["size"]
    vals[254] = spec["colormap"]
    after = {
        "parent": vals[6],
        "theme": vals[7],
        "color": vals[58],
        "size": vals[59],
        "colormap": vals[254],
    }
    batch16_rows.append({
        "vals": vals,
        "audit": {
            "sku": sku,
            "source_row": src_r,
            "asin": vals[12],
            "note": spec["note"],
            "before": before,
            "after": after
        }
    })

b16_work = os.path.join(WORK_DIR, "16-family-misplaced-and-orphan-fixes.xlsm")
b16_audit = os.path.join(WORK_DIR, "batch16_cell_audit.json")
b16_desk = os.path.join(DESKTOP_DIR, "16-family-misplaced-and-orphan-fixes.xlsm")
build_xlsm_from_rows(b16_work, batch16_rows, b16_audit)
shutil.copy2(b16_work, b16_desk)
b16_sha = hashlib.sha256(open(b16_work, "rb").read()).hexdigest()
print(f"Batch 16 built & copied to Desktop! Rows={len(batch16_rows)}, SHA256={b16_sha}")
