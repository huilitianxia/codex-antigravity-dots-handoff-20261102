import os
import shutil
import zipfile
import openpyxl

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]

# Map target SKUs to which infographic(s) they should get
full_glue_skus = [
    "4A 302-Full Adhesive-400",   # B0F2TKL2P5 (340 FBA)
    "4A 303-Full Adhesive-400",   # B07QXJYTZ7 (Cash Cow #1)
    "4A 303-Full Adhesive",       # B0F9L7BVCW
    "4A 304 Full Glue",           # B00SMEFFRE (333 FBA)
    "4A 304-Full Adhesive-400",   # B07QXJWDPL (533 FBA)
    "AAAA 4A 304-Full Glue",      # B07FK975YB (372 FBA)
    "4A 305-Full Adhesive",       # B0FBG138ND (428 FBA)
    "4A 305-Full Adhesive-300",   # B07QXJZKHC (174 FBA)
    "AAAA 4A 305-Full Glue",      # B07FK73B92 (60 FBA)
]
roll_skus = [
    "4A SCPSS 32x6",              # B08DKJ2K3T
    "4A PSS 32x6",                # B08CVLH794
]
pack_skus = [
    "4A 5082-Y-Lx2",              # B0F9L5G6XQ
]

all_targets = set(full_glue_skus + roll_skus + pack_skus)

rows_by_sku = {}
for r in ws.iter_rows(min_row=7, values_only=True):
    if r and len(r) > 42 and r[2] in all_targets:
        rows_by_sku[r[2]] = r

src_dir = r"D:\4A\00_当前工作区_202611\voc_infographics"
img_flagship = os.path.join(src_dir, "00_NanoBanana_Plus_Factory_Full_Adhesive_Guide_2000x2000.jpg")
img_roll = os.path.join(src_dir, "02_PSS_32x6_Roll_Dispenser_Clean_Cut_Guide_2000x2000.jpg")
img_5082 = os.path.join(src_dir, "03_5082_Y_Lx2_4Pads_Packaging_Clarity_2000x2000.jpg")

work_bulk_dir = os.path.join(src_dir, "amazon_bulk_auto_assign")
desk_bulk_dir = r"E:\Desktop\voc_infographics_买家之声防退货附图\直接全选拖入亚马逊批量上传_自动分配"
os.makedirs(work_bulk_dir, exist_ok=True)
os.makedirs(desk_bulk_dir, exist_ok=True)

generated = []
for sku in full_glue_skus + roll_skus + pack_skus:
    if sku not in rows_by_sku:
        continue
    r = rows_by_sku[sku]
    asin = str(r[12]).strip()
    # Check occupied PT01..PT08 (Cols 34..41 -> PT01..PT08)
    occupied = [idx for idx in range(1, 9) if r[33 + idx]]
    max_pt = max(occupied) if occupied else 0
    # Choose next empty slot (or PT08 if all 8 are occupied)
    target_pt = min(max_pt + 1, 8)
    pt_code = f"PT0{target_pt}"

    if sku in full_glue_skus:
        src_img = img_flagship
    elif sku in roll_skus:
        src_img = img_roll
    else:
        src_img = img_5082

    fname = f"{asin}.{pt_code}.jpg"
    dst1 = os.path.join(work_bulk_dir, fname)
    dst2 = os.path.join(desk_bulk_dir, fname)
    shutil.copy2(src_img, dst1)
    shutil.copy2(src_img, dst2)
    generated.append((sku, asin, occupied, fname))
    print(f"{sku:26s} | ASIN={asin} | Occupied PT={occupied} -> Assigned: {fname}")

# Also create a single ZIP file on Desktop in case user wants to upload a ZIP in Bulk Image Upload
zip_path_work = os.path.join(src_dir, "Amazon_Bulk_Images_Auto_Assign.zip")
zip_path_desk = r"E:\Desktop\voc_infographics_买家之声防退货附图\Amazon_Bulk_Images_Auto_Assign.zip"
with zipfile.ZipFile(zip_path_work, "w", zipfile.ZIP_DEFLATED) as zf:
    for _, _, _, fname in generated:
        zf.write(os.path.join(work_bulk_dir, fname), arcname=fname)
shutil.copy2(zip_path_work, zip_path_desk)
print("Created ZIP:", zip_path_desk)
