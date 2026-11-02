import openpyxl

rows = [
    # 行号, 原产品名, 匹配ASIN, 亚马逊价格, 链接, 置信度, 备注
    (77, "Scotch® Magic™ Tape Shoe Dispenser - Zebra", "B00OB5SOQ2", 22.99,
     "https://www.amazon.com/dp/B00OB5SOQ2", "近似",
     "导出无 Zebra 花纹造型座 listing；取同系列动物造型座 Scotch Cat-810 (C810) 近似。2013价$9.99，现价$22.99（造型座涨价，Zebra 款式可能已下架）"),
    (167, "Scotch® Magic™ Tape Dispenser - Dog", "B00EY5GUYM", 24.5,
     "https://www.amazon.com/dp/B00EY5GUYM", "较准",
     "Scotch Dog Dispenser C31 + Magic Tape，明确 Dog 造型座匹配。2013价$9.99，现价$24.5（造型座涨价）"),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "ScotchDispenser"
hdr = ["行号", "原产品名", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
ws.append(hdr)
for r in rows:
    ws.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6]])

# 列宽
widths = [6, 42, 12, 14, 42, 8, 60]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_ScotchDispenser核对表.xlsx"
wb.save(out)
print("已生成:", out)
for r in rows:
    print(f"行{r[0]} | {r[2]} | ${r[3]} | {r[5]}")
