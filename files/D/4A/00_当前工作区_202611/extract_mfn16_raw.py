import json
import openpyxl
import os
import re

path_json = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\residual62-closeout.json'
with open(path_json, 'r', encoding='utf-8') as f:
    closeout_data = json.load(f)

mfn_rows = [r for r in closeout_data['rows'] if r.get('inventory_group') == '仅MFN有申报库存']

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

out = []
for idx, r in enumerate(mfn_rows):
    sku = r['sku']
    asin = r['asin']
    qty = r.get('exact_mfn_declared_quantity')
    conflicts = r.get('conflicting_fields')
    cat = cat_by_sku.get(sku.strip(), {})
    errors = r.get('errors', [])
    
    e8541 = [e for e in errors if str(e.get('code')) == '8541']
    e99022 = [e for e in errors if str(e.get('code')) == '99022']
    
    out.append({
        'idx': idx + 1,
        'sku': sku,
        'asin': asin,
        'qty': qty,
        'conflicts': conflicts,
        'cat_title': cat.get('title'),
        'cat_color': cat.get('color'),
        'cat_color_map': cat.get('color_map'),
        'cat_mfr': cat.get('manufacturer'),
        'cat_model': cat.get('model_number'),
        'cat_pt': cat.get('product_type'),
        'cat_parent': cat.get('parent_sku'),
        'cat_pid': cat.get('product_id'),
        'cat_pid_type': cat.get('product_id_type'),
        'e8541_msgs': [e.get('message') for e in e8541],
        'e99022_msgs': [e.get('message') for e in e99022],
    })

with open(r'D:\4A\00_当前工作区_202611\mfn16_raw_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print("Saved raw extraction to D:\\4A\\00_当前工作区_202611\\mfn16_raw_extracted.json")
