import json

with open(r'D:\4A\00_当前工作区_202611\mfn_72_audit.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

sold_items = [r for r in data if r['oct_units'] > 0]
print(f"Total MFN >=300 SKUs that generated sales in Oct: {len(sold_items)} / {len(data)}")
for r in sold_items:
    sku = r['sku']
    qty = r['declared_quantity']
    oct_u = r['oct_units']
    oct_s = r['oct_sales']
    tpl = r['shipping_template']
    st = r['status']
    print(f"{sku:22} | Qty:{qty:5d} | OctUnits:{oct_u:3d} | OctSales:${oct_s:7.2f} | Tpl:{tpl:20} | Status:{st}")

print("\n--- ZERO-SALES MFN >= 300 SKUS BREAKDOWN ---")
zero_items = [r for r in data if r['oct_units'] == 0]
print(f"Total zero-sales MFN >= 300 SKUs: {len(zero_items)}")

# Check status of zero-sales
st_counts = {}
for r in zero_items:
    st_counts[r['status']] = st_counts.get(r['status'], 0) + 1
print("Status counts for zero-sales:", st_counts)

# Check blockers for zero-sales
blocker_counts = {}
for r in zero_items:
    for b in r['blockers']:
        blocker_counts[b] = blocker_counts.get(b, 0) + 1
print("Blocker breakdown for zero-sales:")
for b, c in sorted(blocker_counts.items(), key=lambda x: -x[1]):
    print(f"  [{c:2d} SKUs] {b}")
