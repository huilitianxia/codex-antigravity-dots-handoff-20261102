import openpyxl, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\24243\Downloads'
names = ['亚马逊供应商和开店总表-2026.xlsx', '亚马逊供应商和开店总表-2026 (1).xlsx', '亚马逊供应商和开店总表-2026 (2).xlsx', '亚马逊供应商和开店总表-2026 (3).xlsx']
tags = ['v0', 'v1', 'v2', 'v3']
FIELDS = ['标价', '折后销售价', 'FOB (SZ)', 'AmazOn Cost', '物流N4.99/B9.99/', '产品满箱数', 'ASIn']
tab = {}
meta = {}
for n, t in zip(names, tags):
    wb = openpyxl.load_workbook(D + '\\' + n, read_only=True, data_only=True)
    rows = [list(r) for r in wb['Sheet1'].iter_rows(values_only=True)]
    hdr = [str(c).replace('\n', '') if c is not None else '' for c in rows[0]]
    def col(name):
        for i, h in enumerate(hdr):
            if h.startswith(name): return i
        return None
    cidx = {f: col(f) for f in FIELDS}
    skus = collections.OrderedDict()
    dup = 0
    for r in rows[1:]:
        if r[0] in (None, ''): continue
        k = str(r[0]).strip()
        if k in skus: dup += 1; continue
        skus[k] = {f: (r[cidx[f]] if cidx[f] is not None and cidx[f] < len(r) else None) for f in FIELDS}
        skus[k]['_extra'] = r[13] if t == 'v3' and len(r) > 13 else None
    tab[t] = skus
    meta[t] = (len(skus), dup)
    print(t, 'SKUs', len(skus), 'dup-skipped', dup, '| col idx', cidx)

def norm(x):
    try: return round(float(x), 4)
    except Exception: return str(x).strip() if x is not None else None

for a, b in [('v0', 'v1'), ('v1', 'v2'), ('v2', 'v3')]:
    A, B = tab[a], tab[b]
    added = [k for k in B if k not in A]
    removed = [k for k in A if k not in B]
    print('\n#### %s -> %s : added %d, removed %d' % (a, b, len(added), len(removed)))
    if added: print('  added:', added[:25])
    if removed: print('  removed:', removed[:25])
    cnt = collections.Counter()
    ex = collections.defaultdict(list)
    for k in A:
        if k in B:
            for f in FIELDS:
                if norm(A[k][f]) != norm(B[k][f]):
                    cnt[f] += 1
                    if len(ex[f]) < 8: ex[f].append((k, A[k][f], B[k][f]))
    print('  changed fields:', dict(cnt))
    for f, e in ex.items():
        print('   ', f, e)
print('\nv3 extra col (idx13) sample:', [(k, v['_extra']) for k, v in list(tab['v3'].items())[:6]])
