import zipfile, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
z = zipfile.ZipFile(r'D:\4A\4A_桌面归档_20261101.zip')
infos = [i for i in z.infolist() if not i.filename.endswith('/')]
by = collections.defaultdict(list)
for i in infos:
    by[(i.CRC, i.file_size)].append(i.filename)

# 1) exact duplicate files inside the archive (same crc+size)
dup_bytes = 0
for k, v in by.items():
    if len(v) > 1:
        dup_bytes += k[1] * (len(v) - 1)
print('files', len(infos), 'total MB', sum(i.file_size for i in infos) // 1048576, '| exact-duplicate surplus MB', dup_bytes // 1048576)

# 2) nested zips: are their members contained in the loose files elsewhere?
import io
loose = set((i.CRC, i.file_size) for i in infos if not i.filename.lower().endswith('.zip'))
print('--- nested zip coverage (members found as loose files elsewhere in archive) ---')
for i in infos:
    if i.filename.lower().endswith('.zip'):
        with z.open(i) as f:
            data = io.BytesIO(f.read())
        try:
            nz = zipfile.ZipFile(data)
        except Exception as e:
            print('ERR', i.filename, e); continue
        mem = [m for m in nz.infolist() if not m.filename.endswith('/')]
        cov = sum(1 for m in mem if (m.CRC, m.file_size) in loose)
        print('%6.1fMB %3d/%3d covered  %s' % (i.file_size / 1048576, cov, len(mem), i.filename))
