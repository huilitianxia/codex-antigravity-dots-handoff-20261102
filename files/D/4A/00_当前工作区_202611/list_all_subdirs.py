import os

base_dirs = [
    r'D:\4A\印刷用图片\电商\亚马逊图片-2021',
    r'D:\4A\印刷用图片\电商\亚马逊图片-2018'
]

for b in base_dirs:
    print(f"\n=================== {b} ===================")
    for cat in sorted(os.listdir(b)):
        cat_p = os.path.join(b, cat)
        if os.path.isdir(cat_p):
            subdirs = [d for d in os.listdir(cat_p) if os.path.isdir(os.path.join(cat_p, d))]
            files = [f for f in os.listdir(cat_p) if os.path.isfile(os.path.join(cat_p, f))]
            print(f"\n[{cat}] (Subdirs: {len(subdirs)}, Files: {len(files)})")
            for sd in sorted(subdirs):
                print(f"   subdir: {sd}")
