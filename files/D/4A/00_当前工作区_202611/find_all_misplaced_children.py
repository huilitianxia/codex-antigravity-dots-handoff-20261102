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

# Let's inspect all rows currently in each of the 21 families that look like they might be misplaced!
by_parent = {}
for r in cat_rows:
    if r and len(r) > 59 and r[5] == "Child":
        by_parent.setdefault(str(r[6]), []).append(r)

def check_misplaced():
    for p, rlist in sorted(by_parent.items()):
        print(f"=== {p} ({len(rlist)} rows) ===")
        for r in rlist:
            sku = str(r[2])
            asin = str(r[12])
            title = str(r[8] or "")
            color = str(r[58] or "")
            size = str(r[59] or "")
            # Print any row where SKU/title seems unusual for the parent
            flag = False
            if p == "PARENT-4A-303-CLASSIC-SQUARE":
                if any(k in sku.upper() or k in title.upper() for k in ["866", "0126", "0127", "0128", "0129", "0130", "70001", "BP ", "GMBP", "1111", "1515", "2222", "406", "073", "DIVIDER", "303M", "MG303", "CYCLIC", "4012", "4013", "301", "305", "404", "508", "608"]):
                    flag = True
            elif p == "PARENT-4A-301-MINI-PADS":
                if any(k in sku.upper() or k in title.upper() for k in ["BP ", "GMBP", "1111", "1515", "2222", "301M", "CYCL", "303", "404", "406", "508", "608"]):
                    flag = True
            elif p == "PARENT-4A-406-MEDIUM-PADS":
                if any(k in sku.upper() or k in title.upper() for k in ["404", "4 X 4", "4X4", "40606", "40607", "40608", "40609", "40621", "40622", "40623", "40624", "068", "069", "070", "071", "072", "073", "DIVIDER", "029", "030", "031"]):
                    flag = True
            elif p == "PARENT-4A-FULL-ADHESIVE-PADS":
                if "FULL" not in sku.upper() and "FULL" not in title.upper() and "063" not in sku.upper() and "064" not in sku.upper() and "065" not in sku.upper() and "066" not in sku.upper() and "067" not in sku.upper():
                    flag = True
            elif p == "PARENT-4A-608-XLARGE-6X8":
                if any(k in sku.upper() or k in title.upper() for k in ["40608", "DIVIDER", "2 2/3"]):
                    flag = True
            elif p == "PARENT-4A-PAPER-PAGE-MARKERS":
                if any(k in sku.upper() or k in title.upper() for k in ["BS 18", "1801", "1802", "1803", "1804", "1805"]):
                    flag = True
            elif p == "PARENT-4A-SIGN-HERE-FLAGS":
                flag = True
            elif p == "PARENT-4A-PSS-ROLL-TAPE":
                if any(k in sku.upper() or k in title.upper() for k in ["PSS 7", "SCPSS 7", "POP-UP NOTE DISPENSER", "1805", "PSS 10", "CR 012", "COLORING"]):
                    flag = True
            elif p == "PARENT-4A-8065-8088-SPECTRUM-24":
                flag = True
            elif p == "PARENT-4A-MEMO-NOTE-CUBES":
                if any(k in sku.upper() or k in title.upper() for k in ["8089", "0177", "3D SHAPE"]):
                    flag = True
            if flag:
                al = all_by_sku.get(sku, {})
                mfn_q = int(al.get("quantity") or 0) if al.get("fulfillment-channel") == "DEFAULT" else 0
                fba_q = fba_by_sku.get(sku, 0)
                print(f"  [MISPLACED?] SKU={sku:25s} | ASIN={asin:11s} | FBA={fba_q:4d} | MFN={mfn_q:4d} | C={color:18s} | S={size:28s} | Title={title[:65]}")

check_misplaced()
