import openpyxl

master_path = r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx'
wb = openpyxl.load_workbook(master_path, data_only=True)
ws = wb['Sheet1']

headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]

targets = ['B01N1T23HH', 'B01N7IT411', 'B01M617ZTH', 'B0784GHSVJ', 'B01M2UDADZ',
           '4A 039', '4A 040', '4A 037', '4A 0166', '4A095', '4A 66114']

print("=== SEARCHING MASTER SHEET FOR ALL TARGETS ===")
for r in range(2, ws.max_row + 1):
    row_vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
    row_str = ' '.join([str(v) for v in row_vals if v is not None])
    for t in targets:
        if t.lower() in row_str.lower():
            sku = ws.cell(r, 1).value
            vc_asin = ws.cell(r, 3).value
            sl_asin = ws.cell(r, 5).value
            title = ws.cell(r, 6).value
            print(f"Row {r:3d} matched '{t}': SKU='{sku}', VC_ASIN='{vc_asin}', SL_ASIN='{sl_asin}'")
            print(f"   Title: {str(title)[:100]}")
            break

wb.close()
