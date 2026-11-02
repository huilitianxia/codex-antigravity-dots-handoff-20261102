import openpyxl, re, csv

files = [
    r"E:\Desktop\Search(Post-it-Notes)-56-US-20260805.xlsx",
    r"E:\Desktop\Search(Post-it-Mini-Notes)-62-US-20260805.xlsx",
    r"E:\Desktop\Search(Post-it-Ultra-Collection-Notes)-56-US-20260805.xlsx",
    r"E:\Desktop\Search(Post-it-Fashionista-Notes)-56-US-20260805.xlsx",
]
EXCLUDE = ["super sticky","super-sticky","cube","\btab","flag","label","pop-up","pop up",
           "page marker","pocket","restickable","full adhesive","dispenser","big notes"]

cand = {}
for fp in files:
    wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
    ws = wb["US"]; data=list(ws.iter_rows(values_only=True))
    idx={h:i for i,h in enumerate(data[0])}
    ai=idx["ASIN"]; ti=idx["商品标题"]; pi=idx["价格($)"]
    for row in data[1:]:
        t=str(row[ti] or ""); tl=t.lower()
        if not re.search(r'post-it',tl): continue
        if not re.search(r'\bnote',tl): continue
        if any(re.search(p,tl) for p in EXCLUDE): continue
        a=row[ai]
        if a in cand: continue
        cand[a]={"price":row[pi],"link":f"https://www.amazon.com/dp/{a}"}

match = {
 "103":("B000BKZ996","⚠️近似","4x6 Lined尺寸对；原Designer Fuchsia无在售，取Sweet Sprinkles粉彩近似"),
 "106":("B0GPS3VDB5","⚠️近似","4x3 Fashionista设计款停产（Fashionista文件无此字样）；取3x3 Polished Patterns Bubble Blush粉色图案款近似"),
 "107":("B0GPSF2ZQY","⚠️近似","4x3 Fashionista设计款停产；取3x3 Polished Patterns Blue Cottage蓝调图案款近似"),
 "127":("B000UI6AG0","✅精准","3x3 Canary Yellow Lined 12 Pads，完全匹配"),
 "129":("B00006JNNP","⚠️近似","1.5x2尺寸对；原Ultra Collection无对应款，取同尺寸Greener Canary近似"),
 "133":("B01C8MCISE","⚠️近似","3x3尺寸对；原Neon Lined无3x3 neon在售，取同尺寸Poptimistic彩色系近似（lined未标注）"),
 "151":("B000UI6AG0","✅精准","3x3 Canary Yellow Lined 12 Pads，与行127同款"),
 "157":("B01C8MCISE","⚠️近似","3x3尺寸对；原Ultra Collection Lined无对应，取同尺寸Poptimistic彩色系近似（lined未标注）"),
}

csvp=r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names={}
with open(csvp,encoding="utf-8-sig") as f:
    for r in csv.DictReader(f): names[r["行号"]]=r["产品名称"]

out=r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_普通核对表.xlsx"
owb=openpyxl.Workbook(); sh=owb.active; sh.title="普通Notes匹配核对"
sh.append(["行号","原产品名称","匹配ASIN","亚马逊价格($)","亚马逊链接","置信度","备注"])
for ln in sorted(match,key=lambda x:int(x)):
    asin,conf,note=match[ln]
    name=names.get(ln,"")
    price=cand.get(asin,{}).get("price","") if asin else ""
    link=cand.get(asin,{}).get("link","") if asin else ""
    sh.append([int(ln),name,asin,price,link,conf,note])
owb.save(out)

ok=sum(1 for v in match.values() if v[1].startswith("✅"))
wa=sum(1 for v in match.values() if v[1].startswith("⚠"))
print("已生成:",out)
print(f"普通Notes共{len(match)}行 | ✅精准:{ok}  ⚠️近似:{wa}")
