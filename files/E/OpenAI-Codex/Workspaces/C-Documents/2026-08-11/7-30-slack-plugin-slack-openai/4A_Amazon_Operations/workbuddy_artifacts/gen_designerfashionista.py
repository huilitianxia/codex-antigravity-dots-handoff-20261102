import openpyxl

rows = [
    # 行号, 原产品名, 匹配ASIN, 亚马逊价格, 链接, 置信度, 备注
    (103, "Post-it® Notes, 4 in x 6 in, Designer Cover, Fucshia Notes, Lined, 1 Pad/Pack", "", None,
     "", "无在售",
     "原 Designer Cover Fucshia 款式在亚马逊无独立 listing；现 Post-it 设计师系列改名 Polished Patterns（如 B0GPSF2ZQY Blue Cottage 3x3 $5.99），但无 4x6 Lined Fucshia 精确款。"),
    (104, "Post-it® Super Sticky Notes, 4 in x 8 in, Floral Brocade w/Magnet, 1 Pad/Pack", "", None,
     "", "无在售",
     "原 Floral Brocade w/Magnet 款式无独立 listing；近似 Floral Fantasy Collection (B00006JNN7 3x3 5 Pads $6.99)，但尺寸3x3 vs 4x8、无 Magnet、非 Brocade 专名，不精确。"),
    (106, "Post-it® Notes, 4 in x 3 in, Fashionista, Purple Shoes Design, 1 Pad/Pack", "", None,
     "", "无在售",
     "Fashionista 系列（Purple Shoes）已完全下架；Search(post-it-fashionista) 导出仅4行且0个 Post-it 候选，确认无售。"),
    (107, "Post-it® Notes, 4 in x 3 in, Fashionista, Shopping Woman Design, 1 Pad/Pack", "", None,
     "", "无在售",
     "Fashionista 系列（Shopping Woman）已完全下架；同 106，Search(post-it-fashionista) 导出0个 Post-it 候选，确认无售。"),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "DesignerFashionista"
hdr = ["行号", "原产品名", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
ws.append(hdr)
for r in rows:
    ws.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6]])

widths = [6, 56, 12, 14, 42, 10, 70]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_DesignerFashionista核对表.xlsx"
wb.save(out)
print("已生成:", out)
for r in rows:
    print(f"行{r[0]} | 无在售")
