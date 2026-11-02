import os, sys, time, re
sys.stdout.reconfigure(encoding='utf-8')
pat = re.compile(r'定价|价格|改价|调价|pricing|price|reprice|促销|coupon|优惠|4A|amazon|亚马逊', re.I)
skip = ('C:\\Windows', 'C:\\Program Files', 'C:\\ProgramData', '$Recycle.Bin', 'node_modules', '\\.workbuddy\\plugins',
        '\\AppData\\Local\\Temp', '\\.gemini\\antigravity\\brain', '\\AppData\\Local\\Packages', 'C:\\Users\\All Users')
hits = []
for a, ds, fs in os.walk('C:\\'):
    if any(s in a for s in skip):
        ds[:] = []; continue
    for f in fs:
        if f.lower().endswith(('.xlsx', '.xlsm', '.xls', '.csv', '.tsv')) and pat.search(f):
            p = os.path.join(a, f)
            try:
                hits.append((os.path.getmtime(p), os.path.getsize(p), p))
            except OSError:
                pass
hits.sort()
for m, s, p in hits:
    print(time.strftime('%Y-%m-%d %H:%M', time.localtime(m)), '%9d' % s, p)
print('count', len(hits))
