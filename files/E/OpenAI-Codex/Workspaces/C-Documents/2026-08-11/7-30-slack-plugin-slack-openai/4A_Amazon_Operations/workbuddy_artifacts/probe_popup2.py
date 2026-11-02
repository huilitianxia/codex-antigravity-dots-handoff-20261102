import openpyxl, re

fp = r"E:\Desktop\Search(Post-it-Pop-up-Notes)-56-US-20260806.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
header = data[0]
idx = {h: i for i, h in enumerate(header)}
ai = idx["ASIN"]; ti = idx["商品标题"]; pi = idx["价格($)"]

pit = []
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I):
        pit.append({"asin": row[ai], "title": t, "price": row[pi]})

def is_disp(t):
    return "dispenser" in t.lower() or "dispenser" in t.lower()

print("=== 全部 %d 个候选（含 Dispenser 与否分组）===\n" % len(pit))
disp = [p for p in pit if is_disp(p["title"])]
refill = [p for p in pit if not is_disp(p["title"])]
print("### Dispenser（座/套装）: %d 个" % len(disp))
for p in disp:
    print(f"  {p['asin']}  ${p['price']}  {p['title']}")
print("\n### 纯 Notes 补充装（refill）: %d 个" % len(refill))
for p in refill:
    print(f"  {p['asin']}  ${p['price']}  {p['title']}")
