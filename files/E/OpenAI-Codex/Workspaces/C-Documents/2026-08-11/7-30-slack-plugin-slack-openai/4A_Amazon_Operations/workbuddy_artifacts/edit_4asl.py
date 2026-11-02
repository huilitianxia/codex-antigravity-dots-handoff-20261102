import openpyxl
from difflib import SequenceMatcher

target = r"E:/Desktop/4A-SL缺货评分好款.xlsx"
wb = openpyxl.load_workbook(target, data_only=False)
ws = wb["被低估好款_最终版"]

# ---- ROW 11 fix: restore "4A " prefix in column B (商品标题_官方) ----
b11 = ws.cell(row=11, column=2).value
print("Row11 B (before):", repr(b11))
if b11 and not b11.startswith("4A "):
    new_b11 = "4A " + b11
    ws.cell(row=11, column=2).value = new_b11
    print("Row11 B (after ):", repr(new_b11))
else:
    print("Row11 B already has 4A prefix or empty; left unchanged.")

# ---- ROW 12 fill: B01MSZSP8F ----
official_title = ("4A Sticky Notes,6 x 8 Inches,Large Size,Neon Green&Red,Lined,"
                  "Self-Stick Notes,100 Sheets/Pad,2 Pads/Pack,4A 608x2-N-L-GR")
batch_title   = ("Sticky Notes,6 x 8 Inches,Large Size,Neon Green&Red,Lined,"
                  "Self-Stick Notes,100 Sheets/Pad,2 Pads/Pack,4A 608x2-N-L-GR")
sim = round(SequenceMatcher(None, official_title, batch_title).ratio(), 2)

row12 = {
    1:  "B01MSZSP8F",                       # A ASIN
    2:  official_title,                     # B 商品标题_官方
    3:  batch_title,                        # C 商品标题_批量查询
    4:  "Inactive",                         # D 官方状态
    5:  9.99,                               # E 价格_官方
    6:  5.0,                                # F 评分
    7:  1,                                  # G 评分数
    8:  "批量查询(标题已校验)",              # H 评分来源
    9:  "极低(<=2评)",                       # I 置信度
    10: "缺货/Inactive",                     # J 在售信号
    11: "标准便利贴",                        # K 推断品类
    12: "高",                               # L 补评分优先级
    13: sim,                                # M 标题相似度
    14: False,                              # N 数据冲突
    15: "B07KR9LD68",                       # O 父ASIN
    16: None,                               # P 兄弟在售ASIN
    17: "否(父体下无在售兄弟)",              # Q 已被兄弟替代
    18: "被低估好款_最终版",                  # R 最终分类
}
for col, val in row12.items():
    ws.cell(row=12, column=col).value = val

print("\nRow12 filled:")
for col in range(1, 19):
    h = ws.cell(row=1, column=col).value
    print(f"  {openpyxl.utils.get_column_letter(col)} [{h}] = {ws.cell(row=12, column=col).value}")

out = r"E:/Desktop/4A-SL缺货评分好款_已填入两款.xlsx"
wb.save(out)
print("\nSaved (new file):", out)
print("(Original locked by another app; wrote to a new file to avoid losing your edits.)")
