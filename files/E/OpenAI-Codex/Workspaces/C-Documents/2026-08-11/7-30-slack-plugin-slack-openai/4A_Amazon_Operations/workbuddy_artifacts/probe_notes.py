import openpyxl, csv, re
from collections import defaultdict, Counter

fp = r"E:\Desktop\Search(Post-it-Notes)-56-US-20260805.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
idx = {h: i for i, h in enumerate(data[0])}
ai = idx["ASIN"]; bi = idx["品牌"]; ti = idx["商品标题"]; pi = idx["价格($)"]
print("导出总行:", len(data) - 1)

# 候选：标题含 post-it 且含 notes，但排除其他子类（避免重复计入 cube/tabs/flags 等）
EXCLUDE = ["cube", "tab", "flag", "label", "pocket", "page marker", "restickable", "full adhesive", "pop-up", "pop up"]
cand = []
for row in data[1:]:
    t = str(row[ti] or "")
    tl = t.lower()
    if re.search(r'post-it', t, re.I) and 'note' in tl:
        if any(x in tl for x in EXCLUDE):
            continue
        cand.append({"asin": row[ai], "title": t, "price": row[pi]})
print("Post-it 普通 Notes 候选(已排除其他子类):", len(cand))

# 子类型/尺寸分布
def size_of(s):
    m = re.search(r'(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)', s)
    if m: return f"{m.group(1)}x{m.group(2)}"
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|in\b)', s.lower())
    return m.group(1) + "in" if m else "?"
sz = Counter(size_of(c["title"]) for c in cand)
print("\n尺寸分布:")
for k, n in sorted(sz.items()):
    print(f"  {n:3d}  {k}")

coll = Counter()
for c in cand:
    tl = c["title"].lower()
    for kw in ["lined", "ruled", "supernova", "neon", "bright", "canary", "jewel", "pink", "pastel",
               "cape", "marrakesh", "tropical", "ultra", "assorted", "primary", "bold", "value pack",
               "mega", "big", "mini", "greener", "recycled", "printed", "floral", "designer", "cabinet"]:
        if kw in tl: coll[kw] += 1
print("\n关键词分布(前15):")
for k, n in coll.most_common(15):
    print(f"  {n:3d}  {k}")

# 原表"普通 Notes"类（类型恰好 Notes，排除所有带前缀的）
csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
print("\n=== 原表 纯 'Notes' 类型行 ===")
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        name = r["产品名称"]
        t = name.split("®", 1)[-1].split(",")[0].strip()
        # 纯 Notes：不含 Super Sticky/Cube/Pop-up/Recycled/Greener/Printed/Label/Flag/Tab/Pocket/Restickable/Page Marker
        if t == "Notes":
            print(f"  行{r['行号']:>3} | 2013价={r['2013价格']} | {name}")
