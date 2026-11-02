import json

path_json = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\residual62-closeout.json'
with open(path_json, 'r', encoding='utf-8') as f:
    closeout_data = json.load(f)

mfn_rows = [r for r in closeout_data['rows'] if r.get('inventory_group') == '仅MFN有申报库存']
target_skus = {r['sku']: r for r in mfn_rows}

txt_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\所有商品报告_11-01-2026.txt'
with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
    headers = f.readline().strip().split('\t')
    print("Headers:", headers[:10])
    sku_idx = headers.index('seller-sku')
    asin_idx = headers.index('asin1') if 'asin1' in headers else -1
    qty_idx = headers.index('quantity') if 'quantity' in headers else -1
    status_idx = headers.index('status') if 'status' in headers else -1
    price_idx = headers.index('price') if 'price' in headers else -1
    
    print(f"Indices: sku={sku_idx}, asin={asin_idx}, qty={qty_idx}, status={status_idx}, price={price_idx}")
    
    found_skus = {}
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) > sku_idx:
            line_sku = parts[sku_idx]
            if line_sku in target_skus:
                found_skus[line_sku] = {
                    'sku': line_sku,
                    'asin': parts[asin_idx] if asin_idx >= 0 and asin_idx < len(parts) else None,
                    'qty': parts[qty_idx] if qty_idx >= 0 and qty_idx < len(parts) else None,
                    'status': parts[status_idx] if status_idx >= 0 and status_idx < len(parts) else None,
                    'price': parts[price_idx] if price_idx >= 0 and price_idx < len(parts) else None,
                    'item-name': parts[headers.index('item-name')] if 'item-name' in headers and headers.index('item-name') < len(parts) else None
                }

print(f"Found {len(found_skus)} of {len(target_skus)} in 11-01 report:")
for sku, info in found_skus.items():
    print(f"  SKU: {sku} | ASIN: {info['asin']} | Qty: {info['qty']} | Status: {info['status']} | Price: {info['price']}")
