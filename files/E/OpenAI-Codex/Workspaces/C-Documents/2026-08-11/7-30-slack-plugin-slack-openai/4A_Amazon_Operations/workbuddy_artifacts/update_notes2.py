import openpyxl

path = r"C:\Users\24243\WorkBuddy\2026-07-24-20-10-20\Notes_SuperSticky核对表.xlsx"
wb = openpyxl.load_workbook(path)
sh = wb.active
full_note = "2次搜索导出均无法命中（亚马逊排名靠后+Sellersprite仅导前页）；需前台手动搜'Post-it Full Adhesive'翻到目标产品、复制详情页dp URL发我"
label_note = "2次搜索导出均无法命中；需前台手动搜'Post-it Label Pads'翻到目标产品、复制详情页dp URL发我"

for row in sh.iter_rows(min_row=2):
    ln = row[0].value
    if ln in (53, 54, 55):
        row[6].value = full_note
    elif ln in (57, 58, 59, 60, 61, 62):
        row[6].value = label_note
wb.save(path)
print("已更新9行备注并保存:", path)
