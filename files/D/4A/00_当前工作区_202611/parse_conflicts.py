import json
import re

with open(r'D:\4A\00_当前工作区_202611\mfn16_raw_extracted.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

for item in items:
    print(f"==================================================")
    print(f"#{item['idx']} SKU: {item['sku']} | ASIN: {item['asin']} | Qty: {item['qty']}")
    print(f"Conflicts: {item['conflicts']}")
    print(f"Cat Title: {item['cat_title']}")
    print(f"Cat Color: {item['cat_color']} | ColorMap: {item['cat_color_map']}")
    print(f"Cat Mfr: {item['cat_mfr']} | Model: {item['cat_model']} | PT: {item['cat_pt']} | Parent: {item['cat_parent']}")
    if item['e8541_msgs']:
        for m in item['e8541_msgs']:
            # extract Merchant vs Amazon values
            # usually in format: 'field' (Merchant [...] / Amazon [...])
            match = re.search(r"'(.*?)'\s*\(Merchant\s*\[(.*?)\]\s*/\s*Amazon\s*\[(.*?)\]\)", m)
            if match:
                fld, merch, amz = match.groups()
                print(f"  Conflict Field: '{fld}'")
                print(f"    Merchant: {merch[:80]}")
                print(f"    Amazon:   {amz[:80]}")
            else:
                print(f"  8541 msg: {m[:200]}")
    if item['e99022_msgs']:
        print(f"  99022 msgs: {item['e99022_msgs'][0][:150]}")
