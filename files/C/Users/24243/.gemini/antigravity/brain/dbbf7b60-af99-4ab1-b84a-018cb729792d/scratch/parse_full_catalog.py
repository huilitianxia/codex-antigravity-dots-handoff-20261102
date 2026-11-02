import openpyxl
import csv
import os
import re
from collections import defaultdict

dl = r"C:\Users\24243\Downloads"
desktop = r"E:\Desktop"

# 1. Load WooCommerce 163 SKUs
woo_skus = {}
woo_file = os.path.join(desktop, "WooCommerce_完整改价_163_SKUs_复核后上传_2026-08-20.csv")
if os.path.exists(woo_file):
    with open(woo_file, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for r in reader:
            sku = r["SKU"].strip()
            woo_skus[sku] = {
                "reg_price": r.get("Regular price", ""),
                "sale_price": r.get("Sale price", "")
            }

# 2. Load 269 Historical Out of Stock Excel
hist_asins = {}
hist_file = None
for f in os.listdir(dl):
    if f.endswith(".xlsx") and "269" in f and "4A" in f:
        hist_file = os.path.join(dl, f)
        break

if hist_file:
    wb = openpyxl.load_workbook(hist_file, data_only=True)
    # Check all sheets
    for sname in wb.sheetnames:
        if "全量" in sname or "好款" in sname:
            ws = wb[sname]
            rows = list(ws.iter_rows(values_only=True))
            if not rows: continue
            for r in rows[1:]:
                if not r or not r[0]: continue
                asin = str(r[0]).strip()
                title = str(r[1]) if len(r) > 1 and r[1] else ""
                status = str(r[2]) if len(r) > 2 and r[2] else ""
                price = r[3] if len(r) > 3 else ""
                stars = r[4] if len(r) > 4 else ""
                reviews = r[5] if len(r) > 5 else 0
                if asin not in hist_asins or (isinstance(reviews, (int, float)) and reviews > hist_asins[asin].get("reviews", 0)):
                    hist_asins[asin] = {
                        "title": title,
                        "status": status,
                        "price": price,
                        "stars": stars,
                        "reviews": reviews if isinstance(reviews, (int, float)) else 0
                    }

# 3. Load 4A-SL缺货好款.xlsx
sl_file = None
for f in os.listdir(dl):
    if f.endswith(".xlsx") and "4A-SL" in f:
        sl_file = os.path.join(dl, f)
        break

if sl_file:
    wb = openpyxl.load_workbook(sl_file, data_only=True)
    for sname in wb.sheetnames:
        ws = wb[sname]
        rows = list(ws.iter_rows(values_only=True))
        if not rows: continue
        for r in rows[1:]:
            if not r or not r[0]: continue
            asin = str(r[0]).strip()
            title = str(r[1]) if len(r) > 1 and r[1] else ""
            status = str(r[3]) if len(r) > 3 and r[3] else ""
            stars = r[5] if len(r) > 5 else ""
            reviews = r[6] if len(r) > 6 else 0
            if asin not in hist_asins or (isinstance(reviews, (int, float)) and reviews > hist_asins[asin].get("reviews", 0)):
                hist_asins[asin] = {
                    "title": title,
                    "status": status,
                    "stars": stars,
                    "reviews": reviews if isinstance(reviews, (int, float)) else 0
                }

print(f"Total Unique Historical ASINs Loaded: {len(hist_asins)}")
print(f"Total WooCommerce Active SKUs: {len(woo_skus)}")

# Group by family based on keywords in title or SKU
families = defaultdict(lambda: {"active_skus": [], "hist_asins": []})

def detect_family(text):
    t = text.upper()
    if "30315" in t: return "30315 彩虹15色家族"
    if "301" in t or "1.5 X 2" in t or "1.5X2" in t: return "301 迷你便签家族 (1.5x2)"
    if "508" in t or "5 X 8" in t or "5X8" in t: return "508 大号横线家族 (5x8)"
    if "608" in t or "6 X 8" in t or "6X8" in t: return "608 特大横线家族 (6x8)"
    if "40609" in t or "4062" in t or "4060" in t or "DIVIDER" in t or "INDEX" in t or "TAB" in t: return "406xx 索引便签条家族"
    if "404" in t or "4 X 4" in t or "4X4" in t: return "404 中号方块家族 (4x4)"
    if "406" in t or "4 X 6" in t or "4X6" in t: return "406 大号便签家族 (4x6)"
    if "PSS" in t or "ROLL" in t or "DISPENSER" in t: return "PSS 满胶卷带及替芯家族"
    if "BS 180" in t or "1801" in t or "1802" in t or "1803" in t or "LEATHER" in t: return "BS 商务礼盒与替芯家族"
    if any(k in t for k in ["SHAPES", "HEART", "LEAF", "ARROW", "BUBBLE", "PUZZLE", "5036", "5061", "5059", "5013", "5020", "5078"]): return "异形便签九大神仙家族"
    if any(k in t for k in ["SIGN HERE", "601", "603", "604"]): return "601/603 办公文档索引及签字贴家族"
    if any(k in t for k in ["303", "3 X 3", "3X3", "FULL GLUE", "FULL ADHESIVE"]): return "303 经典3x3及满胶家族"
    if any(k in t for k in ["806", "807", "808"]): return "8065-8088 24色光谱家族"
    if any(k in t for k in ["BP", "MEETING", "1111", "1515", "2222"]): return "BP/Meeting 会议大看板便签家族"
    if "SMC" in t or "CUBE" in t or "PRINT" in t or "DOG" in t or "CAT" in t: return "SMC/Cube 四面印花便签砖家族"
    return "其他零散/待定家族"

for asin, data in hist_asins.items():
    fam = detect_family(asin + " " + data["title"])
    families[fam]["hist_asins"].append((asin, data["reviews"], data["stars"], data["title"][:50]))

for sku, data in woo_skus.items():
    fam = detect_family(sku)
    families[fam]["active_skus"].append((sku, data["sale_price"]))

report_lines = []
report_lines.append("# 全店 700+ 历史 Listing 与现货全量归类排查总表\n")
total_matched_asins = 0
total_active = 0

for fam, content in sorted(families.items(), key=lambda x: len(x[1]["hist_asins"]) + len(x[1]["active_skus"]), reverse=True):
    h_list = content["hist_asins"]
    a_list = content["active_skus"]
    total_matched_asins += len(h_list)
    total_active += len(a_list)
    
    # Sort historical asins by reviews desc
    h_list.sort(key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True)
    
    report_lines.append(f"## 【{fam}】")
    report_lines.append(f"- **在售活跃现货 SKU 数量**: {len(a_list)} 款")
    report_lines.append(f"- **挖掘出的历史断货/高评老 ASIN 数量**: {len(h_list)} 款")
    
    # Top review summary
    top_revs = [h for h in h_list if isinstance(h[1], (int, float)) and h[1] > 0]
    total_family_reviews = sum(h[1] for h in top_revs)
    report_lines.append(f"- **可聚合的真实历史好评总量**: **{total_family_reviews} 条真实评价！**")
    
    if top_revs:
        report_lines.append("  * **核心高评老祖宗标的**:")
        for asin, rev, star, title in top_revs[:5]:
            report_lines.append(f"    - `{asin}`: **{rev} 评** ({star}★) | {title}")
            
    if a_list:
        report_lines.append("  * **承接现货主力 SKU**:")
        for sku, price in a_list[:6]:
            report_lines.append(f"    - `{sku}` (当前特惠价: ${price})")
    report_lines.append("\n---\n")

report_lines.append(f"\n## 总结统计\n")
report_lines.append(f"- **全量已分类历史断货 ASIN 总数**: {total_matched_asins} 个")
report_lines.append(f"- **在售现货 SKU 挂载覆盖总数**: {total_active} 个")

out_path = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\full_catalog_700_family_audit.md"
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"Report written to {out_path}")
print(f"Total matched historical: {total_matched_asins}, Active SKUs: {total_active}")
