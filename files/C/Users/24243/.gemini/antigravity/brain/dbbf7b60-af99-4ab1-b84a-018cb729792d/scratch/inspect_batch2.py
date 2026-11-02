import os, sys, json
sys.stdout.reconfigure(encoding='utf-8')

p_base = r'E:\Desktop\待上架_新图文素材库_第二批'
txt_path = os.path.join(p_base, '交付说明.txt')
if os.path.exists(txt_path):
    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
        print('=== 交付说明.txt ===')
        print(f.read())

json_path = os.path.join(p_base, '交付总清单.json')
if os.path.exists(json_path):
    with open(json_path, 'r', encoding='utf-8', errors='ignore') as f:
        d = json.load(f)
        print('\n=== 交付总清单.json ===')
        print('Date:', d.get('date'))
        print('Image count:', d.get('image_count'))
        print('Final candidates:', d.get('final_candidates'))
        print('Images overview:')
        for img in d.get('images', []):
            i_id = img.get('id', '')
            sku = img.get('sku', '')
            asin = img.get('asin', '')
            role = img.get('role', '')
            title = img.get('title', '')
            print(f"  {i_id:<18} | SKU: {sku:<20} | ASIN: {asin:<10} | {role:<9} | {title}")
