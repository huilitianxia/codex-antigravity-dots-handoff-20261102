import zipfile, re, json
from xml.etree import ElementTree as ET

ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def col_letter(ref):
    m = re.match(r'([A-Z]+)', ref or '')
    return m.group(1) if m else ''

def read_xlsx(path):
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall(ns+'si'):
            shared.append(''.join(t.text or '' for t in si.iter(ns+'t')))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rid2t = {rel.get('Id'): rel.get('Target') for rel in rels}
    sheets = []
    for s in wb.find(ns+'sheets'):
        rid = s.get(RID); tgt = rid2t.get(rid)
        if tgt and not tgt.startswith('xl/'): tgt = 'xl/'+tgt
        sheets.append((s.get('name'), tgt))
    out = []
    for name, tgt in sheets:
        if not tgt or tgt not in z.namelist(): continue
        root = ET.fromstring(z.read(tgt))
        sd = root.find(ns+'sheetData')
        rows = {}
        for row in sd.findall(ns+'row'):
            rn = int(row.get('r')); cells = {}
            for c in row.findall(ns+'c'):
                col = col_letter(c.get('r')); t = c.get('t')
                v = c.find(ns+'v'); isn = c.find(ns+'is')
                if t == 's' and v is not None: val = shared[int(v.text)]
                elif t == 'inlineStr' and isn is not None: val = ''.join(tt.text or '' for tt in isn.iter(ns+'t'))
                elif v is not None: val = v.text
                else: val = None
                cells[col] = val
            rows[rn] = cells
        hdr = rows.get(1, {})
        out.append((name, hdr, rows))
    return out

# Load vendor table VC-ASINs
with open("vendor_table_data.json") as f:
    vdata = json.load(f)
vc_asins = set()
vc_map = {}
for x in vdata:
    for a in x['vc_asin']:
        vc_asins.add(a)
        vc_map[a] = x['sku']

print(f"Vendor VC-ASINs: {len(vc_asins)}")

files = [
    r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx",
    r"E:/Desktop/Search(4A-sticky-notes)-59-US-20260808.xlsx",
]

asin_data = {}
for fp in files:
    print(f"\nReading {fp.split('/')[-1]} ...")
    try:
        for name, hdr, rows in read_xlsx(fp):
            # map header to col letter
            hmap = {v: k for k, v in hdr.items() if v}
            asin_col = hmap.get('ASIN') or hmap.get('asin')
            if not asin_col:
                continue
            for rn, cells in rows.items():
                if rn == 1: continue
                a = cells.get(asin_col)
                if not a or a not in vc_asins:
                    continue
                def get(label):
                    c = hmap.get(label)
                    return cells.get(c) if c else None
                rec = {
                    'sku': vc_map.get(a),
                    'monthly_sales': get('月销量') or get('月销量(估算)'),
                    'reviews': get('评分数') or get('评论数'),
                    'rating': get('评分'),
                    'sellers': get('卖家数'),
                    'buybox': get('BuyBox卖家') or get('buybox卖家'),
                    'price': get('价格') or get('售价'),
                    'source_file': fp.split('/')[-1],
                }
                asin_data[a] = rec
    except Exception as e:
        print("  ERROR:", e)

print(f"\nMatched VC-ASINs in SellerSprite data: {len(asin_data)}")
print("\n=== Matched records ===")
for a, rec in asin_data.items():
    print(f"  {a} [{rec['sku']}]: sellers={rec['sellers']} buybox={rec['buybox']} rating={rec['rating']} reviews={rec['reviews']} sales={rec['monthly_sales']} price={rec['price']}")

with open("ss_matched.json","w") as f:
    json.dump(asin_data, f, ensure_ascii=False, indent=2)
