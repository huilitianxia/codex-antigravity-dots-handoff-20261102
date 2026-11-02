import openpyxl

file_path = r'd:\下载文件\4A_全店21大家族精细化变体清洗_终极纯净版-processing-summary (1).xlsm'
wb = openpyxl.load_workbook(file_path, data_only=True)
ws_tpl = wb['Template']

print("--- 30315 Rows in Template Sheet ---")
for r in range(7, ws_tpl.max_row + 1):
    sku = str(ws_tpl.cell(r, 5).value or '')
    parent = str(ws_tpl.cell(r, 9).value or '')
    status = ws_tpl.cell(r, 1).value
    num_errs = ws_tpl.cell(r, 2).value
    if '30315' in sku or '30315' in parent:
        title = str(ws_tpl.cell(r, 11).value or '')[:40]
        asin = str(ws_tpl.cell(r, 15).value or '')
        color = str(ws_tpl.cell(r, 54).value or '')
        size = str(ws_tpl.cell(r, 55).value or '')
        print(f"Row {r:3d} | Status: {status:25s} | Errs: {num_errs} | SKU: {sku:20s} | Parent: {parent:30s} | Size: {size}")
