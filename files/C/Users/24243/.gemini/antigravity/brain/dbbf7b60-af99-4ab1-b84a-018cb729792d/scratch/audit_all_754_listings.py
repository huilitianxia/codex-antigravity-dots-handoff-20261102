import csv
import os
import openpyxl
from collections import defaultdict

# 1. Load historical reviews dictionary
hist_reviews = {}
dl = r"C:\Users\24243\Downloads"
for f in os.listdir(dl):
    if f.endswith(".xlsx") and ("269" in f or "4A-SL" in f):
        try:
            wb = openpyxl.load_workbook(os.path.join(dl, f), data_only=True)
            for sname in wb.sheetnames:
                ws = wb[sname]
                for r in ws.iter_rows(values_only=True):
                    if r and r[0] and str(r[0]).startswith("B0"):
                        asin = str(r[0]).strip()
                        # try to find review number in row
                        rev = 0
                        star = 0
                        for val in r[1:]:
                            if isinstance(val, (int, float)):
                                if 1.0 <= val <= 5.0 and star == 0:
                                    star = val
                                elif val > 5 and rev == 0:
                                    rev = int(val)
                        if asin not in hist_reviews or rev > hist_reviews[asin].get("rev", 0):
                            hist_reviews[asin] = {"rev": rev, "star": star}
        except Exception:
            pass

print(f"Loaded {len(hist_reviews)} historical ASIN review records.")

# 2. Parse D:\下载文件\所有商品报告_09-03-2026.txt
all_listings_path = r"D:\下载文件\所有商品报告_09-03-2026.txt"
listings = []
with open(all_listings_path, "r", encoding="utf-8-sig", errors="ignore") as f:
    reader = csv.reader(f, delimiter="\t")
    header = next(reader)
    for row in reader:
        if not row or len(row) < 20: continue
        name = row[0].strip()
        sku = row[3].strip()
        price = row[4].strip()
        qty = row[5].strip()
        asin = row[16].strip()
        upc = row[22].strip()
        channel = row[26].strip() if len(row) > 26 else ""
        status = row[28].strip() if len(row) > 28 else ""
        
        rev_info = hist_reviews.get(asin, {"rev": 0, "star": 0})
        
        listings.append({
            "name": name,
            "sku": sku,
            "price": price,
            "qty": qty,
            "asin": asin,
            "upc": upc,
            "channel": channel,
            "status": status,
            "rev": rev_info["rev"],
            "star": rev_info["star"]
        })

print(f"Loaded {len(listings)} listings from All Listings Report.")

# 3. Categorize into families
def get_family(item):
    text = (item["name"] + " " + item["sku"]).upper()
    if "30315" in text: return "1. 30315 彩虹15色家族"
    if "301" in text or "1.5 X 2" in text or "1.5X2" in text: return "2. 301 迷你便签家族 (1.5x2)"
    if "508" in text or "5 X 8" in text or "5X8" in text: return "3. 508 大横线便签家族 (5x8)"
    if "608" in text or "6 X 8" in text or "6X8" in text: return "4. 608 特大横线便签家族 (6x8)"
    if any(k in text for k in ["40609", "4062", "4060", "DIVIDER", "INDEX", "TAB"]): return "5. 406xx 标签与书签便签家族"
    if "404" in text or "4 X 4" in text or "4X4" in text: return "6. 404 中号方块家族 (4x4)"
    if "406" in text or "4 X 6" in text or "4X6" in text: return "7. 406 大号便签家族 (4x6)"
    if any(k in text for k in ["PSS", "ROLL", "DISPENSER"]): return "8. PSS 满胶卷带及替芯家族"
    if any(k in text for k in ["BS 180", "1801", "1802", "1803", "LEATHER"]): return "9. BS 商务皮质礼盒家族"
    if any(k in text for k in ["SHAPES", "HEART", "LEAF", "ARROW", "BUBBLE", "PUZZLE", "5036", "5061", "5059", "5013", "5020", "5078"]): return "10. 异形便签九大神仙家族"
    if any(k in text for k in ["SIGN HERE", "601", "603", "604"]): return "11. 601/603 办公文档索引及签字贴家族"
    if any(k in text for k in ["806", "807", "808"]): return "12. 8065-8088 24色光谱家族"
    if any(k in text for k in ["BP", "MEETING", "1111", "1515", "2222"]): return "13. BP/Meeting 会议大看板家族"
    if any(k in text for k in ["SMC", "CUBE", "PRINT", "DOG", "CAT", "MEMO CUBE"]): return "14. SMC/Cube 四面印花便签砖家族"
    if any(k in text for k in ["303", "3 X 3", "3X3", "FULL GLUE", "FULL ADHESIVE"]): return "15. 303 经典3x3及满胶家族"
    return "16. 待定及其他专用零散款"

family_buckets = defaultdict(list)
for item in listings:
    fam = get_family(item)
    family_buckets[fam].append(item)

# 4. Generate Comprehensive Audit Report
report_path = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\full_754_all_listings_audit.md"
with open(report_path, "w", encoding="utf-8") as f:
    f.write("# 4A 全店 754 款商品全量归类与大合并映射总表 (基于官方所有商品报告)\n\n")
    f.write(f"> **数据源**：`D:\\下载文件\\所有商品报告_09-03-2026.txt` (全量 754 行)\n")
    f.write(f"> **交叉核验库**：`4A缺货_269款全量_历史好款.xlsx` + `4A-SL缺货好款.xlsx`\n\n")
    
    total_rev_all = 0
    f.write("| 家族序号与名称 | 商品总行数 | FBA在售/现货款 | 历史断货老号 | 可聚合历史评价总量 | 推荐主力 Master ASIN (最高评/最好页面) |\n")
    f.write("| :--- | :---: | :---: | :---: | :---: | :--- |\n")
    
    for fam in sorted(family_buckets.keys()):
        items = family_buckets[fam]
        fba_count = sum(1 for it in items if it["channel"] == "AMAZON_NA" or it["qty"])
        inactive_count = len(items) - fba_count
        fam_rev = sum(it["rev"] for it in items)
        total_rev_all += fam_rev
        
        # Find best ASIN
        best_item = max(items, key=lambda x: x["rev"])
        master_str = f"`{best_item['asin']}` ({best_item['rev']}评 {best_item['star']}★)" if best_item["rev"] > 0 else f"`{best_item['asin']}`"
        
        f.write(f"| **{fam}** | **{len(items)}** | {fba_count} | {inactive_count} | **{fam_rev} 条好评** | {master_str} |\n")
        
    f.write(f"\n\n**总计**：754 款 Listing 归并在 16 个主控大变体家族内，**可激活并聚合的历史客户真实好评总数高达：{total_rev_all} 条！**\n\n")
    
    # Detailed section for each family
    f.write("\n---\n\n## 详细家族归类明细\n\n")
    for fam in sorted(family_buckets.keys()):
        items = family_buckets[fam]
        items.sort(key=lambda x: (x["rev"], 1 if x["channel"]=="AMAZON_NA" else 0), reverse=True)
        f.write(f"### {fam} (共 {len(items)} 款)\n\n")
        f.write("| SKU | ASIN | 渠道 (Channel) | 状态/库存 | 历史评价 | 商品标题 |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :--- |\n")
        for it in items[:15]: # show top 15 in report
            ch = "FBA" if it["channel"] == "AMAZON_NA" else "FBM"
            qty_str = f"现货 {it['qty']}" if it['qty'] else "0库存(断货)"
            rev_str = f"**{it['rev']}评** ({it['star']}★)" if it["rev"] > 0 else "--"
            title_clean = it["name"][:45].replace("|", "/")
            f.write(f"| `{it['sku']}` | `{it['asin']}` | {ch} | {qty_str} | {rev_str} | {title_clean} |\n")
        if len(items) > 15:
            f.write(f"| ... *其余 {len(items)-15} 款已归入该家族后台映射库* | | | | | |\n")
        f.write("\n")

print(f"Saved to {report_path}")
print(f"Total reviews aggregated: {total_rev_all}")
