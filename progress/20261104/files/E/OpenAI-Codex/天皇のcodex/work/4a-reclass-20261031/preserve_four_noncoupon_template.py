from pathlib import Path
import json,zipfile,re,hashlib
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.utils.cell import column_index_from_string
root=Path(__file__).parent
spec=json.loads((root/'10-four-spec.json').read_text('utf-8'))
src=Path(spec['source']);dest=Path(spec['final']);changes=spec['changes']
auth=openpyxl.load_workbook(root/'10-four-authored-cells.xlsx',read_only=True,data_only=True)['Template']
assert all(auth[a].value==v for a,v in changes.items())
part='xl/worksheets/sheet5.xml'
with zipfile.ZipFile(src) as z:
 xml=z.read(part).decode('utf-8')
 assert not re.search(r'<row\b[^>]*\br="(?:[7-9]|\d{2,})"',xml)
 rows=[]
 for rn in range(7,11):
  cells=[]
  for addr,value in changes.items():
   if int(re.search(r'\d+',addr)[0])!=rn:continue
   cells.append(f'<c r="{addr}" t="inlineStr"><is><t>{escape(value)}</t></is></c>' if isinstance(value,str) else f'<c r="{addr}"><v>{value}</v></c>')
  cells.sort(key=lambda c:column_index_from_string(re.search(r'r="([A-Z]+)',c)[1]))
  rows.append(f'<row r="{rn}">'+''.join(cells)+'</row>')
 xml=xml.replace('</sheetData>',''.join(rows)+'</sheetData>')
 xml=re.sub(r'<dimension ref="[^"]+"','<dimension ref="A1:AF10"',xml)
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
  for item in z.infolist():out.writestr(item,xml.encode('utf-8') if item.filename==part else z.read(item.filename))
with zipfile.ZipFile(src) as a,zipfile.ZipFile(dest) as b:
 changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
 assert changed==[part]
w=openpyxl.load_workbook(dest,read_only=True,data_only=False);s=w['Template']
actual={c.coordinate:c.value for row in s.iter_rows(min_row=7) for c in row if c.value is not None}
assert actual==changes
assert len(actual)==48 and len({s[f'A{r}'].value for r in range(7,11)})==4
assert all(s[f'{c}{r}'].value is None for r in range(7,11) for c in ['B','C','D','E','F','G','H','I','J','N','O','Q','R','S','T','AB','AC','AD','AE','AF'])
result={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'rows':4,'authorized_cells':actual,'changed_parts':changed,'all_other_parts_preserved':True,'ordinary_inventory_minmax_shipping_fields_blank':True,'date_semantics':'Sale starts2026-11-02; official template end stops sale at00:00 so2026-11-16 covers11/15 fully. Business tiers persist after sale ends.','tier_replacement':'NGGrid oldsole2units3percent replaced bylevel1=3/2,level2=5/3,level3=10/5. Other3have no prior tiers. No delete tokens. Verify exactly3tiers after upload.','status':'FILE_VERIFIED_NOT_UPLOADED','not_price_discounts_campaign':True}
(root/'10-four-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
