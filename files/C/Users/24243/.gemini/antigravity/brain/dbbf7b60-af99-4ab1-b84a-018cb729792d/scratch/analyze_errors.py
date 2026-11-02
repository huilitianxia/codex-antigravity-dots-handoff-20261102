import openpyxl
from collections import Counter

file_path = r'd:\下载文件\4A_全店21大家族精细化变体清洗_终极纯净版-processing-summary (1).xlsm'
wb = openpyxl.load_workbook(file_path, data_only=True)
ws_fps = wb['Feed Processing Summary']

headers = [ws_fps.cell(1, c).value for c in range(1, ws_fps.max_column + 1)]
print("Feed Processing Summary Headers:", headers)

error_types = Counter()
error_rows = []

for r in range(2, ws_fps.max_row + 1):
    vals = [ws_fps.cell(r, c).value for c in range(1, ws_fps.max_column + 1)]
    if any(vals):
        # usually columns: Original record number, SKU, Error code, Error type, Error message
        sku = vals[1] if len(vals) > 1 else ''
        err_code = vals[2] if len(vals) > 2 else ''
        err_type = vals[3] if len(vals) > 3 else ''
        err_msg = vals[4] if len(vals) > 4 else ''
        
        err_key = f"{err_code} ({err_type})"
        error_types[err_key] += 1
        error_rows.append({
            'row': r,
            'sku': sku,
            'code': err_code,
            'type': err_type,
            'msg': err_msg
        })

print(f"\nTotal error / warning entries: {len(error_rows)}")
print("\nError counts by type/code:")
for err, count in error_types.most_common():
    print(f"  {err}: {count}")

print("\nSample errors for each error code:")
seen_codes = set()
for it in error_rows:
    code = it['code']
    if code not in seen_codes:
        seen_codes.add(code)
        print(f"\n--- Code {code} (Type: {it['type']}) | SKU: {it['sku']} ---")
        msg = str(it['msg'])
        print(f"Message: {msg[:300]}")
