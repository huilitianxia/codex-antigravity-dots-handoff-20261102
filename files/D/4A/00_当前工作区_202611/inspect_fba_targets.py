import json
import openpyxl

target_skus = ['4A 039', '4A 040', '4A 037', '4A 0166', '4A095', '4A 66114', '4A 095']
target_asins = ['B01N1T23HH', 'B01N7IT411', 'B01M617ZTH', 'B0784GHSVJ', 'B01M2UDADZ']

# 1. Check 分类商品报告_10-31-2026.xlsm
cat_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb = openpyxl.load_workbook(cat_path, data_only=True)
ws = wb['Template']

print("=== CHECKING SKUS IN 分类商品报告_10-31-2026.xlsm ===")
found_in_cat = {}
for r in range(4, ws.max_row + 1):
    sku = ws.cell(r, 3).value
    asin = ws.cell(r, 13).value
    pt = ws.cell(r, 4).value
    color = ws.cell(r, 59).value
    mfr = ws.cell(r, 20).value
    title = ws.cell(r, 2).value
    parent = ws.cell(r, 7).value
    action = ws.cell(r, 5).value
    
    for t_sku in target_skus:
        if sku == t_sku:
            found_in_cat[sku] = {
                'row': r,
                'sku': sku,
                'asin': asin,
                'pt': pt,
                'action': action,
                'parent': parent,
                'title': title,
                'color': color,
                'manufacturer': mfr,
                'all_populated': {openpyxl.utils.get_column_letter(c): (ws.cell(4, c).value, ws.cell(r, c).value) 
                                  for c in range(1, ws.max_column + 1) if ws.cell(r, c).value is not None}
            }

for s, data in found_in_cat.items():
    print(f"\nSKU: {s} (Row {data['row']})")
    print(f"  ASIN: {data['asin']}, PT: {data['pt']}, Color: '{data['color']}', Mfr: '{data['manufacturer']}', Parent: '{data['parent']}'")
    print(f"  Title: {data['title'][:100]}...")

wb.close()

# 2. Check 12-processing-receipt-audit.json
audit_path = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\12-processing-receipt-audit.json'
with open(audit_path, 'r', encoding='utf-8') as f:
    audit_data = json.load(f)

print("\n=== CHECKING 12-processing-receipt-audit.json FOR TARGET SKUS / ASINS ===")
# Audit data structure could be list or dict
# Let's inspect its keys/elements
if isinstance(audit_data, dict):
    print("Audit data keys:", list(audit_data.keys())[:10])
    # check if there's errors/items/records
    for k, v in audit_data.items():
        if isinstance(v, list):
            print(f"Key '{k}' has {len(v)} items")
elif isinstance(audit_data, list):
    print(f"Audit data is list with {len(audit_data)} items")

def search_obj(obj, prefix=""):
    results = []
    if isinstance(obj, dict):
        # check if this dict represents an error/record
        obj_str = str(obj)
        match = False
        for s in target_skus + target_asins:
            if s in obj_str:
                match = True
                break
        if match:
            results.append(obj)
    elif isinstance(obj, list):
        for item in obj:
            results.extend(search_obj(item, prefix))
    return results

# Let's search entries in audit_data
matches = []
if isinstance(audit_data, list):
    for idx, item in enumerate(audit_data):
        item_str = json.dumps(item, ensure_ascii=False)
        for s in target_skus + target_asins:
            if s in item_str:
                matches.append((idx, s, item))
                break
elif isinstance(audit_data, dict):
    for k, v in audit_data.items():
        v_str = json.dumps(v, ensure_ascii=False)
        for s in target_skus + target_asins:
            if s in v_str:
                matches.append((k, s, v))
                break

print(f"Total matching records in 12-processing-receipt-audit.json: {len(matches)}")
for key, term, item in matches:
    print(f"\n--- Matched '{term}' at key/index '{key}' ---")
    print(json.dumps(item, ensure_ascii=False, indent=2)[:500])
