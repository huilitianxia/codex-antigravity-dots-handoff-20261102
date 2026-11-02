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

by_asin = {}
for r in cat_rows:
    if r and len(r) > 59 and r[12] and r[5] != "Parent":
        by_asin.setdefault(str(r[12]).strip(), []).append(r)

def classify_asin_v3(asin, rlist):
    skus = [str(r[2] or "").strip() for r in rlist]
    sku_join = " | ".join(skus).upper()
    titles = [str(r[8] or "") for r in rlist if r[8]]
    for s in skus:
        al_t = all_by_sku.get(s, {}).get("item-name", "")
        if al_t: titles.append(al_t)
    best_title = max(titles, key=len) if titles else ""
    t_up = best_title.upper()
    cur_parents = [str(r[6] or "") for r in rlist if r[6]]
    cur_p = cur_parents[0] if cur_parents else ""

    # 1. Sign Here Flags (`60171`, `60174`, `4A 190`, `SIGN HERE`)
    if any(k in sku_join for k in ["60171", "60174", "4A 190"]) or "SIGN HERE" in t_up:
        return "PARENT-4A-SIGN-HERE-FLAGS"

    # 2. 3D Animal/Ocean Printed Memo Pads (`8065..8089`, `0153..0177`, `3DSTICKY`, `STICKY 0031`, `IT-7W6W-L1IC`)
    if any(re.search(r"\b(4A\s*)?(80[678]\d|015[3-9]|016\d|017[0-7])\b", s.upper()) for s in skus) or any(k in sku_join for k in ["3DSTICKY", "STICKY 0031", "IT-7W6W-L1IC", "8066+8067", "8068+8065", "8069+8070", "8071+8083", "8072+8073", "8074+8067", "8075+8076", "8077+8079", "8078+8080", "8084+ 8082", "8085+8086", "8087+8088", "8089+8081"]) or "3D SHAPE PRINTED" in t_up:
        return "PARENT-4A-8065-8088-SPECTRUM-24"

    # 3. Printed Cute Folios (`8663..8667`, `0126..0135`, `70001`, `65000`, `sticky 024-24`) & Shaped Die-Cut (`5013`, `5018`, `5020`, `5021`, `5036`, `5037`, `5047`, `5059`, `5061`, `5078`, `50024`, `TN 789`, `4A052..4A060`, `sticky 013-13`)
    if any(re.search(r"(866[3-7]|012[6-9]|013[0-5]|70001|65000|5013|5018|5020|5021|5036|5037|5047|5059|5061|5078|50024|TN\s*789|4A05[2-9]|4A060)", s.upper()) for s in skus) or any(k in sku_join for k in ["STICKY 024-24", "STICKY 013-13"]):
        return "PARENT-4A-SHAPED-NOVELTY-PADS"

    # 4. 4012 / 4013 PP Box (`4A050` is on B01MZ1PQQ8 which is 4012*2)
    if any(k in sku_join for k in ["4012", "4013", "4A050"]):
        return "PARENT-4A-4012-4013-PPBOX"

    # 5. Executive Leather Sets BS 1801..1805 (`B07WHYRJ6H` has 4A SCBS 1805 & 4A PSS 10)
    if any(k in sku_join for k in ["BS 180", "BS180", "SCBS 180"]):
        return "PARENT-4A-BS-EXECUTIVE-LEATHER"

    # 6. Acrylic Desk Organizers & Pop-Up Note Dispenser (`PSS 7`, `SCPSS 7`, `AC-HOLDER`, `303-HOLDER`)
    if any(k in sku_join for k in ["PSS 7", "SCPSS 7", "AC-HOLDER", "303-HOLDER"]):
        return "PARENT-4A-ACRYLIC-DESK-ORGANIZERS"

    # 7. Big Pads & Meeting Easel Pads (`BP `, `GMBP`, `1111`, `1515`, `2222`, `MEETING`, `0146`, `0147`, `0148`)
    if any(k in sku_join for k in ["BP ", "GMBP", "BP1111", "BP1515", "BP2222", "1111-", "1515-", "2222-", "MEETING", "0146", "0147", "0148"]):
        return "PARENT-4A-BIGPAD-MEETING-EASEL"

    # 8. Desk Planners (`6533`, `6534`, `6411`, `6412`)
    if any(k in sku_join for k in ["6533", "6534", "6411", "6412"]) or "WEEKLY PLANNER" in t_up or "MONTHLY PLANNER" in t_up:
        return "PARENT-4A-DESK-PLANNERS"

    # 9. Label Stickers (`LB 1901`, `LB 1902`, `LB 1903`)
    if any(k in sku_join for k in ["1901", "1902", "1903"]) or "CHALKBOARD LABEL" in t_up or "CIRCLE DOT LABEL" in t_up:
        return "PARENT-4A-LABEL-STICKERS"

    # 10. Memo Note Cubes (`SMC 43`, `MC 43`, `3032`, `3033`, `3035`, `3036`, `3037`, `4A043`, `4A045`, `4A092`, `4A093`, `sticky 010-10`)
    if any(k in sku_join for k in ["SMC 43", "MC 43", "SMC43", "MC43", "4A 3032", "4A 3033", "4A 3035", "4A 3036", "4A 3037", "4A043", "4A045", "4A092", "4A093", "MG-ET8D-JLS7", "STICKY 010-10"]) or "MEMO CUBE" in t_up or "NOTE CUBE" in t_up:
        return "PARENT-4A-MEMO-NOTE-CUBES"

    # 11. Divider Sticky Notes (`40606`, `40607`, `40608`, `40609`, `40621`, `40622`, `40623`, `40624`, `4A068..4A073`, `sticky 015-15`, `sticky 016-16`) & Paper Page Markers (`124418`, `501516`, `501521`, `752516`)
    if any(k in sku_join for k in ["40606", "40607", "40608", "40609", "40621", "40622", "40623", "40624", "4A068", "4A069", "4A070", "4A071", "4A072", "4A073", "STICKY 015-15", "STICKY 016-16", "AAAA 01", "124418", "501516", "501521", "752516"]):
        return "PARENT-4A-PAPER-PAGE-MARKERS"

    # 12. Transparent PET Tabs (`6012`, `6014`, `6018`, `6022`, `6023`, `6031`, `6032`, `6034`, `6035`, `6043`, `6611`, `4A094..4A0103`)
    if any(k in sku_join for k in ["6012", "6014", "6018", "6022", "6023", "6031", "6032", "6034", "6035", "6043", "6611", "4A094", "4A095", "4A096", "4A097", "4A098", "4A099", "4A0100", "4A0101", "4A0102", "4A0103"]):
        return "PARENT-4A-TRANSPARENT-PET-TABS"

    # 13. PSS Roll Sticky Notes (`PSS`, `CR 012`, `4A076..4A091`)
    if any(k in sku_join for k in ["PSS", "CR 012", "4A076", "4A077", "4A078", "4A079", "4A080", "4A081", "4A082", "4A083", "4A084", "4A085", "4A086", "4A087", "4A088", "4A089", "4A090", "4A091"]):
        return "PARENT-4A-PSS-ROLL-TAPE"

    # 14. Color-Cycling Magic Pads (`301M`, `303M`, `MG301`, `MG303`, `0183`, `0185`, `U3032`, `ML-P46A-OV6A`)
    if any(k in sku_join for k in ["301M", "303M", "MG301", "MG303", "0183", "0185", "U3032", "ML-P46A-OV6A"]) or "COLOR-CYCLING" in t_up or "COLOR CYCLIC" in t_up:
        return "PARENT-4A-303M-MAGIC-CYCLING"

    # 15. Full Adhesive Pads (`FULL GLUE`, `FULL ADHESIVE`, `4A063..4A067`)
    if any(k in sku_join for k in ["FULL GLUE", "FULL ADHESIVE", "4A063", "4A064", "4A065", "4A066", "4A067"]) or "FULL ADHESIVE" in t_up:
        return "PARENT-4A-FULL-ADHESIVE-PADS"

    # 16. 30315 15-Color Rainbow (`30315`)
    if "30315" in sku_join:
        return "PARENT-4A-30315-RAINBOW-15"

    # 17. 404 Square 4x4 (`404`, `029`, `030`, `031`, `185`)
    if any(k in sku_join for k in ["404", "4A 029", "4A 030", "4A 031", "4A 185"]):
        return "PARENT-4A-404-SQUARE-4X4"

    # 18. 406 & 305 Medium Pads (`406`, `305`, `026`, `027`, `028`, `032`, `033`, `034`, `186`, `187`, `EP-T1V0-IBUZ`)
    if any(k in sku_join for k in ["406", "305", "4A 026", "4A 027", "4A 028", "4A 032", "4A 033", "4A 034", "4A 186", "4A 187", "EP-T1V0-IBUZ"]):
        return "PARENT-4A-406-MEDIUM-PADS"

    # 19. 508 Large 5x8 (`508`)
    if "508" in sku_join:
        return "PARENT-4A-508-LARGE-5X8"

    # 20. 608 XLarge 6x8 (`608`, `037`, `038`, `039`, `040`, `189`)
    if any(k in sku_join for k in ["608", "4A 037", "4A 038", "4A 039", "4A 040", "4A 189"]):
        return "PARENT-4A-608-XLARGE-6X8"

    # 21. 301 / 202 / 3548 / 4848 Mini Pads (`4A 003`, `4A 004`, `4A000`, `G4-PV5Z-2519`, `0Y-34BT-INQJ`)
    if any(k in sku_join for k in ["301", "202", "3548", "4848", "4A 003", "4A 004", "4A000", "G4-PV5Z-2519", "0Y-34BT-INQJ"]):
        return "PARENT-4A-301-MINI-PADS"

    # 22. 303 Classic Square
    if any(k in sku_join for k in ["303", "4A 007", "4A 008", "4A 010", "4A 011", "4A 012", "4A 013", "4A 014", "4A 015", "4A 016", "4A 017", "4A 018", "4A 019", "4A 020", "4A 021", "4A 022", "4A 023", "4A 024", "4A 194"]):
        return "PARENT-4A-303-CLASSIC-SQUARE"

    return cur_p or "UNKNOWN"

counts = {}
for asin, rlist in sorted(by_asin.items()):
    new_p = classify_asin_v3(asin, rlist)
    counts[new_p] = counts.get(new_p, 0) + len(rlist)

print("=== FAMILY COUNTS AFTER V3 CLEAN CLASSIFICATION ===")
for p, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {p:36s}: {c:4d} rows")
