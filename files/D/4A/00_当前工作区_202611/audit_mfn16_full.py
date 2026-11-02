import json
import openpyxl
import os
import re

# 1. Load residual62-closeout.json
path_json = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\residual62-closeout.json'
with open(path_json, 'r', encoding='utf-8') as f:
    closeout_data = json.load(f)

mfn_rows = [r for r in closeout_data['rows'] if r.get('inventory_group') == '仅MFN有申报库存']

# 2. Category report data
cat_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb_cat = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws_cat = wb_cat['Template']

cat_by_sku = {}
for row_idx, row in enumerate(ws_cat.iter_rows(min_row=6, values_only=True), start=6):
    sku = str(row[2]).strip() if row[2] is not None else ""
    if sku:
        cat_by_sku[sku] = {
            'row_idx': row_idx,
            'title': row[1],
            'sku': row[2],
            'product_type': row[3],
            'parentage_level': row[5],
            'parent_sku': row[6],
            'item_name': row[8],
            'product_id_type': row[11],
            'product_id': row[12],
            'model_number': row[17],
            'manufacturer': row[19],
            'color': row[58],
            'color_map': row[254]
        }
wb_cat.close()

# 3. Master sheet data
master_path = r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx'
wb_m = openpyxl.load_workbook(master_path, read_only=True, data_only=True)

master_rows_s1 = []
for r_idx, row in enumerate(wb_m['Sheet1'].iter_rows(min_row=2, values_only=True), start=2):
    master_rows_s1.append((r_idx, row))

master_rows_s3 = []
for r_idx, row in enumerate(wb_m['Sheet3'].iter_rows(min_row=2, values_only=True), start=2):
    master_rows_s3.append((r_idx, row))

wb_m.close()

# 4. Image search helpers
img_base_2021 = r'D:\4A\印刷用图片\电商\亚马逊图片-2021'
img_base_2018 = r'D:\4A\印刷用图片\电商\亚马逊图片-2018'

print(f"Loaded {len(mfn_rows)} MFN rows.")
