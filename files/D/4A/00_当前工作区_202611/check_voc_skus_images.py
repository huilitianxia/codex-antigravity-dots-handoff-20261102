import openpyxl
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

voc_skus = [
    "4A 305-Full Adhesive",
    "4A 304 Full Glue",
    "4A 302-Full Adhesive-400",
    "4A 303-Full Adhesive-400",
    "4A 304-Full Adhesive-400",
    "4A SCPSS 32x6",
    "4A GM-SCPSS 32x6",
    "4A SCPSS 7",
    "4A 5082-Y-Lx2"
]

for r in range(7, ws.max_row + 1):
    sku = str(ws.cell(r, 3).value or '').strip()
    if sku in voc_skus:
        asin = ws.cell(r, 13).value
        title = ws.cell(r, 9).value
        imgs = [ws.cell(r, c).value for c in range(34, 43) if ws.cell(r, c).value]
        print(f"Row {r:3d} | {sku:25} | ASIN={asin} | Imgs={len(imgs)}")
        print(f"  Title: {title}")
        for idx, u in enumerate(imgs):
            print(f"  Img[{idx}]: {u}")
