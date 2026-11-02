import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

print("Max rows in Template:", ws.max_row, "Max cols:", ws.max_column)

# Inspect headers in rows 1 to 6
for r in range(1, 7):
    print(f"Row {r} sample (cols 1-15):", [ws.cell(r, c).value for c in range(1, 16)])

target_skus = [
    # 5 FBA
    "4A 039", "4A 040", "4A 037", "4A 0166", "4A095",
    # 13 MFN
    "4A092", "4A PSS 9-5 NB", "4A 0153", "4A 0154", "4A 0155",
    "4A 0168", "4A 0169", "4A 0171", "4A 40606", "4A 5036",
    "4A 60238", "4A SF-60238", "4A093",
    # 1 MFN 99022
    "4A GM40624*2"
]

print(f"Searching for {len(target_skus)} target SKUs...")
sku_rows = {}
for r in range(7, ws.max_row + 1):
    val = ws.cell(r, 3).value # col C is SKU
    if val in target_skus:
        sku_rows[val] = r

print(f"Found {len(sku_rows)} of {len(target_skus)} SKUs:")
for sku in target_skus:
    row_idx = sku_rows.get(sku)
    if row_idx:
        ptype = ws.cell(row_idx, 4).value
        pid_type = ws.cell(row_idx, 12).value
        pid = ws.cell(row_idx, 13).value
        print(f"Found {sku:20} at row {row_idx:4d} | Product Type (col D): {ptype} | ID Type (col L): {pid_type} | ID (col M): {pid}")
    else:
        print(f"MISSING: {sku}")
