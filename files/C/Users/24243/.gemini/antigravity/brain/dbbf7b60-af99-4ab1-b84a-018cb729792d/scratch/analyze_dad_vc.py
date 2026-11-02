import sys, json
sys.stdout.reconfigure(encoding='utf-8')

p = r'C:\Users\24243\Documents\Codex\2026-08-28\new-task-handoff-2026-08-28\work\vc_sales_audit_results.json'
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    data = json.load(f)

all_rows = data.get('all', [])

def get_total(x):
    t = x.get('total')
    try:
        return float(t)
    except:
        return 0.0

sorted_vc = sorted(all_rows, key=get_total, reverse=True)

print('=== DAD HISTORICAL VC TOP 20 ===')
for i, r in enumerate(sorted_vc[:20], 1):
    sku = str(r.get('sku') or '')
    asin = str(r.get('asin') or '')
    total = r.get('total') or 0
    amount = r.get('amount') or 0.0
    marked = r.get('marked') or []
    years = r.get('years') or {}
    y24 = years.get('2024') or 0
    print(f"Dad Top {i:2d}: {sku:<22} | ASIN: {asin:<10} | Total: {total} | Amount: ${amount} | 2024: {y24} | Mark: {marked}")
