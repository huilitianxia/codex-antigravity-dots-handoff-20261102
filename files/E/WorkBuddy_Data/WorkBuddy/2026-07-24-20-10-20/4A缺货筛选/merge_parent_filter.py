# -*- coding: utf-8 -*-
"""
在已交叉校验的 269 清单基础上，按父ASIN分组，把
“同一个父体下已经有在售(Active)兄弟款”的缺货款标记为“已被替代/排除”。
父子映射来源：卖家精灵批量查询文件(覆盖269全量) + 卖家精灵品牌分析(Competitor, 覆盖在售兄弟)。
在售判定：以 Seller Central 官方 All Listings Report 的 status 为准(权威)。
"""
import os, openpyxl, csv
from collections import defaultdict

BASE = r"C:/Users/24243/WorkBuddy/2026-07-24-20-10-20"
SRC  = os.path.join(BASE, "4A缺货筛选/output/4A缺货_269评分_交叉校验修正版.xlsx")
OUT  = os.path.join(BASE, "4A缺货筛选/output/4A缺货_269_父子过滤最终版.xlsx")
REPORT = r"E:/Desktop/所有商品报告_08-08-2026.txt"

# ---------- 1) 合并 子ASIN -> 父ASIN ----------
child2parent = {}
for n in os.listdir("E:/Desktop"):
    if n.startswith("Search(") and n.endswith(".xlsx"):
        if not ("B00SMEEF2A" in n or "B07FK7DJDR" in n):
            continue
        p = os.path.join("E:/Desktop", n)
        wb = openpyxl.load_workbook(p, data_only=True, read_only=True)
        ws = wb.active
        rows = ws.iter_rows(values_only=True); hdr = next(rows)
        ai = hdr.index("ASIN"); pi = hdr.index("父ASIN")
        for r in rows:
            a = str(r[ai]).strip() if r[ai] else ""
            par = str(r[pi]).strip() if r[pi] else ""
            if not a:
                continue
            if a not in child2parent or not child2parent[a]:
                child2parent[a] = par
        wb.close()

# Competitor 品牌数据补充在售兄弟的父子关系
wb_c = openpyxl.load_workbook(r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx",
                              data_only=True, read_only=True)
ws_c = wb_c.active
rows_c = ws_c.iter_rows(values_only=True); hdr_c = next(rows_c)
ai_c = hdr_c.index("ASIN"); pi_c = hdr_c.index("父ASIN")
for r in rows_c:
    a = str(r[ai_c]).strip() if r[ai_c] else ""
    par = str(r[pi_c]).strip() if r[pi_c] else ""
    if not a:
        continue
    if a not in child2parent or not child2parent[a]:
        child2parent[a] = par
wb_c.close()

# 父 -> 所有子(asin)
parent2children = defaultdict(set)
for c, par in child2parent.items():
    if par:
        parent2children[par].add(c)

# ---------- 2) 官方报告 status 聚合(权威) ----------
off_status = defaultdict(set)
with open(REPORT, encoding="utf-8-sig", errors="replace") as f:
    for row in csv.DictReader(f, delimiter="\t"):
        a = row.get("asin1", "").strip()
        if a:
            off_status[a].add(row.get("status", ""))

def is_active(asin):
    return "Active" in off_status.get(asin, set())

# ---------- 3) 读交叉校验修正版的“全部269”表 ----------
wb = openpyxl.load_workbook(SRC, data_only=True)
ws = wb["全部269(已交叉校验)"]
hdr = [c.value for c in ws[1]]
all_rows = []
for row in ws.iter_rows(min_row=2, values_only=True):
    all_rows.append(list(row))

# ---------- 4) 对每个 ASIN 做父子判定 ----------
records = []
replaced_total = 0
replaced_ge4 = 0
no_parent = 0
kept_candidate = 0

for row in all_rows:
    a = str(row[0]).strip()
    parent = child2parent.get(a, "")
    rating = row[5]
    reviews = row[6]
    conflict = row[13]  # 数据冲突列

    rec = dict(zip(hdr, row))
    rec["父ASIN"] = parent
    rec["兄弟在售ASIN"] = ""
    rec["已被兄弟替代"] = ""

    if not parent:
        rec["已被兄弟替代"] = "无法判断(无父体信息)"
        no_parent += 1
        kept_candidate += 1
    else:
        sibs = parent2children.get(parent, set())
        active_sibs = [s for s in sibs if s != a and is_active(s)]
        if active_sibs:
            rec["已被兄弟替代"] = "是(已被替代)"
            rec["兄弟在售ASIN"] = ",".join(sorted(active_sibs))
            replaced_total += 1
            try:
                if rating is not None and float(rating) >= 4.0:
                    replaced_ge4 += 1
            except:
                pass
        else:
            rec["已被兄弟替代"] = "否(父体下无在售兄弟)"
            kept_candidate += 1

    # 最终分类
    try:
        rating_f = float(rating) if rating is not None else None
    except:
        rating_f = None
    if rec["已被兄弟替代"].startswith("是"):
        rec["最终分类"] = "已被兄弟款替代_排除"
    elif conflict and str(conflict).strip() not in ("", "无", "None"):
        rec["最终分类"] = "数据冲突_需人工复核"
    elif rating_f is not None and rating_f >= 4.0:
        rec["最终分类"] = "被低估好款_最终版"
    elif rating_f is not None:
        rec["最终分类"] = "评分<4.0_普通缺货"
    else:
        rec["最终分类"] = "无评分_普通缺货"
    records.append(rec)

# ---------- 5) 写新工作簿 ----------
new_wb = openpyxl.Workbook()
new_wb.remove(new_wb.active)

def write_sheet(title, data_rows, columns):
    ws = new_wb.create_sheet(title)
    ws.append(columns)
    for d in data_rows:
        ws.append([d.get(c, "") for c in columns])
    widths = [13, 46, 46, 11, 9, 6, 7, 11, 13, 22, 14, 13, 10, 13, 12, 18, 12, 22]
    for i, w in enumerate(widths[:len(columns)], 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = w
    return ws

cols = ["ASIN","商品标题_官方","商品标题_批量查询","官方状态","价格_官方","评分",
        "评分数","评分来源","置信度","在售信号","推断品类","补评分优先级",
        "标题相似度","数据冲突","父ASIN","兄弟在售ASIN","已被兄弟替代","最终分类"]

# 表1：全部269(父子过滤)
write_sheet("全部269(父子过滤)", records, cols)

# 表2：被低估好款_最终版 (评分>=4.0 & 非冲突 & 未被替代) 按评分数降序
good = [d for d in records if d["最终分类"] == "被低估好款_最终版"]
good.sort(key=lambda d: (d["评分数"] or 0) if d["评分数"] is not None else 0, reverse=True)
write_sheet("被低估好款_最终版", good, cols)

# 表3：已被兄弟款替代_排除
repl = [d for d in records if d["最终分类"] == "已被兄弟款替代_排除"]
repl.sort(key=lambda d: (d["评分数"] or 0) if d["评分数"] is not None else 0, reverse=True)
write_sheet("已被兄弟款替代_排除", repl, cols)

# 表4：数据冲突_需人工复核
conf = [d for d in records if d["最终分类"] == "数据冲突_需人工复核"]
write_sheet("数据冲突_需人工复核", conf, cols)

# 表5：统计
stat = new_wb.create_sheet("统计")
stat.append(["项", "值"])
stat.append(["269清单总数", len(records)])
stat.append(["已被兄弟款替代(排除)", replaced_total])
stat.append(["  其中评分>=4.0(从好款剔除)", replaced_ge4])
stat.append(["无父体信息(无法判断)", no_parent])
stat.append(["父体下无在售兄弟(保留候选)", kept_candidate])
final_good = len(good)
stat.append(["被低估好款_最终版(>=4.0且采信且未被替代)", final_good])
stat.append(["数据冲突_需人工复核", len(conf)])
stat.append(["评分<4.0 普通缺货", sum(1 for d in records if d['最终分类']=='评分<4.0_普通缺货')])
stat.append(["无评分 普通缺货", sum(1 for d in records if d['最终分类']=='无评分_普通缺货')])
stat.column_dimensions["A"].width = 40
stat.column_dimensions["B"].width = 12

new_wb.save(OUT)

print("已生成:", OUT)
print("\n=== 统计 ===")
for r in stat.iter_rows(values_only=True):
    print(f"  {r[0]}: {r[1]}")
print("\n=== 被剔除的'好款'(被兄弟替代且评分>=4.0) ===")
for d in repl:
    try:
        if d["评分"] is not None and float(d["评分"]) >= 4.0:
            print(f"  {d['ASIN']} 评分={d['评分']}/{d['评分数']} 替代兄弟={d['兄弟在售ASIN']} 标题={str(d['商品标题_官方'])[:40]}")
    except:
        pass
print("\n=== 最终版好款 TOP10 ===")
for d in good[:10]:
    print(f"  {d['ASIN']} 评分={d['评分']}/{d['评分数']} 置信={d['置信度']} 标题={str(d['商品标题_官方'])[:38]}")
