import openpyxl
from collections import defaultdict

wb = openpyxl.load_workbook(r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx', data_only=True)
ws = wb.worksheets[1]

# Map all ASINs to their SKUs
asin_to_skus = defaultdict(list)
for r in range(2, ws.max_row + 1):
    sku = str(ws.cell(r, 7).value or '').strip()
    asin = str(ws.cell(r, 8).value or '').strip()
    stock = ws.cell(r, 12).value
    rating = ws.cell(r, 14).value
    status = ws.cell(r, 17).value
    if sku and asin:
        asin_to_skus[asin].append({
            'row': r,
            'sku': sku,
            'stock': stock,
            'rating': rating,
            'status': status
        })

print(f"Total unique ASINs in store: {len(asin_to_skus)}")

# Now examine each 0-stock AAAA SKU
ghost_candidates_safe_to_delete = []
ghost_candidates_need_caution = []

for asin, skus in asin_to_skus.items():
    aaaa_in_asin = [s for s in skus if s['sku'].startswith('AAAA') or s['sku'].startswith('AA ')]
    non_aaaa_in_asin = [s for s in skus if not (s['sku'].startswith('AAAA') or s['sku'].startswith('AA '))]

    for a_sku in aaaa_in_asin:
        # Check if a_sku has 0 stock
        is_zero_stock = a_sku['stock'] in [None, 0, '0', '', 'None']
        if not is_zero_stock:
            continue  # Keep! Has stock

        rating_val = None
        try:
            rating_val = float(a_sku['rating']) if a_sku['rating'] not in [None, 'None', ''] else None
        except:
            pass

        # Check if the ASIN has another active non-AAAA SKU
        has_active_other_sku = any(other['stock'] not in [None, 0, '0', '', 'None'] or other['status'] == 'Active' for other in non_aaaa_in_asin)

        # User's strict criterion: "既没货评分又不高的"
        # 0 stock AND (rating is None or rating < 4.0)
        is_low_or_no_rating = (rating_val is None or rating_val < 4.0)

        item_info = {
            'sku': a_sku['sku'],
            'asin': asin,
            'stock': a_sku['stock'],
            'rating': rating_val,
            'has_other_sku': has_active_other_sku,
            'other_skus': [o['sku'] for o in non_aaaa_in_asin]
        }

        if is_low_or_no_rating:
            ghost_candidates_safe_to_delete.append(item_info)
        else:
            ghost_candidates_need_caution.append(item_info)

print(f"\nGhost AAAA SKUs meeting user criteria (0 Stock AND Rating < 4.0 or None): {len(ghost_candidates_safe_to_delete)}")
print(f"Ghost AAAA SKUs with 0 Stock BUT High Rating (>= 4.0): {len(ghost_candidates_need_caution)}")

print("\n--- Sample of Safe to Delete Ghost SKUs (first 20) ---")
for it in ghost_candidates_safe_to_delete[:20]:
    print(f"  SKU: {it['sku']}, ASIN: {it['asin']}, Rating: {it['rating']}, Other SKUs: {it['other_skus']}")

print("\n--- High Rating Ghost SKUs (>= 4.0) that should be preserved/merged (sample 10) ---")
for it in ghost_candidates_need_caution[:10]:
    print(f"  SKU: {it['sku']}, ASIN: {it['asin']}, Rating: {it['rating']}, Other SKUs: {it['other_skus']}")
