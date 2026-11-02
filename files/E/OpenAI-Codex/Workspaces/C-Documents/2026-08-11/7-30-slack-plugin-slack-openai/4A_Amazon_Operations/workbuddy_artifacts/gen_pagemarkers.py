import openpyxl, csv, re

# 1) 读 export，拿 asin -> price/link
fp = r"E:\Desktop\Search(Post-it-Page-Markers)-56-US-20260806.xlsx"
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

# 2) 人工校订匹配（CSV 行 49-52 为 Page Markers）
match = {
    "49": ("B01M4OB6DI", "⚠️近似", "1x3in 50/pad Ultra Colors，取 4-Pads/Pack(4) 近似（源为12Pads/Pk，无单独在售）"),
    "50": ("B00007FJZ1", "✅较准", "670-5AN 1/2x2 100/pad 5Pads，尺寸/片数/包数精准，色系标 Assorted（源称 Ultra Colors）"),
    "51": ("B007FGY3HI", "⚠️近似", "670-4-D 1/2x1.75in Rainbow，尺寸精准，源为 Bright 50/pad 8Pads，包数/片数近似"),
    "52": ("B00007FJZ1", "✅较准", "与行50同规格(重复条目)，取 670-5AN 1/2x2 100/pad 5Pads 近似"),
}

# 3) 产品名
csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names = {}
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        names[r["行号"]] = r["产品名称"]

# 4) 生成核对表
out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_PageMarkers核对表.xlsx"
owb = openpyxl.Workbook(); sh = owb.active; sh.title = "PageMarkers匹配核对"
sh.append(["行号", "原产品名称", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"])
for ln in sorted(match, key=lambda x: int(x)):
    asin, conf, note = match[ln]
    sh.append([int(ln), names.get(ln, ""), asin,
               info.get(asin, {}).get("price", "") if asin else "无在售",
               info.get(asin, {}).get("link", "") if asin else "",
               conf, note])
owb.save(out)

ok = sum(1 for v in match.values() if v[1].startswith("✅"))
wa = sum(1 for v in match.values() if v[1].startswith("⚠"))
no = sum(1 for v in match.values() if v[1].startswith("❌"))
print("已生成:", out)
print(f"Page Markers 共{len(match)}行 | ✅精准/较准:{ok}  ⚠️近似:{wa}  ❌无在售:{no}")
print("明细:")
for ln in sorted(match, key=lambda x: int(x)):
    a, c, n = match[ln]
    p = info.get(a, {}).get("price", "无") if a else "无在售"
    print(f"  行{ln}: {a}  ${p}  {c}  {n}")
