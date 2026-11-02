import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

wb_19r = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\04_正式处理回执\19-voc-copy-and-pack-clarity-fixes-processing-summary.xlsm", read_only=True, data_only=True)
ws_19r = wb_19r["Template"]
rows = list(ws_19r.iter_rows(min_row=3, max_row=20, values_only=True))
h4 = rows[1]
h5 = rows[2]
r17 = rows[14]  # Row 17 (4A 302-Full Adhesive-400)
for idx, (n4, n5, v) in enumerate(zip(h4, h5, r17)):
    if v is not None and idx >= 270:
        print(f"Receipt 0-idx {idx:3d} ({openpyxl.utils.get_column_letter(idx+1):3s}): {str(n4):45s} | {str(n5)[:38]:38s} | val={v}")
