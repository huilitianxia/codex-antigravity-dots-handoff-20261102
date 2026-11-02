# -*- coding: utf-8 -*-
"""生成 Scotch Tape 核对表(行72-74/77-79/83-85/167) 与 Dispenser 核对表(行93-102)。"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment

HDR_FILL = PatternFill("solid", fgColor="4472C4")
HDR_FONT = Font(bold=True, color="FFFFFF")
NO_FILL = PatternFill("solid", fgColor="F8CBAD")      # 无在售 / 待另搜 橙
OK_FILL = PatternFill("solid", fgColor="C6EFCE")      # 精准 绿
AP_FILL = PatternFill("solid", fgColor="FFEB9C")      # 近似 黄

def style_sheet(sh, headers, widths):
    for c in range(1, len(headers) + 1):
        cell = sh.cell(row=1, column=c)
        cell.font = HDR_FONT
        cell.fill = HDR_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for i, w in enumerate(widths, 1):
        sh.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w

def put(sh, row_data, fill=None, conf_fill=None):
    sh.append(row_data)
    rr = sh.max_row
    if fill:
        for c in range(1, len(row_data) + 1):
            sh.cell(row=rr, column=c).fill = fill
    if conf_fill and row_data[6] in ("✅精准", "⚠️近似", "❌无在售", "⏭️待另搜"):
        sh.cell(row=rr, column=7).fill = conf_fill
        sh.cell(row=rr, column=7).font = Font(bold=True)
    return rr

headers = ["行号", "原产品名", "2013价($)", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"]
widths = [8, 44, 12, 14, 14, 34, 12, 52]

# ============ Scotch Tape (行72-74,77-79,83-85,167) ============
wb = openpyxl.Workbook()
sh = wb.active
sh.title = "ScotchTape核对"
style_sheet(sh, headers, widths)
# 73 有精确近似；其余不在 Magic Tape 导出，需另搜
scotch = [
    (72, "Scotch® Home and Office Masking Tape", 9.59, "", "", "⏭️待另搜",
     "导出无对应候选（仅 Magic Tape 家族）；需另搜 'Scotch Masking Tape' 确认"),
    (73, "Scotch® Magic™ Greener Dispensered Tape", 3.49, "B004Z4E74M", 8.2, "⚠️近似",
     "Greener 6123 6卷/6座，源单卷座款无单独在售；价差大(3.49→8.2)"),
    (74, "Scotch® Double Sided Tape Dispensered Rolls", 5.99, "", "", "⏭️待另搜",
     "导出无对应候选；需另搜 'Scotch Double Sided Tape' 确认"),
    (77, "Scotch® Magic™ Tape Shoe Dispenser - Zebra", 9.99, "", "", "⏭️待另搜",
     "导出无对应候选；需另搜 'Scotch Tape Dispenser' 确认"),
    (78, "Scotch™ Precision Ultra Edge Titanium Scissors", 9.99, "", "", "⏭️待另搜",
     "导出无对应候选；需另搜 'Scotch Scissors' 确认"),
    (79, "Scotch® Pop-up Tape Mountable Dispenser", 2.49, "", "", "⏭️待另搜",
     "导出无对应候选；需另搜 'Scotch Pop-up Tape' 确认"),
    (83, "Scotch® Pop-Up Tape Refill Strips", 2.69, "", "", "⏭️待另搜",
     "导出无对应候选；随 79 一起另搜"),
    (84, "Scotch® Mounting Squares", 3.79, "", "", "⏭️待另搜",
     "导出无对应候选；需另搜 'Scotch Mounting Squares' 确认"),
    (85, "Scotch® Mounting Tape", 8.59, "", "", "⏭️待另搜",
     "导出无对应候选；需另搜 'Scotch Mounting Tape' 确认"),
    (167, "Scotch® Magic™ Tape Dispenser - Dog", 9.99, "", "", "⏭️待另搜",
     "导出无对应候选；需另搜 'Scotch Tape Dispenser Dog' 确认"),
]
for r in scotch:
    ln, name, p2013, asin, price, conf, note = r
    fill = NO_FILL if conf == "⏭️待另搜" else AP_FILL
    put(sh, [ln, name, p2013, asin, price, "", conf, note], fill=fill, conf_fill=fill)
wb.save("Notes_ScotchTape核对表.xlsx")
print("Notes_ScotchTape核对表.xlsx 已生成，共", len(scotch), "行（1近似/9待另搜）")

# ============ Dispenser (行93-102) ============
wb2 = openpyxl.Workbook()
sh2 = wb2.active
sh2.title = "Dispenser核对"
style_sheet(sh2, headers, widths)
disp = [
    (93, "Post-it® Pop-up Notes Dispenser, Apple Shaped, Red", 9.99, "B004YQZPVA", 16.44, "✅精准",
     "APL-330 Apple-Shaped Dispenser，精准"),
    (94, "Post-it® Pop-up Note Dispenser, Clutch Purse style", 9.99, "B01M706Y9R", 8.38, "⚠️近似",
     "原 Clutch Purse 造型座无在售；取通用 Fashion Dispenser 近似"),
    (95, "Post-it® Pop-up Notes Dispenser, Red, Heart Shape", 9.99, "B00008IOXK", 11.51, "⚠️近似",
     "原 Heart 造型座无在售；取通用 Black Base 座近似"),
    (96, "Post-it® Pop-up Notes and Flags Dispenser Starter Kit", 14.99, "B000UHGJTO", 14.02, "✅精准",
     "Note & Flag Dispenser Black Base Clear Top，精准"),
    (97, "Post-it® Pop-up Note Dispenser, Professional Series", 6.49, "B00OILMU8M", 11.66, "⚠️较准",
     "WD-330-BK Black Base Clear Top Professional，较准"),
    (98, "Post-it® Pop-up Notes Dispenser, Black Purse", 9.99, "B00008IOXK", 11.51, "⚠️近似",
     "原 Black Purse 造型座无在售；取通用 Black Base 座近似"),
    (99, "Post-it® Pop-up Notes Value Pack, Pink, 18 Pds w/Dispenser", 9.99, "B0015ZWQBK", 19.99, "⚠️近似",
     "DS330-SSVA Value Pack，源 Pink→现 Assorted，近似"),
    (100, "Post-it® Pop-up Note Dispenser JAX-330, White Electric Glow", 10.99, "B0776KVRHR", 10.05, "⚠️近似",
     "原 JAX-330 白+Electric Glow 无在售；取通用 White 座近似"),
    (101, "Post-it® Pop-up Note Dispenser, Diamond shaped", 9.99, "B07K8YVDZZ", 13.68, "⚠️近似",
     "原 Diamond 造型座无在售；取通用 Geometric 座近似"),
    (102, "Post-it® Note Dispenser, Compact, for 3x3", 6.99, "B0776MC61W", 10.45, "⚠️近似",
     "原 Compact 款无精确匹配；取通用 Black Base 座近似"),
]
for r in disp:
    ln, name, p2013, asin, price, conf, note = r
    fill = OK_FILL if conf.startswith("✅") else AP_FILL
    put(sh2, [ln, name, p2013, asin, price, "", conf, note], fill=fill, conf_fill=fill)
wb2.save("Notes_Dispenser核对表.xlsx")
print("Notes_Dispenser核对表.xlsx 已生成，共", len(disp), "行（2精准/1较准/7近似）")
