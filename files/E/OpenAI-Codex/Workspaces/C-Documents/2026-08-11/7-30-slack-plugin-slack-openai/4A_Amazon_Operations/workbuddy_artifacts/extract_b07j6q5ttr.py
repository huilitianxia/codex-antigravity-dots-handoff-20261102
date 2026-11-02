import zipfile, re, os
from xml.etree import ElementTree as ET

ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def col_letter(ref):
    m = re.match(r'([A-Z]+)', ref or '')
    return m.group(1) if m else ''

def read_xlsx(path, asin):
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
            if asin in list(cells.values()):
                out.append((s.get('name'), rn, hdr, cells))
    return out

asin = "B07J6Q5TTR"
files = [
    r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx",
    r"E:/Desktop/亚马逊供应商和开店总表-2023.xlsx",
]
for f in files:
    if not os.path.exists(f): print("MISSING", f); continue
    print("="*70); print("FILE:", os.path.basename(f))
    for name, rn, hdr, cells in read_xlsx(f, asin):
        print(f"  -- sheet {name} row {rn} --")
        for col in sorted(cells, key=lambda x:(len(x),x)):
            h = hdr.get(col)
            print(f"     {col} [{h}] = {cells[col]}")
