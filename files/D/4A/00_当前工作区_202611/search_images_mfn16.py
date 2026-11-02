import os
import json

path_json = r'D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据\residual62-closeout.json'
with open(path_json, 'r', encoding='utf-8') as f:
    closeout_data = json.load(f)

mfn_rows = [r for r in closeout_data['rows'] if r.get('inventory_group') == '仅MFN有申报库存']

base_dirs = [
    r'D:\4A\印刷用图片\电商\亚马逊图片-2021',
    r'D:\4A\印刷用图片\电商\亚马逊图片-2018'
]

# Walk all subdirectories and files
all_dirs = []
for b in base_dirs:
    for root, dirs, files in os.walk(b):
        all_dirs.append((root, dirs, files))

print(f"Total directories walked: {len(all_dirs)}")

# For each SKU, let's see which dirs/files match
for idx, r in enumerate(mfn_rows):
    sku = r['sku']
    asin = r['asin']
    print(f"\n==========================================")
    print(f"#{idx+1}: SKU={sku} | ASIN={asin}")
    
    # search tokens
    tokens = [sku, asin]
    # Clean sku tokens: e.g. "4A 0153" -> ["0153", "8065"], "4A092" -> ["092", "434", "SMC"], "4A PSS 9-5 NB" -> ["PSS", "9-5", "119600"]
    # We will do exact and substring search
    matched_paths = []
    for root, dirs, files in all_dirs:
        # check if folder name matches
        folder_name = os.path.basename(root)
        matched_files = []
        for f in files:
            f_lower = f.lower()
            if any(t.lower() in f_lower for t in tokens if len(t) > 2):
                matched_files.append(f)
        
        folder_match = any(t.lower() in folder_name.lower() for t in tokens if len(t) > 2)
        if folder_match or matched_files:
            matched_paths.append((root, folder_name, matched_files, files[:5]))
            
    print(f"Found {len(matched_paths)} matching locations:")
    for root, fname, mfiles, some_files in matched_paths[:5]:
        print(f"  Folder: {root}")
        if mfiles:
            print(f"    Matched files: {mfiles[:5]}")
        else:
            print(f"    Sample files in matched folder: {some_files[:5]}")
