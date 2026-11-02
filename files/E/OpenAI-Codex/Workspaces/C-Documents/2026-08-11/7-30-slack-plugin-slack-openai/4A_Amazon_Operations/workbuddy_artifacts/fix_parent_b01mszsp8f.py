import openpyxl

f = r"E:/Desktop/4A-SL缺货评分好款_父体已修正.xlsx"
wb = openpyxl.load_workbook(f, data_only=False)
ws = wb["被低估好款_最终版"]

hdr = {ws.cell(row=1, column=c).value: c for c in range(1, ws.max_column+1)}
col_P = hdr["兄弟在售ASIN"]
col_Q = hdr["已被兄弟替代"]

# find B01MSZSP8F row
row = None
for r in range(2, ws.max_row+1):
    if ws.cell(row=r, column=1).value == "B01MSZSP8F":
        row = r; break
assert row is not None, "B01MSZSP8F not found"

ws.cell(row=row, column=col_P).value = "B01N1T23HH, B01N7IT411"
ws.cell(row=row, column=col_Q).value = "否(兄弟为同款不同色:B01N1T23HH橙粉/B01N7IT411红粉,均Active,本品绿红停售)"

wb.save(f)
print(f"Row {row} (B01MSZSP8F) updated: P='B01N1T23HH, B01N7IT411', Q annotated")
