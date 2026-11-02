import os

search_roots = [
    r'D:\4A\印刷用图片',
    r'D:\4A\02_老资料_表格与订单',
    r'D:\4A\01_便签店运营_2026-10'
]

keywords = ['pss', '32x6', '32-6', '702877126561', '702877126578']

matches = []
for root in search_roots:
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            fl = f.lower()
            for kw in keywords:
                if kw in fl:
                    matches.append(os.path.join(dirpath, f))
                    break

print(f"Total keyword matches: {len(matches)}")
for m in matches[:60]:
    print(m)
if len(matches) > 60:
    print(f"... and {len(matches)-60} more")
