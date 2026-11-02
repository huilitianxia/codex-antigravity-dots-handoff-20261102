import os

paths = [
    r'D:\4A\印刷用图片\电商\亚马逊图片-2021',
    r'D:\4A\印刷用图片\电商\亚马逊图片-2018',
    r'D:\4A\印刷用图片\电商',
    r'D:\4A\印刷用图片'
]

for p in paths:
    if os.path.exists(p):
        items = os.listdir(p)
        print(f"\nPath {p} (total items {len(items)}):")
        # print first 30 items
        for item in sorted(items)[:30]:
            is_dir = os.path.isdir(os.path.join(p, item))
            print(f"  {'[DIR] ' if is_dir else '[FILE]'} {item}")
    else:
        print(f"Path does not exist: {p}")
