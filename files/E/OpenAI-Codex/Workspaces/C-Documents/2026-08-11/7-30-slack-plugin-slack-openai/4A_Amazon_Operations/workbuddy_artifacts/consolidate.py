# -*- coding: utf-8 -*-
import glob, re, os
from collections import OrderedDict, defaultdict
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

SRC_DIR = "E:/Desktop"
OUT = "C:/Users/24243/WorkBuddy/2026-07-24-20-10-20/所有搜索导出产品汇总_去重.xlsx"

files = sorted(glob.glob(os.path.join(SRC_DIR, "Search*.xlsx")))
print("找到导出文件:", len(files))

def parse_category(path):
    m = re.search(r"Search\(([^)]+)\)", os.path.basename(path))
    return m.group(1) if m else os.path.basename(path)

def find_col(hdr, *keys):
    for i, h in enumerate(hdr):
        if h and any(k in str(h) for k in keys):
            return i
    return None

# records keyed by ASIN
records = OrderedDict()          # ASIN -> dict of fields + categories set + rows count
cat_products = defaultdict(set)   # category -> set of ASINs
cat_rows = defaultdict(int)       # category -> total rows read
missing_asin = 0
total_rows = 0

for f in files:
    cat = parse_category(f)
    wb = openpyxl.load_workbook(f, read_only=True, data_only=True)
    ws = wb["US"]
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        continue
    hdr = rows[0]
    idx = {
        "asin": find_col(hdr, "ASIN"),
        "brand": find_col(hdr, "品牌"),
        "title": find_col(hdr, "商品标题"),
        "price": find_col(hdr, "价格($)"),
        "prime": find_col(hdr, "Prime价格"),
        "parent": find_col(hdr, "父ASIN"),
        "link": find_col(hdr, "商品详情页链接"),
        "img": find_col(hdr, "商品主图"),
        "rank": find_col(hdr, "搜索排名"),
        "sales": find_col(hdr, "月销量"),
        "reviews": find_col(hdr, "评分数"),
        "rating": find_col(hdr, "评分"),
    }
    for r in rows[1:]:
        total_rows += 1
        cat_rows[cat] += 1
        asin = r[idx["asin"]] if idx["asin"] is not None else None
        if asin is None or str(asin).strip() == "":
            missing_asin += 1
            continue
        asin = str(asin).strip()
        cat_products[cat].add(asin)
        if asin not in records:
            rec = {k: (r[i] if i is not None else None) for k, i in idx.items()}
            rec["categories"] = set()
            rec["rowcount"] = 0
            records[asin] = rec
        rec = records[asin]
        # fill any still-empty text fields from later occurrences
        for k in ("brand", "title", "price", "prime", "parent", "link", "img", "rank", "sales", "reviews", "rating"):
            if rec[k] in (None, ""):
                rec[k] = r[idx[k]] if idx[k] is not None else None
        rec["categories"].add(cat)
        rec["rowcount"] += 1
    wb.close()

print("总行数:", total_rows, "| 唯一ASIN:", len(records), "| 缺ASIN行:", missing_asin)

# ---- Build consolidated sheet ----
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "汇总去重"

headers = ["ASIN", "品牌", "商品标题", "价格($)", "Prime价格($)", "父ASIN",
           "月销量", "评分", "评分数", "搜索排名", "商品主图", "商品详情页链接",
           "来源分类", "出现分类数"]
ws.append(headers)

rows_out = []
for asin, rec in records.items():
    cats = sorted(rec["categories"])
    row = [
        asin,
        rec["brand"], rec["title"], rec["price"], rec["prime"], rec["parent"],
        rec["sales"], rec["rating"], rec["reviews"], rec["rank"], rec["img"], rec["link"],
        ", ".join(cats), len(cats),
    ]
    rows_out.append((len(cats), rec.get("brand"), asin, row))

# sort: most-overlapped first, then brand, then ASIN
rows_out.sort(key=lambda x: (-x[0], str(x[1] or ""), x[2]))
for _, _, _, row in rows_out:
    ws.append(row)

# styling
hdr_fill = PatternFill("solid", fgColor="1F4E78")
hdr_font = Font(bold=True, color="FFFFFF")
for c in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=c)
    cell.fill = hdr_fill
    cell.font = hdr_font
    cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
widths = [14, 16, 60, 10, 12, 14, 10, 8, 10, 22, 40, 40, 34, 10]
for i, w in enumerate(widths, start=1):
    ws.column_dimensions[get_column_letter(i)].width = w
ws.freeze_panes = "A2"
ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{ws.max_row}"

# ---- Sheet 2: per-category stats ----
ws2 = wb.create_sheet("分类统计")
ws2.append(["来源分类", "该分类产品数(去重)", "仅本分类独有", "与其他分类重复数"])
cat_fill = PatternFill("solid", fgColor="548235")
for c in range(1, 5):
    cell = ws2.cell(row=1, column=c); cell.fill = cat_fill; cell.font = hdr_font
    cell.alignment = Alignment(horizontal="center")
for cat in sorted(cat_products.keys()):
    asins = cat_products[cat]
    only = sum(1 for a in asins if len(records[a]["categories"]) == 1)
    shared = len(asins) - only
    ws2.append([cat, len(asins), only, shared])
for i, w in enumerate([34, 18, 16, 18], start=1):
    ws2.column_dimensions[get_column_letter(i)].width = w
ws2.freeze_panes = "A2"

# ---- Sheet 3: overlap matrix ----
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
            val = len(seta)
            cell = ws3.cell(row=i, column=j, value=val)
            cell.fill = PatternFill("solid", fgColor="D9E1F2")
        else:
            val = len(seta & cat_products[cb])
            cell = ws3.cell(row=i, column=j, value=val)
            if val > 0:
                cell.fill = PatternFill("solid", fgColor="FCE4D6")
ws3.column_dimensions["A"].width = 34
for j in range(2, len(cats) + 2):
    ws3.column_dimensions[get_column_letter(j)].width = max(10, min(22, len(cats[j-2]) + 2))
ws3.freeze_panes = "B2"
# rotate header text
from openpyxl.styles import Alignment as A
for j in range(2, len(cats) + 2):
    ws3.cell(row=1, column=j).alignment = A(horizontal="center", vertical="bottom", text_rotation=90)

wb.save(OUT)
print("已保存:", OUT)
print("汇总行数(唯一ASIN):", len(records))
print("分类数:", len(cats))
overlap = sum(1 for _, rec in records.items() if len(rec["categories"]) > 1)
print("跨分类重复ASIN数:", overlap)
