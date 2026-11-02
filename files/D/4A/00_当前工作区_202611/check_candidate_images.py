import os

candidates = [
    # 1. 4A092
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\9-----4A Memo Cube\4A SMC 434\702877124000.pt01.jpg",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\9-----4A Memo Cube\4A SMC 434\4A SMC 434.JPG",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\9-----4A Memo Cube\SMC 434\702877124000.PT01.JPG",
    # 2. 4A PSS 9-5 NB
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\8-----4A Roll Sticky Notes\4A PSS 9-5 NB\702877123140.MAIN.jpg",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\8-----4A Roll Sticky Notes\4A PSS 9-5 NB\702877123140.PT01.jpg",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\8-----4A Roll Sticky Notes\PSS 9-5 NB\702877123140.main.jpg",
    # 3. 4A 0153 (8065 Tiger)
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\19----3D Printed Sticky Notes\8065\4A-8065-1.jpg",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\19----3D printed sticky notes\8065\702877118474.MAIN.jpg",
    # 4. 4A 40606
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\7-----4A Divider Sticky Notes\4A 40606\702877120040.MAIN.jpg",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\7-----4A Divider Sticky Notes\4A 40606\40606-1.jpg",
    # 5. 4A 5036 (Heart)
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\5-----4A Shapes Sticky Notes\4A 5036\4A 5036-1.JPG",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\5-----4A Shapes Sticky Notes\4A 5036\4A 5036 (1).JPG",
    # 6. 4A 60238
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\10----4A Film Flags\4A 60238\702877121030.main.JPG",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\10----4A Film Flags\4A 60238\60238.JPG",
    # 7. 4A093 (MC 434 Wave)
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\9-----4A Memo Cube\4A MC 434\702877124017.main.jpg",
    r"D:\4A\印刷用图片\电商\亚马逊图片-2018\9-----4A Memo Cube\4A MC 434\4A MC 434.jpg",
    # 8. 4A 186
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\3-----4A Super sticky notes\4A 406S-LineX3\702877118573.main.JPG",
    # 9. 4A 187
    r"D:\4A\印刷用图片\电商\亚马逊图片-2021\3-----4A Super sticky notes\4A 406S-LineX5\702877120200.main.jpg",
]

for c in candidates:
    exists = os.path.exists(c)
    sz = os.path.getsize(c) if exists else 0
    print(f"{'[EXISTS]' if exists else '[MISSING]'} {sz:8d} bytes | {c}")
