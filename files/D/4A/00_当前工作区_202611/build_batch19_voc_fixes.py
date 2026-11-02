import os
import shutil
import json
import hashlib
import openpyxl
from PIL import Image, ImageDraw, ImageFont

# 1. Re-render 01_Full_Adhesive_How_To_Peel_Flat_2000x2000.jpg with clean 28pt font on 4th surface card
out_dir = r"D:\4A\00_当前工作区_202611\voc_infographics"
art_dir = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d"
desk_img_dir = r"E:\Desktop\voc_infographics_买家之声防退货附图"
os.makedirs(out_dir, exist_ok=True)
os.makedirs(desk_img_dir, exist_ok=True)

with open(r"D:\4A\00_当前工作区_202611\build_voc_infographics.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace('font=get_font(33, True), fill=col, anchor="mm")', 'font=get_font(29, True), fill=col, anchor="mm")')
with open(r"D:\4A\00_当前工作区_202611\build_voc_infographics.py", "w", encoding="utf-8") as f:
    f.write(code)

exec(compile(code, r"D:\4A\00_当前工作区_202611\build_voc_infographics.py", "exec"))

for fname in [
    "01_Full_Adhesive_How_To_Peel_Flat_2000x2000.jpg",
    "02_PSS_32x6_Roll_Dispenser_Clean_Cut_Guide_2000x2000.jpg",
    "03_5082_Y_Lx2_4Pads_Packaging_Clarity_2000x2000.jpg",
]:
    src = os.path.join(out_dir, fname)
    shutil.copy2(src, os.path.join(art_dir, fname))
    shutil.copy2(src, os.path.join(desk_img_dir, fname))

# 2. Build Batch 19: 19-voc-copy-and-pack-clarity-fixes.xlsm
cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
tpl_path = r"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\13-0146-office-only.xlsm"
out_xlsm = r"D:\4A\00_当前工作区_202611\19-voc-copy-and-pack-clarity-fixes.xlsm"
audit_json = r"D:\4A\00_当前工作区_202611\batch19_cell_audit.json"

wb_cat = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws_cat = wb_cat["Template"]
cat_rows = list(ws_cat.iter_rows(values_only=True))
h4 = cat_rows[3]
h5 = cat_rows[4]
cat_by_sku = {r[2]: r for r in cat_rows[6:] if r and len(r) > 2 and r[2]}

# Helper to build 5 anti-curl bullets for Full-Adhesive pads while preserving exact size/sheet specs in B1 & B3
def make_full_adhesive_bullets(b1_text, size_str):
    b2 = (
        "90% Full Adhesive Back + 10% Non-Stick Grip Edge: Coated with full-back adhesive so notes lay flush against smooth surfaces without flipping or falling off, while a narrow bottom non-stick strip makes each sheet easy to grab and peel cleanly without residue."
    )
    b3 = (
        f"How to Peel Flat Without Curling ({size_str}): Start at the bottom non-stick grip edge and peel SIDE-TO-SIDE (horizontally) rather than pulling straight up from the bottom. Note: the black dashed line is printed on the top cover sheet only—all inner sheets are 100% blank and unperforated."
    )
    b4 = (
        "Thick No-Bleed Paper & Vibrant Neon Colors: Made of durable, recyclable paper that writes smoothly with ballpoint pens, gel pens, markers, and pencils without ink bleed-through, in bright eye-catching colors that keep key reminders visible."
    )
    b5 = (
        "Best for Clean, Dry, Smooth Surfaces: Adheres firmly to computer monitors, glass, notebooks, planners, binders, refrigerators, and smooth doors or cabinets. Wipe dusty or textured walls clean and dry before applying for maximum hold."
    )
    return {44: b1_text, 45: b2, 46: b3, 47: b4, 48: b5, 9: None}

roll_bullets = {
    44: "6 Rolls Full Adhesive Sticky Notes with Dispensers: Includes 6 rolls of full-adhesive sticky note tape (0.6 in x 393 in / 15 mm x 10 m per roll) in 6 bright neon colors, each housed in a refillable serrated plastic dispenser.",
    45: "How to Dispense & Cut Cleanly: Keep the paper strip threaded under the clear front guide bar, pull out your desired length, press your thumb lightly on top of the roll to hold it steady, and tear diagonally at a 45-degree angle across the serrated blade.",
    46: "Full-Back Adhesive & Residue-Free Removal: Full adhesive coating across the back keeps strips completely flat on books, documents, monitors, planners, and containers without curling up, and peels off cleanly without leaving sticky residue.",
    47: "Custom Length for Any Label or Tab: Easily cut a tiny flag for page marking or a long strip for file folders, storage bins, cables, spice jars, and study notes—no pre-cut size waste.",
    48: "Portable & Organized for Home, School & Office: Compact roll dispensers fit neatly in pencil cases, desk drawers, and bags while protecting the sticky note roll from dust and edge damage.",
    9: None,
}

updates_by_sku = {
    # 1. 4A 5082-Y-Lx2 (B0F9L5G6XQ) - VOC 14.29% NCX "False advertising only 2 packs"
    "4A 5082-Y-Lx2": {
        "reason": "Fix VOC 'only received 2 packs' return on B0F9L5G6XQ: clarify in Title & Bullet 1/5 that 4 Pads (200 Sheets) are delivered as 2 shrink-wrapped twin-packs (each wrap contains 2 stacked 50-sheet pads)",
        "cols": {
            8: "4A 4 Pads Lined Sticky Notes 5 x 8 in (2 Twin-Packs of 2 Stacked Pads), Pastel Yellow Sticky Notes with Lines for Home Office School Supplies, 50 Sheets/Pad, 200 Sheets Total, 4A 5082-Y-Lx2",
            44: "4 Pads Value Bundle (Delivered as 2 Twin-Packs of 2 Stacked Pads): Includes 4 Pads of 5 x 8 in Pastel Yellow Lined Sticky Notes (50 Sheets/Pad, 200 Sheets Total). Each shrink-wrapped pack contains 2 pads stacked together (100 sheets per pack)—please open the outer film wrap to separate the 2 pads inside!",
            45: "Pastel Yellow with Ruled Lines: Soft pastel yellow paper reduces eye strain while crisp ruled lines keep your handwriting neat, structured, and easy to read at a glance.",
            46: "Large 5 x 8 Inch Writing Space: Generous 5 x 8 in size gives you plenty of room for daily to-do lists, meeting action items, project checklists, lecture notes, and phone messages.",
            47: "Reliable Repositionable Adhesive: Top-edge adhesive sticks securely to monitors, desk pads, notebooks, folders, and smooth walls, and removes cleanly without tearing paper or leaving sticky residue.",
            48: "Packaging Note for Buyers: Your order arrives as 2 factory-sealed shrink-wrapped bricks; each brick is labeled '2 Pads / 50 Sheets / 100 Sheets' on the front band (2 Packs x 2 Pads = 4 Pads / 200 Sheets Total).",
            9: None,
        },
    },
    # 2. Full Adhesive SKUs (302, 303, 304, 305)
    "4A 302-Full Adhesive-400": {
        "reason": "VOC anti-curl horizontal peel instruction + cover-only dashed line clarification for 302-Full Adhesive-400 (B0F2TKL2P5, 340 FBA units)",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 2 in (400 Sheets Total): Includes 1 Cube Pack of Full Adhesive Sticky Notes 3 x 2 in, 5 Bright Neon Colors, 80 Sheets/Color, 400 Sheets Total.",
            "3 x 2 Inches",
        ),
    },
    "4A 303-Full Adhesive-400": {
        "reason": "VOC anti-curl horizontal peel instruction + cover-only dashed line clarification for 303-Full Adhesive-400 (B07QXJYTZ7, Cash Cow #1)",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 3 in (400 Sheets Total): Includes 1 Cube Pack of Full Adhesive Sticky Notes 3 x 3 in, 5 Bright Neon Colors, 80 Sheets/Color, 400 Sheets Total.",
            "3 x 3 Inches",
        ),
    },
    "4A GM303-Full Adhesive-400": {
        "reason": "Sync MFN twin 4A GM303-Full Adhesive-400 on ASIN B07QXJYTZ7 with exact same 5 anti-curl bullets",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 3 in (400 Sheets Total): Includes 1 Cube Pack of Full Adhesive Sticky Notes 3 x 3 in, 5 Bright Neon Colors, 80 Sheets/Color, 400 Sheets Total.",
            "3 x 3 Inches",
        ),
    },
    "4A 303-Full Adhesive": {
        "reason": "VOC anti-curl horizontal peel instruction for 4A 303-Full Adhesive (B0F9L7BVCW)",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 3 in (100 Sheets Total): Includes 5 Pads of Full Adhesive Sticky Notes 3 x 3 in, 5 Bright Neon Colors, 20 Sheets/Pad, 100 Sheets Total.",
            "3 x 3 Inches",
        ),
    },
    "4A 304 Full Glue": {
        "reason": "VOC anti-curl horizontal peel instruction for 4A 304 Full Glue (B00SMEFFRE, 333 FBA units, 68 orders/30d)",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 4 in (100 Sheets Total): Includes 5 Pads of Full Adhesive Sticky Notes 3 x 4 in, 5 Bright Neon Colors, 20 Sheets/Pad, 100 Sheets Total.",
            "3 x 4 Inches",
        ),
    },
    "4A 304-Full Adhesive-400": {
        "reason": "VOC anti-curl horizontal peel instruction for 4A 304-Full Adhesive-400 (B07QXJWDPL, 533 FBA units)",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 4 in (400 Sheets Total): Includes 5 Pads of Full Adhesive Sticky Notes 3 x 4 in, 5 Bright Neon Colors, 80 Sheets/Pad, 400 Sheets Total.",
            "3 x 4 Inches",
        ),
    },
    "4A GM304-Full Adhesive-400": {
        "reason": "Sync MFN twin 4A GM304-Full Adhesive-400 on ASIN B07QXJWDPL with exact same 5 anti-curl bullets",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 4 in (400 Sheets Total): Includes 5 Pads of Full Adhesive Sticky Notes 3 x 4 in, 5 Bright Neon Colors, 80 Sheets/Pad, 400 Sheets Total.",
            "3 x 4 Inches",
        ),
    },
    "AAAA 4A 304-Full Glue": {
        "reason": "VOC anti-curl horizontal peel instruction for AAAA 4A 304-Full Glue (B07FK975YB, 372 FBA units)",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 4 in (200 Sheets Total): Includes 10 Pads of Full Adhesive Sticky Notes 3 x 4 in, 5 Bright Neon Colors, 20 Sheets/Pad, 200 Sheets Total.",
            "3 x 4 Inches",
        ),
    },
    "4A 305-Full Adhesive": {
        "reason": "VOC anti-curl horizontal peel instruction for 4A 305-Full Adhesive (B0FBG138ND, 428 FBA units, 123 orders/30d)",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 5 in (100 Sheets Total): Includes 5 Pads of Full Adhesive Sticky Notes 3 x 5 in, 5 Bright Neon Colors, 20 Sheets/Pad, 100 Sheets Total.",
            "3 x 5 Inches",
        ),
    },
    "4A 305-Full Adhesive-300": {
        "reason": "VOC anti-curl horizontal peel instruction for 4A 305-Full Adhesive-300 (B07QXJZKHC, 174 FBA units)",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 5 in (300 Sheets Total): Includes 5 Pads of Full Adhesive Sticky Notes 3 x 5 in, 5 Bright Neon Colors, 60 Sheets/Pad, 300 Sheets Total.",
            "3 x 5 Inches",
        ),
    },
    "4A GM305-Full Adhesive-300": {
        "reason": "Sync MFN twin 4A GM305-Full Adhesive-300 on ASIN B07QXJZKHC with exact same 5 anti-curl bullets",
        "cols": make_full_adhesive_bullets(
            "Full Adhesive Sticky Notes 3 x 5 in (300 Sheets Total): Includes 5 Pads of Full Adhesive Sticky Notes 3 x 5 in, 5 Bright Neon Colors, 60 Sheets/Pad, 300 Sheets Total.",
            "3 x 5 Inches",
        ),
    },
    # 3. Roll Sticky Notes with Dispenser (PSS 32x6)
    "4A SCPSS 32x6": {
        "reason": "VOC 45-degree clean cut dispenser instruction for 4A SCPSS 32x6 (B08DKJ2K3T)",
        "cols": roll_bullets,
    },
    "4A GM-SCPSS 32x6": {
        "reason": "Sync MFN twin 4A GM-SCPSS 32x6 on ASIN B08DKJ2K3T with exact same 5 dispenser instructions",
        "cols": roll_bullets,
    },
    "4A PSS 32x6": {
        "reason": "Populate missing 5 Bullet Points + 45-degree clean cut dispenser instruction on 4A PSS 32x6 (B08CVLH794)",
        "cols": roll_bullets,
    },
}

wb_out = openpyxl.load_workbook(tpl_path, keep_vba=True)
ws_out = wb_out["Template"]
if ws_out.max_row > 7:
    ws_out.delete_rows(8, ws_out.max_row - 7)

audit_records = []
row_idx = 7
for sku, spec in updates_by_sku.items():
    base_row = list(cat_by_sku[sku])
    diffs = {}
    base_row[4] = "Edit (Partial Update)"
    for c_idx, new_val in spec["cols"].items():
        old_val = base_row[c_idx]
        base_row[c_idx] = new_val
        diffs[f"Col_{c_idx}_{h4[c_idx]}"] = {"old": old_val, "new": new_val}
    for c_idx, val in enumerate(base_row, 1):
        ws_out.cell(row=row_idx, column=c_idx, value=val)
    audit_records.append({
        "row": row_idx,
        "sku": sku,
        "asin": base_row[12],
        "reason": spec["reason"],
        "changes": diffs,
    })
    row_idx += 1

wb_out.save(out_xlsm)
shutil.copy2(out_xlsm, r"E:\Desktop\19-voc-copy-and-pack-clarity-fixes.xlsm")
sha256_val = hashlib.sha256(open(out_xlsm, "rb").read()).hexdigest()

with open(audit_json, "w", encoding="utf-8") as f:
    json.dump({"file": out_xlsm, "sha256": sha256_val, "row_count": len(audit_records), "rows": audit_records}, f, ensure_ascii=False, indent=2)

print(f"Built {out_xlsm} | Rows={len(audit_records)} | SHA256={sha256_val}")
