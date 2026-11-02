import openpyxl
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\10-four-noncoupon-promotions.xlsm", data_only=True)
print("10-four-noncoupon-promotions sheets:", wb.sheetnames)
ws = wb['Template']
for r in range(1, ws.max_row + 1):
    vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
    if any(vals):
        print(f"Row {r:2d}: {vals}")

with open(r"D:\4A\00_Codex交接给Gemini_20261101\03_分析证据与JSON\coupon-fullscan-parsed.json", "r", encoding="utf-8") as f:
    c_data = json.load(f)

print("\n=== COUPON FULLSCAN PARSED SUMMARY ===")
if isinstance(c_data, dict):
    print("Keys:", list(c_data.keys()))
    for k, v in c_data.items():
        if isinstance(v, list):
            print(f"  {k}: {len(v)} items")
            for item in v[:15]:
                print("   ", item)
        else:
            print(f"  {k}: {v}")
elif isinstance(c_data, list):
    print(f"List of {len(c_data)} items")
    for item in c_data[:25]:
        print(" ", item)
