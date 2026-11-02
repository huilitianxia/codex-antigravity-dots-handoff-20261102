import openpyxl

rows = [
    (74, "Scotch® Double Sided Tape Dispensered Rolls", "B00006IF63", 5.99,
     "https://www.amazon.com/dp/B00006IF63", "较准",
     "665 系列带座卷装(0.75in x 400in)，价完全匹配2013的5.99；源数据未指定尺寸。备选B00004Z47L(0.5in x 250in 带座 $4.7)为更经典标准款"),
]

wb = openpyxl.Workbook()
sh = wb.active
sh.title = "DoubleSided核对"
header = ["行号", "原产品名", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
sh.append(header)
for r in rows:
    sh.append(list(r))

widths = [6, 40, 14, 12, 40, 8, 55]
for i, w in enumerate(widths, 1):
    sh.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_ScotchDoubleSided核对表.xlsx"
wb.save(out)
print("已生成:", out, "行数:", len(rows))
