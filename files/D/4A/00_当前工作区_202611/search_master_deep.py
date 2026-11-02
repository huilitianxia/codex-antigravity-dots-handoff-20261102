import openpyxl

master_path = r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx'
wb_m = openpyxl.load_workbook(master_path, read_only=True, data_only=True)

search_terms = ['B00V9Z5PS2', 'PSS', '9-5', 'B07FK8CRM9', 'GM40624', '40624', '702877119600', '702877123140']

for sheet in wb_m.sheetnames:
    ws = wb_m[sheet]
    for r_idx, row in enumerate(ws.iter_rows(values_only=True), start=1):
        row_str = " | ".join(str(c) for c in row if c is not None)
        for term in search_terms:
            if term.lower() in row_str.lower():
                print(f"[{sheet} R{r_idx}] Found '{term}': {row_str[:120]}")

wb_m.close()
