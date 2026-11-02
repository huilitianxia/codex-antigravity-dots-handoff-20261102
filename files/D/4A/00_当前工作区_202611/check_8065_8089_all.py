import csv
import openpyxl
import sys
import re

sys.stdout.reconfigure(encoding="utf-8")

cat_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
all_path = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt"
fba_path = r"D:\下载文件\284701020757.txt"

with open(all_path, "r", encoding="utf-8", errors="ignore") as f:
    all_rows = list(csv.DictReader(f, delimiter="\t"))
all_by_sku = {r["seller-sku"]: r for r in all_rows}

fba_by_sku = {}
with open(fba_path, "r", encoding="utf-8", errors="ignore") as f:
    for r in csv.DictReader(f, delimiter="\t"):
        fba_by_sku[r["sku"]] = int(r.get("available") or 0) + int(r.get("fc-transfer") or 0)

wb = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws = wb["Template"]
cat_rows = list(ws.iter_rows(min_row=7, values_only=True))

# Let's see how each ASIN should be classified into one of the 21 families!
# First, let's list the 21 valid Parent SKUs and their Variation Themes:
VALID_PARENTS = {
    "PARENT-4A-301-MINI-PADS": "COLOR/SIZE",
    "PARENT-4A-303-CLASSIC-SQUARE": "COLOR/SIZE",
    "PARENT-4A-30315-RAINBOW-15": "COLOR/SIZE",
    "PARENT-4A-303M-MAGIC-CYCLING": "COLOR/SIZE",
    "PARENT-4A-4012-4013-PPBOX": "COLOR/SIZE",  # Upgrade from COLOR to COLOR/SIZE so 1 Box vs 2 Boxes don't collide!
    "PARENT-4A-404-SQUARE-4X4": "COLOR/SIZE",
    "PARENT-4A-406-MEDIUM-PADS": "COLOR/SIZE",
    "PARENT-4A-508-LARGE-5X8": "COLOR/SIZE",
    "PARENT-4A-608-XLARGE-6X8": "COLOR/SIZE",
    "PARENT-4A-8065-8088-SPECTRUM-24": "COLOR/SIZE",  # Or merge into SHAPED-NOVELTY-PADS!
    "PARENT-4A-ACRYLIC-DESK-ORGANIZERS": "COLOR/SIZE",
    "PARENT-4A-BIGPAD-MEETING-EASEL": "COLOR/SIZE",
    "PARENT-4A-BS-EXECUTIVE-LEATHER": "COLOR/SIZE",
    "PARENT-4A-DESK-PLANNERS": "COLOR/SIZE",
    "PARENT-4A-FULL-ADHESIVE-PADS": "COLOR/SIZE",
    "PARENT-4A-LABEL-STICKERS": "COLOR/SIZE",
    "PARENT-4A-MEMO-NOTE-CUBES": "COLOR/SIZE",
    "PARENT-4A-PAPER-PAGE-MARKERS": "COLOR/SIZE",
    "PARENT-4A-PSS-ROLL-TAPE": "COLOR/SIZE",
    "PARENT-4A-SHAPED-NOVELTY-PADS": "COLOR/SIZE",
    "PARENT-4A-SIGN-HERE-FLAGS": "COLOR/SIZE",
    "PARENT-4A-TRANSPARENT-PET-TABS": "COLOR/SIZE",
}

# Wait: what is currently in PARENT-4A-8065-8088-SPECTRUM-24?
# Earlier we saw 8068..8087 are 3D Animal/Ocean Printed Memo Pads, and their same-ASIN siblings (0156..0175) are in PARENT-4A-SHAPED-NOVELTY-PADS!
# What about all 8065..8089 SKUs across the entire CLR? Let's check every SKU with 806..808 or 0153..0177!
for r in cat_rows:
    if r and len(r) > 59 and r[2]:
        sku = str(r[2])
        title = str(r[8] or "")
        if any(k in sku for k in ["806", "807", "808", "015", "016", "017"]) or "3D Shape" in title:
            print(f"  SKU={sku:24s} | ASIN={str(r[12]):11s} | Parent={str(r[6]):34s} | C={str(r[58]):18s} | S={str(r[59]):30s} | Title={title[:55]}")
