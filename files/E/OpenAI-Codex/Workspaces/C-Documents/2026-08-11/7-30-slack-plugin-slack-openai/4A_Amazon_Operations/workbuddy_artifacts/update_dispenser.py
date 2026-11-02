import openpyxl, csv, re

# 1) 读 dispenser 导出，拿 asin -> (price, link)
fp = r"E:\Desktop\Search(Post-it-Note-Dispenser)-63-US-20260806.xlsx"
wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
ws = wb["US"]
data = list(ws.iter_rows(values_only=True))
idx = {h: i for i, h in enumerate(data[0])}
ai = idx["ASIN"]; ti = idx["商品标题"]; pi = idx["价格($)"]
info = {}
for row in data[1:]:
    t = str(row[ti] or "")
    if re.search(r'post-it', t, re.I) and row[ai]:
        info[row[ai]] = {"price": row[pi], "link": f"https://www.amazon.com/dp/{row[ai]}"}

# 2) 人工校订匹配
match = {
    "93":  ("B004YQZPVA", "✅精准", "Apple 造型座 APL-330，完全匹配（原 Red Apple）"),
    "94":  ("B0BSRB9VPJ", "⚠️近似", "Clutch Purse 造型座无在售，取 Black Wave 设计座近似"),
    "95":  ("B00008IOXK", "⚠️近似", "Heart 造型座无在售，取 Black Base 通用座近似"),
    "96":  ("B000UHGJTO", "✅精准", "Note & Flag 双用座，完全匹配"),
    "97":  ("B00OILMU8M", "✅较准", "Professional 系列 WD-330-BK，Black Base Clear Top 精准"),
    "98":  ("B00008IOXK", "⚠️近似", "Black Purse 造型座无在售，取 Black Base 通用座近似"),
    "99":  ("B0015ZWQBK", "⚠️近似", "Value Pack 带座，原 Pink 18片→现 Assorted 12片 Value Pack(DS330-SSVA)"),
    "100": ("B00OILMU8M", "⚠️近似", "JAX-330 白色+Electric Glow 无在售，取同系列 WD-330-BK 黑色近似"),
    "101": ("B07K8YVDZZ", "⚠️近似", "Diamond 造型座无在售，取 Geometric 设计座近似"),
}

# 3) 更新原表产品名
csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names = {}
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        names[r["行号"]] = r["产品名称"]

# 4) 更新 Pop-up 核对表
popup_path = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_Popup核对表.xlsx"
owb = openpyxl.load_workbook(popup_path)
osh = owb.active
hdr = [c.value for c in osh[1]]
ci = {h: i for i, h in enumerate(hdr)}
for row in osh.iter_rows(min_row=2):
    ln = str(row[ci["行号"]].value)
    if ln in match:
        asin, conf, note = match[ln]
        row[ci["匹配ASIN"]].value = asin
        row[ci["亚马逊价格($)"]].value = info.get(asin, {}).get("price", "")
        row[ci["亚马逊链接"]].value = info.get(asin, {}).get("link", "")
        row[ci["置信度"]].value = conf
        row[ci["备注"]].value = note
owb.save(popup_path)
print("已更新 Pop-up 核对表 9 行:", list(match.keys()))

# 5) 生成独立 Dispenser 核对表
out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_Dispenser核对表.xlsx"
d = openpyxl.Workbook(); sh = d.active; sh.title = "Dispenser匹配核对"
sh.append(["行号", "原产品名称", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"])
for ln in sorted(match, key=lambda x: int(x)):
    asin, conf, note = match[ln]
    sh.append([int(ln), names.get(ln, ""), asin,
               info.get(asin, {}).get("price", ""),
               info.get(asin, {}).get("link", ""), conf, note])
d.save(out)
print("已生成 Dispenser 独立核对表:", out)

# 统计
ok = sum(1 for v in match.values() if v[1].startswith("✅"))
wa = sum(1 for v in match.values() if v[1].startswith("⚠"))
print(f"Dispenser 9行 | ✅精准/较准:{ok}  ⚠️近似:{wa}")
