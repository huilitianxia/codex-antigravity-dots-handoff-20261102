import json,re,zipfile,copy,hashlib,collections,csv,html
from pathlib import Path
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.utils import column_index_from_string,get_column_letter
P=Path(__file__).parent
src=Path('D:/下载文件/分类商品报告_10-31-2026.xlsm')
dest=P.parents[1]/'outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/12-catalog-text-repairs-only.xlsm'
data=json.loads((P/'12-text-operations-draft.json').read_text('utf8'));ops=data['operations']
staged=openpyxl.load_workbook(P/'12-authored-cells.xlsx',read_only=True,data_only=True)['Template']
staged_rows=list(staged.iter_rows(min_row=7,max_row=6+len(ops),max_col=49,values_only=True))
allow={'C','D','E','I','J','L','M','AR','AS','AT','AU','AV','AW'}
assert len(ops)==len({o['sku'] for o in ops})
current={r['seller-sku']:r for r in csv.DictReader(Path('D:/下载文件/所有商品报告_11-01-2026.txt').open(encoding='utf-8-sig'),delimiter='\t')}
numbers=lambda t:set(re.findall(r'\d+(?:\.\d+)?',t))
numeric_checks=[]
for o in ops:
 assert set(o['cells'])<=allow
 assert current[o['sku']]['asin1']==o['asin']
 assert o['cells']['E']=='Edit (Partial Update)'
 if 'I' in o['cells']:
  assert len(o['cells']['I'])<=75 and len(o['cells']['J'])<=125
  assert o['cells']['I'].startswith('4A ')
  assert not re.fullmatch(r'B[A-Z0-9]{9}',o['cells']['J'])
  old=next(v for k,v in o['before'].items() if k.startswith('item_name'))
  clean=re.sub(r',\s*(?:AAAA\s+)?4A\s*[^,]*','',old);clean=re.sub(r'\b4A\b','',clean)
  new=re.sub(r'\b4A\b','',o['cells']['I']+' '+o['cells']['J'])
  assert numbers(clean)==numbers(new),(o['sku'],clean,new)
  numeric_checks.append(o['sku'])
 for k,v in o['changes'].items():
  assert not re.search(r'FREE\s*shipping|good\s*price|high\s*quality|recycl|certif|longer\s*and\s*stronger|https?://|www\.',v,re.I),(o['sku'],k,v)
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
 new=[]
 for n,o in enumerate(ops,7):
  cs=[]
  for col,expected in sorted(o['cells'].items(),key=lambda kv:column_index_from_string(kv[0])):
   value=staged_rows[n-7][column_index_from_string(col)-1];assert value==expected
   attrs=f' r="{col}{n}"'+(f' s="{styles[col]}"'if col in styles else'')
   cs.append(f'<c{attrs} t="inlineStr"><is><t xml:space="preserve">{escape(value)}</t></is></c>')
  new.append(f'<row r="{n}">'+''.join(cs)+'</row>')
 xml=xml[:sd.start(1)]+''.join(keep+new)+xml[sd.end(1):]
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED)as out:
  for part in z.infolist():out.writestr(copy.copy(part),xml.encode()if part.filename==sheet else z.read(part.filename))
 with zipfile.ZipFile(dest)as result:
  changed=[n for n in z.namelist()if z.read(n)!=result.read(n)];assert changed==[sheet];assert result.testzip()is None
original=openpyxl.load_workbook(src,read_only=True,data_only=False)
saved=openpyxl.load_workbook(dest,read_only=True,data_only=False)
assert saved.sheetnames==original.sheetnames
assert list(saved['Template'].iter_rows(max_row=6,values_only=True))==list(original['Template'].iter_rows(max_row=6,values_only=True))
actual=[{get_column_letter(i):v for i,v in enumerate(row,1)if v is not None}for row in saved['Template'].iter_rows(min_row=7,values_only=True)]
assert [r for r in actual if r]==[o['cells']for o in ops]
proof={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'rows':len(ops),'asins':len({o['asin']for o in ops}),'field_counts':data['fields'],'title_pair_numeric_values_preserved':len(numeric_checks),'maximum_title_length':max(len(o['cells'].get('I',''))for o in ops),'maximum_highlight_length':max(len(o['cells'].get('J',''))for o in ops),'populated_columns':sorted(allow,key=column_index_from_string),'all_columns_checked':True,'non_target_fields':0,'price_stock_color_pack_relationship_fields_written':False,'changed_zip_parts':changed,'headers_macros_other_tabs_unchanged':True,'hold_reasons':dict(collections.Counter(h['reason']for h in data['holds'])),'uploaded':False}
(P/'12-package-verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
body=[]
for o in ops:
 body.append('<tr><td>'+html.escape(o['sku'])+'</td><td>'+html.escape(o['asin'])+'</td><td>'+html.escape(o['cells'].get('I',''))+'</td><td>'+html.escape(o['cells'].get('J',''))+'</td><td>'+html.escape(o['cells'].get('AR',''))+'</td><td>'+html.escape('\n'.join(o['cells'].get(c,'')for c in ['AS','AT','AU','AV','AW']))+'</td></tr>')
(P/'12-full-text-review.html').write_text('<!doctype html><meta charset="utf-8"><style>body{font:14px Arial}table{border-collapse:collapse}td,th{padding:10px;border:1px solid #ddd;vertical-align:top;white-space:pre-wrap;min-width:150px}th{background:#eaf0f8;position:sticky;top:0}td:nth-child(n+3){min-width:300px}</style><h1>4A 文本修复逐行核查</h1><p>仅供核查。上传文件为12-catalog-text-repairs-only.xlsm。512条精确现存SKU；价格、库存、颜色、装量、父子字段未写。</p><table><tr><th>SKU</th><th>ASIN</th><th>标题</th><th>商品亮点</th><th>描述</th><th>五点</th></tr>'+''.join(body)+'</table>',encoding='utf8')
print(json.dumps(proof,ensure_ascii=False,indent=2))
