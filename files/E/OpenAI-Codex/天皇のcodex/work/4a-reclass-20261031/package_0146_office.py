import json,re,zipfile,copy,hashlib
from pathlib import Path
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.utils import column_index_from_string,get_column_letter
P=Path(__file__).parent
src=Path('D:/下载文件/分类商品报告_10-31-2026.xlsm')
dest=P.parents[1]/'outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/13-0146-office-only.xlsm'
cells={'C':'4A 0146','D':'WRITING_BOARD','E':'Edit (Partial Update)','L':'ASIN','M':'B0778HMZ9W','GD':'Office'}
source=openpyxl.load_workbook(src,read_only=True,data_only=True)
assert source['Valid Values']['B124'].value=='Recommended Uses For Product - [ WRITING_BOARD ]'
assert source['Valid Values']['L124'].value=='Office'
assert source['Template']['GD5'].value=='recommended_uses_for_product[marketplace_id=ATVPDKIKX0DER][language_tag=en_US]#1.value'
staged=openpyxl.load_workbook(P/'13-authored-cells.xlsx',read_only=True,data_only=True)['Template']
for c,v in cells.items():assert staged[c+'7'].value==v
with zipfile.ZipFile(src)as z:
 sheet='xl/worksheets/sheet5.xml';xml=z.read(sheet).decode();sd=re.search(r'<sheetData>(.*?)</sheetData>',xml,re.S)
 keep=[];styles={}
 for row in re.findall(r'<row\b[^>]*(?:/>|>.*?</row>)',sd[1],re.S):
  n=int(re.search(r'\br="(\d+)"',row)[1])
  if n<7:keep.append(row)
  if n==7:
   for c in re.findall(r'<c\b[^>]*(?:/>|>.*?</c>)',row,re.S):
    col=re.search(r'\br="([A-Z]+)\d+"',c)[1];style=re.search(r'\bs="(\d+)"',c)
    if style:styles[col]=style[1]
 cs=[]
 for col,val in cells.items():
  attrs=f' r="{col}7"'+(f' s="{styles[col]}"'if col in styles else'')
  cs.append(f'<c{attrs} t="inlineStr"><is><t xml:space="preserve">{escape(val)}</t></is></c>')
 xml=xml[:sd.start(1)]+''.join(keep)+'<row r="7">'+''.join(cs)+'</row>'+xml[sd.end(1):]
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as out:
  for part in z.infolist():out.writestr(copy.copy(part),xml.encode()if part.filename==sheet else z.read(part.filename))
 with zipfile.ZipFile(dest)as result:
  changed=[n for n in z.namelist()if z.read(n)!=result.read(n)];assert changed==[sheet];assert result.testzip()is None
saved=openpyxl.load_workbook(dest,read_only=True,data_only=False)
actual=[{get_column_letter(i):v for i,v in enumerate(row,1)if v is not None}for row in saved['Template'].iter_rows(min_row=7,values_only=True)]
assert [r for r in actual if r]==[cells]
assert list(saved['Template'].iter_rows(max_row=6,values_only=True))==list(source['Template'].iter_rows(max_row=6,values_only=True))
proof={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'rows':1,'populated_cells':cells,'all_other_data_cells_blank':True,'changed_zip_parts':changed,'headers_macros_other_tabs_unchanged':True,'valid_value_evidence':'Valid Values!B124 WRITING_BOARD / L124 Office','uploaded':False}
(P/'13-package-verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(proof,ensure_ascii=False,indent=2))
