import openpyxl

cat_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
master_path = r'C:\Users\24243\Downloads\亚马逊供应商和开店总表-2026 (3).xlsx'

print("--- Inspecting Category Report ---")
wb_cat = openpyxl.load_workbook(cat_path, read_only=True)
print("Cat sheets:", wb_cat.sheetnames)
wb_cat.close()

print("--- Inspecting Master Sheet ---")
wb_master = openpyxl.load_workbook(master_path, read_only=True)
print("Master sheets:", wb_master.sheetnames)
wb_master.close()
