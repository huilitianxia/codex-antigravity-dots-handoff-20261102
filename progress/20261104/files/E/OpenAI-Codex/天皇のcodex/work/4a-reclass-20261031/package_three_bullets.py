import json,re,zipfile,copy,hashlib
from pathlib import Path
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.utils import get_column_letter,column_index_from_string
P=Path(__file__).parent
O=Path('E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes')
src=Path('D:/下载文件/分类商品报告_10-31-2026.xlsm')
dest=O/'06-three-skus-five-bullets-only.xlsm'
ops=json.loads((P/'three-bullets-operations.json').read_text(encoding='utf8'))
staged=openpyxl.load_workbook(P/'three-bullets-cells.xlsx',read_only=True,data_only=True)['Template']
allow={'C','D','E','L','M','AS','AT','AU','AV','AW'}
assert len(ops)==3
assert all(set(x['cells'])==allow for x in ops)
with zipfile.ZipFile(src) as z:
 sheet='xl/worksheets/sheet5.xml';xml=z.read(sheet).decode('utf8');sd=re.search(r'<sheetData>(.*?)</sheetData>',xml,re.S)
 keep=[];styles={}
 for row in re.findall(r'<row\b[^>]*(?:/>|>.*?</row>)',sd[1],re.S):
  n=int(re.search(r'\br="(\d+)"',row)[1])
  if n<7:keep.append(row)
  if n==7:
   for c in re.findall(r'<c\b[^>]*(?:/>|>.*?</c>)',row,re.S):
    col=re.search(r'\br="([A-Z]+)\d+"',c)[1];s=re.search(r'\bs="(\d+)"',c)
    if s:styles[col]=s[1]
 new=[]
 for n,op in enumerate(ops,7):
  cells=[]
  for col,expected in sorted(op['cells'].items(),key=lambda kv:column_index_from_string(kv[0])):
   value=staged[f'{col}{n}'].value;assert value==expected
   attrs=f' r="{col}{n}"'+(f' s="{styles[col]}"' if col in styles else '')
   cells.append(f'<c{attrs} t="inlineStr"><is><t xml:space="preserve">{escape(value)}</t></is></c>')
  new.append(f'<row r="{n}">'+''.join(cells)+'</row>')
 xml=xml[:sd.start(1)]+''.join(keep+new)+xml[sd.end(1):]
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
  for part in z.infolist():out.writestr(copy.copy(part),xml.encode() if part.filename==sheet else z.read(part.filename))
 with zipfile.ZipFile(dest) as result:
  changed=[n for n in z.namelist() if z.read(n)!=result.read(n)];assert changed==[sheet];assert result.testzip() is None
original=openpyxl.load_workbook(src,read_only=True,data_only=False)
saved=openpyxl.load_workbook(dest,read_only=True,data_only=False)
assert saved.sheetnames==original.sheetnames
assert list(saved['Template'].iter_rows(max_row=6,values_only=True))==list(original['Template'].iter_rows(max_row=6,values_only=True))
actual=[{get_column_letter(i):v for i,v in enumerate(row,1) if v is not None} for row in saved['Template'].iter_rows(min_row=7,values_only=True)]
actual=[r for r in actual if r]
assert actual==[x['cells'] for x in ops]
for i in range(5):assert f'#{i+1}.value' in str(saved['Template'].cell(5,45+i).value) and 'bullet_point' in str(saved['Template'].cell(5,45+i).value)
proof={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'rows':3,'asins':3,'bullets':15,'populated_columns':sorted(allow,key=column_index_from_string),'all_columns_checked':True,'non_target_fields':0,'changed_zip_parts':changed,'headers_macros_other_tabs_unchanged':True,'uploaded':False}
(P/'three-bullets-package-verification.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(proof))
