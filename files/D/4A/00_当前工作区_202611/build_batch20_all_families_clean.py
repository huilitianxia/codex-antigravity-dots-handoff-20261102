import csv
import openpyxl
import shutil
import hashlib
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
all_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
fba_path = r"D:\下载文件\284701020757.txt"
master_path = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"

work_out = r"D:\4A\00_当前工作区_202611\20-all-families-clean-and-complete-fixes.xlsm"
desktop_out = r"E:\Desktop\20-all-families-clean-and-complete-fixes.xlsm"

# 1. Load data
with open(all_path, "r", encoding="utf-8", errors="ignore") as f:
    all_by_sku = {r["seller-sku"]: r for r in csv.DictReader(f, delimiter="\t")}

fba_by_sku = {}
with open(fba_path, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fba_by_sku[r["sku"]] = int(r.get("available") or 0) + int(r.get("fc-transfer") or 0)

wb_cat = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws_cat = wb_cat["Template"]
cat_rows = list(ws_cat.iter_rows(min_row=7, values_only=True))
wb_cat.close()

cat_by_sku = {}
for r in cat_rows:
    if r and len(r) > 2 and r[2]:
        cat_by_sku[str(r[2]).strip()] = list(r)

# Verify correct column indices:
# 317: List Price
# 347: Your Price
# 351: Sale Price
# 352: Sale From Date
# 353: Sale End Date
# 372: Shipping Template
# 374, 376, 378, 380, 382, 384: Dimension Units (must be 'Inches')
# 385, 386: Package Weight, Package Weight Unit ('Pounds')

full_adhesive_b1 = (
    "HOW TO PEEL FLAT (NO CURLING): Because the entire back is coated with edge-to-edge full adhesive, "
    "always peel horizontally from side-to-side along the edge rather than pulling straight up from the bottom."
)
full_adhesive_b2 = (
    "EDGE-TO-EDGE FULL ADHESIVE HOLD: Full-back adhesive coverage grips monitors, walls, doors, books, "
    "and vertical surfaces firmly without corners lifting or falling off."
)
roll_tape_b1 = (
    "HOW TO THREAD & CUT CLEANLY: Pull the full-adhesive paper tape under the front guide bar and tear "
    "downward at a 45-degree angle against the built-in cutter blade for a clean, straight edge every time."
)
roll_tape_b2 = (
    "CUSTOM-LENGTH FULL ADHESIVE ROLL: Cut any length you need for labeling, indexing, or covering text—"
    "100% full-back adhesive sticks flat without curling and removes cleanly without residue."
)

# 2. Build rows for Batch 20
rows = []

# Part A: Parents that require updates
# Update PARENT-4A-4012-4013-PPBOX and PARENT-4A-8065-8088-SPECTRUM-24 to COLOR/SIZE
for p_sku in ["PARENT-4A-4012-4013-PPBOX", "PARENT-4A-8065-8088-SPECTRUM-24"]:
    r = list(cat_by_sku[p_sku])
    r[4] = "Edit (Partial Update)"
    r[5] = "Parent"
    r[6] = None
    r[7] = "COLOR/SIZE"
    r[9] = None
    r[10] = "4A"
    rows.append(r)

# Part B: The 7 Failed Rows from Batch 19 (fixed columns)
batch19_fixes = {
    "4A 5082-Y-L-GM": {
        "p_sku": "PARENT-4A-508-LARGE-5X8", "theme": "COLOR/SIZE", "c": "Canary Yellow", "s": "2 Pads Lined (5 x 8 in, 100 Sheets/Pad)",
        "items": 2, "box": 1, "list_p": 10.99, "price": 10.99, "sale_p": None, "ship": "Migrated Template"
    },
    "4A 302-Full Adhesive-400": {
        "p_sku": "PARENT-4A-FULL-ADHESIVE-PADS", "theme": "COLOR/SIZE", "c": "Bright Ultra Colors", "s": "2 x 3 in (400 Sheets Total)",
        "b1": full_adhesive_b1, "b2": full_adhesive_b2, "list_p": 9.99, "price": 9.99, "sale_p": 9.49
    },
    "4A 304 Full Glue": {
        "p_sku": "PARENT-4A-FULL-ADHESIVE-PADS", "theme": "COLOR/SIZE", "c": "Classic Assorted", "s": "3 x 4 in (100 Sheets)",
        "b1": full_adhesive_b1, "b2": full_adhesive_b2, "list_p": 9.99, "price": 9.99, "sale_p": 9.49
    },
    "4A 304-Full Adhesive-400": {
        "p_sku": "PARENT-4A-FULL-ADHESIVE-PADS", "theme": "COLOR/SIZE", "c": "Bright Ultra Colors", "s": "3 x 4 in (400 Sheets Total)",
        "b1": full_adhesive_b1, "b2": full_adhesive_b2, "list_p": 9.99, "price": 9.99, "sale_p": 9.49
    },
    "AAAA 4A 304-Full Glue": {
        "p_sku": "PARENT-4A-FULL-ADHESIVE-PADS", "theme": "COLOR/SIZE", "c": "Bright Ultra Colors", "s": "3 x 4 in (10 Pads, 500 Sheets)",
        "b1": full_adhesive_b1, "b2": full_adhesive_b2, "list_p": 8.99, "price": 8.99, "sale_p": 8.54
    },
    "4A 305-Full Adhesive": {
        "p_sku": "PARENT-4A-FULL-ADHESIVE-PADS", "theme": "COLOR/SIZE", "c": "Bright Ultra Colors", "s": "3 x 5 in (5 Pads, 500 Sheets)",
        "b1": full_adhesive_b1, "b2": full_adhesive_b2, "list_p": 9.99, "price": 9.99, "sale_p": 9.49
    },
    "4A 305-Full Adhesive-300": {
        "p_sku": "PARENT-4A-FULL-ADHESIVE-PADS", "theme": "COLOR/SIZE", "c": "Bright Ultra Colors", "s": "3 x 5 in (300 Sheets Total)",
        "b1": full_adhesive_b1, "b2": full_adhesive_b2, "list_p": 9.99, "price": 9.99, "sale_p": 9.49
    },
}

for sku, d in batch19_fixes.items():
    r = list(cat_by_sku[sku])
    r[4] = "Edit (Partial Update)"
    r[5] = "Child"
    r[6] = d["p_sku"]
    r[7] = d["theme"]
    r[8] = None  # Do NOT touch title, avoid 100476
    r[9] = None
    r[10] = "4A"
    if "b1" in d: r[44] = d["b1"]
    if "b2" in d: r[45] = d["b2"]
    if "items" in d: r[56] = d["items"]
    if "box" in d: r[57] = d["box"]
    r[58] = d["c"]
    r[59] = d["s"]
    r[317] = d.get("list_p")
    r[347] = d.get("price")
    r[351] = d.get("sale_p")
    if d.get("sale_p"):
        r[352] = "2026-11-01"
        r[353] = "2026-12-31"
    else:
        r[352] = None
        r[353] = None
    r[332] = None
    r[340] = None
    r[356] = d.get("price")
    r[364] = None
    r[365] = None
    r[366] = None
    if "ship" in d: r[372] = d["ship"]
    for u_col in (374, 376, 378, 380, 382, 384):
        if r[u_col] == "IN": r[u_col] = "Inches"
    rows.append(r)

# Part C: The other 35 rows from Batch 19 that weren't in the user's 38-row upload
batch19_remaining_skus = [
    # Full Adhesive & Roll Tape VOC
    "4A 303-Full Adhesive-400", "4A GM303-Full Adhesive-400", "4A 303-Full Adhesive", "4A GM304-Full Adhesive-400",
    "4A GM305-Full Adhesive-300", "4A SCPSS 32x6", "4A GM-SCPSS 32x6", "4A PSS 32x6",
    # 406x6 Unification & Package Weight
    "4A 033", "4A 406x6", "4A 034", "4A 406x6-N", "4A GM406x6-N", "AAAA 4A 406x6-N", "4A GM406x6-N*2", "4A 406x6-N*2",
    # Expired Stop Selling Dates & Missing Shipping Templates
    "4A 003", "4A GM302-Full Glue*3", "4A GM30512-L", "4A GM5088-N-L",
    # Big Pads Eviction from 303
    "4A BP 1111-Nx4", "4A GMBP 1111-Nx4", "4A BP 1111-Px4", "4A GMBP 1111-Px4", "4A BP 1515-Nx4", "4A GMBP 1515-Nx4",
    # Novelty & Folio Eviction from 303
    "4A 8667", "AAAA 4A 8667+ 8666", "AAAA 4A 8665+8666", "4A 0126", "4A 8663", "4A GM8663", "4A 0127", "4A 8664",
    "4A 0128", "4A 0129", "4A 0130", "4A SCGM70001x8",
    # Dividers Eviction from 303/406
    "4A073", "4A 40607",
    # 303 Active Clean Buttons
    "4A 010", "4A 303 x 6-N-L", "AAAA 4A 303x6-N-L", "4A GMSC303x6-B", "4A SC303x6-B",
    "4A 018", "4A 303 x12-Z", "4A 019", "4A 303 x12-N-Z", "4A ST303X12NZ",
    "4A GM303x18-Y", "4A GM303x6-Y-L*3", "4A 303S-20", "4A GM303S-20",
    "4A GM303Sx12*2", "4A 194", "4A 303Sx12"
]

seen_skus = set(r[2] for r in rows)

# Import specs from rebuild_batch19_clean.py
from rebuild_batch19_clean import evict_to_bigpad, evict_to_novelty, evict_to_markers, clean_303_active

for sku in batch19_remaining_skus:
    if sku in seen_skus or sku not in cat_by_sku:
        continue
    r = list(cat_by_sku[sku])
    r[4] = "Edit (Partial Update)"
    r[5] = "Child"
    r[8] = None  # preserve existing title, avoid 100476
    r[9] = None
    r[10] = "4A"
    r[332] = None
    r[340] = None
    r[364] = None
    r[365] = None
    r[366] = None
    for u_col in (374, 376, 378, 380, 382, 384):
        if r[u_col] == "IN": r[u_col] = "Inches"

    if sku in ("4A 303-Full Adhesive-400", "4A GM303-Full Adhesive-400", "4A 303-Full Adhesive", "4A GM304-Full Adhesive-400", "4A GM305-Full Adhesive-300"):
        r[6] = "PARENT-4A-FULL-ADHESIVE-PADS"
        r[7] = "COLOR/SIZE"
        r[44] = full_adhesive_b1
        r[45] = full_adhesive_b2
        if "303" in sku: r[59] = "3 x 3 in (400 Sheets Total)"
        elif "304" in sku: r[59] = "3 x 4 in (400 Sheets Total)"
        elif "305" in sku: r[59] = "3 x 5 in (300 Sheets Total)"
    elif sku in ("4A SCPSS 32x6", "4A GM-SCPSS 32x6", "4A PSS 32x6"):
        r[6] = "PARENT-4A-PSS-ROLL-TAPE"
        r[7] = "COLOR/SIZE"
        r[44] = roll_tape_b1
        r[45] = roll_tape_b2
        r[58] = "Neon Assorted"
        r[59] = "Tape Roll with Dispenser (2.5 in x 26 ft)"
    elif sku in ("4A 033", "4A 406x6", "4A 034", "4A 406x6-N", "4A GM406x6-N", "AAAA 4A 406x6-N"):
        r[6] = "PARENT-4A-406-MEDIUM-PADS"
        r[7] = "COLOR/SIZE"
        if sku in ("4A 033", "4A 406x6"):
            r[58] = "Pastel Assorted"
            if sku == "4A 033": r[372] = "Migrated Template"
        elif sku in ("4A 034", "4A 406x6-N"):
            r[58] = "Neon Assorted"
            if sku == "4A 034": r[372] = "Migrated Template"
        else:
            r[58] = "Bright Ultra Colors"
            if sku == "4A GM406x6-N": r[372] = "Migrated Template"
        r[59] = "6 Pads Unlined (4 x 6 in)"
        r[379], r[380] = 6.0, "Inches"
        r[381], r[382] = 4.0, "Inches"
        r[383], r[384] = 2.35, "Inches"
        r[385], r[386] = 1.4, "Pounds"
    elif sku in ("4A GM406x6-N*2", "4A 406x6-N*2"):
        r[6] = "PARENT-4A-406-MEDIUM-PADS"
        r[7] = "COLOR/SIZE"
        r[58] = "Bright Ultra Colors"
        r[59] = "12 Pads Unlined (2 Packs of 6, 4 x 6 in)"
        r[379], r[380] = 6.0, "Inches"
        r[381], r[382] = 4.7, "Inches"
        r[383], r[384] = 4.0, "Inches"
        r[385], r[386] = 2.8, "Pounds"
        if sku == "4A GM406x6-N*2": r[372] = "Cube delivery"
    elif sku in ("4A 003", "4A GM302-Full Glue*3"):
        r[355] = "2099-12-31T00:00:00.000Z"
        r[372] = "Migrated Template"
    elif sku in ("4A GM30512-L", "4A GM5088-N-L"):
        r[372] = "Big size delivery"
    elif sku in evict_to_bigpad:
        r[6] = "PARENT-4A-BIGPAD-MEETING-EASEL"
        r[7] = "COLOR/SIZE"
        r[58], r[59] = evict_to_bigpad[sku]
        if sku in ("4A GMBP 1111-Nx4", "4A GMBP 1111-Px4"): r[372] = "Big size delivery"
    elif sku in evict_to_novelty:
        r[6] = "PARENT-4A-SHAPED-NOVELTY-PADS"
        r[7] = "COLOR/SIZE"
        r[58], r[59] = evict_to_novelty[sku]
    elif sku in evict_to_markers:
        r[6] = "PARENT-4A-PAPER-PAGE-MARKERS"
        r[7] = "COLOR/SIZE"
        r[58], r[59] = evict_to_markers[sku]
    elif sku in clean_303_active:
        r[6] = "PARENT-4A-303-CLASSIC-SQUARE"
        r[7] = "COLOR/SIZE"
        r[58], r[59] = clean_303_active[sku]
        if sku == "4A GM303S-20": r[372] = "Cube delivery"

    rows.append(r)
    seen_skus.add(sku)

# Part D: Additional Cross-Family & Button Cleanups across all 21 Families
# Let's add all active / sibling SKUs in the other families that had split-parent or messy (Pack X) buttons!
extra_cleanups = {
    # 4A 4012 & 4013 PP Box (now COLOR/SIZE)
    "4A 4012-B07T-FBA": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Classic Assorted", "1 Box (18 Pads)"),
    "4A GM4012": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Classic Assorted", "1 Box (18 Pads)"),
    "AAAA 4A 4012": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Classic Assorted", "1 Box (18 Pads)"),
    "4A 4012": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Classic Assorted", "2 Boxes (36 Pads)"),
    "4A GM4012*2": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Classic Assorted", "2 Boxes (36 Pads)"),
    "4A050": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Classic Assorted", "2 Boxes (36 Pads)"),
    "4A 4013": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Neon Assorted", "1 Box (18 Pads)"),
    "4A GM4013": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Neon Assorted", "1 Box (18 Pads)"),
    "4A4013-B07T-FBA": ("PARENT-4A-4012-4013-PPBOX", "COLOR/SIZE", "Neon Assorted", "1 Box (18 Pads)"),

    # 30315 Rainbow (clean button names)
    "4A 30315": ("PARENT-4A-30315-RAINBOW-15", "COLOR/SIZE", "15-Color Rainbow", "15 Pads Standard (3 x 3 in)"),
    "4A GM30315": ("PARENT-4A-30315-RAINBOW-15", "COLOR/SIZE", "15-Color Rainbow", "15 Pads Standard (3 x 3 in)"),
    "4A 30315-Z": ("PARENT-4A-30315-RAINBOW-15", "COLOR/SIZE", "15-Color Rainbow", "15 Pads Pop-Up (3 x 3 in)"),
    "4A GM30315-Z": ("PARENT-4A-30315-RAINBOW-15", "COLOR/SIZE", "15-Color Rainbow", "15 Pads Pop-Up (3 x 3 in)"),

    # 508 Large 5x8
    "4A 5084-N-L": ("PARENT-4A-508-LARGE-5X8", "COLOR/SIZE", "Bright Ultra Colors", "4 Pads Lined (5 x 8 in)"),
    "4A GM5084-N-L": ("PARENT-4A-508-LARGE-5X8", "COLOR/SIZE", "Bright Ultra Colors", "4 Pads Lined (5 x 8 in)"),
    "4A GM5084-N-L*2": ("PARENT-4A-508-LARGE-5X8", "COLOR/SIZE", "Bright Ultra Colors", "8 Pads Lined (2 Packs of 4, 5 x 8 in)"),
    "AAAA 4A 5084-N-L": ("PARENT-4A-508-LARGE-5X8", "COLOR/SIZE", "Bright Ultra Colors", "8 Pads Lined (2 Packs of 4, 5 x 8 in)"),
    "4A 5084-N-L*4": ("PARENT-4A-508-LARGE-5X8", "COLOR/SIZE", "Bright Ultra Colors", "16 Pads Lined (4 Packs of 4, 5 x 8 in)"),
    "4A GM5084-N-L*4": ("PARENT-4A-508-LARGE-5X8", "COLOR/SIZE", "Bright Ultra Colors", "16 Pads Lined (4 Packs of 4, 5 x 8 in)"),
    "4A 5088-N-L": ("PARENT-4A-508-LARGE-5X8", "COLOR/SIZE", "Bright Ultra Colors", "8 Pads Lined (8 Colors, 5 x 8 in)"),
    "4A 5088-Rainbow": ("PARENT-4A-508-LARGE-5X8", "COLOR/SIZE", "Rainbow Colors", "8 Pads Lined Multi-Color (5 x 8 in)"),

    # 608 XLarge 6x8
    "4A 608-N-L-210": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "1 Pad Thick Block (210 Sheets, 6 x 8 in)"),
    "4A 608-NL-210": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "1 Pad Thick Block (210 Sheets, 6 x 8 in)"),
    "AAAA 4A 608-N-L-210": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "1 Pad Thick Block (210 Sheets, 6 x 8 in)"),
    "4A 608-N-L-210-FBA": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "1 Pad Thick Block (210 Sheets, 6 x 8 in)"),
    "4A 608-N-L-210*2": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "2 Pads Thick Block (420 Sheets, 6 x 8 in)"),
    "4A GM608-N-L-210*2": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "2 Pads Thick Block (420 Sheets, 6 x 8 in)"),
    "4A GM608S-Linex4": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "4 Pads Super Sticky Lined (6 x 8 in)"),
    "AAAA 4A 608S-Linex4": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "4 Pads Super Sticky Lined (6 x 8 in)"),
    "4A 189": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Lined Bulk (3 Packs of 4, 6 x 8 in)"),
    "4A GM608S-Linex4*3": ("PARENT-4A-608-XLARGE-6X8", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Lined Bulk (3 Packs of 4, 6 x 8 in)"),

    # Executive Leather & Acrylic Holders
    "4A BS 1801": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Black Leather Set", "Standard Executive Set (Built-in Tabs)"),
    "4A GMBS 1801": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Black Leather Set", "Standard Executive Set (Built-in Tabs)"),
    "4A BS 1801-FBA": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Black Leather Set", "Standard Executive Set (Built-in Tabs)"),
    "4A BS 1801 Refill": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Multi-Color Refill", "Replacement Paper & Tabs Refill Pack"),
    "4A BS 1802": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Brown Leather Set", "Executive Organizer Box Set"),
    "4A BS 1803": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Black Executive Box", "Deluxe Desk Organizer Box Set"),
    "4A BS 1803-FBA": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Black Executive Box", "Deluxe Desk Organizer Box Set"),
    "4A BS 1804": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Compact Leather Set", "Compact Note Organizer Set"),
    "4A GMSCBS 1804": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Compact Leather Set", "Compact Note Organizer Set"),
    "4A SCBS 1804": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Compact Leather Set", "Compact Note Organizer Set"),
    "4A SCBS 1805": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Organizer Bundle", "Sticky Note Bundle Set with Pop-Up Flags"),
    "4A PSS 10": ("PARENT-4A-BS-EXECUTIVE-LEATHER", "COLOR/SIZE", "Organizer Bundle", "Sticky Note Bundle Set with Pop-Up Flags"),

    # Acrylic Desk Organizers
    "303-AC-holder": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Clear Acrylic (3 x 3)", "Dispenser with 8-Color 3x3 Notes & Flags"),
    "4A 303-AC-holder": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Clear Acrylic (3 x 3)", "Dispenser with 8-Color 3x3 Notes & Flags"),
    "4A GM303-AC-holder": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Clear Acrylic (3 x 3)", "Dispenser with 8-Color 3x3 Notes & Flags"),
    "4A 303-Holder+Flag": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Clear Acrylic (3 x 3)", "Dispenser with 8-Color 3x3 Notes & Flags"),
    "4A 404-AC-holder": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Clear Acrylic (4 x 4)", "Dispenser with 8-Color 4x4 Notes & Flags"),
    "4A 404-AC-Holder": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Clear Acrylic (4 x 4)", "Dispenser with 8-Color 4x4 Notes & Flags"),
    "4A GMSC404-AC-holder": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Clear Acrylic (4 x 4)", "Dispenser with 8-Color 4x4 Notes & Flags"),
    "4A SC404-AC-holder": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Clear Acrylic (4 x 4)", "Dispenser with 8-Color 4x4 Notes & Flags"),
    "4A PSS 7": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Black Dispenser", "Pop-Up Note Dispenser (Black)"),
    "4A GMSCPSS 7": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Black Dispenser", "Pop-Up Note Dispenser (Black)"),
    "4A SCPSS 7": ("PARENT-4A-ACRYLIC-DESK-ORGANIZERS", "COLOR/SIZE", "Black Dispenser", "Pop-Up Note Dispenser (Black)"),

    # Sign Here Flags
    "4A 190": ("PARENT-4A-SIGN-HERE-FLAGS", "COLOR/SIZE", "Neon Yellow & Red", "100 Flags (1 x 1.7 in)"),
    "4A 60171": ("PARENT-4A-SIGN-HERE-FLAGS", "COLOR/SIZE", "Neon Yellow & Red", "100 Flags (1 x 1.7 in)"),
    "4A GM60171*3": ("PARENT-4A-SIGN-HERE-FLAGS", "COLOR/SIZE", "Neon Yellow & Red", "300 Flags (3 Packs of 100, 1 x 1.7 in)"),
    "4A 60174-Sign Herex2": ("PARENT-4A-SIGN-HERE-FLAGS", "COLOR/SIZE", "Neon Multi-Color", "200 Flags (2 Packs of 100, 1 x 1.7 in)"),
    "4A GM60174-Sign Herex2": ("PARENT-4A-SIGN-HERE-FLAGS", "COLOR/SIZE", "Neon Multi-Color", "200 Flags (2 Packs of 100, 1 x 1.7 in)"),
    "4A 60174x2": ("PARENT-4A-SIGN-HERE-FLAGS", "COLOR/SIZE", "Neon Multi-Color", "200 Flags (2 Packs of 100, 1 x 1.7 in)"),

    # Big Meeting Easel Pads
    "4A Meeting 52x4": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Tabletop Easel", "4 Packs Tabletop Easel Pad 2-in-1 (20 x 23 in)"),
    "4A GMSC-MEETING-52x4": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Tabletop Easel", "4 Packs Tabletop Easel Pad 2-in-1 (20 x 23 in)"),
    "4A Meeting 52x4-FBA": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Tabletop Easel", "4 Packs Tabletop Easel Pad 2-in-1 (20 x 23 in)"),
    "4A-MEETING-52X4": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Tabletop Easel", "4 Packs Tabletop Easel Pad 2-in-1 (20 x 23 in)"),
    "4A Meeting 42x4": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Easel Pad", "4 Packs Super Sticky Easel Pad (25 x 30 in)"),
    "4A GMSCMeeting 42X4": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Easel Pad", "4 Packs Super Sticky Easel Pad (25 x 30 in)"),
    "4A-MEETING-42X4": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Easel Pad", "4 Packs Super Sticky Easel Pad (25 x 30 in)"),
    "4A GMMeeting-6": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Dry Erase Surface", "Dry Erase Whiteboard Sheet (2.5 x 2.7 ft)"),
    "AAAA 4A Meeting-6": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Dry Erase Surface", "Dry Erase Whiteboard Sheet (2.5 x 2.7 ft)"),
    "4A 0146": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Dry Erase Surface", "Dry Erase Whiteboard Sheet (2.5 x 2.7 ft)"),
    "4A Meeting-6": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "White Dry Erase Surface", "Dry Erase Whiteboard Sheet (2.5 x 2.7 ft)"),
    "4A BP 2222-Nx4": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "Bright Ultra Colors", "4 Pads (22 x 22 in)"),
    "4A GMBP 2222-Nx4": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "Bright Ultra Colors", "4 Pads (22 x 22 in)"),
    "4A BP 2222-Nx4-FBA": ("PARENT-4A-BIGPAD-MEETING-EASEL", "COLOR/SIZE", "Bright Ultra Colors", "4 Pads (22 x 22 in)"),

    # Desk Planners
    "4A 6533": ("PARENT-4A-DESK-PLANNERS", "COLOR/SIZE", "Classic Assorted", "Weekly Planner Pad 11 x 3.25 in (60 Sheets)"),
    "4A 6533-FBA": ("PARENT-4A-DESK-PLANNERS", "COLOR/SIZE", "Classic Assorted", "Weekly Planner Pad 11 x 3.25 in (60 Sheets)"),
    "4A 6534": ("PARENT-4A-DESK-PLANNERS", "COLOR/SIZE", "Classic Assorted", "Monthly Planner Pad 11 x 8.5 in (60 Sheets)"),

    # Die-Cut Novelty Shapes (5013 Arrow, 5036 Heart, 5059 Bubble, 5061 Leaf, 5047 Hand, 5020 Puzzle, 50024)
    "4A 5013": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Arrow Shape (2.7 x 2.6 in)"),
    "4A052": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Arrow Shape (2.7 x 2.6 in)"),
    "4A5013-B00SM-FBA": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Arrow Shape (2.7 x 2.6 in)"),
    "4A 5036": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Heart Shape 1 Pack (3 x 3 in)"),
    "4A 5036-B00SM-FBA": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Heart Shape 1 Pack (3 x 3 in)"),
    "4A 5036x2": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Heart Shape 2 Packs (2 x 100 Sheets, 3 x 3 in)"),
    "4A 5059": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Speech Bubble Shape (3.4 x 1.9 in)"),
    "4A053": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Speech Bubble Shape (3.4 x 1.9 in)"),
    "4A 5059-B00SM-FBA": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Speech Bubble Shape (3.4 x 1.9 in)"),
    "4A 5061": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Leaf Shape 1 Pack (2.8 x 2.8 in)"),
    "4A054": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Leaf Shape 1 Pack (2.8 x 2.8 in)"),
    "4A 5061-B00SM-FBA": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Leaf Shape 1 Pack (2.8 x 2.8 in)"),
    "4A 5061x2": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Leaf Shape 2 Packs (2 x 100 Sheets, 2.8 x 2.8 in)"),
    "4A 5047": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Neon Assorted", "Thumbs Up Hand Shape (2.8 x 2.8 in)"),
    "4A056": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Neon Assorted", "Thumbs Up Hand Shape (2.8 x 2.8 in)"),
    "4A 5047-B00SM-FBA": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Neon Assorted", "Thumbs Up Hand Shape (2.8 x 2.8 in)"),
    "4A 5037": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Neon Assorted", "Tree Shape 1 Pack (2.6 x 2.7 in)"),
    "4A055": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Neon Assorted", "Tree Shape 1 Pack (2.6 x 2.7 in)"),
    "4A 5037x2": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Neon Assorted", "Tree Shape 2 Packs (2 x 100 Sheets, 2.6 x 2.7 in)"),
    "4A 5020x3": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Puzzle Shape 3 Packs (3 x 100 Sheets, 2.9 x 2.6 in)"),
    "4A GM5020x3": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Puzzle Shape 3 Packs (3 x 100 Sheets, 2.9 x 2.6 in)"),
    "4A 5020x3-FBA": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Bright Ultra Colors", "Puzzle Shape 3 Packs (3 x 100 Sheets, 2.9 x 2.6 in)"),
    "4A 50024": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Pastel Assorted", "Novelty Shapes 24 Pads Value Pack"),
    "4A GM50024": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Pastel Assorted", "Novelty Shapes 24 Pads Value Pack"),
    "4A 5021X2": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Neon Assorted", "Door Hanger Note Pads (2 Pads)"),
    "4A GM5021X2": ("PARENT-4A-SHAPED-NOVELTY-PADS", "COLOR/SIZE", "Neon Assorted", "Door Hanger Note Pads (2 Pads)"),

    # 3D Animal / Ocean Spectrum 24 (giving real button names instead of (Pack X))
    "4A 0166": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "White", "Ocean Shark & Dolphin Print (3.75 x 4.13 in)"),
    "4A 0172": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "South African Lion Print (3.75 x 4.13 in)"),
    "4A 8084": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "South African Lion Print (3.75 x 4.13 in)"),
    "4A 0173": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Emperor Penguin Print (3.75 x 4.13 in)"),
    "4A 8085": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Emperor Penguin Print (3.75 x 4.13 in)"),
    "4A 0175": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Fraser's Dolphin Print (3.75 x 4.13 in)"),
    "4A 8087": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Fraser's Dolphin Print (3.75 x 4.13 in)"),
    "4A 0165": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Pinna Fox Print (3.75 x 4.13 in)"),
    "4A 8077": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Pinna Fox Print (3.75 x 4.13 in)"),
    "4A 8076": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Ocean Whale Print (3.75 x 4.13 in)"),
    "4A 0163": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Long-Nosed Dolphin Print (3.75 x 4.13 in)"),
    "4A 8075": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Long-Nosed Dolphin Print (3.75 x 4.13 in)"),
    "4A 0162": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Pygmy Sperm Whale Print (3.75 x 4.13 in)"),
    "4A 8074": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Pygmy Sperm Whale Print (3.75 x 4.13 in)"),
    "4A 0159": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Petit Dog Print (3.75 x 4.13 in)"),
    "4A 8071": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Petit Dog Print (3.75 x 4.13 in)"),
    "4A 0161": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "American Shorthair Cat Print (3.75 x 4.13 in)"),
    "4A 8073": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "American Shorthair Cat Print (3.75 x 4.13 in)"),
    "4A 0154": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Havana Brown Cat Print (3.75 x 4.13 in)"),
    "4A 0155": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Berman Cat Print (3.75 x 4.13 in)"),
    "4A 0158": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "White", "White Persian Cat Print (3.75 x 4.13 in)"),
    "4A 8070": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "White", "White Persian Cat Print (3.75 x 4.13 in)"),
    "4A 0168": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Risso's Dolphin Print (3.75 x 4.13 in)"),
    "4A 0169": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Japanese Spitz Dog Print (3.75 x 4.13 in)"),
    "4A 0171": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Polar Bear Print (3.75 x 4.13 in)"),
    "4A 0167": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Snow Geese Bird Print (3.75 x 4.13 in)"),
    "4A 8079": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Snow Geese Bird Print (3.75 x 4.13 in)"),
    "4A 0153": ("PARENT-4A-8065-8088-SPECTRUM-24", "COLOR/SIZE", "Classic Assorted", "Tiger Print (3.75 x 4.13 in)"),

    # Transparent PET Tabs (6043, 6034, 6035, 6031, 6022, 6012, 6611)
    "4A 6043": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (100 Tabs with PP Ruler, 1 x 1.7 in)"),
    "4A099": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (100 Tabs with PP Ruler, 1 x 1.7 in)"),
    "4A 6043-FBA": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (100 Tabs with PP Ruler, 1 x 1.7 in)"),
    "4A GMVC6043": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (100 Tabs with PP Ruler, 1 x 1.7 in)"),
    "4A GM6043*2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "2 Packs (200 Tabs with PP Ruler, 1 x 1.7 in)"),
    "4A 6034": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (100 Tabs, 1 x 1.5 in)"),
    "4A0102": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (100 Tabs, 1 x 1.5 in)"),
    "4A GMVC6034": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (100 Tabs, 1 x 1.5 in)"),
    "4A 6034x2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "2 Packs (200 Tabs, 1 x 1.5 in)"),
    "4A GM6034*2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "2 Packs (200 Tabs, 1 x 1.5 in)"),
    "4A 6035": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (80 Heavy Duty Tabs, 2 x 1.5 in)"),
    "4A0103": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (80 Heavy Duty Tabs, 2 x 1.5 in)"),
    "4A 6035-FBA": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack (80 Heavy Duty Tabs, 2 x 1.5 in)"),
    "4A GM6035*2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "2 Packs (160 Heavy Duty Tabs, 2 x 1.5 in)"),
    "4A 6035x5": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "5 Packs (400 Heavy Duty Tabs, 2 x 1.5 in)"),
    "4A GM6035x5": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "5 Packs (400 Heavy Duty Tabs, 2 x 1.5 in)"),
    "4A 6031x4": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "4 Packs (400 Tabs, 1 x 1.1 in)"),
    "4A GM6031x4": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "4 Packs (400 Tabs, 1 x 1.1 in)"),
    "4A 66113": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Pop-Up Index Tabs (0.5 x 1.7 in)"),
    "4A094": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Pop-Up Index Tabs (0.5 x 1.7 in)"),
    "4A GMSC66113*2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "2 Packs Pop-Up Index Tabs (0.5 x 1.7 in)"),
    "4A 66114": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Pop-Up Arrow Tabs (0.5 x 1.7 in)"),
    "4A095": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Pop-Up Arrow Tabs (0.5 x 1.7 in)"),
    "4A GMSC66114*2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "2 Packs Pop-Up Arrow Tabs (0.5 x 1.7 in)"),
    "4A 60237": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Bright Ultra Colors", "1 Pack Film Flags with Ruler (0.5 x 1.7 in)"),
    "4A096": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Bright Ultra Colors", "1 Pack Film Flags with Ruler (0.5 x 1.7 in)"),
    "4A 60237x2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Bright Ultra Colors", "2 Packs Film Flags with Ruler (0.5 x 1.7 in)"),
    "4A 60187": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Flags in Portable Dispenser (0.5 x 1.7 in)"),
    "4A0101": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Flags in Portable Dispenser (0.5 x 1.7 in)"),
    "4A GMSC60187": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Flags in Portable Dispenser (0.5 x 1.7 in)"),
    "4A 60144x2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "2 Packs Arrow Flags (0.5 x 1.7 in)"),
    "4A 60222": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Bright Ultra Colors", "2 Packs Film Flags (0.5 x 1.7 in)"),
    "4A GM60222": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Bright Ultra Colors", "2 Packs Film Flags (0.5 x 1.7 in)"),
    "4A 60122-8": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Bright Ultra Colors", "8 Pads Pop-Up Flags (1 x 1.7 in)"),
    "4A GM60122-4x2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Bright Ultra Colors", "8 Pads Pop-Up Flags (1 x 1.7 in)"),
    "4A 60122-4x2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Bright Ultra Colors", "8 Pads Pop-Up Flags (1 x 1.7 in)"),
    "4A 6032": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack Durable File Tabs (1 x 1.5 in)"),
    "4A GM6032*2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "2 Packs Durable File Tabs (1 x 1.5 in)"),
    "4A 6032x5": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "5 Packs Durable File Tabs (1 x 1.5 in)"),
    "4A GM6032x5": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "5 Packs Durable File Tabs (1 x 1.5 in)"),
    "4A 60239": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack Durable File Tabs with Ruler (1 x 1.5 in)"),
    "4A098": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "1 Pack Durable File Tabs with Ruler (1 x 1.5 in)"),
    "4A GM60239*2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Transparent Writable", "2 Packs Durable File Tabs with Ruler (1 x 1.5 in)"),
    "4A 60238": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Sticky Flags with Ruler (0.5 x 1.7 in)"),
    "4A SF-60238": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "1 Pack Sticky Flags with Ruler (0.5 x 1.7 in)"),
    "4A GM60238*2": ("PARENT-4A-TRANSPARENT-PET-TABS", "COLOR/SIZE", "Neon Assorted", "2 Packs Sticky Flags with Ruler (0.5 x 1.7 in)"),

    # Paper Page Markers & Dividers (40606, 40607, 40608, 40609, 40621, 40622, 40623, 40624, 124418, 501516, 501521, 752516)
    "4A 40606": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Neon Assorted", "3 3/8 x 2 3/4 in (1 Pack, Tabbed Lined)"),
    "4A 40606*2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Neon Assorted", "3 3/8 x 2 3/4 in (2 Packs, Tabbed Lined)"),
    "4A GM40606*3": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Neon Assorted", "3 3/8 x 2 3/4 in (3 Packs, Tabbed Lined)"),
    "4A GM40607*3": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "3 3/8 x 2 3/4 in (3 Packs, Tabbed Lined)"),
    "4A 40608": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Neon Assorted", "2 2/3 x 2 7/8 in (1 Pack, Tabbed Lined)"),
    "4A 40608*2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Neon Assorted", "2 2/3 x 2 7/8 in (2 Packs, Tabbed Lined)"),
    "AAAA 4A 40608": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Neon Assorted", "2 2/3 x 2 7/8 in (2 Packs, Tabbed Lined)"),
    "4A 40609": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "2 2/3 x 2 7/8 in (1 Pack, Tabbed Lined)"),
    "4A GM40609*2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "2 2/3 x 2 7/8 in (2 Packs, Tabbed Lined)"),
    "AAAA 4A 40609": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "2 2/3 x 2 7/8 in (2 Packs, Tabbed Lined)"),
    "4A 40609x4": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "2 2/3 x 2 7/8 in (4 Packs, Tabbed Lined)"),
    "4A GM40609x4": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "2 2/3 x 2 7/8 in (4 Packs, Tabbed Lined)"),
    "4A 40623": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Neon Assorted", "4 x 6 in (1 Pack, Large Tabbed Lined)"),
    "4A 40623x6": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Neon Assorted", "4 x 6 in (6 Packs, Large Tabbed Lined)"),
    "4A 40624": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "4 x 6 in (1 Pack, Large Tabbed Lined)"),
    "4A071": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "4 x 6 in (1 Pack, Large Tabbed Lined)"),
    "4A GM40624*2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "4 x 6 in (2 Packs, Large Tabbed Lined)"),
    "4A 40624x6": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "White", "4 x 6 in (6 Packs, Large Tabbed Lined)"),
    "4A 124418": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "16 Pads (1/2 x 1 3/4 in, 16 Colors)"),
    "AAAA 4A 124418": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "16 Pads (1/2 x 1 3/4 in, 16 Colors)"),
    "4A 124418*3": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "48 Pads (3 Packs of 16, 1/2 x 1 3/4 in)"),
    "4A GM124418*3": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "48 Pads (3 Packs of 16, 1/2 x 1 3/4 in)"),
    "4A 501516": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "16 Pads (0.6 x 2 in, 16 Colors)"),
    "4A SC501516": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "16 Pads (0.6 x 2 in, 16 Colors)"),
    "4A SC501516*2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "32 Pads (2 Packs of 16, 0.6 x 2 in)"),
    "4A 501521x2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "42 Pads (2 Packs of 21, 0.6 x 2 in)"),
    "4A SC501521*2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "42 Pads (2 Packs of 21, 0.6 x 2 in)"),
    "4A 752516x2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "32 Pads (2 Packs of 16, 1 x 3 in)"),
    "4A SC752516*2": ("PARENT-4A-PAPER-PAGE-MARKERS", "COLOR/SIZE", "Bright Ultra Colors", "32 Pads (2 Packs of 16, 1 x 3 in)"),

    # Memo Note Cubes (SMC 434, SMC 435, SMC 436, SMC 437, SMC 438, 4A092, 4A093, 3031..3037)
    "4A GMSMC 434": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Bubble Print", "2.5 x 2.5 in (500 Sheets Cube)"),
    "AAAA 4A SMC 434": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Bubble Print", "2.5 x 2.5 in (500 Sheets Cube)"),
    "4A092": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Bubble Print", "2.5 x 2.5 in (500 Sheets Cube)"),
    "4A093": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Wave Print", "3 1/4 x 3 1/4 in (650 Sheets Cube)"),
    "4A GMSCMC 434": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Wave Print", "3 1/4 x 3 1/4 in (650 Sheets Cube)"),
    "MG-ET8D-JLS7": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Wave Print", "3 1/4 x 3 1/4 in (650 Sheets Cube)"),
    "4A SMC 435": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Love Cat Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "AAAA 4A SMC 435": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Love Cat Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "4A SMC 435-FBA": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Love Cat Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "4A SMC 436": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Cat Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "AAAA 4A SMC 436": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Cat Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "4A GMSCSMC 436": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Cat Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "4A SMC 437": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "White Dog Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "AAAA 4A SMC 437": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "White Dog Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "4A SMC 438": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Wearing Dog Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "AAAA 4A SMC 438": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Wearing Dog Print", "2.87 x 2.87 in (400 Sheets Cube)"),
    "AAAA 4A 3031": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Neon Assorted", "3 x 3 in Cube (400 Sheets)"),
    "AAAA 4A 3034": ("PARENT-4A-MEMO-NOTE-CUBES", "COLOR/SIZE", "Bright Ultra Colors", "3 x 3 in Cube (400 Sheets)"),

    # Label Stickers
    "4A LB 1901": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "16 Colors Assorted", "3/4 in Round Dot Labels (16 Colors, 1056 Labels)"),
    "4A SCLB 1901": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "16 Colors Assorted", "3/4 in Round Dot Labels (16 Colors, 1056 Labels)"),
    "4A GMSCLB 1901": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "16 Colors Assorted", "3/4 in Round Dot Labels (16 Colors, 1056 Labels)"),
    "4A LB 1902": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "Black Chalkboard", "Chalkboard Labels 2.5 x 3.5 in (96 Labels)"),
    "4A SCLB 1902": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "Black Chalkboard", "Chalkboard Labels 2.5 x 3.5 in (96 Labels)"),
    "4A GMSCLB 1902": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "Black Chalkboard", "Chalkboard Labels 2.5 x 3.5 in (96 Labels)"),
    "4A LB 1903": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "Gold Border Chalkboard", "Gold Border Labels Mixed Sizes (168 Labels)"),
    "4A SCLB 1903": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "Gold Border Chalkboard", "Gold Border Labels Mixed Sizes (168 Labels)"),
    "4A GMSCLB 1903": ("PARENT-4A-LABEL-STICKERS", "COLOR/SIZE", "Gold Border Chalkboard", "Gold Border Labels Mixed Sizes (168 Labels)"),

    # Mini Pads 301 / 202 / 3548 / 4848
    "4A 004": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "24 Pads (1.5 x 2 in, 1 Tower)"),
    "4A 301x24": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "24 Pads (1.5 x 2 in, 1 Tower)"),
    "AAAA 4A 301x12-N": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "24 Pads (1.5 x 2 in, 1 Tower)"),
    "4A 301x24-Y": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Canary Yellow", "48 Pads (1.5 x 2 in, 2 Towers)"),
    "4A GM301x24*2": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "48 Pads (1.5 x 2 in, 2 Towers)"),
    "4A 301x24x2": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "48 Pads (1.5 x 2 in, 2 Towers)"),
    "4A 30132": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "32 Pads Value Pack (1.5 x 2 in)"),
    "4A GM30132": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "32 Pads Value Pack (1.5 x 2 in)"),
    "4A 30132-FBA": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "32 Pads Value Pack (1.5 x 2 in)"),
    "4A 2028-N": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "8 Pads (2 x 2 in, 8 Colors)"),
    "4A 2028-N-FBA": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "8 Pads (2 x 2 in, 8 Colors)"),
    "4A GM2028-N*3": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "24 Pads (3 Packs of 8, 2 x 2 in)"),
    "4A 20232": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "16 Colors Assorted", "32 Pads Value Pack (2 x 2 in)"),
    "4A GM20232": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "16 Colors Assorted", "32 Pads Value Pack (2 x 2 in)"),
    "4A 354818": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "18 Pads (1 3/8 x 1 7/8 in)"),
    "4A 354818*2": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Bright Ultra Colors", "36 Pads (2 Packs of 18, 1 3/8 x 1 7/8 in)"),
    "4A 354832": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "16 Colors Assorted", "32 Pads (1 3/8 x 1 7/8 in)"),
    "4A GM354832": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "16 Colors Assorted", "32 Pads (1 3/8 x 1 7/8 in)"),
    "4A 354832-FBA": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "16 Colors Assorted", "32 Pads (1 3/8 x 1 7/8 in)"),
    "4A 484812-N-FBA": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "12 Pads (1 7/8 x 1 7/8 in)"),
    "4A 484812-N": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "12 Pads (1 7/8 x 1 7/8 in)"),
    "4A GM484812-N*2": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "24 Pads (2 Packs of 12, 1 7/8 x 1 7/8 in)"),
    "4A 484812-N*3": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "36 Pads (3 Packs of 12, 1 7/8 x 1 7/8 in)"),
    "4A GM484812-N*3": ("PARENT-4A-301-MINI-PADS", "COLOR/SIZE", "Neon Assorted", "36 Pads (3 Packs of 12, 1 7/8 x 1 7/8 in)"),

    # Square 4x4 Pads
    "4A 031": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Neon Assorted", "6 Pads Lined (4 x 4 in)"),
    "4A 404S-Lx6": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Neon Assorted", "6 Pads Super Sticky Lined (4 x 4 in)"),
    "AAAA 4A 404S-Linex6": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Neon Assorted", "6 Pads Super Sticky Lined (4 x 4 in)"),
    "4A 185": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Neon Assorted", "12 Pads Super Sticky Lined (2 Packs of 6, 4 x 4 in)"),
    "4A GM404S-Linex6*2": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Neon Assorted", "12 Pads Super Sticky Lined (2 Packs of 6, 4 x 4 in)"),
    "4A 030": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "6 Pads Unlined (4 x 4 in)"),
    "4A 404 x 6-N": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "6 Pads Unlined (4 x 4 in)"),
    "4A 404x6-N": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "6 Pads Unlined (4 x 4 in)"),
    "4A 404x6-N*2": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Unlined (2 Packs of 6, 4 x 4 in)"),
    "4A GM404x6-N*2": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Unlined (2 Packs of 6, 4 x 4 in)"),
    "4A 40412": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Unlined (4 x 4 in)"),
    "4A GM40412": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Unlined (4 x 4 in)"),
    "4A 40412-L": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Lined (4 x 4 in)"),
    "4A GM40412-L": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Lined (4 x 4 in)"),
    "4A 404SL-15": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "6 Pads Extra Bright Lined (4 x 4 in)"),
    "4A GM404SL-15": ("PARENT-4A-404-SQUARE-4X4", "COLOR/SIZE", "Bright Ultra Colors", "6 Pads Extra Bright Lined (4 x 4 in)"),

    # Medium 406 & 305 Pads
    "4A 026": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Pastel Assorted", "6 Pads Unlined (3 x 5 in)"),
    "4A 305 x 6": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Pastel Assorted", "6 Pads Unlined (3 x 5 in)"),
    "4A 027": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "6 Pads Unlined (3 x 5 in)"),
    "4A 305 x 6-N": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "6 Pads Unlined (3 x 5 in)"),
    "4A 305x6-N": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "6 Pads Unlined (3 x 5 in)"),
    "4A GM305x6-N*2": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "12 Pads Unlined (2 Packs of 6, 3 x 5 in)"),
    "4A 305 x 6-Y": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Canary Yellow", "6 Pads Unlined (3 x 5 in)"),
    "4A 305x6-Y": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Canary Yellow", "6 Pads Unlined (3 x 5 in)"),
    "4A 028": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "6 Pads Lined (3 x 5 in)"),
    "4A 305 x 6-N-L": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "6 Pads Lined (3 x 5 in)"),
    "4A 305x6-N-Lx4": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "24 Pads Lined (4 Packs of 6, 3 x 5 in)"),
    "4A 30512": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Unlined (3 x 5 in)"),
    "4A GM30512": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Unlined (3 x 5 in)"),
    "4A 30512-L": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Lined (3 x 5 in)"),
    "4A GM30512-L": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Lined (3 x 5 in)"),
    "4A 032": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Canary Yellow", "6 Pads Lined (4 x 6 in)"),
    "4A 406x6-Y": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Canary Yellow", "6 Pads Lined (4 x 6 in)"),
    "AAAA 4A 406x6": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Pastel Assorted", "6 Pads Unlined (4 x 6 in)"),
    "4A 40612": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Unlined (4 x 6 in)"),
    "4A GM40612": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "12 Pads Unlined (4 x 6 in)"),
    "4A 40612-L": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "12 Pads Lined (4 x 6 in)"),
    "4A GM40612-L": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "12 Pads Lined (4 x 6 in)"),
    "4A 406SL-10": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "6 Pads Extra Bright Lined (4 x 6 in)"),
    "4A GM406SL-10": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "6 Pads Extra Bright Lined (4 x 6 in)"),
    "4A 186": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "9 Pads Super Sticky Lined (3 Packs of 3, 4 x 6 in)"),
    "4A GM406S-Linex3*3": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "9 Pads Super Sticky Lined (3 Packs of 3, 4 x 6 in)"),
    "4A 187": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "15 Pads Super Sticky Lined (3 Packs of 5, 4 x 6 in)"),
    "4A GM406S-Linex5*3": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Bright Ultra Colors", "15 Pads Super Sticky Lined (3 Packs of 5, 4 x 6 in)"),
    "4A GM406S-Linex3": ("PARENT-4A-406-MEDIUM-PADS", "COLOR/SIZE", "Neon Assorted", "3 Pads Super Sticky Lined (4 x 6 in)"),

    # PSS Full Adhesive Roll Tapes & Refills
    "4A PSS 9-1 NYGrid": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow Grid", "1 Roll Dispenser with Cutter (2 in x 26 ft)"),
    "4A PSS 9-1 NY": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A076": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "AAAA 4A PSS 9-1 NY": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A PSS 9-1 NY Gridx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow Grid", "2 Rolls with Cutter (2 in x 26 ft)"),
    "4A GM-SC-PSS 9-1 NYNRx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow & Red", "2 Rolls with Dispenser + 2 Refills (2 in x 26 ft)"),
    "AAAA 4A PSS 9-1 NGGrid": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow & Red", "2 Rolls with Dispenser + 2 Refills (2 in x 26 ft)"),
    "4A GM-PSS 9-1 NYNRx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow & Red", "2 Rolls with Dispenser + 2 Refills (2 in x 26 ft)"),
    "4A PSS 9-1 NYNRx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow & Red", "2 Rolls with Dispenser + 2 Refills (2 in x 26 ft)"),
    "4A PSS 9-1 Grid-NYNGx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow & Green Grid", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A PSS 9-1 NGGrid": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow & Green Grid", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A PSS 9-1 Grid-NYNGx2-FBA": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Yellow & Green Grid", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A GMPSS 9-1 Grid-NBNPx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Blue & Pink Grid", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A PSS 9-1 Grid-NBNPx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Blue & Pink Grid", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A GMPSS 9-1 NGNOx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Green & Orange", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A PSS 9-1 NGNOx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Green & Orange", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A PSS 9-1 NGNOx2-FBA": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Green & Orange", "2 Rolls with Dispenser (2 in x 26 ft)"),
    "4A GMPSS 9-1 Refill": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Assorted Refill", "4 Replacement Refill Rolls (2 in x 26 ft)"),
    "4A PSS 9-1 Refill": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Neon Assorted Refill", "4 Replacement Refill Rolls (2 in x 26 ft)"),
    "4A GM-SC-PSS 9-1 Grid Refill": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Grid Lines Refill", "4 Grid Replacement Refill Rolls (2 in x 26 ft)"),
    "4A PSS 9-1 Grid Refill": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Grid Lines Refill", "4 Grid Replacement Refill Rolls (2 in x 26 ft)"),
    "4A GM-PSS 9-3 YOR": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Yellow, Orange, Red", "3 Rolls with Dispenser (0.6 in x 26 ft)"),
    "4A PSS 9-3 YOR": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Yellow, Orange, Red", "3 Rolls with Dispenser (0.6 in x 26 ft)"),
    "4A PSS 9-3 YORx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Yellow, Orange, Red", "6 Rolls with 2 Dispensers (0.6 in x 26 ft)"),
    "4A PSS 9-3 2 Sets": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Bright Ultra Colors", "6 Rolls with 2 Dispensers (0.6 in x 26 ft)"),
    "4A PSS 9-3 2 Sets-FBA": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Bright Ultra Colors", "6 Rolls with 2 Dispensers (0.6 in x 26 ft)"),
    "4A PSS 9-3 Refill": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Multi-Color Refill", "4 Replacement Refill Rolls (0.6 in x 26 ft)"),
    "4A PSS 9-3 Refill-FBA": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Multi-Color Refill", "4 Replacement Refill Rolls (0.6 in x 26 ft)"),
    "4A PSS 9-5 NANBx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Bright Ultra Colors", "10 Rolls with 2 Dispensers (0.4 in x 26 ft)"),
    "4A GM-SC-PSS 9-5 NANBx2": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Bright Ultra Colors", "10 Rolls with 2 Dispensers (0.4 in x 26 ft)"),
    "4A PSS 9-5 NANBx2-FBA": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Bright Ultra Colors", "10 Rolls with 2 Dispensers (0.4 in x 26 ft)"),
    "4A PSS 9-5 Refill": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Multi-Color Refill", "4 Replacement Refill Rolls (0.4 in x 26 ft)"),
    "4A GMPSS 9-5 Refill": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Multi-Color Refill", "4 Replacement Refill Rolls (0.4 in x 26 ft)"),
    "AAAA 4A PSS 9-5 NB": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Multi-Color Refill", "4 Replacement Refill Rolls (0.4 in x 26 ft)"),
    "4A GMSCCR 012": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Coloring Roll Patterns", "Continuous Coloring Roll Tape"),
    "4A SCCR 012": ("PARENT-4A-PSS-ROLL-TAPE", "COLOR/SIZE", "Coloring Roll Patterns", "Continuous Coloring Roll Tape"),
}

for sku, (p_sku, theme, c, s) in extra_cleanups.items():
    if sku in seen_skus or sku not in cat_by_sku:
        continue
    r = list(cat_by_sku[sku])
    r[4] = "Edit (Partial Update)"
    r[5] = "Child"
    r[6] = p_sku
    r[7] = theme
    r[8] = None  # preserve existing title, avoid 100476
    r[9] = None
    r[10] = "4A"
    r[58] = c
    r[59] = s
    r[332] = None
    r[340] = None
    r[364] = None
    r[365] = None
    r[366] = None
    for u_col in (374, 376, 378, 380, 382, 384):
        if r[u_col] == "IN": r[u_col] = "Inches"
    rows.append(r)
    seen_skus.add(sku)

# Part E: Enforce 100% same-ASIN unification across all rows in Batch 20!
# If an ASIN has multiple SKUs, they MUST have identical (Parent, Theme, Color, Size).
asin_canonical = {}
for r in rows:
    if r[5] != "Parent" and r[12]:
        a = str(r[12]).strip()
        sku = r[2]
        # Prefer the explicitly cleaned up specs from extra_cleanups or batch19_fixes
        if sku in extra_cleanups or sku in batch19_fixes:
            asin_canonical[a] = (r[6], r[7], r[58], r[59])

for r in rows:
    if r[5] != "Parent" and r[12]:
        a = str(r[12]).strip()
        if a in asin_canonical:
            canon_p, canon_t, canon_c, canon_s = asin_canonical[a]
            r[6] = canon_p
            r[7] = canon_t
            r[58] = canon_c
            r[59] = canon_s
        else:
            # If neither had extra_cleanup, unify all siblings to the first sibling's values
            first_r = [x for x in rows if str(x[12]).strip() == a][0]
            r[6] = first_r[6]
            r[7] = first_r[7]
            r[58] = first_r[58]
            r[59] = first_r[59]

print(f"Total rows assembled for Batch 20: {len(rows)}")

# Write to file
shell_path = cat_path
shutil.copy2(shell_path, work_out)
wb = openpyxl.load_workbook(work_out, keep_vba=True)
ws = wb["Template"]

if ws.max_row >= 7:
    ws.delete_rows(7, ws.max_row - 6)

for row_idx, r_vals in enumerate(rows, start=7):
    for col_idx, val in enumerate(r_vals, start=1):
        ws.cell(row=row_idx, column=col_idx, value=val)

wb.save(work_out)
wb.close()

shutil.copy2(work_out, desktop_out)
old_19_desk = r"E:\Desktop\19-voc-copy-and-pack-clarity-fixes.xlsm"
import os
if os.path.exists(old_19_desk):
    try:
        os.remove(old_19_desk)
        print(f"Removed old {old_19_desk} from Desktop.")
    except Exception as e:
        print(f"Could not remove old 19: {e}")

sha = hashlib.sha256(open(desktop_out, "rb").read()).hexdigest()
print(f"Generated {desktop_out} with {len(rows)} rows | SHA256: {sha}")
