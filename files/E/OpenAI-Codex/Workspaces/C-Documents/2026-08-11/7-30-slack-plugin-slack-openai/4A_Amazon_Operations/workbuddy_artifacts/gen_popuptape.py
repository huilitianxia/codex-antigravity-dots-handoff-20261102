import openpyxl

rows = [
    (79, "Scotch® Pop-up Tape Mountable Dispenser", "", "",
     "", "无在售",
     "两次 Sellersprite 搜索(Scotch Pop-up Tape / Scotch Pop-up Tape Dispenser)均0命中，导出返回的全是普通 Desktop Tape Dispenser(配Magic Tape的C60/C18/C19座)，非Pop-up专用结构；该产品在亚马逊美国站无独立在售listing(2013价仅2.49，低价配件)，标无在售"),
    (83, "Scotch® Pop-Up Tape Refill Strips", "", "",
     "", "无在售",
     "同上，两次搜索均未命中Pop-up Tape补充条 listing；与行79一并标无在售"),
]

wb = openpyxl.Workbook()
sh = wb.active
sh.title = "PopupTape核对"
header = ["行号", "原产品名", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
sh.append(header)
for r in rows:
    sh.append(list(r))

widths = [6, 38, 14, 12, 12, 10, 65]
for i, w in enumerate(widths, 1):
    sh.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_ScotchPopupTape核对表.xlsx"
wb.save(out)
print("已生成:", out, "行数:", len(rows))
