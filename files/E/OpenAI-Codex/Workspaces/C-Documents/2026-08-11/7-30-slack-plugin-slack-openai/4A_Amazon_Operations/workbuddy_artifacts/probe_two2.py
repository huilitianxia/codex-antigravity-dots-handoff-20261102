import openpyxl, re

files = {
    "FULL": r"E:\Desktop\Search(Post-it-Full-Adhesive)-73-US-20260804.xlsx",
    "LABEL": r"E:\Desktop\Search(Post-it-Label-Pads)-56-US-20260804.xlsx",
}

def size_of(s):
    m = re.search(r'(\d+(?:\.\d+)?)\s*[xX]\s*(\d+(?:\.\d+)?)', s)
    if m: return f"{m.group(1)}x{m.group(2)}"
    m = re.search(r'(\d+(?:\.\d+)?)\s*inch', s.lower())
    return f"{m.group(1)}in" if m else "?"

for tag, fp in files.items():
    wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
    ws = wb["US"]
    data = list(ws.iter_rows(values_only=True))
    header = data[0]; idx = {h:i for i,h in enumerate(header)}
    ai = idx["ASIN"]; ti = idx["商品标题"]; pi = idx["价格($)"]; li = idx["商品详情页链接"]
    print(f"\n########## {tag} 导出 (总行 {len(data)-1}) ##########")
    cand = []
    for row in data[1:]:
        t = str(row[ti] or "")
        if re.search(r'post-it', t, re.I):
            cand.append({"asin":row[ai],"title":t,"price":row[pi],"link":row[li]})
    print(f"Post-it 候选: {len(cand)} 个\n")
    for c in cand:
        print(f"{c['asin']}  ${c['price']}  [{size_of(c['title'])}]")
        print(f"   {c['title'][:120]}")
