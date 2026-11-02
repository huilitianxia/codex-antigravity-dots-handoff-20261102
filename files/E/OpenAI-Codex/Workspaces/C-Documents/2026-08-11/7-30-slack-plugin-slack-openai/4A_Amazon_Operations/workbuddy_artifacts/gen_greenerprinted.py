import openpyxl, csv

# Greener-Printed 导出(50行) Post-it 候选 22 个，以 Greener Notes(654/653系列) 与 Greener Pop Up 为主；
# 不含 Recycled Super Sticky 与 Printed Pop-up 候选，故再生系(125/136/137/144/145/148)与印花系(138/139)
# 维持 SuperSticky 批原匹配，不在此覆盖。本批仅覆盖 Greener 系列 + Printed Notes(108无候选)。
match = {
    "108": ("", "❌无在售", "Printed Notes 4x3 Hipster 1 Pad，导出无 Printed Notes 候选，疑停产"),
    "118": ("B000BKZ996", "⚠️近似", "Greener Notes 4x6 Sweet Sprinkles 5 Lined Pads(100% Recycled)，尺寸/片数/包数精准，色系为 Sweet Sprinkles 非 Canary Yellow"),
    "120": ("B09PG9K36M", "⚠️近似", "Greener Pop Up Notes 3x3 18 Pads，尺寸精准，源为 Sunwashed Pier 6 Pads，包数/花色不符"),
    "121": ("B09PG9K36M", "⚠️近似", "Greener Pop Up Notes 3x3 18 Pads，尺寸精准，源为 Canary Yellow 12 Pads，包数/花色不符"),
}

csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names = {}
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        names[r["行号"]] = r["产品名称"]

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_GreenerPrinted核对表.xlsx"
owb = openpyxl.Workbook(); sh = owb.active; sh.title = "GreenerPrinted匹配核对"
sh.append(["行号", "原产品名称", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"])
for ln in sorted(match, key=lambda x: int(x)):
    asin, conf, note = match[ln]
    sh.append([int(ln), names.get(ln, ""), asin,
               "" if not asin else "",
               "" if not asin else f"https://www.amazon.com/dp/{asin}",
               conf, note])
owb.save(out)

ok = sum(1 for v in match.values() if v[1].startswith("✅"))
wa = sum(1 for v in match.values() if v[1].startswith("⚠"))
no = sum(1 for v in match.values() if v[1].startswith("❌"))
print("已生成:", out)
print(f"Greener+Printed 本批 {len(match)} 行 | ✅:{ok}  ⚠️近似:{wa}  ❌无在售:{no}")
for ln in sorted(match, key=lambda x: int(x)):
    a,c,n=match[ln]
    print(f"  行{ln}: {a}  {c}  {n}")
print("\n注：再生系 125/136/137/144/145/148 与印花系 138/139 已在 SuperSticky 批匹配，本导出无对应候选，不覆盖。")
