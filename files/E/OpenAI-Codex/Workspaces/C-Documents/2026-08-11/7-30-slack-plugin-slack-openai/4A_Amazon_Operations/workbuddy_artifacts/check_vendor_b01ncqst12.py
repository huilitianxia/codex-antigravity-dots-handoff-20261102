import openpyxl, os, re

paths = [
    r"E:/Desktop/亚马逊供应商和开店总表-2026 (1).xlsx",
    r"E:/Desktop/亚马逊供应商和开店总表-2023.xlsx",
    r"E:/Desktop/供应商和开店总表.xlsx",
    r"C:/Users/24243/WorkBuddy/2026-07-24-20-10-20/亚马逊供应商和开店总表-2023.xlsx"
]

keywords = ["B01N0QNOCN", "B01NCQST12", "702877118610", "702877118603", "4A001", "301x12-N"]

for p in paths:
    if not os.path.exists(p):
        continue
    print("="*70); print("FILE:", p)
    wb = openpyxl.load_workbook(p, data_only=True)
    for ws in wb.worksheets:
        found_any = False
        # find header row (may not be row 1)
        for hr in range(1, min(ws.max_row, 10)+1):
            hdr = [ws.cell(row=hr, column=c).value for c in range(1, ws.max_column+1)]
            if any(kw in [str(v).upper() for v in hdr if v] for kw in ["ASIN", "UPC", "SKU"]):
                break
        else:
            hr = 1
        hdr = [ws.cell(row=hr, column=c).value for c in range(1, ws.max_column+1)]
        for r in range(hr+1, ws.max_row+1):
            vals = [ws.cell(row=r, column=c).value for c in range(1, ws.max_column+1)]
            svals = [str(v).upper() for v in vals if v is not None]
            if any(k.upper() in svals for k in keywords):
                if not found_any:
                    print(f"  Sheet: {ws.title} | header row {hr}")
                    found_any = True
                print(f"    Row {r}:")
                for i, v in enumerate(vals):
                    if v is not None:
                        h = hdr[i] if i < len(hdr) else f"col{i+1}"
                        print(f"      {h} = {v}")
    wb.close()
