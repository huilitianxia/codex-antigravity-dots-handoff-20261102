import os, sys, re, shutil
sys.stdout.reconfigure(encoding='utf-8')
R = r'D:\4A'

OPS = os.path.join(R, '01_便签店运营_2026-10')
OLD = os.path.join(R, '02_老资料_表格与订单')
SPI = os.path.join(R, '03_Spider项目_2026-09')
REF = os.path.join(R, '04_参考图_2026-08')
for d in (OPS, OLD, SPI, REF):
    os.makedirs(d, exist_ok=True)

moved = []
def mv(src, dst_dir):
    dst = os.path.join(dst_dir, os.path.basename(src))
    if os.path.exists(dst):
        print('SKIP exists', dst); return
    shutil.move(src, dst)
    moved.append((os.path.basename(src), os.path.basename(dst_dir)))

# 1) operations archive: new lean zip + manifests; remove superseded big zip (content preserved in lean zip)
tmp = os.path.join(R, '_待整理中')
lean = os.path.join(tmp, '4A便签店运营归档_精简版_20261101.zip')
assert os.path.exists(lean)
mv(lean, OPS)
mv(os.path.join(tmp, 'dropped.json'), OPS)
mv(os.path.join(R, '_桌面归档清单_20261101.json'), OPS)
os.rmdir(tmp)
old_zip = os.path.join(R, '4A_桌面归档_20261101.zip')
if os.path.exists(old_zip):
    os.remove(old_zip)
    print('removed superseded zip', old_zip)

SKIP = {'印刷用图片', '网站备份', os.path.basename(OPS), os.path.basename(OLD), os.path.basename(SPI), os.path.basename(REF)}
spider_pat = re.compile(r'^(Spider|操作提示28张|屏幕修订|运行状态图|成品压缩包|高速便携式双激光雕刻机)')
hashjpg = re.compile(r'^[0-9a-f]{32}\.jpg$')

for n in sorted(os.listdir(R)):
    if n in SKIP:
        continue
    p = os.path.join(R, n)
    if n.startswith('~$'):
        try:
            os.remove(p); print('removed Excel lock file', n)
        except Exception as e:
            print('lock file kept', n, e)
        continue
    if hashjpg.match(n):
        mv(p, REF)
    elif spider_pat.match(n):
        mv(p, SPI)
    elif os.path.isfile(p):
        mv(p, OLD)
    else:
        print('UNCLASSIFIED dir left in place:', n)

print('moved', len(moved))
for tgt in (OPS, OLD, SPI, REF):
    print(os.path.basename(tgt), len(os.listdir(tgt)))
print('root now:', sorted(os.listdir(R)))
