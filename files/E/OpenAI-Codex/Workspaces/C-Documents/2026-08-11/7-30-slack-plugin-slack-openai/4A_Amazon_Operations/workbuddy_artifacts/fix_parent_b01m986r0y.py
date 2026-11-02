import openpyxl

src = r"E:/Desktop/4A-SL缺货评分好款_已填入两款.xlsx"
out = r"E:/Desktop/4A-SL缺货评分好款_父体已修正.xlsx"

wb = openpyxl.load_workbook(src, data_only=False)
ws = wb["被低估好款_最终版"]

# locate columns
hdr = {ws.cell(row=1, column=c).value: c for c in range(1, ws.max_column+1)}
col_O = hdr["父ASIN"]          # 15
col_P = hdr["兄弟在售ASIN"]     # 16
col_Q = hdr["已被兄弟替代"]     # 17

# find B01M986R0Y row
row = None
for r in range(2, ws.max_row+1):
    if ws.cell(row=r, column=1).value == "B01M986R0Y":
        row = r; break
assert row is not None, "B01M986R0Y not found"

# Apply edits
ws.cell(row=row, column=col_O).value = "B07JN9LKQZ"
ws.cell(row=row, column=col_P).value = "B07DJPQ7GW, B00SMEDVEI"
ws.cell(row=row, column=col_Q).value = "否(兄弟规格不同:24片装B07DJPQ7GW/Pop-up装B00SMEDVEI,均非本品2片装替代)"

# Also update row 12 (B01MSZSP8F) sibling check for consistency
# Its parent is B07KR9LD68 - verify siblings from official report
import csv
with open(r"E:/Desktop/所有商品报告_08-08-2026.txt", encoding="utf-8-sig", errors="replace") as f:
    rep = list(csv.reader(f, delimiter="\t"))
rep_hdr = rep[0]
asin_idx = rep_hdr.index("asin1")
status_idx = rep_hdr.index("status")
name_idx = rep_hdr.index("item-name")
# gather rows whose item-name contains "Sticky Notes" and status Active, to find B01MSZSP8F siblings
# Actually we don't reliably know B07KR9LD68 children without SellerSprite; skip auto-fill, note manual.

wb.save(out)
print("Saved:", out)
print(f"Row {row} updated: O=B07JN9LKQZ, P='B07DJPQ7GW, B00SMEDVEI', Q annotated")
