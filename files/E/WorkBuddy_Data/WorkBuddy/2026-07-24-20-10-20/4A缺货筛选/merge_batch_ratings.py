import os, openpyxl, csv
from collections import defaultdict

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
for n in os.listdir("E:/Desktop"):
    if not (n.startswith("Search(") and n.endswith(".xlsx")):
        continue
    if not ("B00SMEEF2A" in n or "B07FK7DJDR" in n):
        continue
    p = os.path.join("E:/Desktop", n)
    wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    hdr = next(rows)
    ai = hdr.index("ASIN"); ti = hdr.index("商品标题"); pi = hdr.index("父ASIN")
    si = hdr.index("月销量"); pri = hdr.index("价格($)"); ni = hdr.index("评分数")
    ri = hdr.index("评分"); bi = hdr.index("Buybox卖家"); ui = hdr.index("上架时间")
    for r in rows:
        a = str(r[ai]).strip() if r[ai] else ""
        if not a or a == "ASIN":
            continue
        records[a] = dict(title=r[ti], parent=r[pi], sales=r[si], price=r[pri],
                          reviews=r[ni], rating=norm_rating(r[ri]), buybox=r[bi],
                          launched=r[ui], src=n[:30])
    wb.close()
print("批量查询文件提取 ASIN 数:", len(records))

# 2) 官方 All Listings Report 状态
off_status = defaultdict(list)
with open(r"E:/Desktop/所有商品报告_08-08-2026.txt", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        a = row.get("asin1", "").strip()
        if a in records:
            off_status[a].append(row.get("status", ""))

# 3) 269 模板里的官方状态
wb2 = openpyxl.load_workbook("4A缺货筛选/output/4A缺货_269评分补录表.xlsx", data_only=True)
ws2 = wb2.active
hdr2 = [c.value for c in ws2[1]]
ai2 = hdr2.index("ASIN")
tmpl = {}
for r in ws2.iter_rows(min_row=2, values_only=True):
    tmpl[str(r[ai2]).strip()] = dict(status=r[3], price=r[5], cat=r[6], prio=r[7],
                                     title=r[1], sku=r[2], qty=r[4])

# 4) 输出合并表
print("\n%-12s %-5s %-6s %-16s %-12s %-14s %s" % ("ASIN", "评分", "评分数", "官方状态", "卖家精灵销量", "BuyBox", "状态信号"))
print("-" * 95)
ge4 = []
for a in sorted(records, key=lambda x: (records[x]["rating"] or 0), reverse=True):
    rec = records[a]
    off = ",".join(sorted(set(off_status.get(a, [])))) or "无(不在官方报告)"
    sales = rec["sales"]
    if isinstance(sales, (int, float)) and sales > 0:
        sig = "在售有销量"
    elif rec["buybox"] and "4A" in str(rec["buybox"]):
        sig = "BuyBox=4A(在售)"
    else:
        sig = "无销量信号(可能缺货)"
    rating = rec["rating"]; reviews = rec["reviews"]
    print("%-12s %-5s %-6s %-16s %-12s %-14s %s" % (a, rating, reviews, off, str(sales), str(rec["buybox"]), sig))
    if rating is not None and rating >= 4.0:
        ge4.append((a, rating, reviews, tmpl.get(a, {}).get("cat", ""), off))

print("\n>>> 本批 40 个中 评分>=4.0 的:", len(ge4))
for g in ge4:
    print("    ", g)

# 5) 回填模板并保存更新版
wb3 = openpyxl.load_workbook("4A缺货筛选/output/4A缺货_269评分补录表.xlsx")
ws3 = wb3.active
hdr3 = [c.value for c in ws3[1]]
ai3 = hdr3.index("ASIN"); ri3 = hdr3.index("评分(待填)"); ni3 = hdr3.index("评分数(待填)"); note3 = hdr3.index("备注")
for row in ws3.iter_rows(min_row=2):
    a = str(row[ai3].value).strip() if row[ai3].value else ""
    if a in records:
        rec = records[a]
        row[ri3].value = rec["rating"]
        row[ni3].value = rec["reviews"]
        if rec["rating"] is not None and rec["rating"] >= 4.0:
            row[note3].value = "评分>=4.0，建议补货"
wb3.save("4A缺货筛选/output/4A缺货_269评分补录表_已补40.xlsx")
print("\n已保存更新版: 4A缺货_269评分补录表_已补40.xlsx")
