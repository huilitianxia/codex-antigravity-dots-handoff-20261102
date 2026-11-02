import openpyxl

rows = [
    # 行号, 原产品名, ASIN, 亚马逊价, 链接, 置信度, 备注
    (72, "Scotch® Home and Office Masking Tape", "B00347A8E4", 10.58,
     "https://www.amazon.com/dp/B00347A8E4", "较准",
     "3436 家庭办公系列 3 卷装(0.70in x 54.6yd)，价贴近2013的9.59；源数据仅写系列名未指定尺寸/卷数"),
]

wb = openpyxl.Workbook()
sh = wb.active
sh.title = "MaskingTape核对"
header = ["行号", "原产品名", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
sh.append(header)
for r in rows:
    sh.append(list(r))

# 列宽
widths = [6, 38, 14, 12, 40, 8, 50]
for i, w in enumerate(widths, 1):
    sh.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_ScotchMasking核对表.xlsx"
wb.save(out)
print("已生成:", out, "行数:", len(rows))
