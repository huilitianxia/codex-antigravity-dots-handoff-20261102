import openpyxl

path = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_SuperSticky核对表.xlsx"
wb = openpyxl.load_workbook(path)
ws = wb.active

# 满胶 4A 自有替代款（用户前端确认）
updates = {
    53: ("B07QXJYTZ7", 22.99, "https://www.amazon.com/dp/B07QXJYTZ7",
         "✅4A自有替代", "3M Full Adhesive 3x3已停产，4A USA自有替代款(3x3满胶400张)"),
    54: ("B07QXJYTZ7", 22.99, "https://www.amazon.com/dp/B07QXJYTZ7",
         "⚠️近似", "原Farmers Market色已停产，取4A USA 3x3满胶近似款"),
    55: ("B0F2TKL2P5", 17.99, "https://www.amazon.com/dp/B0F2TKL2P5",
         "✅4A自有替代", "3M Full Adhesive 2x2已停产，4A USA自有替代款"),
}
# Label Pads：3M美区无正品，4A USA暂未搜到对应款，先标停产跳过
for r in range(57, 63):
    updates[r] = ("", "停产", "", "❌无在售(停产)",
                  "3M Label Pads美区无正品，4A USA暂未搜到对应款，先标停产跳过")

cnt = 0
for row in ws.iter_rows():
    ln = row[0].value
    if ln in updates:
        asin, price, link, conf, note = updates[ln]
        row[2].value = asin
        row[3].value = price
        row[4].value = link
        row[5].value = conf
        row[6].value = note
        cnt += 1

wb.save(path)
print(f"已更新 {cnt} 行")
