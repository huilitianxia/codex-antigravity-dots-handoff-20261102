import openpyxl
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm", data_only=True)
ws = wb['Template']

templates = Counter()
missing_weight_by_template = defaultdict(list)

for r in range(7, ws.max_row + 1):
    sku = ws.cell(r, 3).value
    if not sku:
        continue
    status = ws.cell(r, 1).value
    channel = ws.cell(r, 343).value # Col 342 (0-based)
    qty = ws.cell(r, 344).value     # Col 343 (0-based)
    price = ws.cell(r, 348).value   # Col 347 (0-based)
    tmpl = ws.cell(r, 373).value    # Col 372 (0-based)
    pkg_w = ws.cell(r, 386).value   # Col 385 (0-based)
    item_w = ws.cell(r, 148).value  # let's check item weight too
    if channel and "Merchant" in str(channel):
        templates[str(tmpl)] += 1
        if pkg_w is None and (qty and float(qty) > 0):
            missing_weight_by_template[str(tmpl)].append((r, sku, ws.cell(r, 13).value, qty, price, status))

print("=== MFN SHIPPING TEMPLATES COUNT ===")
for k, v in templates.most_common():
    print(f"  {k:40} : {v:4d} SKUs (Missing PkgWeight w/ Qty>0: {len(missing_weight_by_template[k])})")

print("\n=== IN-STOCK MFN SKUS WITH MISSING PACKAGE WEIGHT (COL 385) ===")
for tmpl, items in missing_weight_by_template.items():
    print(f"\nTemplate: {tmpl} ({len(items)} SKUs)")
    for r, sku, asin, qty, price, status in items:
        print(f"  Row {r:3d} | {sku:24} | ASIN={str(asin):12} | Qty={str(qty):6} | Price={str(price):6} | Status={status}")
