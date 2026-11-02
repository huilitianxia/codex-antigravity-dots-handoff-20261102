import openpyxl, csv, re

fp = r"E:\Desktop\Search(Post-it-Note-Dispenser)-63-US-20260806.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
header = data[0]
idx = {h: i for i, h in enumerate(header)}
ai = idx["ASIN"]; bi = idx["品牌"]; ti = idx["商品标题"]; pi = idx["价格($)"]; li = idx["商品详情页链接"]

print("导出总行:", len(data) - 1)
print("品牌列非空值:", sorted({str(r[bi] or "") for r in data[1:] if r[bi]})[:10])

pit = []
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I):
        pit.append({"asin": row[ai], "title": t, "price": row[pi], "link": row[li]})

print("Post-it 候选:", len(pit), "\n")

# 标题里带 dispenser 的
disp = [p for p in pit if re.search(r'dispens', p["title"], re.I)]
print("=== 标题含 'dispenser' 的候选 (%d) ===" % len(disp))
for p in disp:
    print(f"{p['asin']}  ${p['price']}")
    print(f"   {p['title']}")
