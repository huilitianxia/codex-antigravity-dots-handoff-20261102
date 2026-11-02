import zipfile, sys, os, json, collections, copy
sys.stdout.reconfigure(encoding='utf-8')
OLD = r'D:\4A\4A_桌面归档_20261101.zip'
NEW_DIR = r'D:\4A\_待整理中'
os.makedirs(NEW_DIR, exist_ok=True)
NEW = os.path.join(NEW_DIR, '4A便签店运营归档_精简版_20261101.zip')

z = zipfile.ZipFile(OLD)
infos = [i for i in z.infolist() if not i.filename.endswith('/')]

def top2(fn):
    p = fn.split('/')
    return '/'.join(p[:2])

# hashes of the "素材库" folders (the master copies)
master = set()
for i in infos:
    t = top2(i.filename).split('/')[-1]
    if t.startswith('待上架_') and not i.filename.lower().endswith('.zip'):
        master.add((i.CRC, i.file_size))

# per top-level dir coverage for upload-pack folders
dirs = collections.defaultdict(list)
for i in infos:
    dirs[top2(i.filename)].append(i)

drop_dirs = set()
print('--- upload-pack folder coverage vs 素材库 folders ---')
for d, fl in dirs.items():
    name = d.split('/')[-1]
    if d.startswith('1_图包/4A_') and '上传' in name and not name.lower().endswith('.zip'):
        cov = sum(1 for i in fl if (i.CRC, i.file_size) in master)
        print('%2d/%2d  %s' % (cov, len(fl), d))
        if cov == len(fl):
            drop_dirs.add(d)

# nested zips fully covered by loose files (all but the 30315 review zip which has 3 unique members)
import io
loose = set((i.CRC, i.file_size) for i in infos if not i.filename.lower().endswith('.zip'))
drop_zips = set()
for i in infos:
    if i.filename.lower().endswith('.zip'):
        nz = zipfile.ZipFile(io.BytesIO(z.read(i)))
        mem = [m for m in nz.infolist() if not m.filename.endswith('/')]
        if all((m.CRC, m.file_size) in loose for m in mem):
            drop_zips.add(i.filename)
print('dropping dirs:', len(drop_dirs), 'dropping nested zips:', len(drop_zips))

kept = dropped = 0
kept_b = dropped_b = 0
with zipfile.ZipFile(NEW, 'w', allowZip64=True) as nz:
    for i in infos:
        if i.filename in drop_zips or top2(i.filename) in drop_dirs:
            dropped += 1; dropped_b += i.file_size; continue
        zi = zipfile.ZipInfo(i.filename, i.date_time)
        zi.compress_type = i.compress_type
        zi.external_attr = i.external_attr
        nz.writestr(zi, z.read(i))
        kept += 1; kept_b += i.file_size
print('kept files', kept, 'MB', kept_b // 1048576, '| dropped files', dropped, 'MB', dropped_b // 1048576)
print('new zip MB', os.path.getsize(NEW) // 1048576)

# verify new zip
v = zipfile.ZipFile(NEW)
print('testzip:', v.testzip(), 'entries:', len(v.infolist()))
json.dump({'dropped_dirs': sorted(drop_dirs), 'dropped_zips': sorted(drop_zips)},
          open(os.path.join(NEW_DIR, 'dropped.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
