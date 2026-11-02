import json

with open(r'D:\4A\00_当前工作区_202611\mfn16_raw_extracted.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

for item in items[5:11]:
    print(f"=== #{item['idx']} SKU: {item['sku']} | ASIN: {item['asin']} | Qty: {item['qty']} ===")
    print("Title:", item['cat_title'])
    print("Color:", item['cat_color'], "| Mfr:", item['cat_mfr'], "| Model:", item['cat_model'])
    for m in item['e8541_msgs']:
        print("  8541:", m)
