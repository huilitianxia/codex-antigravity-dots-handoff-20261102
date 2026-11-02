import re
from collections import defaultdict

with open('E:/Desktop/extracted_order_data.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for order blocks
blocks = re.split(r'(?=\d{3}-\d{7}-\d{7})', text)
print(f'Total blocks: {len(blocks)}')

full_glue_total = 0.0
non_full_glue_total = 0.0

full_glue_orders = []
non_full_glue_orders = []

for b in blocks:
    if not b.strip(): continue
    m_id = re.search(r'(\d{3}-\d{7}-\d{7})', b)
    if not m_id: continue
    oid = m_id.group(1)
    
    # check date
    m_date = re.search(r'(2026/10/\d{2}|10月\d{2}日|2026-10-\d{2})', b)
    date_str = m_date.group(1) if m_date else ''
    
    # check sku
    m_sku = re.search(r'(?:SKU|sku)[\s:\"]+([A-Za-z0-9\-\+\s]+)', b)
    sku = m_sku.group(1).strip() if m_sku else 'Unknown'
    
    # check price
    m_price = re.search(r'[\$US]+(\d+\.\d{2})', b)
    price = float(m_price.group(1)) if m_price else 0.0
    
    is_full_glue = any(k in b.lower() or k in sku.lower() for k in ['full adhesive', 'full glue', '满胶', '304 full', '303-full'])
    
    if is_full_glue:
        full_glue_total += price
        full_glue_orders.append((oid, sku[:25], price, date_str))
    else:
        non_full_glue_total += price
        non_full_glue_orders.append((oid, sku[:25], price, date_str))

print(f'Full Glue Orders: {len(full_glue_orders)}, Total: ${full_glue_total:.2f}')
print(f'Non-Full Glue (Optimized/Conventional) Orders: {len(non_full_glue_orders)}, Total: ${non_full_glue_total:.2f}')
print('\nSample Non-Full Glue Orders:')
for o in non_full_glue_orders[:15]:
    print(' ', o)
