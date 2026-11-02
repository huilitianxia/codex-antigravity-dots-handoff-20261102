import zipfile, re, os, csv
from xml.etree import ElementTree as ET

ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def col_letter(ref):
    m = re.match(r'([A-Z]+)', ref or '')
    return m.group(1) if m else ''

def read_xlsx_zip(path, parent_term=None):
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall(ns+'si'):
            shared.append(''.join(t.text or '' for t in si.iter(ns+'t')))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rid2t = {rel.get('Id'): rel.get('Target') for rel in rels}
    out = []
    for s in wb.find(ns+'sheets'):
        rid = s.get(RID); tgt = rid2t.get(rid)
        if tgt and not tgt.startswith('xl/'): tgt = 'xl/'+tgt
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
        for rn, cells in rows.items():
            if rn == 1: continue
            for col, h in hdr.items():
                if h and '父' in str(h) and cells.get(col) == parent_term:
                    out.append((s.get('name'), rn, hdr, cells))
    return out

parent = "B07KR9LD68"
files = [
 r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx",
 r"E:/Desktop/Search(4A-sticky-notes)-59-US-20260808.xlsx",
]
print("Children of parent", parent, "from SellerSprite exports:")
for f in files:
    if not os.path.exists(f):
        print("MISSING", f); continue
    print("-"*60); print(os.path.basename(f))
    try:
        for name, rn, hdr, cells in read_xlsx_zip(f, parent_term=parent):
            asin = cells.get('A')
            title = cells.get('F')
            print(f"  {asin} | {title}")
    except Exception as e:
        import traceback; traceback.print_exc()

# Now check each child's status in official report
with open(r"E:/Desktop/所有商品报告_08-08-2026.txt", encoding="utf-8-sig", errors="replace") as fh:
    rep = list(csv.reader(fh, delimiter="\t"))
rh = rep[0]
ai = rh.index("asin1"); si = rh.index("status"); ni = rh.index("item-name"); qi = rh.index("quantity")
# collect children asins mentioned above - we need them; re-run parse to collect
children = []
for f in files:
    if not os.path.exists(f): continue
    for name, rn, hdr, cells in read_xlsx_zip(f, parent_term=parent):
        children.append(cells.get('A'))
print("\nOfficial report status for each child:")
for child in children:
    for r in rep[1:]:
        if child in r:
            print(f"  {child} | status={r[si]} | qty={r[qi]} | {r[ni][:50]}")
            break
    else:
        print(f"  {child} | NOT in our official report")
