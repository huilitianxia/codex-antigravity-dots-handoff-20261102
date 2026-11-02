import zipfile, re, os
from xml.etree import ElementTree as ET

ns = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
RID = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'

def col_letter(ref):
    m = re.match(r'([A-Z]+)', ref or '')
    return m.group(1) if m else ''

def read_xlsx_zip(path, search_term=None, parent_term=None):
    """Return rows where any cell == search_term, OR where 父ASIN col == parent_term."""
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
        for rn, cells in rows.items():
            if rn == 1: continue
            vals = list(cells.values())
            hit = False
            if search_term and search_term in vals:
                hit = True
            if parent_term:
                # find 父ASIN header column
                for col, h in hdr.items():
                    if h and '父' in str(h):
                        if cells.get(col) == parent_term:
                            hit = True
            if hit:
                out.append((name, rn, hdr, cells))
    return out

# Official report
print("="*70)
print("OFFICIAL REPORT for B07JN9LKQZ")
with open(r"E:/Desktop/所有商品报告_08-08-2026.txt", encoding="utf-8-sig", errors="replace") as f:
    rows = list(__import__('csv').reader(f, delimiter="\t"))
hdr = rows[0]
for r in rows[1:]:
    if "B07JN9LKQZ" in r:
        for i, v in enumerate(r):
            if i < len(hdr):
                print(f"  [{hdr[i]}] = {v}")
        break
else:
    print("  NOT FOUND in official report")

files = [
 r"E:/Desktop/Search(4A-sticky-notes)-59-US-20260808.xlsx",
 r"E:/Desktop/Competitor-US-Last-30-days-217940.xlsx",
 r"E:/Desktop/Search(B00SMEEF2A,B00SMEF4RU,B00SMEFE48,B00SMEFEFM,B00V9Z5UMI,B00V9Z5Y56,B00V9Z5YCO,B01JGGQ4WQ,B01LW6N0WA,B01LWA44KM,B01M21QGV3,B01M58HPUJ,B01M6181P0,B01MA0ZWWR,B01MDJGBD5,B01MEBRJQE,B01MQW8U03,B01MQW96JR,B01MQXZ2LP,B01MRZCNY9,.xlsx",
 r"E:/Desktop/Search(B07FK7DJDR,B07FK7JN8Q,B07FK7XDRL,B07FK7Y7YC,B07FK89D9D,B07FK8BSJT,B07FK8DX1J,B07FK8FM6W,B07FK8GGN2,B07FK8MBLS,B07FK8ML41,B07FK8R3J3,B07FK8RTZH,B07FK8VCR6,B07FK8XDQ3,B07FK8YCKR,B07FK958BT,B07FK98YTX,B07FK9BMYQ,B07FK9NRP5,.xlsx",
]

print("\n" + "="*70)
print("Search all xlsx for B07JN9LKQZ itself OR parent == B07JN9LKQZ")
for f in files:
    if not os.path.exists(f):
        print("MISSING", f); continue
    print("-"*70); print("FILE:", os.path.basename(f))
    try:
        res = read_xlsx_zip(f, search_term="B07JN9LKQZ", parent_term="B07JN9LKQZ")
        if not res:
            print("  (no match)")
        for name, rn, hdr, cells in res:
            # print key cols
            keys = {}
            for col, h in hdr.items():
                if h and any(k in str(h) for k in ['ASIN','标题','父','评分','评分数','价格','配送','状态','Status','condition']):
                    keys[col] = (h, cells.get(col))
            print(f"  -- sheet {name} row {rn} --")
            for col in sorted(keys, key=lambda x:(len(x),x)):
                h, v = keys[col]
                print(f"     {col} [{h}] = {v}")
    except Exception as e:
        import traceback; traceback.print_exc()
