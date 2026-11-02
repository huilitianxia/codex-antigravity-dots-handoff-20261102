import openpyxl, csv

# 本批导出 56 行，Post-it 候选 21 个，但无 1 个是 Pockets 产品；
# 全表 31 个含 "pocket" 的行均为第三方品牌（Zonon/Chinco/Avery/Five Star 等），
# Post-it 品牌 Pockets（w/Closure、Wall Pockets）已无在售 → 全部标 无在售。
match = {
    "63": ("", "❌无在售", "Pockets w/Closure Medium 5 1/4x7 7/8 Clear w/Dots 3/Pk，导出无 Post-it Pockets 候选，疑停产"),
    "64": ("", "❌无在售", "Pockets Large 9x12 Clear with Dots 1/Pack，同上无在售"),
    "65": ("", "❌无在售", "Pockets with Closure Small 5 3/8x5 5/8 Clear w/Dots 3/Pk，同上无在售"),
    "66": ("", "❌无在售", "Wall Pockets Medium 5 3/8x7 7/8 Greek Key 2/Pack，同上无在售"),
}

csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names = {}
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        names[r["行号"]] = r["产品名称"]

out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_Pockets核对表.xlsx"
owb = openpyxl.Workbook(); sh = owb.active; sh.title = "Pockets匹配核对"
sh.append(["行号", "原产品名称", "匹配ASIN", "亚马逊价格($)", "亚马逊链接", "置信度", "备注"])
for ln in sorted(match, key=lambda x: int(x)):
    asin, conf, note = match[ln]
    sh.append([int(ln), names.get(ln, ""), asin,
               "" if not asin else "",
               "" if not asin else "",
               conf, note])
owb.save(out)

no = sum(1 for v in match.values() if v[1].startswith("❌"))
print("已生成:", out)
print(f"Pockets 共{len(match)}行 | ❌无在售:{no}（Post-it 品牌 Pockets 全线疑似停产/退亚马逊）")
