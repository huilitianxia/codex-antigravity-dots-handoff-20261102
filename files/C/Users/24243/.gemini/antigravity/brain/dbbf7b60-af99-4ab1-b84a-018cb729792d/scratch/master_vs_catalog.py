import openpyxl, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
D = r'C:\Users\24243\Downloads'
def load(n):
    wb = openpyxl.load_workbook(D + '\\' + n, read_only=True, data_only=True)
    rows = [list(r) for r in wb['Sheet1'].iter_rows(values_only=True)]
    out = {}
    for r in rows[1:]:
        if r[0]: out[str(r[0]).strip()] = (r[11], r[12])
    return out
def f(x):
    try: return round(float(x), 2)
    except Exception: return None
cat = {}
for l in open(r'D:\下载文件\所有商品报告_09-03-2026.txt', encoding='utf-8', errors='ignore'):
    p = l.split('\t')
    if len(p) > 4:
        try: cat[p[3].strip()] = round(float(p[4]), 2)
        except Exception: pass
for n in ['亚马逊供应商和开店总表-2026 (2).xlsx', '亚马逊供应商和开店总表-2026 (3).xlsx']:
    d = load(n)
    c = collections.Counter()
    for sku, (lp, sp) in d.items():
        if sku not in cat: c['not_in_catalog'] += 1; continue
        live = cat[sku]
        if f(lp) == live: c['catalog==标价'] += 1
        elif f(sp) == live: c['catalog==折后价'] += 1
        else: c['neither'] += 1
    print(n, dict(c))
# v3 sale/list overview
d3 = load('亚马逊供应商和开店总表-2026 (3).xlsx')
filled = sum(1 for lp, sp in d3.values() if sp not in (None, ''))
print('v3 rows with 折后销售价 filled:', filled, 'of', len(d3))
d2 = load('亚马逊供应商和开店总表-2026 (2).xlsx')
print('v2 rows with 折后销售价 filled:', sum(1 for lp, sp in d2.values() if sp not in (None, '')), 'of', len(d2))
tot = [(f(d3[k][0]) - f(d2[k][0])) for k in d3 if k in d2 and f(d3[k][0]) is not None and f(d2[k][0]) is not None and f(d3[k][0]) != f(d2[k][0])]
print('list-price changes v2->v3: n', len(tot), 'avg delta', round(sum(tot) / len(tot), 2) if tot else None, 'min', min(tot), 'max', max(tot))
print('delta distribution:', collections.Counter(round(x, 2) for x in tot).most_common(6))
