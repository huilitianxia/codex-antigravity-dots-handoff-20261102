import os, openpyxl, csv
from collections import defaultdict
from difflib import SequenceMatcher

def norm_rating(v):
    if v is None: return None
    try: f=float(v)
    except: return None
    if f>10: f=f/10
    if f<0 or f>5: return None
    return round(f,2)

def similar(a,b):
    return SequenceMatcher(None, (a or "").lower(), (b or "").lower()).ratio()

# 1) 读 269 清单
wb=openpyxl.load_workbook("4A缺货筛选/output/4A缺货_269评分补录表_已补40.xlsx", data_only=True)
ws=wb.active
hdr=[c.value for c in ws[1]]
ai=hdr.index("ASIN"); ti=hdr.index("商品标题"); sti=hdr.index("官方状态")
pri=hdr.index("价格($)") if "价格($)" in hdr else None
cati=hdr.index("推断品类") if "推断品类" in hdr else None
prio_i=hdr.index("建议补评分优先级") if "建议补评分优先级" in hdr else None
rows269=[]
for r in ws.iter_rows(min_row=2, values_only=True):
    rows269.append(dict(asin=str(r[ai]).strip(), title=r[ti], status=r[sti], price=r[pri] if pri else None,
                        cat=r[cati] if cati else None, prio=r[prio_i] if prio_i else None))

# 2) 官方报告：取每个 ASIN 的真实标题和聚合状态
official={}
with open(r"E:/Desktop/所有商品报告_08-08-2026.txt",encoding="utf-8-sig") as f:
    for row in csv.DictReader(f,delimiter="\t"):
        a=row.get("asin1","").strip()
        if not a: continue
        if a not in [x["asin"] for x in rows269]: continue
        if a not in official:
            official[a]=dict(titles=[], statuses=[], prices=[], qtys=[])
        t=row.get("item-name","").strip()
        if t: official[a]["titles"].append(t)
        official[a]["statuses"].append(row.get("status",""))
        try: official[a]["prices"].append(float(row.get("price","")))
        except: pass
        try: official[a]["qtys"].append(float(row.get("quantity","")))
        except: pass

for a,d in official.items():
    d["title"]=max(d["titles"], key=len) if d["titles"] else ""
    d["status"]=",".join(sorted(set(s for s in d["statuses"] if s)))
    d["price"]=max(d["prices"]) if d["prices"] else None
    d["qty"]=sum(d["qtys"]) if d["qtys"] else 0

# 3) 品牌数据评分
brand={}
wb2=openpyxl.load_workbook(r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx",data_only=True,read_only=True)
ws2=wb2.active
hdr2=next(ws2.iter_rows(values_only=True))
ai2=hdr2.index("ASIN"); ti2=hdr2.index("商品标题"); ri2=hdr2.index("评分"); ni2=hdr2.index("评分数"); pi2=hdr2.index("父ASIN"); pri2=hdr2.index("价格($)")
for row in ws2.iter_rows(values_only=True):
    a=str(row[ai2]).strip() if row[ai2] else ""
    if a in [x["asin"] for x in rows269]:
        brand[a]=dict(title=row[ti2], rating=norm_rating(row[ri2]), reviews=row[ni2], parent=row[pi2], price=row[pri2])
wb2.close()

# 4) 批量查询文件：严格按标题匹配，过滤污染数据
batch_files=[os.path.join("E:/Desktop",n) for n in os.listdir("E:/Desktop")
             if n.startswith("Search(") and n.endswith(".xlsx") and ("B00SMEEF2A" in n or "B07FK7DJDR" in n)]
batch_raw=defaultdict(list)
for p in batch_files:
    wb3=openpyxl.load_workbook(p,data_only=True,read_only=True)
    ws3=wb3.active
    rows=ws3.iter_rows(values_only=True); hdr3=next(rows)
    ai3=hdr3.index("ASIN"); ti3=hdr3.index("商品标题")
    ri3=hdr3.index("评分"); ni3=hdr3.index("评分数"); pri3=hdr3.index("价格($)")
    si3=hdr3.index("月销量"); bi3=hdr3.index("Buybox卖家")
    for r in rows:
        a=str(r[ai3]).strip() if r[ai3] else ""
        if a not in [x["asin"] for x in rows269]: continue
        batch_raw[a].append(dict(title=r[ti3], rating=norm_rating(r[ri3]), reviews=r[ni3],
                                  price=r[pri3], sales=r[si3], buybox=r[bi3]))
    wb3.close()

# 5) 交叉校验并生成最终结果
out_rows=[]
for rec in rows269:
    a=rec["asin"]
    off=official.get(a,{})
    off_title=off.get("title","")
    off_status=off.get("status","不在官方报告")
    off_price=off.get("price")
    b_brand=brand.get(a)
    b_batch_list=batch_raw.get(a,[])

    # 选最可信的评分来源
    rating=None; reviews=None; source=None; conflict=False

    # 品牌分析最可靠
    if b_brand and b_brand["rating"] is not None:
        rating=b_brand["rating"]; reviews=b_brand["reviews"]; source="品牌分析"

    # 批量查询需要标题一致才采信；严格匹配避免子体污染
    def consistent(t_off, t_batch):
        to=(t_off or "").lower(); tb=(t_batch or "").lower()
        # 尺寸/颜色/关键特征反例直接判为不一致
        # 抓取官方标题中的尺寸规格
        import re
        off_dims=set(re.findall(r'\b(\d+(?:\.\d+)?\s*(?:x|×)\s*\d+(?:\.\d+)?)\b', to))
        bat_dims=set(re.findall(r'\b(\d+(?:\.\d+)?\s*(?:x|×)\s*\d+(?:\.\d+)?)\b', tb))
        if off_dims and bat_dims and not off_dims.intersection(bat_dims):
            return False, 0
        # grid vs lined/colors 反例
        off_grid=('grid' in to) or ('black grid' in to)
        bat_grid='grid' in tb
        if off_grid!=bat_grid:
            return False, 0
        sim=similar(t_off, t_batch)
        return sim>=0.75, sim

    best_batch=None
    for bb in b_batch_list:
        ok, sim = consistent(off_title, bb["title"])
        if ok:
            if best_batch is None or sim>best_batch["sim"]:
                best_batch={**bb, "sim":sim}

    if rating is None and best_batch and best_batch["rating"] is not None:
        rating=best_batch["rating"]; reviews=best_batch["reviews"]; source="批量查询(标题已校验)"
    elif b_batch_list and not best_batch:
        conflict=True
        source="批量查询标题冲突-废弃"

    # 置信度
    if rating is None:
        confidence="无评分"
    else:
        try: rc=int(reviews) if reviews is not None else 0
        except: rc=0
        if rc>=20: confidence="高(>=20评)"
        elif rc>=10: confidence="中(10-19评)"
        elif rc>=3: confidence="低(3-9评)"
        else: confidence="极低(<=2评)"

    # 在售信号
    buybox_sig=""
    if best_batch and best_batch.get("buybox"):
        bbv=str(best_batch["buybox"])
        if "4A" in bbv.upper(): buybox_sig="BuyBox=4A(疑似在售)"
        elif bbv and bbv not in ("--","NA","N/A","None"): buybox_sig=f"BuyBox={bbv[:20]}"
    if not buybox_sig:
        # 官方状态任一 Active 即在售
        if "Active" in off_status: buybox_sig="官方报告Active"
        else: buybox_sig="缺货/Inactive"

    out_rows.append({
        "ASIN":a,
        "商品标题_官方":off_title,
        "商品标题_批量查询":best_batch["title"] if best_batch else (b_batch_list[0]["title"] if b_batch_list else ""),
        "官方状态":off_status,
        "价格_官方":off_price,
        "评分":rating,
        "评分数":reviews,
        "评分来源":source,
        "置信度":confidence,
        "在售信号":buybox_sig,
        "推断品类":rec["cat"],
        "补评分优先级":rec["prio"],
        "标题相似度":round(best_batch["sim"],2) if best_batch else ("未匹配" if conflict else "无批量数据"),
        "数据冲突":conflict
    })

# 6) 写文件
out=openpyxl.Workbook()
ws_out=out.active; ws_out.title="全部269(已交叉校验)"
headers=["ASIN","商品标题_官方","商品标题_批量查询","官方状态","价格_官方","评分","评分数","评分来源","置信度","在售信号","推断品类","补评分优先级","标题相似度","数据冲突"]
ws_out.append(headers)
for row in out_rows:
    ws_out.append([row[h] for h in headers])

# 被低估好款(严格版)
ws2=out.create_sheet("被低估好款_严格版")
ws2.append(headers)
good=[r for r in out_rows if r["评分"] is not None and r["评分"]>=4.0 and not r["数据冲突"]]
# 按可信度排序
order={"高(>=20评)":0,"中(10-19评)":1,"低(3-9评)":2,"极低(<=2评)":3}
good.sort(key=lambda x:(order.get(x["置信度"],9), -(x["评分数"] if isinstance(x["评分数"],(int,float)) else 0)))
for row in good:
    ws2.append([row[h] for h in headers])

# 数据冲突待复核
ws3=out.create_sheet("数据冲突_需人工复核")
ws3.append(headers)
conf=[r for r in out_rows if r["数据冲突"]]
for row in conf:
    ws3.append([row[h] for h in headers])

# 统计
ws4=out.create_sheet("统计")
ws4.append(["项","值"])
ws4.append(["总数",len(out_rows)])
ws4.append(["有评分且>=4.0",len(good)])
ws4.append(["数据冲突",len(conf)])
ws4.append(["无评分",sum(1 for r in out_rows if r["评分"] is None and not r["数据冲突"])])
from collections import Counter
ws4.append([])
ws4.append(["置信度分布",str(dict(Counter(r["置信度"] for r in out_rows if r["评分"] is not None)))])

# 列宽
for wsx in [ws_out,ws2,ws3]:
    widths=[14,60,60,14,10,8,8,18,12,16,12,16,12,10]
    for i,w in enumerate(widths,1):
        wsx.column_dimensions[openpyxl.utils.get_column_letter(i)].width=w

out.save("4A缺货筛选/output/4A缺货_269评分_交叉校验修正版.xlsx")
print("已生成: 4A缺货_269评分_交叉校验修正版.xlsx")
print(f"总数: {len(out_rows)}")
print(f"有评分且>=4.0(严格版): {len(good)}")
print(f"数据冲突待复核: {len(conf)}")
print(f"无评分: {sum(1 for r in out_rows if r['评分'] is None and not r['数据冲突'])}")
print("\n严格版 >=4.0 列表:")
for r in good:
    print(f"  {r['ASIN']} | {r['评分']}/{r['评分数']} | {r['置信度']} | {r['商品标题_官方'][:50]}")
