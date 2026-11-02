import openpyxl, sys
sys.stdout.reconfigure(encoding='utf-8')
base = r'C:\Users\24243\Documents\Codex\2026-08-11\7-30-slack-plugin-slack-openai\outputs\019ff179-ce00-7621-9ae6-13daf0989ce8'
def load(f):
    ws = openpyxl.load_workbook(base + '\\' + f, data_only=True)['Template']
    rows = list(ws.iter_rows(values_only=True))
    hdr = rows[3]
    data = {}
    order = []
    for r in rows[6:]:
        if r[0]:
            data[str(r[0]).strip()] = r
            order.append(str(r[0]).strip())
    return hdr, rows[:6], data, order
h1, top1, d100, o100 = load('4A_PriceAndQuantity_100_SKUs_2026-08-17.xlsx')
h2, top2, d23, o23 = load('4A_PriceAndQuantity_SC核验版_23_SKUs_2026-08-17.xlsx')
print('header same:', h1 == h2)
print('columns:', [str(c)[:34] for c in h1])
print('rows 100-file:', len(d100), '| 23-file:', len(d23), '| 23 in 100:', len(set(d23) & set(d100)), '| only in 23:', len(set(d23) - set(d100)))
print('feed header row0 same:', top1[0] == top2[0])
print('--- rows 4-6 of 100-file (template guide rows) ---')
for r in top1[4:6]: print([str(c)[:20] if c is not None else '' for c in r[:12]])
# column index map
idx = {i: str(c) for i, c in enumerate(h1)}
diffcols = {}
for sku in sorted(set(d23) & set(d100)):
    a, b = d100[sku], d23[sku]
    ch = [(idx[i][:30], a[i], b[i]) for i in range(len(a)) if a[i] != b[i]]
    if ch:
        diffcols[sku] = ch
print('SKUs in both with differing values:', len(diffcols))
for sku, ch in list(diffcols.items())[:25]:
    print(sku, ch)
print('--- only in 23 ---', sorted(set(d23) - set(d100)))
print('--- sample 100-file rows ---')
for s in o100[:5]: print([str(c)[:16] if c is not None else '' for c in d100[s][:12]])
