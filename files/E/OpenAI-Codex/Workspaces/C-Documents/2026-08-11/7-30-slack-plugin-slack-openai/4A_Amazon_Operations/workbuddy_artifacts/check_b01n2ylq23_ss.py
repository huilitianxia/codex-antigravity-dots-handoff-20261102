import zipfile, re, os
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
        for rn, cells in rows.items():
            if rn == 1: continue
            if any(x in list(cells.values()) for x in ["B01N2YLQ23", "B01NCQST12"]):
                print(f"\n=== Sheet {name}, Row {rn} ===")
                for col in sorted(cells, key=lambda x: (len(x), x)):
                    h = hdr.get(col)
                    print(f"  {col} [{h}] = {cells[col]}")

files = [
    r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx",
]
for f in files:
    if os.path.exists(f):
        print("FILE:", f)
        read_xlsx(f)
