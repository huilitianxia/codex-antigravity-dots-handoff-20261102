import json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\24243\Documents\Codex\2026-08-28\new-task-handoff-2026-08-28\work\vc_sales_audit_results.json', 'r', encoding='utf-8', errors='ignore') as f:
    d = json.load(f)

rows = d.get('all', [])

def get_val(r):
    try:
        return float(r.get('D', 0))
    except:
        return 0.0

sorted_rows = sorted(rows, key=get_val, reverse=True)
print(f'Total rows: {len(sorted_rows)}')
for i, r in enumerate(sorted_rows[:30], 1):
    sku = r.get('B', '')
    asin = r.get('C', '')
    qty = r.get('D', 0)
    rev = float(r.get('E', 0))
    y24 = r.get('AC', 0)
    print(f"Dad VC #{i:2d} | SKU: {sku:<22} | ASIN: {asin:<10} | Total Qty: {qty:>6} | Rev: ${rev:>10.2f} | 2024: {y24:>5}")
