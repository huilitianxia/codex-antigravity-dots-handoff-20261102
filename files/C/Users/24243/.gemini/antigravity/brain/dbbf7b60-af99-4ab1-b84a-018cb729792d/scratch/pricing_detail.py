import openpyxl, sys, collections, csv
sys.stdout.reconfigure(encoding='utf-8')
base = r'C:\Users\24243\Documents\Codex\2026-08-11\7-30-slack-plugin-slack-openai\outputs\019ff179-ce00-7621-9ae6-13daf0989ce8'
ws = openpyxl.load_workbook(base + '\\4A_PriceAndQuantity_100_SKUs_2026-08-17.xlsx', data_only=True)['Template']
rows = list(ws.iter_rows(values_only=True))
hdr = [str(c) for c in rows[3]]
data = [r for r in rows[6:] if r[0]]
col = {h[:28] + '#' + str(i): i for i, h in enumerate(hdr)}
def cnt(i): return collections.Counter(str(r[i]) for r in data).most_common(4)
print('n', len(data))
print('sale start', cnt(11)); print('sale end', cnt(12)); print('fulfil', cnt(1)); print('qty', cnt(2))
print('B2B price col(15) filled:', sum(1 for r in data if r[15] not in (None, '')))
print('qty price type(20):', cnt(20)); print('thr1(21):', cnt(21)); print('qty price1(22):', cnt(22))
print('shipping tmpl(31):', cnt(31))
# compare to the latest all-listings report
cur = {}
with open(r'D:\下载文件\所有商品报告_09-03-2026.txt', encoding='utf-8', errors='ignore') as f:
    for l in f:
        p = l.split('\t')
        if len(p) > 4:
            cur[p[3]] = p[4]
same = diff = miss = 0
ex = []
for r in data:
    sku = str(r[0]).strip()
    if sku not in cur: miss += 1; continue
    try:
        if abs(float(cur[sku]) - float(r[6])) < 0.005: same += 1
        else:
            diff += 1
            if len(ex) < 12: ex.append((sku, 'file', r[6], 'catalog(09-03)', cur[sku]))
    except Exception: miss += 1
print('vs 09-03 catalog price: same', same, 'diff', diff, 'not-found', miss)
for e in ex: print(e)
