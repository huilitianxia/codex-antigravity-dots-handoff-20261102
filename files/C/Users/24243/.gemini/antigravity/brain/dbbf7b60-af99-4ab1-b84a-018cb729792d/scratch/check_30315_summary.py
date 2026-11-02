import openpyxl

file_path = r'd:\下载文件\4A_全店21大家族精细化变体清洗_终极纯净版-processing-summary (1).xlsm'
wb = openpyxl.load_workbook(file_path, data_only=True)
ws_tpl = wb['Template']

print("--- 30315 in Template Sheet of Processing Summary ---")
# Let's find columns
headers = [ws_tpl.cell(4, c).value for c in range(1, 20)]
print("Headers:", headers)

for r in range(7, ws_tpl.max_row + 1):
    sku = str(ws_tpl.cell(r, 2).value or '')
    if '30315' in sku or 'B07FKG29KB' in str([ws_tpl.cell(r, c).value for c in range(1, 15)]):
        vals = [ws_tpl.cell(r, c).value for c in range(1, 15)]
        # Also check error columns at the far right or status columns
        status_col = ws_tpl.cell(r, 1).value
        # Check last few columns
        err_info = [ws_tpl.cell(r, c).value for c in range(ws_tpl.max_column - 5, ws_tpl.max_column + 1) if ws_tpl.cell(r, c).value is not None]
        print(f"Row {r} | SKU: {sku} | Action: {ws_tpl.cell(r, 4).value} | Parent: {ws_tpl.cell(r, 6).value} | Status/Err: {status_col} {err_info}")
