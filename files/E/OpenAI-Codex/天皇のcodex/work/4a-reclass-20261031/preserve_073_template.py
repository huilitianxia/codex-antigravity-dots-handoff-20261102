from pathlib import Path
import json, zipfile, re, hashlib
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.utils.cell import column_index_from_string
root=Path(__file__).parent
spec=json.loads((root/'09-073-spec.json').read_text('utf-8'))
src=Path(spec['source']);dest=Path(spec['final']);changes=spec['changes']
auth=openpyxl.load_workbook(root/'09-073-authored-cells.xlsx',read_only=True,data_only=True)['Template']
assert all(auth[a].value==v for a,v in changes.items())
part='xl/worksheets/sheet5.xml'
with zipfile.ZipFile(src) as z:
 xml=z.read(part).decode('utf-8')
 assert not re.search(r'<row\b[^>]*\br="(?:[7-9]|\d{2,})"',xml)
 cells=[]
 for addr,value in changes.items():
  cells.append(f'<c r="{addr}" t="inlineStr"><is><t>{escape(value)}</t></is></c>' if isinstance(value,str) else f'<c r="{addr}"><v>{value}</v></c>')
 cells.sort(key=lambda c:column_index_from_string(re.search(r'r="([A-Z]+)',c)[1]))
 xml=xml.replace('</sheetData>','<row r="7">'+''.join(cells)+'</row></sheetData>')
 xml=re.sub(r'<dimension ref="[^"]+"','<dimension ref="A1:AF7"',xml)
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
  for item in z.infolist():out.writestr(item,xml.encode('utf-8') if item.filename==part else z.read(item.filename))
with zipfile.ZipFile(src) as a,zipfile.ZipFile(dest) as b:
 changed=[n for n in a.namelist() if a.read(n)!=b.read(n)]
 assert changed==[part]
w=openpyxl.load_workbook(dest,read_only=True,data_only=False);s=w['Template']
actual={c.coordinate:c.value for row in s.iter_rows(min_row=7) for c in row if c.value is not None}
assert actual==changes
result={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'rows':1,'authorized_cells':actual,'changed_parts':changed,'all_other_parts_preserved':True,'ordinary_sale_stock_min_max_shipping_blank':True,'old_tier_replacement':'Old sole level 1 was 10 units / 8 percent. File overwrites level 1 with 3 / 2, adds level 2 = 5 / 3 and level 3 = 10 / 5. No delete token or duplicate SKU rows. Live readback must show exactly these 3 levels before Coupon enrollment.','status':'FILE_VERIFIED_NOT_UPLOADED'}
(root/'09-073-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
