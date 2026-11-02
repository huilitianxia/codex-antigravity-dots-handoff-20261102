# -*- coding: utf-8 -*-
"""
把 Amazon 官方 All Listings Report（权威库存状态）与卖家精灵评分表（评分/评分数/月销）
按 ASIN 合并，产出 4A「评分>=4.0 且 currently unavailable」的终版优先补货清单。

输入：
  - 官方库存报告 txt： E:/Desktop/所有商品报告_08-08-2026.txt
  - 卖家精灵评分 xlsx： E:/Desktop/Competitor-US-Last-30-days-217940.xlsx （US 表）
输出：
  - output/4A缺货补货清单_终版.xlsx
"""
import csv, os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

RATING_MIN = 4.0

ALL_LISTINGS = r"E:/Desktop/所有商品报告_08-08-2026.txt"
SELLERS = r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx"
OUT_DIR = r"C:/Users/24243/WorkBuddy/2026-07-24-20-10-20/4A缺货筛选/output"
OUT = os.path.join(OUT_DIR, "4A缺货补货清单_终版_已修正.xlsx")
os.makedirs(OUT_DIR, exist_ok=True)

def to_num(x):
    try:
        return float(str(x).strip())
    except:
        return None

def norm_rating(x):
    """评分可能按×10存(44=4.4)；>10 视为×10。"""
    v = to_num(x)
    if v is None:
        return None
    if v > 10:
        v = v / 10.0
    return v

# ---------- 1. 读卖家精灵评分表 ----------
wb = openpyxl.load_workbook(SELLERS, read_only=True, data_only=True)
ws = wb.worksheets[0]
rows = list(ws.iter_rows(values_only=True))
hdr = rows[0]
def col_any(name):
    for i, h in enumerate(hdr):
        if h and name in str(h):
            return i
    return None
def col_exact(name):
    for i, h in enumerate(hdr):
        if h and str(h).strip() == name:
            return i
    return None
ai = col_any("ASIN"); ti = col_any("商品标题"); mi = col_any("月销量"); pi = col_any("价格($)")
# 评分列：优先精确匹配 '评分'，避免误配到 '评分数'(评论数)
ri = col_exact("评分")
if ri is None:
    for i, h in enumerate(hdr):
        if h and "评分" in str(h) and "评分数" not in str(h):
            ri = i; break
rci = col_any("评分数")  # 评分数 = 评论数量
rating_map = {}
for r in rows[1:]:
    a = str(r[ai]).strip() if r[ai] else ""
    if not a or a == "None":
        continue
    rating_map[a] = {
        "rating": norm_rating(r[ri]),
        "reviews": to_num(r[rci]),
        "sales": to_num(r[mi]),
        "title_ss": str(r[ti]).strip() if r[ti] else "",
        "price_ss": to_num(r[pi]),
    }
print("卖家精灵评分表 ASIN 数:", len(rating_map))

# ---------- 2. 读官方 All Listings Report（按 ASIN 聚合，避免同一 ASIN 多行互相覆盖）----------
from collections import defaultdict
asin_rows = defaultdict(list)
with open(ALL_LISTINGS, encoding="utf-8-sig", errors="replace") as fh:
    rdr = csv.DictReader(fh, delimiter="\t")
    for r in rdr:
        asin = (r.get("asin1") or "").strip()
        if not asin:
            continue
        status = (r.get("status") or "").strip()
        qty_raw = (r.get("quantity") or "").strip()
        asin_rows[asin].append({
            "asin": asin,
            "name": (r.get("item-name") or "").strip(),
            "sku": (r.get("seller-sku") or "").strip(),
            "price": to_num(r.get("price")),
            "qty": to_num(qty_raw),
            "status": status,
        })
print("官方 ASIN 数:", len(asin_rows))

# ---------- 3. 判定 currently unavailable ----------
def choose_repr(rows):
    """同一 ASIN 无 Active 时，取库存数量最多的那条作为代表行。"""
    best = rows[0]
    best_qty = best["qty"] if best["qty"] is not None else -1
    for r in rows[1:]:
        q = r["qty"] if r["qty"] is not None else -1
        if q > best_qty:
            best = r
            best_qty = q
    return best

unavail = []
for asin, rows in asin_rows.items():
    statuses = [r["status"].lower() for r in rows]
    # 同一 ASIN 下只要有任意 Active 行，就视为当前在售，不再判定为缺货
    if "active" in statuses:
        continue
    # 没有 Active：取代表性行
    unavail.append(choose_repr(rows))
print("currently unavailable 总数:", len(unavail))

# ---------- 4. 合并分类 ----------
priority = []   # 评分>=4.0 且缺货
lowrate = []    # 评分<4.0 且缺货
norate = []     # 缺货但卖家精灵无评分
for r in unavail:
    m = rating_map.get(r["asin"])
    rec = {
        "asin": r["asin"],
        "name": r["name"] or (m["title_ss"] if m else ""),
        "sku": r["sku"],
        "status": r["status"],
        "qty": r["qty"],
        "rating": m["rating"] if m else None,
        "reviews": m["reviews"] if m else None,
        "sales": m["sales"] if m else None,
        "price": r["price"] if r["price"] is not None else (m["price_ss"] if m else None),
    }
    if not m:
        norate.append(rec)
    elif (m["rating"] or 0) >= RATING_MIN:
        priority.append(rec)
    else:
        lowrate.append(rec)

# 排序：评分数降序（口碑基础大、且缺货，补货价值高）
priority.sort(key=lambda x: -(x["reviews"] or 0))
lowrate.sort(key=lambda x: -(x["reviews"] or 0))
norate.sort(key=lambda x: x["asin"])

print(f"优先补货(评分>=4.0 且缺货): {len(priority)}")
print(f"缺货_低评分(<4.0): {len(lowrate)}")
print(f"缺货_评分未知(未收录): {len(norate)}")

# ---------- 5. 写出 Excel ----------
wb2 = openpyxl.Workbook()
hdr_font = Font(bold=True, color="FFFFFF")
hdr_fill = PatternFill("solid", fgColor="4472C4")
thin = openpyxl.styles.Border()

def add_sheet(name, data, note_col=True):
    wsx = wb2.create_sheet(name)
    head = ["ASIN", "商品标题", "卖家SKU", "官方状态", "库存数量", "评分", "评分数", "月销量", "价格($)"]
    if note_col:
        head.append("说明")
    wsx.append(head)
    for c in range(1, len(head)+1):
        cell = wsx.cell(row=1, column=c)
        cell.font = hdr_font
        cell.fill = hdr_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for d in data:
        note = ""
        if note_col:
            if d["rating"] is None:
                note = "卖家精灵未收录评分，需另查确认是否≥4.0"
            elif d["status"].lower() == "incomplete":
                note = "Listing 信息不完整(可能被抑制)，先修复再补货"
            elif d["status"].lower() == "inactive":
                note = "官方状态Inactive(非在售)"
            elif d["qty"] == 0:
                note = "在售但库存为0(断货)"
        wsx.append([
            d["asin"], d["name"], d["sku"], d["status"],
            (d["qty"] if d["qty"] is not None else ""),
            (d["rating"] if d["rating"] is not None else ""),
            (d["reviews"] if d["reviews"] is not None else ""),
            (d["sales"] if d["sales"] is not None else ""),
            (d["price"] if d["price"] is not None else ""),
            note,
        ])
    # 列宽
    widths = [14, 52, 16, 12, 10, 8, 10, 10, 10, 40]
    for i, w in enumerate(widths, 1):
        wsx.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    wsx.freeze_panes = "A2"
    return wsx

add_sheet("优先补货清单", priority)
add_sheet("缺货_低评分(<4.0)", lowrate)
add_sheet("缺货_评分未知(未收录)", norate)

# 统计表
active_asins = sum(1 for rows in asin_rows.values() if any(r["status"].lower()=="active" for r in rows))
unavail_status_counts = {}
for r in unavail:
    s = r["status"].lower()
    unavail_status_counts[s] = unavail_status_counts.get(s, 0) + 1

wss = wb2.create_sheet("统计")
stat_rows = [
    ["指标", "数值"],
    ["官方 ASIN 总数", len(asin_rows)],
    ["其中 当前在售(含至少一条 Active)", active_asins],
    ["其中 当前不可售(无 Active)", len(unavail)],
    ["— 不可售中 Inactive", unavail_status_counts.get("inactive", 0)],
    ["— 不可售中 Incomplete", unavail_status_counts.get("incomplete", 0)],
    ["— 不可售中 Closed/其他", sum(c for s,c in unavail_status_counts.items() if s not in ("inactive","incomplete"))],
    ["currently unavailable 合计", len(unavail)],
    ["— 优先补货(评分>=4.0 且缺货)", len(priority)],
    ["— 缺货但评分<4.0", len(lowrate)],
    ["— 缺货但卖家精灵无评分", len(norate)],
    ["卖家精灵评分表收录 ASIN 数", len(rating_map)],
]
for r in stat_rows:
    wss.append(r)
wss["A1"].font = hdr_font; wss["A1"].fill = hdr_fill
wss["B1"].font = hdr_font; wss["B1"].fill = hdr_fill
wss.column_dimensions["A"].width = 42
wss.column_dimensions["B"].width = 14

# 删除默认 sheet
if wb2.sheetnames[0] == "Sheet":
    del wb2["Sheet"]
wb2.save(OUT)
print("\n已生成:", OUT)
