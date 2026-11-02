import zipfile, re, os
from xml.etree import ElementTree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
ASIN = "B01M986R0Y"

def col_letter(ref):
    m = re.match(r'([A-Z]+)', ref or '')
    return m.group(1) if m else ''

def read_xlsx_zip(path):
    z = zipfile.ZipFile(path)
    shared = []
    if 'xl/sharedStrings.xml' in z.namelist():
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall(NS + 'si'):
            shared.append(''.join(t.text or '' for t in si.iter(NS + 't')))
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    rid2t = {rel.get('Id'): rel.get('Target') for rel in rels}
    sheets = []
    for s in wb.find(NS + 'sheets'):
        rid = s.get(RID)
        tgt = rid2t.get(rid)
        if tgt and not tgt.startswith('xl/'):
            tgt = 'xl/' + tgt
        sheets.append((s.get('name'), tgt))
    out = []
    for name, tgt in sheets:
        if not tgt or tgt not in z.namelist():
            continue
        root = ET.fromstring(z.read(tgt))
        sd = root.find(NS + 'sheetData')
        rows = {}
        for row in sd.findall(NS + 'row'):
            rn = int(row.get('r'))
            cells = {}
            for c in row.findall(NS + 'c'):
                col = col_letter(c.get('r'))
                t = c.get('t')
                v = c.find(NS + 'v')
                isn = c.find(NS + 'is')
                if t == 's' and v is not None:
                    val = shared[int(v.text)]
                elif t == 'inlineStr' and isn is not None:
                    val = ''.join(tt.text or '' for tt in isn.iter(NS + 't'))
                elif v is not None:
                    val = v.text
                else:
                    val = None
                cells[col] = val
            rows[rn] = cells
        hdr = rows.get(1, {})
        for rn, cells in rows.items():
            if rn == 1:
                continue
            if ASIN in list(cells.values()):
                out.append((name, rn, hdr, cells))
    return out

f = r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx"
res = read_xlsx_zip(f)
for name, rn, hdr, cells in res:
    print("-- sheet", name, "row", rn, "--")
    for col in ['A', 'B', 'C', 'F', 'I', 'X', 'AB', 'AD', 'I']:
        pass
    for col in sorted(cells, key=lambda x: (len(x), x)):
        print("   %s [%s] = %s" % (col, hdr.get(col), cells[col]))
