import os, sys, time, datetime
sys.stdout.reconfigure(encoding='utf-8')
root = r'C:\Users\24243'
cut = datetime.datetime(2026, 10, 15).timestamp()
skip = ('\\AppData\\Local\\Temp', '\\AppData\\Local\\Google', '\\AppData\\Local\\Microsoft', '\\AppData\\Roaming\\Microsoft',
        '\\.gemini\\antigravity\\brain', '\\node_modules', '\\.cache', '\\AppData\\Local\\Packages', '\\AppData\\Local\\pip')
hits = []
for a, ds, fs in os.walk(root):
    if any(s in a for s in skip):
        ds[:] = []; continue
    for f in fs:
        if f.lower().endswith(('.xlsx', '.xlsm', '.xls', '.csv', '.tsv')):
            p = os.path.join(a, f)
            try:
                m = os.path.getmtime(p)
            except OSError:
                continue
            if m > cut:
                hits.append((m, os.path.getsize(p), p))
hits.sort()
for m, s, p in hits:
    print(time.strftime('%m-%d %H:%M', time.localtime(m)), '%9d' % s, p)
print('count', len(hits))
