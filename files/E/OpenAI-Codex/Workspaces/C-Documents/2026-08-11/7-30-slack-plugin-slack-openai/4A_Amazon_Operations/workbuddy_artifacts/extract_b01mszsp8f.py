import zipfile, re, os
from xml.etree import ElementTree as ET

NS = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
ASIN = "B01MSZSP8F"

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

files = [
    r"E:/Desktop/Search(4A-sticky-notes)-59-US-20260808.xlsx",
    r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx",
    r"E:/Desktop/Search(B00SMEEF2A,B00SMEF4RU,B00SMEFE48,B00SMEFEFM,B00V9Z5UMI,B00V9Z5Y56,B00V9Z5YCO,B01JGGQ4WQ,B01LW6N0WA,B01LWA44KM,B01M21QGV3,B01M58HPUJ,B01M6181P0,B01MA0ZWWR,B01MDJGBD5,B01MEBRJQE,B01MQW8U03,B01MQW96JR,B01MQXZ2LP,B01MRZCNY9,.xlsx",
    r"E:/Desktop/Search(B07FK7DJDR,B07FK7JN8Q,B07FK7XDRL,B07FK7Y7YC,B07FK89D9D,B07FK8BSJT,B07FK8DX1J,B07FK8FM6W,B07FK8GGN2,B07FK8MBLS,B07FK8ML41,B07FK8R3J3,B07FK8RTZH,B07FK8VCR6,B07FK8XDQ3,B07FK8YCKR,B07FK958BT,B07FK98YTX,B07FK9BMYQ,B07FK9NRP5,.xlsx",
]

for f in files:
    if not os.path.exists(f):
        print("MISSING", f)
        continue
    print("=" * 70)
    print("FILE:", os.path.basename(f))
    try:
        res = read_xlsx_zip(f)
        if not res:
            print("  (no match for", ASIN, ")")
        for name, rn, hdr, cells in res:
            print("  -- sheet", name, "row", rn, "--")
            for col in sorted(cells, key=lambda x: (len(x), x)):
                print("     %s [%s] = %s" % (col, hdr.get(col), cells[col]))
    except Exception:
        import traceback
        traceback.print_exc()
