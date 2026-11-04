import json,re,zipfile,hashlib,html,copy,sys
from pathlib import Path
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.utils import column_index_from_string,get_column_letter
root=Path(__file__).parent
out=Path('E:/OpenAI-Codex/天皇のcodex/outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes')
out.mkdir(parents=True,exist_ok=True)
consolidated='--consolidated' in sys.argv
d=json.loads((root/('consolidated-repairs-data.json' if consolidated else 'urgent-batches-data.json')).read_text(encoding='utf8'))
raw=json.loads((root/'category-report-raw.json').read_text(encoding='utf8'))
rb={x['contribution_sku#1.value']:x for x in raw['rows']}
checks=[]
specs=[('operations','03-catalog-errors-consolidated','D:/下载文件/分类商品报告_10-31-2026.xlsm')] if consolidated else [('price_updates','01-price-title-fixes','D:/下载文件/分类商品报告_10-31-2026.xlsm'),('restore','02-restore-original-skus','D:/下载文件/restore-batch-01-New_Version.xlsm')]
for key,stem,src in specs:
 aw=openpyxl.load_workbook(root/(stem+'-cells.xlsx'),read_only=True,data_only=True)['Template']
 with zipfile.ZipFile(src) as z:
  sheet='xl/worksheets/sheet5.xml';xml=z.read(sheet).decode('utf8')
  sd=re.search(r'<sheetData>(.*?)</sheetData>',xml,re.S);assert sd
  oldrows=re.findall(r'<row\b[^>]*\br="(\d+)"[^>]*(?:/>|>.*?</row>)',sd[1],re.S)
  keep=[];style={}
  for row in re.findall(r'<row\b[^>]*(?:/>|>.*?</row>)',sd[1],re.S):
   n=int(re.search(r'\br="(\d+)"',row)[1])
   if n<7:keep.append(row)
   if n==7:
    for c in re.findall(r'<c\b[^>]*(?:/>|>.*?</c>)',row,re.S):
     col=re.search(r'\br="([A-Z]+)\d+"',c)[1];s=re.search(r'\bs="(\d+)"',c)
     if s:style[col]=s[1]
  newrows=[]
  for n,op in enumerate(d[key],7):
   cells=[]
   for col,expected in sorted(op['cells'].items(),key=lambda kv:column_index_from_string(kv[0])):
    v=aw[f'{col}{n}'].value;assert v==expected,(col,n,v,expected)
    attrs=f' r="{col}{n}"'+(f' s="{style[col]}"' if col in style else '')
    if isinstance(v,(int,float)):cell=f'<c{attrs}><v>{v}</v></c>'
    else:cell=f'<c{attrs} t="inlineStr"><is><t xml:space="preserve">{escape(str(v))}</t></is></c>'
    cells.append(cell)
   newrows.append(f'<row r="{n}">'+''.join(cells)+'</row>')
  xml=xml[:sd.start(1)]+''.join(keep+newrows)+xml[sd.end(1):]
  xml=re.sub(r'(<dimension\b[^>]*\bref="[A-Z]+\d+:[A-Z]+)(\d+)(")',lambda m:m[1]+str(max(int(m[2]),len(d[key])+6))+m[3],xml,count=1)
  dest=out/(stem+'.xlsm')
  with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as o:
   for part in z.infolist():o.writestr(copy.copy(part),xml.encode('utf8') if part.filename==sheet else z.read(part.filename))
  with zipfile.ZipFile(dest) as t:changed=[n for n in z.namelist() if z.read(n)!=t.read(n)]
  assert changed==[sheet]
 ow=openpyxl.load_workbook(src,read_only=True,data_only=False)
 nw=openpyxl.load_workbook(dest,read_only=True,data_only=False)
 for a,b in zip(ow['Template'].iter_rows(max_row=6,values_only=True),nw['Template'].iter_rows(max_row=6,values_only=True)):assert a==b
 found=[]
 for n,row in enumerate(nw['Template'].iter_rows(min_row=7,values_only=True),7):
  actual={get_column_letter(i):v for i,v in enumerate(row,1) if v is not None}
  if actual:found.append(actual)
 assert found==[x['cells'] for x in d[key]]
 checks.append({'file':str(dest),'rows':len(found),'only_changed_zip_part':sheet,'headers_macros_and_other_sheets_preserved':True,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
(root/('consolidated-package-verification.json' if consolidated else 'urgent-package-verification.json')).write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')

def table(headers,rows):
 return '<table><thead><tr>'+''.join('<th>'+html.escape(str(h))+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape('—' if v is None else str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</tbody></table>'
if consolidated:
 # This batch must never override quantities, prices, fulfillment, or relationships.
 allowed={'C','D','E','I','J','L','M','T','BG'}
 assert all(set(x['cells']) <= allowed for x in d['operations'])
 assert len({x['sku'] for x in d['operations']}) == len(d['operations'])
 assert all(len(x['cells']['I']) <= 75 and len(x['cells']['J']) <= 80 for x in d['operations'])
 assert all(x['asin'] not in d['stats']['ui_reserved_asins'] for x in d['operations'])
 changed=[]
 for n,x in enumerate(d['operations'],7):
  for c,v in x['cells'].items():
   if c in {'C','D','E','L','M'}:continue
   label,key=raw['headers'][column_index_from_string(c)-1]
   changed.append([n,x['sku'],x['asin'],label,x['before'].get(c),v,'；'.join(x['sources'])])
 body='<h1>164条商品信息集中修复</h1><p>2026-10-31。供用户上传的文件；尚未上传。使用Amazon原始分类商品模板，保留宏、说明、验证和其他工作表。</p>'
 body+='<h2>本次提交范围</h2>'+table(['SKU数','ASIN数','标题及亮点','颜色','制造商'],[[d['stats']['rows'],d['stats']['asins'],d['stats']['title_rows'],d['stats']['color_rows'],d['stats']['manufacturer_rows']]])
 body+='<p>本批集中处理上一批回执明确的100476标题/亮点错误及8541目录冲突，并把同一ASIN的对应SKU统一。标题不超过75字符；装量、尺寸和功能依据同ASIN原始描述。颜色和制造商使用回执明确给出的Amazon美国站目录值。各字段计数可重叠。</p>'
 body+='<p>价格、企业价格、库存数量、FBA/FBM履约方式、配送模板和父子关系不在本批写入字段中。之前已经接受的价格不重复上传。六个正在或已经通过Chrome处理的ASIN已排除，避免同字段重叠。</p>'
 body+='<h2>如何上传</h2><p>上传 03-catalog-errors-consolidated.xlsm 到商品批量上传入口，提交后查看处理状态并下载处理报告。后台接收成功不等于所有目录字段已经显示；完成后按回执和页面回读核验。</p>'
 body+='<h2>逐字段修改前后</h2>'+table(['上传行','SKU','ASIN','字段','原值','新值','依据'],changed)
 body+='<h2>需要单独处理的事项</h2>'+table(['事项','当前状态'],[
  ['原FBA滞留库存','实时页面0件商品、无筛选；此前恢复批次已起效。'],
  ['303抽取式','售价10.99已生效；启售由Chrome继续处理，本批排除。'],
  ['重复页与双报价','同ASIN保持FBA/FBM各自SKU；不同ASIN只有完全同款才申请目录合并，实际库存不迁移。'],
  ['家族重组','全店归类和真实多包装仍需核实；本批没有修改父子关系，不能把本批称为全店家族已修复。'],
  ['PSS 9-5 Refill','重复变体100899需要家族关系处理，普通标题修改不保证解除。'],
  ['305黄色六本装 / CR012 / 60122','商标、真实合规文件或目录标题限制仍需单独核查。'],
  ['四款新运费','模板费率与SKU分配已确认；实际买家运费同步仍需回读。']])
 geo=json.loads((root/'order-timezone-summary.json').read_text(encoding='utf8'))
 body+='<h2>近30天买家地域</h2><p>美国、USD、非取消订单：668个订单、686条商品明细，商品金额13,965.30美元。包含仍待处理的订单，不扣退款，不含运费和税。全部686条邮编已匹配；邮编对应时区是地域估计，不是精确到住宅边界的地理定位。</p>'
 body+=table(['地区','订单数','订单占比','商品金额USD','金额占比'],[[x['region'],x['orders'],f"{x['order_share']:.1%}",f"{x['item_amount']:,.2f}",f"{x['amount_share']:.1%}"]for x in geo['regions']])
 body+='<p>订单来源：用户提供的175793876516020757.txt。邮编时区来源：<a href="https://github.com/seanpianka/Zipcodes/blob/master/scripts/data/zip_code_database.csv">Zipcodes公开邮编数据</a>。订单在本机汇总，报告未包含客户身份或详细地址。</p>'
 style='body{font:15px/1.65 "Microsoft YaHei",Arial,sans-serif;color:#243047;max-width:1500px;margin:28px auto;padding:0 24px}h1{font-size:27px}h2{font-size:21px;margin-top:30px}table{border-collapse:collapse;width:100%;font-size:12px}th{background:#243b5a;color:#fff;text-align:left}td,th{padding:9px;border:1px solid #d9e0e8;vertical-align:top;overflow-wrap:anywhere}tr:nth-child(even){background:#f5f7fb}p{max-width:1150px}'
 (out/'03-集中修复改动说明.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>4A集中修复改动说明</title><style>'+style+'</style>'+body+'</html>',encoding='utf8')
 print(json.dumps({'files':checks,'modified_fields':len(changed),'protected_fields_untouched':True},ensure_ascii=False))
 sys.exit(0)
changes=[]
identity={'C','D','E','L','M'}
for n,x in enumerate(d['price_updates'],7):
 for col,new in x['cells'].items():
  if col in identity:continue
  label,key=raw['headers'][column_index_from_string(col)-1]
  changes.append([n,x['sku'],x['asin'],label,rb[x['sku']].get(key),new,'；'.join(x['reasons']),'；'.join(x['sources'])])
status='文件已生成并完成字段核对；尚未上传，后台尚未因本批次发生改动。'
body='<h1>4A 批量修复改动说明</h1><p>核查日期：2026-10-31。'+status+'</p>'
body+='<h2>本批次范围</h2>'+table(['文件','记录数','修改内容'],[['01-price-title-fixes.xlsm',106,'82条普通价、29条企业价、3条最低价、3条标题/亮点、1组企业数量优惠；计数可重叠'],['02-restore-original-skus.xlsm',9,'原SKU原ASIN重建FBA报价；对应10月30日库存快照298件，不写入库存数量']])
body+='<p>第一表使用 Partial Update。未填入的家族、品牌、图片、库存、配送模板和运费不在本批修改范围内。保留原模板及宏。第二表为原SKU报价恢复，不创建新ASIN，不迁移仓库实物。提交成功仍须复查可售状态。</p>'
body+='<p>企业阶梯特殊修正：PSS 9-3 2 Sets 原为5件减24.99%、30件减22.49%，属于越买单位价越高。改为5件减2%、30件减5%，基础企业价29.99改为23.99。此处为较小折扣方案，实际净利润仍缺仓储/发货成本核验。</p>'
body+='<h2>逐字段修改前后</h2>'+table(['上传行','SKU','ASIN','字段','原值','新值','原因','依据'],changes)
body+='<h2>原报价恢复</h2>'+table(['SKU','ASIN','恢复售价USD','10月30日可售件数','价格依据'],[[x['sku'],x['asin'],x['price'],x['units10_30'],x['basis']] for x in d['restore']])
body+='<h2>普通价暂缓修改</h2><p>以下仅暂停普通价覆盖；若企业价已高于现有效售价，仍可能在第一表中修正企业价。不能仅凭同ASIN把多包改成单包价。</p>'+table(['SKU','ASIN','当前价','Excel候选价','暂缓原因','当前描述','Excel描述'],[[x['sku'],x['asin'],x.get('current'),x.get('excel'),x['reason'],x.get('title'),x.get('source_title')] for x in d['price_holds']])
body+='<h2>仍须继续处理</h2>'+table(['项目','已核实情况','后续动作'],[
 ['滞留库存','11条、349件；4012和124418虽已被接受仍滞留','9条上传恢复；另2条核查关联与生效状态'],
 ['已停售但有FBM数量','7条合计1251件，包含858件303抽取式及271件60187','重新启售需核对实物装量和报价；整箱4A003暂缓'],
 ['BuyBox','14条因价格高不符合要求：12FBM、2FBA','售价和到手运费联合调整；不能保证调价立即获得BuyBox'],
 ['配送运费','默认4.99/单+4.99/磅；30315 Cube8.99/单','缺真实邮资、包装尺寸及拣货费，尚未调整运费'],
 ['搜索抑制/主图','1条标题过长；另5条明确主图问题','标题写入本批；图片需按真实产品重做或补图'],
 ['305x6-Y B01N0R4QI8','457件FBM填报库存，商标相关详情页移除','核查具体侵权位置；换图不保证解除'],
 ['CR012 B0822QC8Z2','140件FBM填报库存，玩具文件审核要求','本批修标题和亮点；仍需真实材料，不能生成虚假文件'],
 ['PSS95替芯','报价建立但颜色/尺寸组合重复错误100899','家族关系另批处理，本批不重建父子关系'],
 ['全部家族、包装优惠、清仓','全量804SKU报告、129有货FNSKU已纳入分析','最终家族映射、包装价比较、全部清仓策略尚未完成']])
body+='<h2>来源与核验范围</h2><p>普通属性及原值：分类商品报告_10-31-2026.xlsm，Template数据行7起。定价：用户2026总表，逐行见依据。库存快照：10月30日FBA报告；与10月31日实时后台的滞留页、已停售76条、缺报价98条、搜索抑制5条、详情页移除7条交叉检查。报告库存与实际仓库实盘不同，不将空白当作0。</p>'
document='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>4A批量修复改动说明</title><style>body{font:15px/1.6 "Microsoft YaHei",sans-serif;color:#243047;max-width:1600px;margin:30px auto;padding:0 24px}h1{font-size:28px}h2{margin-top:32px;font-size:22px}table{border-collapse:collapse;width:100%;font-size:12px}th{background:#243b5a;color:white;text-align:left}th,td{padding:10px;border:1px solid #d9e0e8;vertical-align:top;overflow-wrap:anywhere}tr:nth-child(even){background:#f4f7fa}p{max-width:1100px}</style>'+body+'</html>'
(out/'改动范围与逐项说明.html').write_text(document,encoding='utf8')
print(json.dumps(checks,ensure_ascii=False))
print('changed field entries',len(changes),'held price rows',len(d['price_holds']))
