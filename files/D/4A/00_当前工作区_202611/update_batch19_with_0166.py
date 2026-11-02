import os
import shutil
import json
import hashlib
import openpyxl
from PIL import Image, ImageDraw, ImageFont

out_dir = r"D:\4A\00_当前工作区_202611\voc_infographics"
art_dir = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d"
desk_img_dir = r"E:\Desktop\voc_infographics_买家之声防退货附图"

def get_font(size, bold=True):
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

# Build 2000x2000 flagship composite combining NanoBanana 2.1 (voc_instructional_infographic_1.png) + Factory Real Pad (702877118504.pt01.jpg)
nb_img = Image.open(os.path.join(out_dir, "voc_instructional_infographic_1.png")).convert("RGB")
canvas0 = Image.new("RGB", (2000, 2000), (248, 250, 252))
draw0 = ImageDraw.Draw(canvas0)

# Header
draw0.rounded_rectangle((40, 35, 1960, 225), radius=26, fill=(15, 23, 42))
draw0.text((1000, 98), "HOW TO PEEL FLAT & PREVENT CURLING", font=get_font(64, True), fill=(255, 255, 255), anchor="mm")
draw0.text((1000, 175), "90% Full Adhesive Back + 10% Non-Stick Grip Edge — Peel Sideways for 100% Flat Hold", font=get_font(36, False), fill=(253, 224, 71), anchor="mm")

# Left side: NanoBanana 2.1 1:1 action comparison scaled to 1160x1160
nb_resized = nb_img.resize((1160, 1160), Image.Resampling.LANCZOS)
draw0.rounded_rectangle((36, 256, 1204, 1424), radius=24, fill=(255, 255, 255), outline=(203, 213, 225), width=4)
canvas0.paste(nb_resized, (40, 260))

# Right side: Real 4A Pad Anatomy (702877118504.pt01.jpg + 305-FULL-GLUE-8.jpg)
draw0.rounded_rectangle((1230, 256, 1960, 1424), radius=24, fill=(255, 255, 255), outline=(30, 64, 175), width=4)
draw0.rounded_rectangle((1230, 256, 1960, 350), radius=24, fill=(30, 64, 175))
draw0.text((1595, 303), "REAL PAD DESIGN", font=get_font(38, True), fill=(255, 255, 255), anchor="mm")

img_pt01 = Image.open(r"D:\4A\印刷用图片\电商\亚马逊图片-2018\6-----4A Full Adhesive Notes\302-FULL GLUE\702877118504.pt01.jpg").convert("RGB")
img_pt01.thumbnail((680, 560), Image.Resampling.LANCZOS)
canvas0.paste(img_pt01, (1595 - img_pt01.width // 2, 380))

img_strip = Image.open(r"D:\4A\印刷用图片\电商\亚马逊图片-2018\6-----4A Full Adhesive Notes\305-FULL GLUE\305-FULL-GLUE-8.jpg").convert("RGB")
img_strip.thumbnail((680, 220), Image.Resampling.LANCZOS)
canvas0.paste(img_strip, (1595 - img_strip.width // 2, 980))

draw0.rounded_rectangle((1255, 1185, 1935, 1395), radius=18, fill=(239, 246, 255), outline=(59, 130, 246), width=3)
draw0.text((1595, 1235), "Dashed Line = Cover Sheet Only!", font=get_font(32, True), fill=(30, 58, 138), anchor="mm")
draw0.text((1595, 1290), "All inner sheets are 100% blank", font=get_font(28, False), fill=(30, 64, 175), anchor="mm")
draw0.text((1595, 1332), "& unperforated (10% glue-free edge", font=get_font(28, False), fill=(30, 64, 175), anchor="mm")
draw0.text((1595, 1372), "at bottom for easy side-peeling).", font=get_font(28, False), fill=(30, 64, 175), anchor="mm")

# Bottom Banner: Best Surfaces
draw0.rounded_rectangle((40, 1460, 1960, 1960), radius=26, fill=(255, 255, 255), outline=(203, 213, 225), width=4)
draw0.rounded_rectangle((40, 1460, 1960, 1555), radius=26, fill=(15, 23, 42))
draw0.text((1000, 1508), "APPLY TO CLEAN, DRY, SMOOTH SURFACES FOR MAXIMUM HOLD", font=get_font(40, True), fill=(255, 255, 255), anchor="mm")

surfaces = [
    ("Monitors & Screens", "Stays 100% flat without dropping", (22, 163, 74), (240, 253, 244)),
    ("Notebooks & Planners", "Flush full-back hold in bags", (22, 163, 74), (240, 253, 244)),
    ("Glass, Fridges & Doors", "Resists drafts & page flipping", (22, 163, 74), (240, 253, 244)),
    ("Wipe Dusty Walls First", "Best on smooth, dry surfaces", (217, 119, 6), (254, 252, 232)),
]
for idx, (title, desc, col, bg) in enumerate(surfaces):
    x0 = 70 + idx * 470
    x1 = x0 + 440
    draw0.rounded_rectangle((x0, 1595, x1, 1925), radius=20, fill=bg, outline=col, width=3)
    draw0.text(((x0 + x1) // 2, 1705), title, font=get_font(31, True), fill=col, anchor="mm")
    draw0.text(((x0 + x1) // 2, 1795), desc, font=get_font(26, False), fill=(51, 65, 85), anchor="mm")

out0 = os.path.join(out_dir, "00_NanoBanana_Plus_Factory_Full_Adhesive_Guide_2000x2000.jpg")
canvas0.save(out0, quality=95)
shutil.copy2(out0, os.path.join(art_dir, os.path.basename(out0)))
shutil.copy2(out0, os.path.join(desk_img_dir, os.path.basename(out0)))
print("Saved composite:", out0)

# Now update Batch 19 to include:
# - 4A 0166 (Row 7): Color (58) = 'White-atlantic Ocean', Color Map (254) = None, Package units (380,382,384) = 'Inches', Col 10 (Item Highlight) = None
# - 4A 039, 4A 040, 4A 037, 4A 60238, 4A SF-60238: keep their exact unlocked Colors + clear Col 10 (Item Highlight, 0-based index 10 = Excel Col K!)
# - All 15 VOC SKUs: also clear Col 10 (Item Highlight, 0-based index 10 = Excel Col K)

from build_batch19_voc_fixes import updates_by_sku, cat_by_sku, h4, tpl_path, out_xlsm, audit_json

extra_batch18_clean = {
    "4A 0166": {
        "reason": "Final 8541 color match on 4A 0166 (549 FBA units, B0784GHSVJ): set Color='White-atlantic Ocean' + Package Units='Inches' + clear Col K Item Highlight",
        "cols": {10: None, 54: "4A", 58: "White-atlantic Ocean", 254: None, 380: "Inches", 382: "Inches", 384: "Inches"},
    },
    "4A 039": {
        "reason": "Clear Col K (index 10) Item Highlight on 4A 039 while preserving unlocked Color='Orange&pink' and Manufacturer='4A'",
        "cols": {10: None, 54: "4A", 58: "Orange&pink", 254: "Orange"},
    },
    "4A 040": {
        "reason": "Clear Col K (index 10) Item Highlight on 4A 040 while preserving unlocked Color='Red&pink' and Manufacturer='4A'",
        "cols": {10: None, 54: "4A", 58: "Red&pink", 254: "Red"},
    },
    "4A 037": {
        "reason": "Clear Col K (index 10) Item Highlight on 4A 037 while preserving unlocked Color='Green&yellow' and Manufacturer='4A'",
        "cols": {10: None, 54: "4A", 58: "Green&yellow", 254: "Green"},
    },
    "4A 60238": {
        "reason": "Clear Col K (index 10) Item Highlight on 4A 60238 while preserving unlocked Color='Colors-60238' and Manufacturer='4A'",
        "cols": {10: None, 54: "4A", 58: "Colors-60238", 254: "Multicolor"},
    },
    "4A SF-60238": {
        "reason": "Clear Col K (index 10) Item Highlight on 4A SF-60238 while preserving unlocked Color='Colors-60238' and Manufacturer='4A'",
        "cols": {10: None, 54: "4A", 58: "Colors-60238", 254: "Multicolor"},
    },
}

combined_updates = {}
combined_updates.update(extra_batch18_clean)
for k, v in updates_by_sku.items():
    v["cols"][10] = None  # Excel Col K is 0-based index 10!
    combined_updates[k] = v

wb_out = openpyxl.load_workbook(tpl_path, keep_vba=True)
ws_out = wb_out["Template"]
if ws_out.max_row > 7:
    ws_out.delete_rows(8, ws_out.max_row - 7)

audit_records = []
row_idx = 7
for sku, spec in combined_updates.items():
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

print(f"Updated {out_xlsm} | Rows={len(audit_records)} | SHA256={sha256_val}")
