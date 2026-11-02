import os, sys, time
sys.stdout.reconfigure(encoding='utf-8')
r = r'D:\4A'
def size(p):
    if os.path.isfile(p):
        return os.path.getsize(p)
    return sum(os.path.getsize(os.path.join(a, f)) for a, b, c in os.walk(p) for f in c)
rows = []
for n in os.listdir(r):
    p = os.path.join(r, n)
    rows.append((size(p), n, os.path.isdir(p), time.strftime('%m-%d', time.localtime(os.path.getmtime(p)))))
rows.sort(reverse=True)
print('items', len(rows), 'total MB', sum(x[0] for x in rows) // 1048576)
for s, n, d, m in rows:
    print('%8.1fMB %s %s %s' % (s / 1048576, 'D' if d else 'F', m, n))
