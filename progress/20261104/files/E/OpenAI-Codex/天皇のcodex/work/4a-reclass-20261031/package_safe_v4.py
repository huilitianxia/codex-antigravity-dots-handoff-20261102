import json,re,zipfile,copy,hashlib,html,sys
from pathlib import Path
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.utils import column_index_from_string,get_column_letter
P=Path(__file__).parent
O=Path('E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes')
stem='04-reviewed-nonincident-fixes'
def rd(n):return json.loads((P/n).read_text(encoding='utf8'))
identity={'C','D','E','L','M'}; copycols={'AS','AT','AU','AV','AW'}
pricecols={'MJ','ML','MN','MO','MP','MS','MX','MY','MZ','NA','NB','NC','ND','NE','NF','NG','NH'}
raw=rd('category-report-raw.json'); rb={x['contribution_sku#1.value']:x for x in raw['rows']}
audit=rd('v1-price-incident-audit.json'); draft=rd('execution-batch-data.json')
blocked={x['asin'] for x in audit['records'] if x['drop_pct']>=30 or x['status'].startswith('已确认错误') or x['status'].startswith('待复核')}
blocked.add('B07RQ6HLK3')
blocked.add('B07FKGPCQM')  # 02 restoration price baseline 19.99 -> 12.99 needs separate review.
if '--prepare' in sys.argv:
 ops=[];excluded=[]
 for x in draft['operations']:
  if x['asin'] in blocked:
   excluded.append({'sku':x['sku'],'asin':x['asin'],'reason':'4013已在线提交' if x['asin']=='B07RQ6HLK3' else '价格事故相关ASIN，本批所有字段排除'});continue
  cells={k:v for k,v in x['cells'].items() if k in identity|copycols}
  if not set(cells)&copycols:continue
  # Verify exact SKU/ASIN identity from source, preserving identifiers and product type.
  assert x['sku'] in rb and cells['C']==x['sku'] and cells['M']==x['asin']
  ops.append({**x,'cells':cells,'before':{k:v for k,v in x['before'].items() if k in copycols},'reasons':['清理原要点中的促销/无依据声明；保留产品事实'],'sources':['10/31分类报告同SKU原始要点及标题']})
 approved=rd('v4-approved-price-rows.json') if '--with-approved-prices' in sys.argv else []
 for approved_row in approved:
  assert approved_row['asin'] not in blocked
  pc=approved_row['allowed_price_cells'];assert pc and set(pc)<=pricecols
  old=next(x for x in draft['operations'] if x['sku']==approved_row['sku'] and x['asin']==approved_row['asin'])
  target=next((x for x in ops if x['sku']==old['sku']),None)
  if target is None:
   target={**old,'cells':{k:v for k,v in old['cells'].items() if k in identity},'before':{}};ops.append(target)
  target['cells'].update(pc)
  target['before'].update({k:old['before'].get(k) for k in pc})
  target['sources'].append('逐行独立价格审核白名单及主代理现态促销核验')
 data={'operations':ops,'excluded':excluded,'blocked_asins':sorted(blocked),'pricing':approved,'pricing_policy':'仅写入获批白名单列，其余价格字段不写入','stats':{'rows':len(ops),'asins':len({x['asin']for x in ops}),'full_bullet_rows':sum('AS'in x['cells'] for x in ops),'bullet5_rows':sum('AW'in x['cells'] for x in ops),'price_rows':len(approved)}}
 (P/'safe-v4-data.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(data['stats'],ensure_ascii=False));sys.exit()
d=rd('safe-v4-data.json');assert not({x['asin'] for x in d['operations']}&blocked)
approved_by={x['sku']:x for x in d['pricing']}
for x in d['operations']:
 assert set(x['cells'])<=identity|copycols|pricecols
 assert {k:v for k,v in x['cells'].items() if k in pricecols}==approved_by.get(x['sku'],{}).get('allowed_price_cells',{})
src=Path('D:/下载文件/分类商品报告_10-31-2026.xlsm')
aw=openpyxl.load_workbook(P/(stem+'-cells.xlsx'),read_only=True,data_only=True)['Template']
with zipfile.ZipFile(src) as z:
 sheet='xl/worksheets/sheet5.xml';xml=z.read(sheet).decode('utf8');sd=re.search(r'<sheetData>(.*?)</sheetData>',xml,re.S);assert sd
 keep=[];style={}
 for row in re.findall(r'<row\b[^>]*(?:/>|>.*?</row>)',sd[1],re.S):
  n=int(re.search(r'\br="(\d+)"',row)[1])
  if n<7:keep.append(row)
  if n==7:
   for c in re.findall(r'<c\b[^>]*(?:/>|>.*?</c>)',row,re.S):
    col=re.search(r'\br="([A-Z]+)\d+"',c)[1];s=re.search(r'\bs="(\d+)"',c)
    if s:style[col]=s[1]
 new=[]
 for n,x in enumerate(d['operations'],7):
  cells=[]
  for col,expected in sorted(x['cells'].items(),key=lambda kv:column_index_from_string(kv[0])):
   v=aw[f'{col}{n}'].value;assert v==expected
   attrs=f' r="{col}{n}"'+(f' s="{style[col]}"' if col in style else '')
   cells.append(f'<c{attrs}><v>{v}</v></c>' if isinstance(v,(int,float)) else f'<c{attrs} t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>')
  new.append(f'<row r="{n}">'+''.join(cells)+'</row>')
 xml=xml[:sd.start(1)]+''.join(keep+new)+xml[sd.end(1):]
 dest=O/(stem+'.xlsm');O.mkdir(exist_ok=True,parents=True)
 with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as o:
  for part in z.infolist():o.writestr(copy.copy(part),xml.encode('utf8') if part.filename==sheet else z.read(part.filename))
 with zipfile.ZipFile(dest) as t:
  changed=[n for n in z.namelist() if z.read(n)!=t.read(n)];assert changed==[sheet]
  assert t.testzip() is None
source=openpyxl.load_workbook(src,read_only=True,data_only=False);saved=openpyxl.load_workbook(dest,read_only=True,data_only=False)
assert source.sheetnames==saved.sheetnames
for a,b in zip(source['Template'].iter_rows(max_row=6,values_only=True),saved['Template'].iter_rows(max_row=6,values_only=True)):assert a==b
found=[]
for row in saved['Template'].iter_rows(min_row=7,values_only=True):
 actual={get_column_letter(i):v for i,v in enumerate(row,1) if v is not None}
 if actual:found.append(actual)
assert found==[x['cells'] for x in d['operations']]
assert len({x['C'] for x in found})==len(found)
check={'file':str(dest),'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'rows':len(found),'asins':len({r['M']for r in found}),'changed_zip_parts':changed,'all_544_columns_checked':True,'approved_price_rows':len(d['pricing']),'unapproved_price_fields_populated':0,'stock_shipping_family_fields_populated':0,'header_rows_1_6_unchanged':True,'other_tabs_macros_validations_unchanged':True,'excluded_asins_absent':True}
(P/'safe-v4-package-verification.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf8')
def table(h,rows):return '<table><tr>'+''.join('<th>'+html.escape(str(v))+'</th>'for v in h)+'</tr>'+''.join('<tr>'+''.join('<td>'+html.escape(''if v is None else str(v))+'</td>'for v in row)+'</tr>'for row in rows)+'</table>'
changes=[]
for n,x in enumerate(d['operations'],7):
 for c,v in x['cells'].items():
  if c in identity:continue
  key=raw['headers'][column_index_from_string(c)-1][1]
  if c in copycols:assert x['before'][c]==rb[x['sku']].get(key)
  changes.append([n,x['sku'],x['asin'],c,x['before'][c],v])
body='<h1>第04批事故外商品修复</h1><p>2026-11-01。本文件尚未上传。</p>'
body+=('<p>清理商品要点，并仅加入独立复核白名单中的'+str(len(d['pricing']))+'条价格操作。未获批价格、运费、库存和家族字段不写入。</p>' if d['pricing'] else '<p>仅清理商品要点；所有售价、促销价、企业价、数量阶梯、促销日期、运费、库存及家族字段均未填写。本版不会通过价格字段造成v1那样的降价，不能等同于原促销方案已执行。</p>')
body+=table(['SKU数','ASIN数','第5要点','全部5点'],[[len(found),check['asins'],d['stats']['bullet5_rows'],d['stats']['full_bullet_rows']]])
if d['pricing']:
 body+='<h2>16条限时促销及企业数量优惠</h2><p>普通售价不覆盖。限时价日期为2026-11-01至2026-11-30（结束日00:00，覆盖至11月29日）；企业价和企业数量阶梯没有同一自动结束日期，将持续保留到另行修改。企业数量折扣按企业价计算，表中的累计折扣相对原普通价。</p>'
 body+=table(['SKU','原普通价USD','限时价USD','限时降幅','企业价USD','数量阶梯','最低企业单价USD','最大累计企业折扣','费用后现金USD'],[[x['sku'],x['ordinary_base'],x['sale_new'],str(x['sale_drop_percent'])+'%',x['business_price'],'；'.join(str(q)+'件减'+str(p)+'%'for q,p in x['business_tiers']),x['minimum_business_unit_price'],str(x['maximum_cumulative_business_discount_percent'])+'%',x['maximum_stack_cash']]for x in d['pricing']])
 body+='<p>费用后现金按最深企业阶梯价、15%估算销售佣金和当前FBA费计算，未扣采购、头程、仓储、广告、退货。已核对这16个ASIN不与当前两组Coupon重叠；当前促销总览与品牌定制页面未见其他运行中的叠加活动。后续新建优惠仍需重新核算。</p>'
body+='<p>使用原分类报告的Partial Update模板，544列、表头、其他工作表和宏保留。上传后仍需下载处理回执及检查页面显示。4013已在线提交的五点和事故相关ASIN已排除；原任务与待核价格没有删除。</p>'
body+='<h2>逐字段修改前后</h2>'+table(['行','SKU','ASIN','字段','修改前','修改后'],changes)
body+='<h2>本批排除项</h2>'+table(['SKU','ASIN','原因'],[[x['sku'],x['asin'],x['reason']]for x in d['excluded']])
body+='<h2>价格方案处理</h2>'
if d['pricing']:
 body+=table(['SKU','ASIN','获批字段','审核依据'],[[x['sku'],x['asin'],json.dumps(x['allowed_price_cells'],ensure_ascii=False),json.dumps(x.get('evidence',x),ensure_ascii=False)]for x in d['pricing']])
 body+='<p>未列入白名单的原草案价格方案继续暂缓，不以Excel单元格直接覆盖现有报价。划线展示仍需买家页面回读，上传接收不等于展示生效。</p>'
else:body+='<p>原草案的全部29条价格操作暂不进入本文件，包括限时价、企业价和阶梯。因FBA包邮基准、运费口径、降幅或叠加尚待逐行确认，不以Excel单元格直接覆盖现有报价。可以先上传本文件处理明确的文案错误，促销另行审核交付。</p>'
style='body{font:15px/1.6 Arial,"Microsoft YaHei",sans-serif;max-width:1500px;margin:30px auto;padding:0 24px;color:#243047}table{border-collapse:collapse;width:100%;font-size:12px}th,td{padding:9px;border:1px solid #d9e0e8;vertical-align:top;overflow-wrap:anywhere}th{background:#243b5a;color:white}tr:nth-child(even){background:#f5f7fb}'
(O/'04-事故外商品改动说明.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>第04批事故外商品修复</title><style>'+style+'</style>'+body+'</html>',encoding='utf8')
print(json.dumps(check,ensure_ascii=False))
