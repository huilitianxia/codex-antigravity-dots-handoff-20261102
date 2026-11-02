import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb_cat = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws_cat = wb_cat['Template']

cat_prices = {}
for r in range(7, ws_cat.max_row + 1):
    sku = ws_cat.cell(r, 3).value
    if sku:
        cat_prices[str(sku).strip()] = {
            "price": ws_cat.cell(r, 348).value,
            "b2b": ws_cat.cell(r, 357).value,
            "sale": ws_cat.cell(r, 352).value,
            "asin": ws_cat.cell(r, 13).value
        }

for bfile in ["05-remove-temporary-minimums.xlsm", "07-star-full-adhesive-price-reset.xlsm", "09-073-business-only.xlsm", "10-four-noncoupon-promotions.xlsm"]:
    fp = rf"D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\{bfile}"
    wb = openpyxl.load_workbook(fp, data_only=True)
    ws = wb['Template']
    print(f"=== {bfile} ===")
    for r in range(7, ws.max_row + 1):
        vals = [ws.cell(r, c).value for c in range(1, ws.max_column + 1)]
        if any(vals):
            print(f"  Row {r:2d}: SKU={vals[0]!r:24} | OurPrice={vals[6]} | SalePrice={vals[10]} ({vals[11]}..{vals[12]}) | B2B={vals[15]} | Tiers={vals[20:27]}")

target_skus = [
    # Group 1 (3 SKUs / 448u)
    "4A 304 Full Glue", "4A 5020x3", "4A 5082-Y-L-GM",
    # Group 2 (6 SKUs / 1847u)
    "4A 304-Full Adhesive-400", "4A 305-Full Adhesive", "AAAA 4A 304-Full Glue",
    "4A 302-Full Adhesive-400", "4A 305-Full Adhesive-300", "AAAA 4A 305-Full Glue",
    # Group 3 Aged >365d (5 SKUs; 4A 004 already in Batch 10)
    "4A055", "4A 6031x4", "4A073", "4A 5088-Rainbow"
]

print("\n=== TARGET SKUS IN CATEGORY REPORT ===")
for s in target_skus:
    print(f"  {s:26} : {cat_prices.get(s)}")
