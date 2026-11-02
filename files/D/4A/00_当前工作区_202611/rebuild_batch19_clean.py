import hashlib
import shutil
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
shell_path = r"E:\Desktop\19-voc-copy-and-pack-clarity-fixes.xlsm"
out_work = r"D:\4A\00_当前工作区_202611\19-voc-copy-and-pack-clarity-fixes.xlsm"
out_desk = r"E:\Desktop\19-voc-copy-and-pack-clarity-fixes.xlsm"

wb_cat = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws_cat = wb_cat["Template"]
cat_by_sku = {}
for r in ws_cat.iter_rows(min_row=7, values_only=True):
    if r and len(r) > 2 and r[2]:
        cat_by_sku[str(r[2]).strip()] = list(r)
wb_cat.close()

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

# Group F: Clean up PARENT-4A-303-CLASSIC-SQUARE (evict Christmas/Printed sets, 11x11/15x15 Big Pads, Divider Tabs; fix 3x3 active Size/Color labels)
evict_to_novelty = {
    "4A 8667": ("Classic Assorted", "Christmas Set 6x4.3 in (8 Pads)"),
    "AAAA 4A 8667+ 8666": ("Classic Assorted", "Christmas Set 6x4.3 in (2 Packs)"),
    "AAAA 4A 8665+8666": ("Classic Assorted", "Christmas Set 6x4.3 in (Assorted 2 Packs)"),
    "4A 0126": ("Classic Assorted", "Country Symbol Set 8.5x6 in"),
    "4A 8663": ("Classic Assorted", "Country Symbol Set 8.5x6 in"),
    "4A GM8663": ("Classic Assorted", "Country Symbol Set 8.5x6 in (GM)"),
    "4A 0127": ("Classic Assorted", "Coffee Theme Set 8.5x6 in"),
    "4A 8664": ("Classic Assorted", "Coffee Theme Set 8.5x6 in"),
    "4A 0128": ("Multicolor Assorted", "Vintage Carriage Set 4.5x6 in"),
    "4A 0129": ("Classic Assorted", "Cute Designs Set 6x3 in (Style A)"),
    "4A 0130": ("Classic Assorted", "Cute Designs Set 6x3 in (Style B)"),
    "4A SCGM70001x8": ("Classic Assorted", "Cute Printed Value Pack 4.8x2.2 in (8 Pads)"),
}

evict_to_bigpad = {
    "4A BP 1111-Nx4": ("Bright Ultra Colors", "4 Pads (11 x 11 in)"),
    "4A GMBP 1111-Nx4": ("Bright Ultra Colors", "4 Pads (11 x 11 in)"),
    "4A BP 1111-Px4": ("Pastel Assorted", "4 Pads (11 x 11 in)"),
    "4A GMBP 1111-Px4": ("Pastel Assorted", "4 Pads (11 x 11 in)"),
    "4A BP 1515-Nx4": ("Bright Ultra Colors", "4 Pads (15 x 15 in)"),
    "4A GMBP 1515-Nx4": ("Bright Ultra Colors", "4 Pads (15 x 15 in)"),
}

evict_to_markers = {
    "4A073": ("White", "Divider Sticky Notes 3.38 x 2.75 in (12 Pads)"),
    "4A 40607": ("White", "Divider Sticky Notes 3.38 x 2.75 in (12 Pads)"),
}

clean_303_active = {
    "4A 010": ("Neon Assorted", "6 Pads Lined (3 x 3 in)"),
    "4A 303 x 6-N-L": ("Neon Assorted", "6 Pads Lined (3 x 3 in)"),
    "AAAA 4A 303x6-N-L": ("Bright Ultra Colors", "6 Pads Lined (3 x 3 in)"),
    "4A GMSC303x6-B": ("Black", "6 Pads Flat (3 x 3 in)"),
    "4A SC303x6-B": ("Black", "6 Pads Flat (3 x 3 in)"),
    "4A 018": ("Pastel Assorted", "12 Pads Pop-Up (3 x 3 in)"),
    "4A 303 x12-Z": ("Pastel Assorted", "12 Pads Pop-Up (3 x 3 in)"),
    "4A 019": ("Neon Assorted", "12 Pads Pop-Up (3 x 3 in)"),
    "4A 303 x12-N-Z": ("Neon Assorted", "12 Pads Pop-Up (3 x 3 in)"),
    "4A ST303X12NZ": ("Bright Ultra Colors", "12 Pads Pop-Up (3 x 3 in)"),
    "4A GM303x18-Y": ("Canary Yellow", "18 Pads Flat (3 x 3 in)"),
    "4A GM303x6-Y-L*3": ("Canary Yellow", "18 Pads Lined (3 x 3 in)"),
    "4A 303S-20": ("Bright Ultra Colors", "20 Pads Super Sticky (3 x 3 in)"),
    "4A GM303S-20": ("Bright Ultra Colors", "20 Pads Super Sticky (3 x 3 in)"),
    "4A GM303Sx12*2": ("Bright Ultra Colors", "24 Pads Super Sticky (3 x 3 in)"),
    "4A 194": ("Bright Ultra Colors", "24 Pads Super Sticky (3 x 3 in)"),
    "4A 303Sx12": ("Bright Ultra Colors", "24 Pads Super Sticky (3 x 3 in)"),
}

target_skus_order = [
    # Group A: Batch 14/16/18 follow-up & catalog locks (6 SKUs)
    "4A 0166",
    "4A 039",
    "4A 040",
    "4A 037",
    "4A 60238",
    "4A SF-60238",
    # Group B: 5082 Family Unification + Pack Clarity (4 SKUs)
    "4A 5082-Y-Lx2",
    "4A 5082-Y-L",
    "4A 5082-Y-L-GM",
    "4A 5082-Y-L-FBA",
    # Group C: VOC Full Adhesive (11 SKUs) + Roll Dispenser (3 SKUs)
    "4A 302-Full Adhesive-400",
    "4A 303-Full Adhesive-400",
    "4A GM303-Full Adhesive-400",
    "4A 303-Full Adhesive",
    "4A 304 Full Glue",
    "4A 304-Full Adhesive-400",
    "4A GM304-Full Adhesive-400",
    "AAAA 4A 304-Full Glue",
    "4A 305-Full Adhesive",
    "4A 305-Full Adhesive-300",
    "4A GM305-Full Adhesive-300",
    "4A SCPSS 32x6",
    "4A GM-SCPSS 32x6",
    "4A PSS 32x6",
    # Group D: 406x6 Family Unification & MFN Package Weight / Shipping Fixes (8 SKUs)
    "4A 033",
    "4A 406x6",
    "4A 034",
    "4A 406x6-N",
    "4A GM406x6-N",
    "AAAA 4A 406x6-N",
    "4A GM406x6-N*2",
    "4A 406x6-N*2",
    # Group E: Remaining Expired Stop Selling Dates + '4A Parcel 7.99 plus 2.99 per lb'
    "4A 003",
    "4A GM302-Full Glue*3",
    "4A GM30512-L",
    "4A GM5088-N-L",
]

# Append Group F SKUs (avoiding duplicates)
for s in list(evict_to_bigpad) + list(evict_to_novelty) + list(evict_to_markers) + list(clean_303_active):
    if s not in target_skus_order and s in cat_by_sku:
        target_skus_order.append(s)

rows_to_write = []
for sku in target_skus_order:
    r = list(cat_by_sku[sku])
    r[4] = "Edit (Partial Update)"
    r[9] = None
    r[10] = "4A"
    for u_col in (374, 376, 378, 380, 382, 384):
        if r[u_col] == "IN":
            r[u_col] = "Inches"

    if sku == "4A 0166":
        r[58] = "White-atlantic Ocean"
        r[59] = "Novelty Die-Cut Shape (Pack 60)"
        r[62] = None
    elif sku == "4A 039":
        r[8] = "4A Sticky Notes 3x3 Inches, Orange & Pink, 8 Pads/Pack, 72 Sheets/Pad (4A 039)"
        r[58] = "Orange&pink"
    elif sku == "4A 040":
        r[8] = "4A Sticky Notes 3x3 Inches, Red & Pink, 8 Pads/Pack, 72 Sheets/Pad (4A 040)"
        r[58] = "Red&pink"
    elif sku == "4A 037":
        r[8] = "4A Sticky Notes 3x3 Inches, Green & Yellow, 8 Pads/Pack, 72 Sheets/Pad (4A 037)"
        r[58] = "Green&yellow"
    elif sku in ("4A 60238", "4A SF-60238"):
        r[8] = "4A Sticky Notes Cube 2.75x2.75 Inches, Bright Assorted Colors, 1 Cube, 360 Sheets (4A 60238)"
        r[58] = "Colors-60238"
        r[59] = "Standard Size (Pack 31)"
    elif sku == "4A 5082-Y-Lx2":
        r[8] = "4A Lined Sticky Notes 5x8 Inches, Canary Yellow, 4 Pads Total (2 Packs of 2 Pads, 100 Sheets/Pad, 400 Sheets Total)"
        r[44] = "VALUE BUNDLE OF 4 PADS TOTAL (400 SHEETS): Includes 2 factory-sealed packs of 2 pads (4 pads total, 100 lined sheets per pad, 400 sheets total) in classic Canary Yellow."
        r[56] = 4
        r[57] = 1
        r[58] = "Canary Yellow"
        r[59] = "4 Pads Lined (2 Packs of 2, 5 x 8 in)"
    elif sku in ("4A 5082-Y-L", "4A 5082-Y-L-GM", "4A 5082-Y-L-FBA"):
        r[56] = 2
        r[58] = "Canary Yellow"
        r[59] = "2 Pads Lined (5 x 8 in, 100 Sheets/Pad)"
        if sku == "4A 5082-Y-L-GM":
            r[340] = 10.99
            r[347] = 10.99
            r[356] = 10.99
    elif sku in (
        "4A 302-Full Adhesive-400",
        "4A 303-Full Adhesive-400",
        "4A GM303-Full Adhesive-400",
        "4A 303-Full Adhesive",
        "4A 304 Full Glue",
        "4A 304-Full Adhesive-400",
        "4A GM304-Full Adhesive-400",
        "AAAA 4A 304-Full Glue",
        "4A 305-Full Adhesive",
        "4A 305-Full Adhesive-300",
        "4A GM305-Full Adhesive-300",
    ):
        r[44] = full_adhesive_b1
        r[45] = full_adhesive_b2
        if sku in ("4A 303-Full Adhesive-400", "4A GM303-Full Adhesive-400"):
            r[59] = "3 x 3 in"
        elif sku in ("4A 304-Full Adhesive-400", "4A GM304-Full Adhesive-400"):
            r[59] = "3 x 4 in (Pack 4)"
        elif sku in ("4A 305-Full Adhesive-300", "4A GM305-Full Adhesive-300"):
            r[59] = "3 x 5 in (Pack 11)"
        if sku == "4A 304 Full Glue":
            r[340] = 9.99
            r[347] = 9.99
            r[356] = 9.99
            r[364] = 9.49
            r[365] = "2026-11-01"
            r[366] = "2026-12-31"
        elif sku in ("4A 302-Full Adhesive-400", "4A 304-Full Adhesive-400", "4A 305-Full Adhesive", "4A 305-Full Adhesive-300"):
            r[340] = 9.99
            r[347] = 9.99
            r[356] = 9.99
            r[364] = 9.49
            r[365] = "2026-11-01"
            r[366] = "2026-12-31"
        elif sku == "AAAA 4A 304-Full Glue":
            r[340] = 8.99
            r[347] = 8.99
            r[356] = 8.99
            r[364] = 8.54
            r[365] = "2026-11-01"
            r[366] = "2026-12-31"
    elif sku in ("4A SCPSS 32x6", "4A GM-SCPSS 32x6", "4A PSS 32x6"):
        r[44] = roll_tape_b1
        r[45] = roll_tape_b2
        if sku in ("4A SCPSS 32x6", "4A GM-SCPSS 32x6"):
            r[59] = "Standard Size (Pack 38)"
    elif sku in ("4A 033", "4A 406x6"):
        r[5] = "Child"
        r[6] = "PARENT-4A-406-MEDIUM-PADS"
        r[7] = "COLOR/SIZE"
        r[58] = "Pastel Assorted"
        r[59] = "6 Pads Unlined (4 x 6 in)"
        r[379], r[380] = 6.0, "Inches"
        r[381], r[382] = 4.0, "Inches"
        r[383], r[384] = 2.35, "Inches"
        r[385], r[386] = 1.4, "Pounds"
        if sku == "4A 033":
            r[372] = "Migrated Template"
    elif sku in ("4A 034", "4A 406x6-N"):
        r[5] = "Child"
        r[6] = "PARENT-4A-406-MEDIUM-PADS"
        r[7] = "COLOR/SIZE"
        r[58] = "Neon Assorted"
        r[59] = "6 Pads Unlined (4 x 6 in)"
        r[379], r[380] = 6.0, "Inches"
        r[381], r[382] = 4.0, "Inches"
        r[383], r[384] = 2.35, "Inches"
        r[385], r[386] = 1.4, "Pounds"
        if sku == "4A 034":
            r[372] = "Migrated Template"
    elif sku in ("4A GM406x6-N", "AAAA 4A 406x6-N"):
        r[5] = "Child"
        r[6] = "PARENT-4A-406-MEDIUM-PADS"
        r[7] = "COLOR/SIZE"
        r[58] = "Bright Ultra Colors"
        r[59] = "6 Pads Unlined (4 x 6 in)"
        r[379], r[380] = 6.0, "Inches"
        r[381], r[382] = 4.0, "Inches"
        r[383], r[384] = 2.35, "Inches"
        r[385], r[386] = 1.4, "Pounds"
        if sku == "4A GM406x6-N":
            r[372] = "Migrated Template"
    elif sku in ("4A GM406x6-N*2", "4A 406x6-N*2"):
        r[5] = "Child"
        r[6] = "PARENT-4A-406-MEDIUM-PADS"
        r[7] = "COLOR/SIZE"
        r[58] = "Bright Ultra Colors"
        r[59] = "12 Pads Unlined (2 Packs of 6, 4 x 6 in)"
        r[379], r[380] = 6.0, "Inches"
        r[381], r[382] = 4.7, "Inches"
        r[383], r[384] = 4.0, "Inches"
        r[385], r[386] = 2.8, "Pounds"
        if sku == "4A GM406x6-N*2":
            r[372] = "Cube delivery"
    elif sku in ("4A 003", "4A GM302-Full Glue*3"):
        r[355] = "2099-12-31T00:00:00.000Z"
        r[372] = "Migrated Template"
    elif sku in ("4A GM30512-L", "4A GM5088-N-L"):
        r[372] = "Big size delivery"

    # Group F: Evict misplaced non-3x3 SKUs & clean up PARENT-4A-303-CLASSIC-SQUARE
    if sku in evict_to_bigpad:
        r[5] = "Child"
        r[6] = "PARENT-4A-BIGPAD-MEETING-EASEL"
        r[7] = "COLOR/SIZE"
        r[58], r[59] = evict_to_bigpad[sku]
        if sku in ("4A GMBP 1111-Nx4", "4A GMBP 1111-Px4"):
            r[372] = "Big size delivery"
    elif sku in evict_to_novelty:
        r[5] = "Child"
        r[6] = "PARENT-4A-SHAPED-NOVELTY-PADS"
        r[7] = "COLOR/SIZE"
        r[58], r[59] = evict_to_novelty[sku]
    elif sku in evict_to_markers:
        r[5] = "Child"
        r[6] = "PARENT-4A-PAPER-PAGE-MARKERS"
        r[7] = "COLOR/SIZE"
        r[58], r[59] = evict_to_markers[sku]
    elif sku in clean_303_active:
        r[5] = "Child"
        r[6] = "PARENT-4A-303-CLASSIC-SQUARE"
        r[7] = "COLOR/SIZE"
        r[58], r[59] = clean_303_active[sku]
        if sku == "4A GM303S-20":
            r[372] = "Cube delivery"

    rows_to_write.append(r)

if __name__ == "__main__":
    shutil.copy2(shell_path, out_work)
    wb = openpyxl.load_workbook(out_work, keep_vba=True)
    ws = wb["Template"]

    if ws.max_row >= 7:
        ws.delete_rows(7, ws.max_row - 6)

    for row_idx, r_vals in enumerate(rows_to_write, start=7):
        for col_idx, val in enumerate(r_vals, start=1):
            ws.cell(row=row_idx, column=col_idx, value=val)

    wb.save(out_work)
    wb.close()
    shutil.copy2(out_work, out_desk)

    sha = hashlib.sha256(open(out_desk, "rb").read()).hexdigest()
    print(f"Rebuilt {out_desk} with {len(rows_to_write)} rows | SHA256: {sha}")
