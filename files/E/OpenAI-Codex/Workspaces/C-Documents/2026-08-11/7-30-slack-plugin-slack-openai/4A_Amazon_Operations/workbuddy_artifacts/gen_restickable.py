# -*- coding: utf-8 -*-
"""生成 Restickable 核对表（行80-82，全部标无在售）。
用户确认：导出 Search(Post-it-Restickable) 无 restickable 候选，3 行直接标无在售跳过。
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

rows = [
    # 行号, 原产品名, 2013价, 备注
    (80, "Scotch® Restickable Designs - Dogs", 3.19,
     "无在售：导出无 restickable 候选；Scotch Restickable 系列疑似已退出亚马逊在售"),
    (81, "Scotch® Restickable Designs - Sports", 3.19,
     "无在售：导出无 restickable 候选；Scotch Restickable 系列疑似已退出亚马逊在售"),
    (82, "Scotch® Restickable Dots", 4.29,
     "无在售：导出无 restickable 候选；Scotch Restickable 系列疑似已退出亚马逊在售"),
]

wb = openpyxl.Workbook()
sh = wb.active
sh.title = "Restickable核对"

headers = ["行号", "原产品名", "2013价($)", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
sh.append(headers)
for c in range(1, len(headers) + 1):
    cell = sh.cell(row=1, column=c)
    cell.font = Font(bold=True, color="FFFFFF")
    cell.fill = PatternFill("solid", fgColor="4472C4")
    cell.alignment = Alignment(horizontal="center", vertical="center")

no_fill = PatternFill("solid", fgColor="F8CBAD")  # 无在售 橙色
for r in rows:
    line_no, name, price2013, note = r
    sh.append([line_no, name, price2013, "", "", "", "❌无在售", note])
    rr = sh.max_row
    sh.cell(row=rr, column=7).fill = no_fill
    sh.cell(row=rr, column=7).font = Font(bold=True, color="9C0006")

widths = [8, 42, 12, 14, 14, 30, 12, 50]
for i, w in enumerate(widths, 1):
    sh.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

out = "Notes_Restickable核对表.xlsx"
wb.save(out)
print("已生成", out, "共", len(rows), "行（全部无在售）")
