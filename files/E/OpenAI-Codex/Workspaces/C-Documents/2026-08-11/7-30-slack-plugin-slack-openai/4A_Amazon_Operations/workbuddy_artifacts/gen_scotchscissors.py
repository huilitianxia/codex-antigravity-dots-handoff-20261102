import openpyxl

rows = [
    # 行号, 原产品名, 匹配ASIN, 亚马逊价格, 链接, 置信度, 备注
    (78, "Scotch™ Precision Ultra Edge Titanium Scissors", "B004QJU99I", 9.98,
     "https://www.amazon.com/dp/B004QJU99I", "较准",
     "Precision Ultra-Edge Titanium Scissors, Pointed Tip, 8 Inch, Assorted Colors；名称完全匹配，价$9.98 极接近2013的$9.99。备选：B004OWIOD0(6-Pack $51.89)、B00SSVNNZC(3-Pack $19)"),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "ScotchScissors"
hdr = ["行号", "原产品名", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
ws.append(hdr)
for r in rows:
    ws.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6]])

widths = [6, 46, 12, 14, 42, 8, 60]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_ScotchScissors核对表.xlsx"
wb.save(out)
print("已生成:", out)
for r in rows:
    print(f"行{r[0]} | {r[2]} | ${r[3]} | {r[5]}")
