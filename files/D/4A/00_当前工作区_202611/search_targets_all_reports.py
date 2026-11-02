import openpyxl

targets = ['B01N1T23HH', 'B01N7IT411', 'B01M617ZTH', 'B0784GHSVJ', 'B01M2UDADZ',
           '4A 039', '4A 040', '4A 037', '4A 0166', '4A095', '4A 66114']

print("=== CHECKING 所有商品报告_11-01-2026.txt ===")
with open(r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt', 'r', encoding='utf-8', errors='ignore') as f:
    headers = f.readline().strip().split('\t')
    for line_idx, line in enumerate(f, 2):
        parts = line.strip().split('\t')
        row_dict = dict(zip(headers, parts))
        sku = row_dict.get('seller-sku', '')
        asin1 = row_dict.get('asin1', '')
        for t in targets:
            if t == sku or t == asin1:
                print(f"Line {line_idx} matched '{t}': seller-sku='{sku}', asin1='{asin1}', status='{row_dict.get('status')}', price='{row_dict.get('price')}', afn='{row_dict.get('fulfillment-channel')}'")
                print(f"   item-name: {row_dict.get('item-name', '')[:90]}")
                break

print("\n=== CHECKING 2023 MASTER ===")
wb = openpyxl.load_workbook(r'D:\4A\02_老资料_表格与订单\亚马逊供应商和开店总表-2023.xlsx', data_only=True)
ws = wb['Sheet1']
for r in range(2, ws.max_row + 1):
    r_str = ' '.join([str(ws.cell(r, c).value) for c in range(1, ws.max_column + 1) if ws.cell(r, c).value is not None])
    for t in targets:
        if t.lower() in r_str.lower():
            sku = ws.cell(r, 1).value
            print(f"2023 Master Row {r} matched '{t}': SKU='{sku}', Row={r_str[:120]}")
            break
wb.close()
