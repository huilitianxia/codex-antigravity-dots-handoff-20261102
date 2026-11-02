import openpyxl

cat_report_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
wb = openpyxl.load_workbook(cat_report_path, data_only=True)
print('Sheet names:', wb.sheetnames)

terms = ['PSS 32', 'PSS32', 'B08DKJ2K3T', 'B08CVLH794', '702877126561', '702877126578', 'B0HPTC18T2']
target_skus = ['4A GM-SCPSS 32x6', '4A SCPSS 32x6', '4A PSS 32x6']

template_sheet = wb['Template']
# In Amazon category templates, row 1 is group/category, row 2 is display name, row 3 is field name (attribute name)
# Let's verify rows 1, 2, 3
r1 = [template_sheet.cell(1, c).value for c in range(1, template_sheet.max_column + 1)]
r2 = [template_sheet.cell(2, c).value for c in range(1, template_sheet.max_column + 1)]
r3 = [template_sheet.cell(3, c).value for c in range(1, template_sheet.max_column + 1)]

print(f'Max columns: {template_sheet.max_column}, Max rows: {template_sheet.max_row}')

# Let's search all rows in Template sheet
matches = []
sku_rows = {}

for r in range(4, template_sheet.max_row + 1):
    row_vals = [template_sheet.cell(r, c).value for c in range(1, template_sheet.max_column + 1)]
    row_str = ' '.join([str(v) for v in row_vals if v is not None])
    
    sku_val = template_sheet.cell(r, 3).value # Column C is typically SKU
    if sku_val in target_skus:
        sku_rows[sku_val] = (r, row_vals)
    
    for t in terms:
        if t.lower() in row_str.lower():
            matches.append((r, t, sku_val))
            break

print(f'Matches in Template sheet: {len(matches)}')
for r, t, s in matches:
    print(f'  Row {r}: term="{t}", sku="{s}"')

print('\n=== Detailed dump for target SKUs ===')
for sku, (r, row_vals) in sku_rows.items():
    print(f'\n--- SKU: {sku} (Row {r}) ---')
    for c_idx, val in enumerate(row_vals, start=1):
        if val is not None:
            col_letter = openpyxl.utils.get_column_letter(c_idx)
            header_disp = r2[c_idx - 1]
            header_attr = r3[c_idx - 1]
            print(f'  Col {col_letter} ({c_idx}) [{header_attr} / {header_disp}]: {val}')

wb.close()
