import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

wb = openpyxl.load_workbook(r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx", read_only=True, data_only=True)
ws = wb["Sheet1"]
for i, r in enumerate(ws.iter_rows(min_row=1, max_row=15, values_only=True), 1):
    print(f"Row {i:2d}: {[str(c) if c is not None else '' for c in r[:22]]}")
wb.close()

wb2 = openpyxl.load_workbook(r"D:\4A\02_老资料_表格与订单\4A_暑期要回老品_工厂排产复产推荐清单.xlsx", read_only=True, data_only=True)
ws2 = wb2[wb2.sheetnames[0]]
print("\n=== 工厂复产推荐表 ===")
for i, r in enumerate(ws2.iter_rows(min_row=1, max_row=35, values_only=True), 1):
    print(f"Row {i:2d}: {[str(c) if c is not None else '' for c in r[:15]]}")
wb2.close()
