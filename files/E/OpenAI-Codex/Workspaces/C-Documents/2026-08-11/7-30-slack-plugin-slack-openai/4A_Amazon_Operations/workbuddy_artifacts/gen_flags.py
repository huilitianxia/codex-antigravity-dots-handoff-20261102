import openpyxl, csv, re

# 1) 读 export，拿 asin -> price/link
fp = r"E:\Desktop\Search(Post-it-Flags)-56-US-20260806.xlsx"
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

# 2) 人工校订匹配（行96已在Dispenser批匹配，跳过）
match = {
    "23":  ("B000E93LZI", "✅较准", "Highlighting Flags Brights w/ Highlighter(680-PPBGVA)，精准"),
    "24":  ("B00QL1AW00", "⚠️近似", "On-the-Go 1in P/B/G 无精确款，取 Combo On-the-Go 套装近似"),
    "25":  ("B00QL1AW00", "⚠️近似", "On-the-Go 1in Alternating 无精确款，取 Combo On-the-Go 套装近似"),
    "26":  ("B00008IS18", "⚠️近似", "Bright Pink 1in 无在售，取 1in Multicolor 4 Dispensers 近似"),
    "27":  ("B00006JNMF", "✅精准", "Yellow 1in 50/Disp 2/Pack (680-YW2) 完全匹配"),
    "28":  ("B00006JNO7", "✅精准", "Blue 1in 50/Disp 2/Pack 完全匹配"),
    "29":  ("B00006JNMN", "⚠️近似", "Message Flags Signature Set 无，取 Sign Here Assorted 4 Pack 近似"),
    "30":  ("B000MK4RAM", "✅较准", "Highlighting Flags 683-VAD1 (35/Disp 8/Pack, 含Arrow) 精准"),
    "31":  ("B0006ZERXA", "⚠️近似", "Brights .47x1.7 约88/Pack，取 5色 100/Pack 近似"),
    "32":  ("B000BM869E", "✅精准", "Arrow Flags Primary 1/2in 100/Disp 完全匹配"),
    "33":  ("", "❌无在售", "Medical Flags 3/8in 候选池无，疑停产"),
    "34":  ("B00125QDD0", "⚠️近似", "Primary 1in Value Pack 200+Flag Pen，取 680-RD12 Red 12 Disp 近似(无混色款)"),
    "35":  ("B00006JNM7", "⚠️近似", "Sign and Date 无，取 Sign Here 1in 2 Dispensers 近似"),
    "36":  ("B00006JNMF", "✅精准", "Yellow 1in 50/Disp 2/Pack (680-YW2) 同27"),
    "37":  ("B077W3BNRF", "✅较准", "On-the-Go 1/2in Assorted 190 Flags，精准"),
    "38":  ("B00006JNMN", "⚠️近似", "Sign Here Brights 1in 200/Pack 无精确款，取 Sign Here .47 4 Pack 近似"),
    "39":  ("B00125QDD0", "⚠️近似", "同34 Primary 1in Value Pack，取 680-RD12 近似"),
    "40":  ("B01C5IHTOY", "⚠️近似", "1in+1/2in 240/Pk Primary，取 683-VAD1 (.47+Arrow) 近似"),
    "41":  ("B000E93LZI", "⚠️近似", "Flag+Highlighter 无精确款，取 Flags+Highlighter 组合包近似"),
    "42":  ("B000E93LZI", "⚠️近似", "同41 Flag+Highlighter，取 Flags+Highlighter 组合包近似"),
    "43":  ("B09B15L8Q5", "⚠️近似", "Combo Pack (1/2in Flags+3x3 Notes+Pen) 无精确款，取 Ultimate Flags&Tabs 组合包近似"),
}

# 3) 产品名
csvp = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\3M价格_搜索辅助.csv"
names = {}
with open(csvp, encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        names[r["行号"]] = r["产品名称"]

# 4) 生成核对表
out = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_Flags核对表.xlsx"
owb = openpyxl.Workbook(); sh = owb.active; sh.title = "Flags匹配核对"
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
print(f"Flags 共{len(match)}行 | ✅精准/较准:{ok}  ⚠️近似:{wa}  ❌无在售:{no}")
print("无在售:", [ln for ln, v in match.items() if v[1].startswith("❌")])
