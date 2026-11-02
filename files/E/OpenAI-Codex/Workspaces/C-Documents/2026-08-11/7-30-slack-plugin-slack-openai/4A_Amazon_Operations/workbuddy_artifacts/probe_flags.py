import openpyxl, csv, re

fp = r"E:\Desktop\Search(Post-it-Flags)-56-US-20260806.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
header = data[0]
idx = {h: i for i, h in enumerate(header)}
ai = idx["ASIN"]; bi = idx["品牌"]; ti = idx["商品标题"]; pi = idx["价格($)"]

print("导出总行:", len(data) - 1)
brands = sorted({str(r[bi] or "") for r in data[1:] if r[bi]})
print("品牌列非空值:", brands[:12])

pit = []
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I):
        pit.append({"asin": row[ai], "title": t, "price": row[pi]})
print("Post-it 候选:", len(pit), "\n")

# 标题含 flag 的
flag = [p for p in pit if re.search(r'flag', p["title"], re.I)]
print("=== 标题含 'flag' 的候选 (%d) ===" % len(flag))
for p in flag:
    print(f"{p['asin']}  ${p['price']}")
    print(f"   {p['title']}")
