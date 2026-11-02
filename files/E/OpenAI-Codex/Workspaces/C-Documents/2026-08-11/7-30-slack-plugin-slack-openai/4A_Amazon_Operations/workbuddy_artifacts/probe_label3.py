import openpyxl, re

fp = r"E:\Desktop\Search(Post-it-Label-Pads)-62-US-20260804.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
header = data[0]; idx = {h:i for i,h in enumerate(header)}
ai = idx["ASIN"]; ti = idx["商品标题"]; pi = idx["价格($)"]; bi = idx["品牌"]; li = idx["商品详情页链接"]
print(f"导出总行: {len(data)-1}")
print("非空品牌值:", set(str(r[bi] or "") for r in data[1:] if r[bi]))

cand = []
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I):
        cand.append({"asin":row[ai],"title":t,"price":row[pi],"brand":str(row[bi] or ""),"link":row[li]})
print(f"\nPost-it 候选: {len(cand)} 个")
print("="*80)
for c in cand:
    print(f"{c['asin']}  ${c['price']}  [{c['brand']}]")
    print(f"   {c['title'][:120]}")
