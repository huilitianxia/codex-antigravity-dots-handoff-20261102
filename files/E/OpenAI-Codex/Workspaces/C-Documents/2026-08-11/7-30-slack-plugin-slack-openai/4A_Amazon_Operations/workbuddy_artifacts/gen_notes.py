import openpyxl, csv, re

fp = r"E:\Desktop\Search(Post-it-Super-Sticky-Notes)-60-US-20260804.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
idx = {h: i for i, h in enumerate(data[0])}
ai = idx["ASIN"]; ti = idx["商品标题"]; pi = idx["价格($)"]
cand = {}
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I):
        cand[row[ai]] = {"price": row[pi], "link": f"https://www.amazon.com/dp/{row[ai]}"}

match = {
 "53": ("", "待另搜", "Full Adhesive款，本批搜索无此候选，需另搜 Post-it Super Sticky Full Adhesive Notes"),
 "54": ("", "待另搜", "同上"),
 "55": ("", "待另搜", "同上"),
 "57": ("", "待另搜", "Label Pads款，需另搜 Post-it Super Sticky Label Pads"),
 "58": ("", "待另搜", "同上"),
 "59": ("", "待另搜", "同上"),
 "60": ("", "待另搜", "同上"),
 "61": ("", "待另搜", "同上"),
 "62": ("", "待另搜", "同上"),
 "104": ("B076XG2XRS", "近似", "原4x8 Floral Brocade特殊款无在售，取Multi-Size Supernova Neons近似"),
 "109": ("B07RK52772", "近似", "Apple形状款停产，取3x3 Assorted Brights近似"),
 "110": ("B07RK52772", "近似", "Heart形状款停产，取Assorted Brights近似"),
 "111": ("B07RK52772", "近似", "Tulip/Daisy花形款停产，取Assorted Brights近似"),
 "112": ("B07RK52772", "近似", "Star形状款停产，取Assorted Brights近似"),
 "113": ("B07RK52772", "近似", "Scroll形状款停产，取Assorted Brights近似"),
 "123": ("B076XG2XRS", "近似", "5x8 Jewel Pop Lined停产，取Multi-Size Lined近似"),
 "124": ("B09MWQPJZ8", "近似", "4x6 Asstd Lined，取Supernova Neons 5 Lined Pads（尺寸/lined对，颜色近似）"),
 "125": ("B0BPJW13CM", "近似", "Recycled 3x3 Tropical停产，取Recycled Pastels 5 Pads近似"),
 "128": ("B01D8F5NLY", "近似", "3x3 Jewel Pop 5 Pads停产，取Supernova Neons 5 Pads近似"),
 "130": ("B076XG2XRS", "近似", "Assorted Sizes Electric Glow停产，取Multi-Size近似"),
 "131": ("B076XG2XRS", "近似", "Assorted Sizes Jewel Pop停产，取Multi-Size近似"),
 "136": ("", "无在售", "Recycled 4x4 Farmers Market候选无，疑停产"),
 "137": ("B0BPJYH7FS", "近似", "Recycled 3x3 Tropical停产，取Recycled Pastels 12 Pads近似"),
 "138": ("", "无在售", "Printed Pop-up 3x3专用款，在售候选仅Recycled Pop-up 1.875不符"),
 "139": ("B01D8F5RW4", "近似", "4x4 w/Print停产，取Supernova Neons Lined近似"),
 "140": ("", "无在售", "Pop-up 3x3 Canary专用款，在售候选仅Recycled Pop-up 1.875不符"),
 "141": ("", "无在售", "Pop-up 4x4 Canary Lined专用款，在售候选仅Recycled Pop-up 1.875不符"),
 "144": ("", "无在售", "Recycled 4x4 Tropical Lined候选无，疑停产"),
 "145": ("B0BPJZ7P4T", "近似", "Recycled 4x6 Tropic Breeze，取Recycled Oasis 8 Pads近似"),
 "146": ("B07RK52772", "近似", "3x3 Assorted Jewel Pop停产，取Assorted Brights近似"),
 "147": ("B0002DOEOS", "较准", "4x6 Canary Yellow Lined 4 Pads，精准匹配（候选5 Pads）"),
 "148": ("B0BPJZ7P4T", "近似", "Recycled 4x6 Tropic Breeze，取Recycled Oasis近似（同145）"),
 "150": ("B0FZXNKJHV", "近似", "8x6 Bright停产，取6x6 Big Notes Washed Denim 2 Pads近似（尺寸接近）"),
 "155": ("", "无在售", "Pop-up 3x3 Jewel Pop专用款，在售候选仅Recycled Pop-up 1.875不符"),
 "156": ("B076XG2XRS", "近似", "5x8 Jewel Pop Lined停产，取Multi-Size Lined近似"),
 "158": ("B01D8F5NLY", "近似", "3x3 Electric Glow停产，取Supernova Neons 5 Pads近似"),
}

csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names = {}
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        names[r["行号"]] = r["产品名称"]

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_SuperSticky核对表.xlsx"
owb = openpyxl.Workbook()
sh = owb.active
sh.title = "SuperSticky匹配核对"
sh.append(["行号", "原产品名称", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"])
for ln in sorted(match, key=lambda x: int(x)):
    asin, conf, note = match[ln]
    name = names.get(ln, "")
    if asin:
        price = cand.get(asin, {}).get("price", "")
        link = cand.get(asin, {}).get("link", "")
    else:
        price = conf
        link = ""
    sh.append([int(ln), name, asin, price, link, conf, note])
owb.save(out)

ok = sum(1 for v in match.values() if v[1] == "较准")
wa = sum(1 for v in match.values() if v[1] == "近似")
no = sum(1 for v in match.values() if v[1] == "无在售")
wt = sum(1 for v in match.values() if v[1] == "待另搜")
print("已生成:", out)
print(f"Super Sticky系列共{len(match)}行 | 较准:{ok}  近似:{wa}  无在售:{no}  待另搜:{wt}")
print("待另搜行号:", [ln for ln, v in match.items() if v[1] == "待另搜"])
print("无在售行号:", [ln for ln, v in match.items() if v[1] == "无在售"])
