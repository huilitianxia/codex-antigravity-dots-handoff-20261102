import openpyxl

path = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_SuperSticky核对表.xlsx"
wb = openpyxl.load_workbook(path)
sh = wb.active
# 列: 0行号 1名称 2ASIN 3价格 4链接 5置信度 6备注
full_note = "导出的'Full Adhesive'搜索结果被普通Super Sticky Notes淹没，无Full Adhesive款；需改搜'Post-it Full Adhesive Notes'重导"
label_note = "导出的'Label Pads'搜索结果被普通Notes淹没，无Label Pads款；需改搜'Post-it Label Pads'重导"

for row in sh.iter_rows(min_row=2):
    ln = row[0].value
    if ln in (53, 54, 55):
        row[6].value = full_note
        print(f"行{ln} 备注已更新 -> Full Adhesive")
    elif ln in (57, 58, 59, 60, 61, 62):
        row[6].value = label_note
        print(f"行{ln} 备注已更新 -> Label Pads")
wb.save(path)
print("已保存:", path)
