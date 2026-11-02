import openpyxl

cat_report_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb = openpyxl.load_workbook(cat_report_path, data_only=True)
ws = wb['Template']

print("Searching for all children of PARENT-4A-PSS-ROLL-TAPE or PSS:")
for r in range(4, ws.max_row + 1):
    sku = ws.cell(r, 3).value
    parent = ws.cell(r, 7).value
    title = ws.cell(r, 2).value
    color = ws.cell(r, 59).value
    size = ws.cell(r, 60).value
    num_items = ws.cell(r, 57).value
    asin = ws.cell(r, 13).value
    
    if parent == 'PARENT-4A-PSS-ROLL-TAPE' or (sku and 'pss' in str(sku).lower()) or (parent and 'pss' in str(parent).lower()):
        print(f"Row {r:3d} | SKU: {str(sku):25s} | Parent: {str(parent):25s} | ASIN: {str(asin):10s} | Color: {str(color):15s} | Size: {str(size):25s} | NumItems: {num_items}")

wb.close()
