import openpyxl, csv, re

# 1) 读 Sellersprite 导出
fp = r"E:\Desktop\Search(Post-it-Pop-up-Notes)-56-US-20260806.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
header = data[0]
idx = {h: i for i, h in enumerate(header)}
ai = idx["ASIN"]; ti = idx["商品标题"]; pi = idx["价格($)"]
print("导出总行:", len(data) - 1)

pit = []
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I):
        pit.append({"asin": row[ai], "title": t, "price": row[pi]})
print("Post-it 候选:", len(pit))

# 2) 原CSV 里 Pop-up 系列
csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
want = []
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        name = r["产品名称"]
        t = name.split("®", 1)[-1].split(",")[0].strip()
        if "Pop-up" in t or t == "Pop-up Notes":
            want.append((r["行号"], name, r["2013价格"]))

print(f"\n原表 Pop-up 系列: {len(want)} 行")
for ln, name, old in want:
    print(f"  行{ln:>3} | 2013价={old} | {name}")
