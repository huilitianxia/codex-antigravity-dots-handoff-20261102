import openpyxl, re

files = [
    r"E:\Desktop\Search(Post-it-Notes)-56-US-20260805.xlsx",
    r"E:\Desktop\Search(Post-it-Mini-Notes)-62-US-20260805.xlsx",
    r"E:\Desktop\Search(Post-it-Ultra-Collection-Notes)-56-US-20260805.xlsx",
    r"E:\Desktop\Search(Post-it-Fashionista-Notes)-56-US-20260805.xlsx",
]

EXCLUDE = ["super sticky","super-sticky","cube","\btab","flag","label","pop-up","pop up",
           "page marker","pocket","restickable","full adhesive","dispenser","big notes"]

cand = {}  # asin -> {price,link,title,src}
for fp in files:
    wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
    ws = wb["US"]
    data = list(ws.iter_rows(values_only=True))
    idx = {h:i for i,h in enumerate(data[0])}
    ai=idx["ASIN"]; ti=idx["商品标题"]; pi=idx["价格($)"]
    tag = fp.split("\\")[-1].split("US-")[0].replace("Search(","").replace(")","")
    for row in data[1:]:
        t = str(row[ti] or "")
        tl = t.lower()
        if not re.search(r'post-it', tl): continue
        if not re.search(r'\bnote', tl): continue
        if any(re.search(p, tl) for p in EXCLUDE): continue
        a = row[ai]
        if a in cand: continue
        cand[a] = {"asin":a,"price":row[pi],"link":f"https://www.amazon.com/dp/{a}","title":t,"src":tag}

print(f"合并后 普通Notes候选: {len(cand)} 个\n")

def norm(s):
    s=s.lower().replace("x","x")
    return s

targets = {
 "103":("4x6","designer"),
 "106":("4x3","fashionista"),
 "107":("4x3","fashionista"),
 "127":("3x3","canary"),
 "129":("1.5x2","ultra"),
 "133":("3x3","neon"),
 "151":("3x3","canary"),
 "157":("3x3","ultra"),
}

for ln,(sz,kw) in targets.items():
    kw_pool=[(k,c) for k,c in cand.items() if kw in c["title"].lower()]
    sz_pool=[(k,c) for k,c in cand.items() if sz.replace("x","x") in c["title"].lower().replace(" ","")]
    print(f"\n===== 行{ln} 目标尺寸{sz} 关键词:{kw} =====")
    print(f"  关键词'{kw}'命中 {len(kw_pool)} 个:")
    for k,c in kw_pool[:8]:
        print(f"    {c['src'][:14]:<14} {k} ${c['price']} | {c['title'][:80]}")
    if sz_pool:
        print(f"  尺寸'{sz}'命中 {len(sz_pool)} 个 (前5):")
        for k,c in sz_pool[:5]:
            print(f"    {c['src'][:14]:<14} {k} ${c['price']} | {c['title'][:80]}")
