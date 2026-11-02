import openpyxl

rows = [
    (84, "Scotch® Mounting Squares", "B0002V28ES", 3.88,
     "https://www.amazon.com/dp/B0002V28ES", "较准",
     "Permanent Mounting Squares 1in x 1in White Foam 16 Squares，价3.88极接近2013的3.79；系列名完全匹配"),
    (85, "Scotch® Mounting Tape", "B00004Z4BU", 7.33,
     "https://www.amazon.com/dp/B00004Z4BU", "较准",
     "Scotch 4010 Clear Mounting Tape 1in x 60in，经典Mounting Tape款，价接近2013的8.59；备选B0007P5G8Y(314H-MED Indoor 1in x 125in $4.79)"),
]

wb = openpyxl.Workbook()
sh = wb.active
sh.title = "Mounting核对"
header = ["行号", "原产品名", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
sh.append(header)
for r in rows:
    sh.append(list(r))

widths = [6, 32, 14, 12, 40, 8, 55]
for i, w in enumerate(widths, 1):
    sh.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_ScotchMounting核对表.xlsx"
wb.save(out)
print("已生成:", out, "行数:", len(rows))
