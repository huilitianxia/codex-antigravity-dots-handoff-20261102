import openpyxl

master_path = r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx'
wb = openpyxl.load_workbook(master_path, data_only=True)
ws = wb['Sheet1']

headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]

skus_to_check = ['4A 039', '4A 040', '4A 037', '4A 0166', '4A095', '4A 66114', '4A 095']

print("=== CHECKING MASTER SHEET FOR 5 FBA SKUS ===")
for r in range(2, ws.max_row + 1):
    sku = ws.cell(r, 1).value
    if sku in skus_to_check:
        print(f"\nRow {r}: SKU '{sku}'")
        for c in range(1, ws.max_column + 1):
            val = ws.cell(r, c).value
            h = headers[c - 1]
            if val is not None:
                print(f"  {h}: {val}")

wb.close()
