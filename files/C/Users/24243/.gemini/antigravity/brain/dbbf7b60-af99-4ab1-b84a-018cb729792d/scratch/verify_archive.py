import zipfile, json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
z = zipfile.ZipFile(r'D:\4A\4A_桌面归档_20261101.zip')
print('testzip first bad file:', z.testzip())
info = {i.filename: i.file_size for i in z.infolist()}
m = json.load(open(r'C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\archive_manifest.json', encoding='utf-8'))
miss = []
for src, arc, size in m:
    key = arc.replace('\\', '/')
    if info.get(key) != size or not os.path.exists(src) or os.path.getsize(src) != size:
        miss.append(src)
print('manifest', len(m), 'zip entries', len(info), 'mismatch/missing', len(miss))
for x in miss[:10]:
    print(' ', x)
