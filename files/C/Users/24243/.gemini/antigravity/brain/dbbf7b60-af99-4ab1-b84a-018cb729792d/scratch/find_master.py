import os, sys, time, string
sys.stdout.reconfigure(encoding='utf-8')
hits = []
skip = ('\\Windows', '\\Program Files', '\\ProgramData', '$Recycle.Bin', 'node_modules', 'System Volume Information', '\\.gemini\\antigravity\\brain')
for letter in string.ascii_uppercase:
    root = letter + ':\\'
    if not os.path.exists(root):
        continue
    for a, ds, fs in os.walk(root):
        if any(s in a for s in skip):
            ds[:] = []; continue
        for f in fs:
            if '亚马逊供应商和开店总表' in f:
                p = os.path.join(a, f)
                try:
                    hits.append((os.path.getmtime(p), os.path.getsize(p), p))
                except OSError:
                    pass
hits.sort()
for m, s, p in hits:
    print(time.strftime('%Y-%m-%d %H:%M', time.localtime(m)), '%10d' % s, p)
print('count', len(hits))
