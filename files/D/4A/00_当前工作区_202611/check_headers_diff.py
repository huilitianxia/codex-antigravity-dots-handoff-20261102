import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

wb = openpyxl.load_workbook(r"E:\Desktop\19-voc-copy-and-pack-clarity-fixes.xlsm", read_only=True, data_only=True)
ws = wb["Template"]
rows = list(ws.iter_rows(min_row=7, values_only=True))
print(f"Total rows in Batch 19: {len(rows)}")
for idx, r in enumerate(rows, start=7):
    in_units = [u for u in (374, 376, 378, 380, 382, 384) if r[u] == "IN"]
    print(
        f"Row {idx:2d}: SKU={str(r[2]):26s} | Act={r[4]} | Hi={r[9]} | Brand={r[10]} | "
        f"Color={str(r[58]):20s} | Size={str(r[59])[:32]:32s} | Wt={r[385]} | Tpl={r[372]} | Stop={r[355]} | IN={in_units}"
    )
