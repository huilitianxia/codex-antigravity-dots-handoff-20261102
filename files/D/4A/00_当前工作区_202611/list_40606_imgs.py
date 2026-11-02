import os

p1 = r'D:\4A\印刷用图片\电商\亚马逊图片-2021\7-----4A Divider Sticky Notes\4A 40606'
p2 = r'D:\4A\印刷用图片\电商\亚马逊图片-2018\7-----4A Divider Sticky Notes\4A 40606'
p3 = r'D:\4A\印刷用图片\电商\亚马逊图片-2018\7-----4A Divider Sticky Notes\40606'

for p in [p1, p2, p3]:
    if os.path.exists(p):
        for root, dirs, files in os.walk(p):
            for f in files:
                if f.lower().endswith(('.jpg', '.png')):
                    print(os.path.join(root, f))
