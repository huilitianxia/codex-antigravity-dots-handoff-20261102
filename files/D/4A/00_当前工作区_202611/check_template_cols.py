import openpyxl

cat_report_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb = openpyxl.load_workbook(cat_report_path, data_only=True)
ws = wb['Template']

print("=== TEMPLATE COLUMNS CHECK ===")
target_fields = ['SKU', 'Product Type', 'Listing Action', 'Record Action', 'Product Id Type', 'Product Id', 'Color', 'Manufacturer']

found = {}
for c in range(1, ws.max_column + 1):
    c_letter = openpyxl.utils.get_column_letter(c)
    lbl = ws.cell(4, c).value
    attr = ws.cell(5, c).value
    
    # Check specific targets
    if c in [3, 4, 5, 12, 13, 20, 59] or any(t.lower() in str(lbl).lower() or t.lower() in str(attr).lower() for t in target_fields):
        print(f"Col {c_letter} (Index {c}): Label(R4)='{lbl}', Attr(R5)='{attr}'")

# Check Valid Values sheet for Color, Manufacturer, Record Action, Product Id Type, Product Type
if 'Valid Values' in wb.sheetnames:
    ws_vv = wb['Valid Values']
    print(f"\n=== VALID VALUES SHEET (Max col: {ws_vv.max_column}, Max row: {ws_vv.max_row}) ===")
    # Print header row in Valid Values
    vv_headers = [ws_vv.cell(1, c).value or ws_vv.cell(2, c).value for c in range(1, ws_vv.max_column + 1)]
    for idx, h in enumerate(vv_headers, 1):
        if h:
            h_str = str(h)
            for t in ['color', 'manufacturer', 'record_action', 'action', 'product_type', 'type', 'id']:
                if t in h_str.lower():
                    # get first 5 valid values
                    vals = [ws_vv.cell(r, idx).value for r in range(3, min(ws_vv.max_row + 1, 15))]
                    vals = [v for v in vals if v is not None]
                    print(f"VV Col {openpyxl.utils.get_column_letter(idx)} ({idx}) '{h}': sample values -> {vals[:5]}")
                    break

wb.close()
