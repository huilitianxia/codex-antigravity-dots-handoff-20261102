import openpyxl

rows = [
    # 行号, 原产品名, 匹配ASIN, 亚马逊价格, 链接, 置信度, 备注
    (67, "Post-it® Full Adhesive Roll, 1 in x 400 in, Pink/Green, 1 Paper Roll/Pack", "", None,
     "", "无在售",
     "3M Post-it 正品满胶卷已停产退出亚马逊；本导出 23 个 full adhesive/roll 候选全是 4A 品牌替代款，无 Post-it 正品。按用户决定标停产跳过（同 Label Pads 处理）。"
     "最接近 4A 卷款参考：B08DKJ2K3T（4A PSS 32x6, 0.6x393in 6色带座 $13.99）、B07R2KSW34（2x315in 黄绿带格 $22.99）。用户之前给的 B07QXJYTZ7($22.99)/B0F2TKL2P5($17.99) 为 4A 满胶便签本(非卷)，可作同系列替代参考。"),
]

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "FullAdhesiveRoll"
hdr = ["行号", "原产品名", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
ws.append(hdr)
for r in rows:
    ws.append([r[0], r[1], r[2], r[3], r[4], r[5], r[6]])

widths = [6, 50, 12, 14, 42, 10, 70]
for i, w in enumerate(widths, 1):
    ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_FullAdhesiveRoll核对表.xlsx"
wb.save(out)
print("已生成:", out)
print(f"行67 | 无在售 | 满胶卷 3M 正品停产")
