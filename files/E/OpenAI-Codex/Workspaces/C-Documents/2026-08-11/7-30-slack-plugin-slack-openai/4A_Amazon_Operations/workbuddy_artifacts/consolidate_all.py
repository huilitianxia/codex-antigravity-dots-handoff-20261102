# -*- coding: utf-8 -*-
import glob, os, re
from collections import OrderedDict, defaultdict
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

SRC_DIR = "E:/Desktop"
OUT = "C:/Users/24243/WorkBuddy/2026-07-24-20-10-20/所有搜索导出产品汇总_去重.xlsx"
ORIG = "E:/xwechat_files/wxid_81xkainbu5d822_de43/msg/file/2026-07/3M价格_原版备份_20260807.xls"

# ---------- 1. read all export files ----------
files = sorted(glob.glob(os.path.join(SRC_DIR, "Search*.xlsx")))
print("桌面导出文件数:", len(files))

def parse_cat(path):
    m = re.search(r"Search\(([^)]+)\)", os.path.basename(path))
    return m.group(1) if m else os.path.basename(path)

def norm_cat(raw):
    c = raw.replace("®", "")
    if c.lower() == "post-it-fashionista":
        return "Post-it-Fashionista-Notes"
    if c == "Post-it-Full-Adhesive-Roll":
        return "Post-it-Full-Adhesive"
    return c

def find_col(hdr, *keys):
    for i, h in enumerate(hdr):
        if h and any(k in str(h) for k in keys):
            return i
    return None

records = OrderedDict()
cat_products = defaultdict(set)
cat_rows = defaultdict(int)
total_rows = 0
missing_asin = 0

for f in files:
    cat = norm_cat(parse_cat(f))
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    ws = wb["US"]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        wb.close(); continue
    hdr = rows[0]
    idx = {k: find_col(hdr, *ks) for k, ks in {
        "asin": ("ASIN",), "brand": ("品牌",), "title": ("商品标题",),
        "price": ("价格($)",), "prime": ("Prime价格",), "parent": ("父ASIN",),
        "link": ("商品详情页链接",), "img": ("商品主图",), "rank": ("搜索排名",),
        "sales": ("月销量",), "reviews": ("评分数",), "rating": ("评分",),
    }.items()}
    for r in rows[1:]:
        total_rows += 1
        cat_rows[cat] += 1
        asin = r[idx["asin"]] if idx["asin"] is not None else None
        if asin is None or str(asin).strip() == "":
            missing_asin += 1; continue
        asin = str(asin).strip()
        cat_products[cat].add(asin)
        if asin not in records:
            rec = {k: (r[i] if i is not None else None) for k, i in idx.items()}
            rec["categories"] = set(); rec["rowcount"] = 0
            records[asin] = rec
        rec = records[asin]
        for k in ("brand", "title", "price", "prime", "parent", "link", "img", "rank", "sales", "reviews", "rating"):
            if rec[k] in (None, ""):
                rec[k] = r[idx[k]] if idx[k] is not None else None
        rec["categories"].add(cat)
        rec["rowcount"] += 1
    wb.close()

print("总行数:", total_rows, "| 唯一ASIN:", len(records), "| 缺ASIN:", missing_asin)

# ---------- 2. build consolidated sheet ----------
wb = openpyxl.Workbook()
ws = wb.active; ws.title = "汇总去重"
headers = ["ASIN", "品牌", "商品标题", "价格($)", "Prime价格($)", "父ASIN",
           "月销量", "评分", "评分数", "搜索排名", "商品主图", "商品详情页链接",
           "来源分类", "出现分类数"]
ws.append(headers)
rows_out = []
for asin, rec in records.items():
    cats = sorted(rec["categories"])
    row = [asin, rec["brand"], rec["title"], rec["price"], rec["prime"], rec["parent"],
           rec["sales"], rec["rating"], rec["reviews"], rec["rank"], rec["img"], rec["link"],
           ", ".join(cats), len(cats)]
    rows_out.append((len(cats), rec.get("brand"), asin, row))
rows_out.sort(key=lambda x: (-x[0], str(x[1] or ""), x[2]))
for _, _, _, row in rows_out:
    ws.append(row)

hdr_fill = PatternFill("solid", fgColor="1F4E78")
hdr_font = Font(bold=True, color="FFFFFF")
for c in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=c); cell.fill = hdr_fill; cell.font = hdr_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
for i, w in enumerate([14, 16, 60, 10, 12, 14, 10, 8, 10, 22, 40, 40, 38, 10], start=1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{ws.max_row}"

# ---------- 3. per-category stats ----------
ws2 = wb.create_sheet("分类统计")
ws2.append(["来源分类(归并后)", "该分类产品数(去重)", "仅本分类独有", "与其他分类重复数"])
cat_fill = PatternFill("solid", fgColor="548235")
for c in range(1, 5):
    cell = ws2.cell(row=1, column=c); cell.fill = cat_fill; cell.font = hdr_font
    cell.alignment = Alignment(horizontal="center")
for cat in sorted(cat_products.keys()):
    asins = cat_products[cat]
    only = sum(1 for a in asins if len(records[a]["categories"]) == 1)
    ws2.append([cat, len(asins), only, len(asins) - only])
for i, w in enumerate([38, 18, 16, 18], start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.freeze_panes = "A2"

# ---------- 4. overlap matrix ----------
cats = sorted(cat_products.keys())
ws3 = wb.create_sheet("重复交叉矩阵")
ws3.cell(row=1, column=1, value="分类 \\ 分类")
for j, c in enumerate(cats, start=2):
    ws3.cell(row=1, column=j, value=c)
for cell in ws3[1]:
    cell.fill = cat_fill; cell.font = hdr_font
    cell.alignment = Alignment(horizontal="center", wrap_text=True)
for i, ca in enumerate(cats, start=2):
    ws3.cell(row=i, column=1, value=ca).font = Font(bold=True)
    seta = cat_products[ca]
    for j, cb in enumerate(cats, start=2):
        if ca == cb:
            cell = ws3.cell(row=i, column=j, value=len(seta))
            cell.fill = PatternFill("solid", fgColor="D9E1F2")
        else:
            val = len(seta & cat_products[cb])
            cell = ws3.cell(row=i, column=j, value=val)
            if val > 0:
                cell.fill = PatternFill("solid", fgColor="FCE4D6")
ws3.column_dimensions["A"].width = 38
for j in range(2, len(cats) + 2):
    ws3.column_dimensions[get_column_letter(j)].width = max(10, min(24, len(cats[j-2]) + 2))
ws3.freeze_panes = "B2"
for j in range(2, len(cats) + 2):
    ws3.cell(row=1, column=j).alignment = Alignment(horizontal="center", vertical="bottom", text_rotation=90)

# ---------- 5. coverage / missing check vs original 3M price file ----------
import xlrd
owb = xlrd.open_workbook(ORIG)
ows = owb.sheet_by_index(0)
orig_rows = []
for r in range(ows.nrows):
    v = ows.cell_value(r, 2)
    if v and str(v).strip():
        orig_rows.append(str(v).strip())

def family_of(name):
    n = name
    rules = [
        ("Scotch Restickable", ["Restickable"]),
        ("Scotch Mounting", ["Mounting"]),
        ("Scotch Double Sided Tape", ["Double Sided Tape"]),
        ("Scotch Masking Tape", ["Masking Tape"]),
        ("Scotch Pop-up Tape", ["Pop-up Tape", "Pop-Up Tape"]),
        ("Scotch Tape Dispenser", ["Tape Dispenser", "Tape Shoe Dispenser"]),
        ("Scotch Scissors", ["Scissors"]),
        ("Scotch Magic Tape", ["Magic"]),
        ("Post-it Full Adhesive", ["Full Adhesive Roll"]),
        ("Super Sticky Full Adhesive Notes", ["Full Adhesive Notes"]),
        ("Label Pads", ["Label Pads"]),
        ("Post-it Pockets", ["Pockets"]),
        ("Post-it Page Markers", ["Page Markers"]),
        ("Post-it Flags", ["Flags", "Flag"]),
        ("Post-it Note Dispenser", ["Note Dispenser", "Pop-up Notes Dispenser"]),
        ("Post-it Pop-up Notes", ["Pop-up Notes"]),
        ("Post-it Designer Notes", ["Designer"]),
        ("Post-it Fashionista Notes", ["Fashionista"]),
        ("Post-it Printed Notes", ["Printed Notes"]),
        ("Post-it Greener", ["Greener"]),
        ("Post-it Notes Cube", ["Notes Cube", " Cube"]),
        ("Post-it Ultra Collection Notes", ["Ultra Collection"]),
        ("Post-it Mini Notes", ["1.5 in x 2 in"]),
        ("Post-it Recycled Super Sticky", ["Recycled"]),
        ("Post-it Super Sticky Notes", ["Super Sticky Notes", "Super Sticky"]),
        ("Post-it Tabs", ["Note Tabs", "Tabs"]),
        ("Post-it Notes", ["Notes"]),
    ]
    for fam, kws in rules:
        for kw in kws:
            if kw in n:
                return fam
    return "其他/未归类"

present_cats = set(cat_products.keys())
family_exports = {
    "Scotch Restickable": {"Post-it-Restickable"},
    "Scotch Mounting": {"Scotch-Mounting"},
    "Scotch Double Sided Tape": {"Scotch-Double-Sided-Tape"},
    "Scotch Masking Tape": {"Scotch-Masking-Tape"},
    "Scotch Pop-up Tape": {"Scotch-Pop-up-Tape", "Scotch-Pop-up-Tape-Dispenser"},
    "Scotch Tape Dispenser": {"Scotch-Tape-Dispenser", "Scotch-Pop-up-Tape-Dispenser"},
    "Scotch Scissors": {"Scotch-Scissors"},
    "Scotch Magic Tape": {"Scotch-Magic-Tape"},
    "Post-it Full Adhesive": {"Post-it-Full-Adhesive"},
    "Super Sticky Full Adhesive Notes": {"Post-it-Super-Sticky-Full-Adhesive-Notes"},
    "Label Pads": {"Post-it-Label-Pads", "Post-it-Super-Sticky-Label-Pads"},
    "Post-it Pockets": {"Post-it-Pockets"},
    "Post-it Page Markers": {"Post-it-Page-Markers"},
    "Post-it Flags": {"Post-it-Flags"},
    "Post-it Note Dispenser": {"Post-it-Note-Dispenser"},
    "Post-it Pop-up Notes": {"Post-it-Pop-up-Notes"},
    "Post-it Designer Notes": {"Post-it-Designer-Notes"},
    "Post-it Fashionista Notes": {"Post-it-Fashionista-Notes"},
    "Post-it Printed Notes": {"Post-it-Printed-Notes"},
    "Post-it Greener": {"Post-it-Greener-Printed"},
    "Post-it Notes Cube": {"Post-it-Notes-Cube"},
    "Post-it Ultra Collection Notes": {"Post-it-Ultra-Collection-Notes"},
    "Post-it Mini Notes": {"Post-it-Mini-Notes"},
    "Post-it Recycled Super Sticky": {"Post-it-Recycled-Super-Sticky"},
    "Post-it Super Sticky Notes": {"Post-it-Super-Sticky-Notes"},
    "Post-it Tabs": {"Post-it-Tabs", "Post-it-Tabs-3-inch"},
    "Post-it Notes": {"Post-it-Notes"},
    "其他/未归类": set(),
}
# subset note for families that are likely covered by a broader search
subset_note = {}

fam_count = defaultdict(int)
for name in orig_rows:
    fam_count[family_of(name)] += 1

ws4 = wb.create_sheet("分类对照_遗漏检查")
ws4.append(["原始产品家族", "原始产品数", "是否有导出", "对应导出分类", "备注"])
miss_fill = PatternFill("solid", fgColor="FFC7CE")
ok_fill = PatternFill("solid", fgColor="C6EFCE")
for c in range(1, 6):
    cell = ws4.cell(row=1, column=c); cell.fill = cat_fill; cell.font = hdr_font
    cell.alignment = Alignment(horizontal="center", wrap_text=True)
for fam in sorted(fam_count.keys()):
    exp = family_exports.get(fam, set())
    covered = bool(exp & present_cats)
    if fam == "其他/未归类":
        continue
    note = subset_note.get(fam, "")
    if covered:
        status, fill = "✓ 有", ok_fill
    else:
        status, fill = "✗ 无导出", miss_fill
    ws4.append([fam, fam_count[fam], status, ", ".join(sorted(exp & present_cats)) or "—", note])
    ws4.cell(row=ws4.max_row, column=3).fill = fill
for i, w in enumerate([30, 12, 12, 40, 50], start=1):
    ws4.column_dimensions[get_column_letter(i)].width = w
ws4.freeze_panes = "A2"

# missing summary
missing = [f for f in fam_count if f != "其他/未归类" and not (family_exports.get(f, set()) & present_cats)]
print("\n缺失导出家族:", missing)
print("归并后分类数:", len(cats))

wb.save(OUT)
print("已保存:", OUT)
