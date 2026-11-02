import json

with open(r'D:\4A\00_当前工作区_202611\image_dirs_summary.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for sku, dir_list in data.items():
    print(f"\n==========================================")
    print(f"SKU: {sku}")
    for d in dir_list:
        print(f"  Dir: {d['dir']}")
        print(f"  Files ({len(d['files'])}): {d['files'][:10]}")
