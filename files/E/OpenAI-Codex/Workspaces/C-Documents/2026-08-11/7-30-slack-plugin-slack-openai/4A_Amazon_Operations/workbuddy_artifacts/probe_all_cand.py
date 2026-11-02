import openpyxl, re

files = {
 "Notes(泛搜)": r"E:\Desktop\Search(Post-it-Notes)-56-US-20260805.xlsx",
 "Mini-Notes": r"E:\Desktop\Search(Post-it-Mini-Notes)-62-US-20260805.xlsx",
 "Ultra": r"E:\Desktop\Search(Post-it-Ultra-Collection-Notes)-56-US-20260805.xlsx",
 "Fashionista": r"E:\Desktop\Search(Post-it-Fashionista-Notes)-56-US-20260805.xlsx",
}
EXCLUDE = ["super sticky","super-sticky","cube","\btab","flag","label","pop-up","pop up",
           "page marker","pocket","restickable","full adhesive","dispenser","big notes"]

for tag,fp in files.items():
    wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
    ws = wb["US"]; data=list(ws.iter_rows(values_only=True))
    idx={h:i for i,h in enumerate(data[0])}
    ai=idx["ASIN"]; ti=idx["商品标题"]; pi=idx["价格($)"]
    rows=[]
    for row in data[1:]:
        t=str(row[ti] or ""); tl=t.lower()
        if not re.search(r'post-it',tl): continue
        if not re.search(r'\bnote',tl): continue
        if any(re.search(p,tl) for p in EXCLUDE): continue
        rows.append((row[ai],row[pi],t))
    print(f"\n########## {tag}: {len(rows)} 个普通Notes候选 ##########")
    for a,p,t in rows:
        print(f"  {a}  ${p}\n     {t}")
