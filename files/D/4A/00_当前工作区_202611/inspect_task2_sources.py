import json
import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Inspect coupon-fullscan-parsed.json
coupon_path = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\coupon-fullscan-parsed.json"
with open(coupon_path, "r", encoding="utf-8") as f:
    cdata = json.load(f)
    print("Coupon data keys:", list(cdata.keys()) if isinstance(cdata, dict) else len(cdata))
    if isinstance(cdata, dict):
        for k in list(cdata.keys())[:5]:
            print(" ", k, "->", str(cdata[k])[:80])

# 2. Inspect 【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx
master_path = r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx"
wb = openpyxl.load_workbook(master_path, read_only=True, data_only=True)
print("Master sheets:", wb.sheetnames)
ws1 = wb['Sheet1']
for r in ws1.iter_rows(min_row=1, max_row=3, values_only=True):
    print("Sheet1 row:", r[:12])
wb.close()
