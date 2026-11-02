import openpyxl

wb = openpyxl.load_workbook(r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx', data_only=True)
ws = wb.worksheets[1]

headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
print("Headers count:", len(headers))
for i, h in enumerate(headers):
    print(f"Col {i+1}: {h}")

aaaa_items = []
for r in range(2, ws.max_row + 1):
    sku = str(ws.cell(r, 7).value or '').strip()
    asin = str(ws.cell(r, 8).value or '').strip()
    stock = ws.cell(r, 12).value
    sales = ws.cell(r, 13).value
    rating = ws.cell(r, 14).value
    status = ws.cell(r, 17).value
    action = ws.cell(r, 18).value
    title = ws.cell(r, 19).value

    if sku.startswith('AAAA') or sku.startswith('AA '):
        aaaa_items.append({
            'row': r,
            'sku': sku,
            'asin': asin,
            'stock': stock,
            'sales': sales,
            'rating': rating,
            'status': status,
            'action': action,
            'title': title
        })

print(f"\nTotal AAAA items found: {len(aaaa_items)}")

with_stock = [it for it in aaaa_items if it['stock'] not in [None, 0, '0', '', 'None']]
no_stock = [it for it in aaaa_items if it['stock'] in [None, 0, '0', '', 'None']]

print(f"AAAA with stock > 0: {len(with_stock)}")
for it in with_stock:
    print(f"  SKU: {it['sku']}, ASIN: {it['asin']}, Stock: {it['stock']}, Rating: {it['rating']}")

print(f"\nAAAA with 0 stock: {len(no_stock)}")
ratings_summary = {}
for it in no_stock:
    r_val = str(it['rating'])
    ratings_summary[r_val] = ratings_summary.get(r_val, 0) + 1
print("Ratings summary for 0-stock AAAA:", ratings_summary)

print("\nSample of 0-stock AAAA with rating detail:")
for it in no_stock[:15]:
    print(f"  SKU: {it['sku']}, ASIN: {it['asin']}, Rating: {it['rating']}, Status: {it['status']}")
