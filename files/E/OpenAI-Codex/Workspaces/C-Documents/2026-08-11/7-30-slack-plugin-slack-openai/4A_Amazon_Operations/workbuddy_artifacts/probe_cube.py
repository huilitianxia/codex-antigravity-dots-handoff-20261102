import openpyxl, csv, re
from collections import defaultdict, Counter

fp = r"E:\Desktop\Search(Post-it-Notes-Cube)-56-US-20260805.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
header = data[0]
idx = {h: i for i, h in enumerate(header)}
ai = idx["ASIN"]; bi = idx["品牌"]; ti = idx["商品标题"]; pi = idx["价格($)"]
print("导出总行:", len(data) - 1)

# 候选：标题含 post-it 且含 cube
cand = []
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I) and 'cube' in t.lower():
        cand.append({"asin": row[ai], "title": t, "price": row[pi]})
print("Post-it Cube 候选:", len(cand))

# 按尺寸/子类分组
def size_of(s):
    m = re.search(r'(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)', s)
    if m: return f"{m.group(1)}x{m.group(2)}"
    m = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|in\b)', s.lower())
    return m.group(1) + "in" if m else "?"

buckets = defaultdict(list)
for c in cand:
    buckets[size_of(c["title"])].append(c)

print("\n=== 候选池按尺寸分组 ===")
for sz in sorted(buckets):
    print(f"\n## 尺寸 {sz}: {len(buckets[sz])} 个")
    for c in buckets[sz]:
        print(f"  {c['asin']}  ${c['price']}")
        print(f"     {c['title']}")

# 原表 Cube 类行
csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
print("\n=== 原表 Cube 类 ===")
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        name = r["产品名称"]
        t = name.split("®", 1)[-1].split(",")[0].strip()
        if "cube" in t.lower():
            print(f"  行{r['行号']:>3} | 2013价={r['2013价格']} | {name}")
