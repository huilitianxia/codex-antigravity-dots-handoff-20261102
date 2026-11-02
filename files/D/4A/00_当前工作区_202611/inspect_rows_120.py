import openpyxl

master_path = r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx'
wb_m = openpyxl.load_workbook(master_path, read_only=True, data_only=True)
ws_s1 = wb_m['Sheet1']

for r_idx in range(120, 132):
    row = list(ws_s1.iter_rows(min_row=r_idx, max_row=r_idx, values_only=True))[0]
    print(f"R{r_idx}: SKU={row[0]} | UPC_VC={row[1]} | ASIN_VC={row[2]} | UPC_SL={row[3]} | ASIN_SL={row[4]} | Title={row[6][:50] if row[6] else ''}")

print("\n--- Sheet 3 rows around 40624 or 40606 ---")
ws_s3 = wb_m['Sheet3']
for r_idx, row in enumerate(ws_s3.iter_rows(values_only=True), start=1):
    row_str = " | ".join(str(c) for c in row if c is not None)
    if any(k in row_str for k in ['GM', '40624', 'PSS', '9-5', 'B00V9Z5PS2', 'B07FK8CRM9']):
        print(f"Sheet3 R{r_idx}: {row_str[:120]}")

wb_m.close()
