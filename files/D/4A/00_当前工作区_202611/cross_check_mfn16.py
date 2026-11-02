import json
import openpyxl
import os

# 1. Load residual62-closeout.json
path_json = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\residual62-closeout.json'
with open(path_json, 'r', encoding='utf-8') as f:
    closeout_data = json.load(f)

mfn_rows = [r for r in closeout_data['rows'] if r.get('inventory_group') == '仅MFN有申报库存']
target_skus = {r['sku']: r for r in mfn_rows}
print(f"Target SKUs count: {len(target_skus)}")

# 2. Query 分类商品报告_10-31-2026.xlsm
cat_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb_cat = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws_cat = wb_cat['Template']

cat_data = {}
for row_idx, row in enumerate(ws_cat.iter_rows(min_row=6, values_only=True), start=6):
    sku = row[2]
    if sku in target_skus or (sku and any(sku.strip() == t_sku.strip() for t_sku in target_skus)):
        matched_target = sku if sku in target_skus else [t for t in target_skus if t.strip() == sku.strip()][0]
        cat_data[matched_target] = {
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
            'color': row[58]
        }
wb_cat.close()

print(f"Matched in category report: {len(cat_data)} / {len(target_skus)}")
for sku in target_skus:
    if sku not in cat_data:
        print(f"  NOT FOUND IN CAT REPORT: {sku}")

# 3. Query Master Sheet
master_path = r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx'
wb_m = openpyxl.load_workbook(master_path, read_only=True, data_only=True)

master_matches = {sku: [] for sku in target_skus}

# Check Sheet1
ws_s1 = wb_m['Sheet1']
for r_idx, row in enumerate(ws_s1.iter_rows(min_row=2, values_only=True), start=2):
    sku_val = str(row[0]) if row[0] is not None else ""
    asin_val = str(row[2]) if row[2] is not None else ""
    asin_sl_val = str(row[4]) if row[4] is not None else ""
    upc_vc = str(row[1]) if row[1] is not None else ""
    upc_sl = str(row[3]) if row[3] is not None else ""
    title = str(row[6]) if row[6] is not None else ""
    
    for t_sku, t_row in target_skus.items():
        t_asin = t_row.get('asin', '')
        # check if matches sku or asin
        matched = False
        if t_sku.lower().replace(" ", "") == sku_val.lower().replace(" ", "") and sku_val:
            matched = True
        elif t_asin and (t_asin in asin_val or t_asin in asin_sl_val):
            matched = True
        
        if matched:
            master_matches[t_sku].append({
                'sheet': 'Sheet1',
                'row_idx': r_idx,
                'master_sku': sku_val,
                'upc_vc': upc_vc,
                'asin_vc': asin_val,
                'upc_sl': upc_sl,
                'asin_sl': asin_sl_val,
                'title': title,
                'mfn_logistics': str(row[7]),
                'carton_qty': str(row[8]),
                'fob': str(row[9]),
                'cost': str(row[10]),
                'list_price': str(row[11]),
                'sale_price': str(row[12])
            })

# Check Sheet3
ws_s3 = wb_m['Sheet3']
for r_idx, row in enumerate(ws_s3.iter_rows(min_row=2, values_only=True), start=2):
    upc_vc = str(row[0]) if row[0] is not None else ""
    asin_vc = str(row[1]) if row[1] is not None else ""
    upc_sl = str(row[2]) if row[2] is not None else ""
    asin_sl = str(row[3]) if row[3] is not None else ""
    sku_val = str(row[4]) if row[4] is not None else ""
    title = str(row[6]) if row[6] is not None else ""
    
    for t_sku, t_row in target_skus.items():
        t_asin = t_row.get('asin', '')
        matched = False
        if t_sku.lower().replace(" ", "") == sku_val.lower().replace(" ", "") and sku_val:
            matched = True
        elif t_asin and (t_asin in asin_vc or t_asin in asin_sl):
            matched = True
        
        if matched:
            master_matches[t_sku].append({
                'sheet': 'Sheet3',
                'row_idx': r_idx,
                'master_sku': sku_val,
                'upc_vc': upc_vc,
                'asin_vc': asin_vc,
                'upc_sl': upc_sl,
                'asin_sl': asin_sl,
                'title': title
            })

wb_m.close()

print(f"\nMaster sheet search results:")
for t_sku in target_skus:
    matches = master_matches[t_sku]
    print(f"  {t_sku}: {len(matches)} match(es)")
    for m in matches:
        print(f"    [{m['sheet']} R{m['row_idx']}] SKU:{m['master_sku']} | ASIN_VC:{m.get('asin_vc')} | ASIN_SL:{m.get('asin_sl')} | UPC_SL:{m.get('upc_sl')} | Title:{m.get('title')[:60]}")
