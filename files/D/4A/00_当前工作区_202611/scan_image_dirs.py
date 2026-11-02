import os
import json

# Check the image folders for each of the 16 items
image_dirs_to_check = {
    "4A092": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\9-----4A Memo Cube\4A SMC 434",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\9-----4A Memo Cube\4A SMC 434",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\9-----4A Memo Cube\SMC 434"
    ],
    "4A PSS 9-5 NB": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\8-----4A Roll Sticky Notes\4A PSS 9-5 NB",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\8-----4A Roll Sticky Notes\4A PSS 9-5 NB",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\8-----4A Roll Sticky Notes\PSS 9-5 NB"
    ],
    "4A 0153": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\19----3D Printed Sticky Notes\8065",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\19----3D printed sticky notes\8065"
    ],
    "4A 0154": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\19----3D Printed Sticky Notes\8066",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\19----3D printed sticky notes\8066"
    ],
    "4A 0155": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\19----3D Printed Sticky Notes\8067",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\19----3D printed sticky notes\8067"
    ],
    "4A 0168": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\19----3D Printed Sticky Notes\8080",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\19----3D printed sticky notes\8080"
    ],
    "4A 0169": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\19----3D Printed Sticky Notes\8081",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\19----3D printed sticky notes\8081"
    ],
    "4A 0171": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\19----3D Printed Sticky Notes\8083",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\19----3D printed sticky notes\8083"
    ],
    "4A 186": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\3-----4A Super sticky notes\4A 406S-LineX3",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\3-----4A Super sticky notes\4A 406S-LineX3"
    ],
    "4A 187": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\3-----4A Super sticky notes\4A 406S-LineX5",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\3-----4A Super sticky notes\4A 406S-LineX5"
    ],
    "4A 40606": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\7-----4A Divider Sticky Notes\4A 40606",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\7-----4A Divider Sticky Notes\4A 40606",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\7-----4A Divider Sticky Notes\40606"
    ],
    "4A 5036": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\5-----4A Shapes Sticky Notes\4A 5036",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\5-----4A Shapes Sticky Notes\4A 5036",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\5-----4A Shapes Sticky Notes\5036"
    ],
    "4A 60238": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\10----4A Film Flags\4A 60238",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\10----4A Film Flags\4A 60238"
    ],
    "4A GM40624*2": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\7-----4A Divider Sticky Notes\4A 40624",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\7-----4A Divider Sticky Notes\4A 40624",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\7-----4A Divider Sticky Notes\40624"
    ],
    "4A SF-60238": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\10----4A Film Flags\4A 60238",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\10----4A Film Flags\4A 60238"
    ],
    "4A093": [
        r"D:\4A\印刷用图片\电商\亚马逊图片-2021\9-----4A Memo Cube\4A MC 434",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\9-----4A Memo Cube\4A MC 434",
        r"D:\4A\印刷用图片\电商\亚马逊图片-2018\9-----4A Memo Cube\MC 434"
    ]
}

results = {}
for sku, dirs in image_dirs_to_check.items():
    results[sku] = []
    for d in dirs:
        if os.path.exists(d):
            files = [f for f in os.listdir(d) if os.path.isfile(os.path.join(d, f))]
            subdirs = [sd for sd in os.listdir(d) if os.path.isdir(os.path.join(d, sd))]
            results[sku].append({
                'dir': d,
                'files': files,
                'subdirs': subdirs
            })
            # Also check immediate subdirs if any
            for sd in subdirs:
                sd_path = os.path.join(d, sd)
                sd_files = [f for f in os.listdir(sd_path) if os.path.isfile(os.path.join(sd_path, f))]
                results[sku].append({
                    'dir': sd_path,
                    'files': sd_files,
                    'subdirs': []
                })

with open(r'D:\4A\00_当前工作区_202611\image_dirs_summary.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print("Image dirs scanned. Summary saved to D:\\4A\\00_当前工作区_202611\\image_dirs_summary.json")
