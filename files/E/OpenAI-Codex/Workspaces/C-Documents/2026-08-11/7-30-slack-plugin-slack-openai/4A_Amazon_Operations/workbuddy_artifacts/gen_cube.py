import openpyxl, csv, re

fp = r"E:\Desktop\Search(Post-it-Notes-Cube)-56-US-20260805.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
idx = {h: i for i, h in enumerate(data[0])}
ai = idx["ASIN"]; ti = idx["商品标题"]; pi = idx["价格($)"]

cand = {}
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I) and 'cube' in t.lower():
        cand[row[ai]] = {"price": row[pi], "link": f"https://www.amazon.com/dp/{row[ai]}"}

match = {
    "117": ("B0C3J5ZFXG", "⚠️近似", "3x3 Bright Colors；原'3x3+1x3 Assorted Brights 6 Pads组合装'无完全对应，取最近3x3 Brights单cube"),
    "132": ("B0C3J5ZFXG", "⚠️近似", "与117同款重复行，取同一款"),
    "135": ("B07DGRDG8C", "⚠️近似", "2x2 Neon Collection无在售cube（候选池仅3x3），取3x3 Supernova Neons近似，尺寸有差"),
    "149": ("B0C3J5ZFXG", "⚠️近似", "Ultra Collection 3x3无在售，取3x3 Bright Colors近似，色系不同"),
}

csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names = {}
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        names[r["行号"]] = r["产品名称"]

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_Cube核对表.xlsx"
owb = openpyxl.Workbook(); sh = owb.active; sh.title = "Cube匹配核对"
sh.append(["行号", "原产品名称", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"])
for ln in sorted(match, key=lambda x: int(x)):
    asin, conf, note = match[ln]
    name = names.get(ln, "")
    price = cand.get(asin, {}).get("price", "") if asin else "无在售"
    link = cand.get(asin, {}).get("link", "") if asin else ""
    sh.append([int(ln), name, asin, price, link, conf, note])
owb.save(out)
print("已生成:", out)
print("Cube 类共", len(match), "行，全部为⚠️近似（老款/组合装无完全对应）")
