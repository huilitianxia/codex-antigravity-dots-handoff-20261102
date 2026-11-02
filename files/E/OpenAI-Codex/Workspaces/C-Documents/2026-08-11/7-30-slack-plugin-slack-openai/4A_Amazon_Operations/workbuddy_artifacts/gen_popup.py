import openpyxl, csv, re

fp = r"E:\Desktop\Search(Post-it-Pop-up-Notes)-56-US-20260806.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
header = data[0]
idx = {h: i for i, h in enumerate(header)}
ai = idx["ASIN"]; ti = idx["商品标题"]; pi = idx["价格($)"]
cand = {}
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I):
        cand[row[ai]] = {"price": row[pi], "link": f"https://www.amazon.com/dp/{row[ai]}"}

# 人工校订：仅 Notes 本体行（Dispenser 座 → 待另搜）
match = {
    # ---- Notes 本体（本批可匹配）----
    "120": ("B0DX47M2HS", "⚠️近似", "Greener 3x3 Sunwashed Pier 6片 → 取100% Recycled Super Sticky 3x3 Oasis 5片（Greener≈Recycled，色系近似）"),
    "121": ("B0BPJXLXB7", "⚠️近似", "Greener 3x3 Canary 12片 → 取100% Recycled Super Sticky 3x3 Canary 6片（片数不同）"),
    "126": ("B01C8MCISE", "⚠️近似", "Pop-up 3x3 Ultra Collection 5片 → Ultra已无，取Notes 3x3 Poptimistic 18片近似"),
    "138": ("B001AS8B8E", "⚠️近似", "Super Sticky Printed Pop-up 3x3 3色 6片 → 取Super Sticky Pop-up Poptimistic 6片近似（Printed图案款无）"),
    "140": ("B000TSE48W", "✅精准", "Super Sticky Pop-up 3x3 Canary 12片，完全匹配"),
    "141": ("", "❌无在售", "Super Sticky Pop-up 4x4 Canary Lined 5片 → 候选池无4x4款，疑停产"),
    "142": ("B00006JNL4", "✅精准", "Pop-up 3x3 Canary Yellow Lined 6片，完全匹配"),
    "143": ("B002IXCE3S", "⚠️近似", "Pop-up 3x3 Assorted Citrus 6片 → 取Assorted Brights 5片近似（Citrus≈Brights）"),
    "155": ("B001AS8B8E", "⚠️近似", "Super Sticky Pop-up 3x3 Jewel Pop 6片 → Jewel Pop已无，取Poptimistic 6片近似"),
    # ---- Dispenser 座（本批无候选，需另搜 Post-it Note Dispenser）----
    "93":  ("", "⏳待另搜", "Pop-up Notes Dispenser Apple Shaped Red 3x3 → 需搜'Post-it Note Dispenser'"),
    "94":  ("", "⏳待另搜", "Pop-up Note Dispenser Clutch Purse 3x3 → 需搜'Post-it Note Dispenser'"),
    "95":  ("", "⏳待另搜", "Pop-up Notes Dispenser Red Heart Shape 3x3 → 需搜'Post-it Note Dispenser'"),
    "96":  ("", "⏳待另搜", "Pop-up Notes and Flags Dispenser Starter Kit → 需搜'Post-it Note Dispenser'"),
    "97":  ("", "⏳待另搜", "Pop-up Note Dispenser Professional Series 3x3 → 需搜'Post-it Note Dispenser'"),
    "98":  ("", "⏳待另搜", "Pop-up Notes Dispenser Black Purse 3x3 → 需搜'Post-it Note Dispenser'"),
    "99":  ("", "⏳待另搜", "Pop-up Notes Value Pack 3x3 Pink 18Pds WITH Dispenser → 需搜'Post-it Note Dispenser'"),
    "100": ("", "⏳待另搜", "Pop-up Note Dispenser JAX-330 White Electric Glow → 需搜'Post-it Note Dispenser'"),
    "101": ("", "⏳待另搜", "Pop-up Note Dispenser Diamond shaped 3x3 → 需搜'Post-it Note Dispenser'"),
}

# 行79 是 Scotch 胶带座，归 Tape 批，不在本表
csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names = {}
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        names[r["行号"]] = r["产品名称"]

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_Popup核对表.xlsx"
owb = openpyxl.Workbook(); sh = owb.active; sh.title = "Popup匹配核对"
sh.append(["行号", "原产品名称", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"])
# 排序：先 Notes 本体再 Dispenser
order = [120, 121, 126, 138, 140, 141, 142, 143, 155, 93, 94, 95, 96, 97, 98, 99, 100, 101]
for ln in order:
    asin, conf, note = match[str(ln)]
    name = names.get(str(ln), "")
    price = cand.get(asin, {}).get("price", "") if asin else ("待另搜" if "待另搜" in conf else "无在售")
    link = cand.get(asin, {}).get("link", "") if asin else ""
    sh.append([int(ln), name, asin, price, link, conf, note])
owb.save(out)

ok = sum(1 for v in match.values() if v[1].startswith("✅"))
wa = sum(1 for v in match.values() if v[1].startswith("⚠"))
no = sum(1 for v in match.values() if v[1].startswith("❌"))
wt = sum(1 for v in match.values() if v[1].startswith("⏳"))
print("已生成:", out)
print(f"Popup 系列共{len(match)}行(不含行79 Scotch胶带座) | ✅精准:{ok}  ⚠️近似:{wa}  ❌无在售:{no}  ⏳待另搜:{wt}")
print("待另搜行号(Dispenser座):", [ln for ln, v in match.items() if v[1].startswith('⏳')])
