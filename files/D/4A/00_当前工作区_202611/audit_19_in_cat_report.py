import openpyxl
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

target_skus = [
    # 5 FBA
    "4A 039", "4A 040", "4A 037", "4A 0166", "4A095",
    # 13 MFN
    "4A092", "4A PSS 9-5 NB", "4A 0153", "4A 0154", "4A 0155",
    "4A 0168", "4A 0169", "4A 0171", "4A 40606", "4A 5036",
    "4A 60238", "4A SF-60238", "4A093",
    # 1 MFN 99022
    "4A GM40624*2"
]

sku_map = {}
for r in range(7, ws.max_row + 1):
    val = ws.cell(r, 3).value
    if val in target_skus:
        sku_map[val] = r

print(f"Total target SKUs: {len(target_skus)}, Found: {len(sku_map)}")

for sku in target_skus:
    r = sku_map[sku]
    ptype = ws.cell(r, 4).value
    action = ws.cell(r, 5).value
    pid_type = ws.cell(r, 12).value
    pid = ws.cell(r, 13).value
    mfg = ws.cell(r, 20).value # Col T
    color = ws.cell(r, 59).value # Col BG
    colormap = ws.cell(r, 255).value # Col IU
    print(f"Row {r:3d} | {sku:18} | PT: {ptype:15} | ID: {pid_type:4} {pid:10} | Mfg: {mfg!r:18} | Color: {color!r:20} | ColorMap: {colormap!r}")
