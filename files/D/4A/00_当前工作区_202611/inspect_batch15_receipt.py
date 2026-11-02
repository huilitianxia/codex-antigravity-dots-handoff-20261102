import openpyxl
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

src = r"D:\下载文件\15-vc-classics-shipping-and-spec-fixes-processing-summary.xlsm"
dst = r"D:\4A\00_Codex交接给Gemini_20261101\04_正式处理回执\15-vc-classics-shipping-and-spec-fixes-processing-summary.xlsm"
shutil.copy2(src, dst)

wb = openpyxl.load_workbook(src, data_only=True)
ws_sum = wb['Feed Processing Summary']
print("=== FEED PROCESSING SUMMARY (BATCH 15) ===")
for r in range(1, ws_sum.max_row + 1):
    vals = [ws_sum.cell(r, c).value for c in range(1, 12)]
    if any(vals):
        print(f"Row {r:2d}: {vals}")

ws_tpl = wb['Template']
print("\n=== TEMPLATE ROWS (BATCH 15) ===")
for r in range(7, 35):
    sku = ws_tpl.cell(r, 5).value
    status = ws_tpl.cell(r, 1).value
    errs = ws_tpl.cell(r, 2).value
    warns = ws_tpl.cell(r, 3).value
    if sku or status:
        print(f"Row {r:2d} | Status={str(status):22} | Err={errs} | Warn={warns} | SKU={sku}")
