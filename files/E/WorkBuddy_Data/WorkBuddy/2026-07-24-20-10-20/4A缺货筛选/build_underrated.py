import os, openpyxl, csv
from collections import defaultdict, Counter

def norm_rating(v):
    if v is None:
        return None
    try:
        f = float(v)
    except Exception:
        return None
    if f > 10:
        f = f / 10
    if f < 0 or f > 5:
        return None
    return round(f, 2)

# 1) 读两个批量查询文件
records = {}
rows_per_file = {}
for n in os.listdir("E:/Desktop"):
    if not (n.startswith("Search(") and n.endswith(".xlsx")):
        continue
    if not ("B00SMEEF2A" in n or "B07FK7DJDR" in n):
        continue
    p = os.path.join("E:/Desktop", n)
    wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
    ws = wb.active
    rs = ws.iter_rows(values_only=True)
    hdr = next(rs)
    ai = hdr.index("ASIN"); ti = hdr.index("商品标题"); bi_col = hdr.index("品牌")
    si = hdr.index("月销量"); pri = hdr.index("价格($)"); ni = hdr.index("评分数")
    ri = hdr.index("评分"); bb = hdr.index("Buybox卖家")
    cnt = 0
    for r in rs:
        a = str(r[ai]).strip() if r[ai] else ""
        if not a or a == "ASIN":
            continue
        cnt += 1
        # 仅保留品牌=4A 的记录（避免混入竞品）
        if str(r[bi_col]).strip().upper() != "4A":
            continue
        if a not in records:
            records[a] = dict(title=r[ti], sales=r[si], price=r[pri],
                              reviews=r[ni], rating=norm_rating(r[ri]),
                              buybox=r[bb])
    rows_per_file[n[:40]] = cnt
    wb.close()
print("两文件返回行数:", rows_per_file)
print("去重后纳入(品牌=4A)ASIN 数:", len(records))

# 2) 官方 All Listings Report 状态
off_status = defaultdict(list)
with open(r"E:/Desktop/所有商品报告_08-08-2026.txt", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        a = row.get("asin1", "").strip()
        if a in records:
            off_status[a].append(row.get("status", ""))

# 3) 269 模板
wb2 = openpyxl.load_workbook("4A缺货筛选/output/4A缺货_269评分补录表.xlsx", data_only=True)
ws2 = wb2.active
tmpl = {}
for r in ws2.iter_rows(min_row=2, values_only=True):
    tmpl[str(r[0]).strip()] = dict(status=r[3], price=r[5], cat=r[6], prio=r[7], qty=r[4])

# 4) 置信度分级 + 是否在售信号
def confidence(rev):
    if rev is None:
        return "无评分"
    rev = float(rev) if isinstance(rev, (int, float)) else 0
    if rev >= 20:
        return "高(>=20评)"
    if rev >= 10:
        return "中(10-19评)"
    if rev >= 3:
        return "低(3-9评)"
    return "极低(1-2评)"

def live_signal(rec):
    sales = rec.get("sales")
    if isinstance(sales, (int, float)) and sales > 0:
        return "近30天有销量(疑似仍在售)"
    bb = str(rec.get("buybox") or "")
    if "4A (USA) LIMITED" in bb:
        return "BuyBox=4A(疑似仍在售)"
    return "无在售信号(确为缺货)"

# 5) 构建全量 + 好款
all_rows = []
good = []
for a, rec in records.items():
    off = ",".join(sorted(set(off_status.get(a, [])))) or "无(不在官方报告)"
    rating = rec["rating"]; reviews = rec["reviews"]
    cat = tmpl.get(a, {}).get("cat", "")
    prio = tmpl.get(a, {}).get("prio", "")
    conf = confidence(reviews)
    live = live_signal(rec)
    row = [a, rec["title"], off, rec["price"], rating, reviews, conf, live, cat, prio]
    all_rows.append(row)
    if rating is not None and rating >= 4.0:
        good.append(row)

# 排序：好款按评分数降序（样本多=更可信）
good.sort(key=lambda x: (x[5] if x[5] is not None else 0), reverse=True)
all_rows.sort(key=lambda x: (x[4] if x[4] is not None else -1), reverse=True)

print("\n=== 统计 ===")
print("有评分的:", sum(1 for x in all_rows if x[4] is not None), "/", len(all_rows))
print("评分>=4.0 的(被低估好款候选):", len(good))
print("其中置信度分布:", Counter(x[6] for x in good))
print("官方状态分布(全部):", Counter(x[2] for x in all_rows))
print("在售信号分布(全部):", Counter(x[7] for x in all_rows))

print("\n=== 被低估好款 TOP 20（按评分数，最可信优先）===")
for x in good[:20]:
    print("  %-12s 评分%-4s 评数%-4s %-12s %-22s %-16s" % (x[0], x[4], x[5], x[2], x[6], (x[1] or "")[:30]))

# 6) 写最终 xlsx
wb_out = openpyxl.Workbook()
ws_good = wb_out.active; ws_good.title = "被低估好款(评分>=4.0)"
ws_all = wb_out.create_sheet("全部269(已补评分)")
ws_stat = wb_out.create_sheet("统计")
h_full = ["ASIN", "商品标题", "官方状态", "价格($)", "评分", "评分数", "置信度", "在售信号", "推断品类", "补评分优先级"]
for ws_, data in [(ws_good, good), (ws_all, all_rows)]:
    ws_.append(h_full)
    for row in data:
        ws_.append(row)
ws_stat.append(["指标", "数值"])
ws_stat.append(["纳入ASIN总数", len(all_rows)])
ws_stat.append(["有评分数", sum(1 for x in all_rows if x[4] is not None)])
ws_stat.append(["评分>=4.0(好款候选)", len(good)])
for k, v in Counter(x[6] for x in good).items():
    ws_stat.append(["  好款-置信度:" + k, v])
for k, v in Counter(x[2] for x in all_rows).items():
    ws_stat.append(["  官方状态:" + k, v])
for k, v in Counter(x[7] for x in all_rows).items():
    ws_stat.append(["  在售信号:" + k, v])
# 列宽
for ws_ in (ws_good, ws_all):
    for i, w in enumerate([14, 55, 14, 9, 7, 8, 12, 24, 16, 16], 1):
        ws_.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
wb_out.save("4A缺货筛选/output/4A缺货_269评分已补全_被低估好款.xlsx")
print("\n已保存: 4A缺货_269评分已补全_被低估好款.xlsx")
