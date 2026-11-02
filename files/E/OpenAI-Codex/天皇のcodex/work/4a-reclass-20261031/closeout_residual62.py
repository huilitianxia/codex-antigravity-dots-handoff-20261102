import csv,json,re,collections,datetime
from pathlib import Path
P=Path(__file__).parent
final=json.loads((P/'12-final-processing-summary.json').read_text(encoding='utf8'))
receipt=json.loads((P/'12-processing-receipt-audit.json').read_text(encoding='utf8'))
catalog={r['seller-sku']:r for r in csv.DictReader(Path('D:/下载文件/所有商品报告_11-01-2026.txt').open(encoding='utf-8-sig'),delimiter='\t')}
base=json.loads((P/'analysis.json').read_text(encoding='utf8'))
fees=json.loads((P/'fba-live-fees.json').read_text(encoding='utf8'))
fba={r['fnsku']:dict(r,skus=list(r['skus']),source='2026-10-30 FBA inventory')for r in base['fba_unique']if r.get('market')=='US'}
for r in fees:
 fn=r.get('fnsku') or next((k for k,v in fba.items()if r['sku']in v['skus']),r['sku'])
 old=fba.get(fn,{})
 fba[fn]={**old,'fnsku':fn,'asin':r['asin'],'skus':list(set(old.get('skus',[])+[r['sku']])),'available':r['available'],'source':'2026-11-01 02:46 seller FBA scan'}
def qty(v):
 try:return float(v)
 except (ValueError,TypeError):return None
byasin=collections.defaultdict(list)
for r in catalog.values():byasin[r['asin1']].append(r)
def stock(asin,sku):
 exact=[v for v in fba.values()if sku in v.get('skus',[])and v['asin']==asin]
 shared=[v for v in fba.values()if v['asin']==asin]
 exact_qty=sum(qty(v['available'])or 0 for v in exact) if exact else None
 shared_qty=sum(qty(v['available'])or 0 for v in shared) if shared else None
 c=catalog.get(sku,{})
 mfn=qty(c.get('quantity'))if c.get('fulfillment-channel')=='DEFAULT'else None
 active_mfn=[{'sku':v['seller-sku'],'declared_quantity':qty(v['quantity'])}for v in byasin[asin]if v['fulfillment-channel']=='DEFAULT'and v['status']=='Active'and(qty(v['quantity'])or 0)>0]
 active_fba_alias=[v['seller-sku']for v in byasin[asin]if v['fulfillment-channel']=='AMAZON_NA'and v['status']=='Active']
 if (exact_qty or 0)>0:group='有货FBA：错误同SKU'
 elif (shared_qty or 0)>0:group='同ASIN其他FBA有货'
 elif active_mfn:group='仅MFN有申报库存'
 elif shared_qty==0 and not active_mfn:group='无可售库存或零库存草稿（已有快照）'
 elif byasin[asin] and all(v.get('fulfillment-channel')=='DEFAULT'and qty(v.get('quantity'))==0 for v in byasin[asin]):group='无可售库存或零库存草稿（已有快照）'
 elif (mfn or 0)>0:group='MFN有申报数量但非在售'
 else:group='库存未知或未证实存在'
 return {'inventory_group':group,'exact_sku_present_in_11_01_report':bool(c),'listing_status':c.get('status'),'offer_channel':c.get('fulfillment-channel'),'exact_fba_available':exact_qty,'same_asin_fba_available':shared_qty,'fba_sources':sorted({v['source']for v in shared}),'exact_mfn_declared_quantity':mfn,'active_mfn_aliases':active_mfn,'active_fba_aliases':active_fba_alias,'all_catalog_aliases':[{'sku':v['seller-sku'],'status':v['status'],'channel':v['fulfillment-channel']}for v in byasin[asin]]}
orders=list(csv.DictReader(Path('D:/下载文件/175793876516020757.txt').open(encoding='utf-8-sig'),delimiter='\t'))
usable=[r for r in orders if r['ship-country']=='US'and r['currency']=='USD']
def order_stats(asin,sku=None):
 selected=[r for r in usable if r['asin']==asin and(sku is None or r['sku']==sku)]
 cancelled=[r for r in selected if r['order-status']=='Cancelled'or r['item-status']=='Cancelled']
 pending=[r for r in selected if r not in cancelled and r['order-status']=='Pending']
 effective=[r for r in selected if r not in cancelled and r not in pending and int(r['quantity']or 0)>0]
 dates=[r['purchase-date']for r in effective]
 return {'valid_nonpending_orders':len({r['amazon-order-id']for r in effective}),'units':sum(int(r['quantity']or 0)for r in effective),'gross_item_usd':round(sum(float(r['item-price']or 0)for r in effective),2),'pending_orders':len({r['amazon-order-id']for r in pending}),'cancelled_orders':len({r['amazon-order-id']for r in cancelled}),'latest_valid_purchase':max(dates)if dates else None}
errors=collections.defaultdict(list)
for x in receipt['sku_errors']:errors[x['count_or_sku']].append(x)
targets=[r for r in final['rows']if r['primary_bucket']in['目录属性冲突待核','SKU或ASIN不存在或不能匹配']]
assert len(targets)==62
rows=[]
for r in targets:
 es=errors[r['sku']];fields=set()
 for e in es:
  if e['code']=='8541':
   fields.update(re.findall(r"(?:conflict with Amazon catalog value\(s\):|contradict.*?:) '([a-z_]+)'",e['message']))
   if '{color.standardized_values,color.value}'in e['message']:fields.add('color')
  if e['code']=='99022':fields.add('color')
 if r['primary_bucket'].startswith('SKU'):fields.add('SKU/ASIN/UPC mapping')
 if not fields:fields.add('catalog identity (see exact error)')
 actions=[]
 if 'SKU/ASIN/UPC mapping'in fields:actions.append('先核精确SKU空格与别名、原UPC和现存ASIN；报告有记录不代表处理器可用。不要删除重建、猜ASIN或迁移库存。')
 if 'color'in fields:actions.append('用实物/包装图、颜色或图案和UPC核对目录；只在确为同货且目录正确时修color，否则提供证据申诉。')
 if 'manufacturer'in fields:actions.append('核包装制造商名称、供应商发票或品牌证明；不能把China当制造商，也不能为通过校验盲写4A公司名。')
 if 'standard_product_id'in fields:actions.append('核实实物UPC/GTIN与正确型号及装量，查原始SKU到ASIN对应；不猜条码、不把当前目录ASIN照抄为正确货号。')
 if 'item_classification'in fields:actions.append('涉及base_product/目录分类与父子身份；先核商品身份，父子关系调整按家族暂缓。')
 if any(c in r['all_codes']for c in['100899','100893','8801','8047','8066','8603']):actions.append('伴随家族错误，相关父子/颜色尺寸组合本轮暂缓。')
 rows.append({**r,**stock(r['asin'],r['sku']),'conflicting_fields':sorted(fields),'same_asin_order_snapshot':order_stats(r['asin']),'exact_sku_order_snapshot':order_stats(r['asin'],r['sku']),'safe_next_steps':actions,'physical_evidence_needed':bool(fields&{'color','manufacturer','item_classification','standard_product_id','SKU/ASIN/UPC mapping'}),'fields_not_written_by_12':sorted(fields),'errors':es})
priority={'有货FBA：错误同SKU':0,'同ASIN其他FBA有货':1,'仅MFN有申报库存':2,'MFN有申报数量但非在售':3,'无可售库存或零库存草稿（已有快照）':4,'库存未知或未证实存在':5}
rows.sort(key=lambda r:(priority[r['inventory_group']],-(r['same_asin_fba_available']or 0),-r['same_asin_order_snapshot']['units'],r['sku']))
compliance=[
 {'asin':'B0822QC8Z2','name':'CR012','blocked_by':'冻结面板要求ps_toys_dv_us真实合规文件，当前已有证据为非在售。','evidence':['cr012-freeze-reason.txt:998-1004','v4-receipt-repair-plan.json (100390/100477)'],'prepare':['与实际商品及ASIN对应的型号、包装/标签照片、制造商身份信息','已存在且真实的检测或合规文件；具体文档类别以对应合规入口的请求为准，现有证据未列全清单'],'do_not':'不以改标题代替合规文件，不生成或编造检测证书。'},
 {'asin':'B01N0R4QI8','name':'305Y','blocked_by':'12回执18370：Trademark on Product Detail Page；4A 305x6-Y另有13013。','evidence':['12-processing-receipt-audit.json','root-final-305y.txt'],'prepare':['原始商品/包装照片与品牌、型号、UPC对应证据','若已有，商标权属、授权或供应链来源凭证','对应绩效/侵权通知全文，确认被指向的商标和具体内容；现有回执未给权利人明细'],'do_not':'不直接认定侵权成立，不代写/提交申诉，不猜测权利人或授权。'},
 {'asin':'B01MEBRJQE','name':'024','blocked_by':'12回执100227版权提示、19083商品商标提示、19084其他限制；两SKU共用同ASIN。','evidence':['12-processing-receipt-audit.json','cr012-freeze-reason.txt (同列表024非在售记录)'],'prepare':['原始商品/包装照片、原图/图案设计来源或授权证明','品牌/商标授权及采购凭证（如确有）','版权/商标绩效通知全文与对应被投诉内容，逐项区分处理'],'do_not':'不通过换SKU/换页绕开限制，不提交未经核实的权属声明。'}]
for r in compliance:r['catalog_offers']=byasin[r['asin']];r['stock_snapshot']=stock(r['asin'],byasin[r['asin']][0]['seller-sku']if byasin[r['asin']]else'');r['orders_snapshot']=order_stats(r['asin'])
out={'scope':'Only 62 residual rows (39 catalog conflicts + 23 mapping failures); read-only offline reconciliation, no live changes.','inventory_sources':['11/1 11:43 all-listings report: exact SKU/ASIN/status/MFN quantity','11/1 02:46 FBA seller scan overrides matching FNSKU','10/30 FBA inventory fills other FNSKU; deduplicated'],'order_source':'175793876516020757.txt downloaded10/31; US country + USD; cancelled and pending separated; not a current live order scan','order_purchase_range':[min(r['purchase-date']for r in orders),max(r['purchase-date']for r in orders)],'inventory_groups':dict(collections.Counter(r['inventory_group']for r in rows)),'exact_skus_absent_from_latest_report':sum(not r['exact_sku_present_in_11_01_report']for r in rows),'group_note':'Same-ASIN FBA stock can belong to another SKU. MFN quantities are seller-declared and are not warehouse counts. Mapping error is not proof that the report row was deleted.','rows':rows,'compliance_blockers':compliance,'root_exclusive_untouched':['4A 0146 recommended uses','4A 6035x2 unit count']}
(P/'residual62-closeout.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
lines=['12剩余问题收尾清单（只读，未提交任何新更改）','',
'本清单仅覆盖39条目录冲突与23条SKU/ASIN匹配问题，不把99条OTHER ERROR当成99条新增失败。',
'库存依据：11/1 02:46 FBA页面扫描，未覆盖FNSKU回退10/30库存；精确SKU/ASIN/状态与MFN申报数取11/1 11:43全商品报告。订单取10/31导出，US/USD、有效/待付款/取消分开；不是截至此刻的实时销量。','',
'优先级：4条错误SKU自身FBA有货（合计22件）；1条错误SKU同ASIN另一FBA有2件；16条仅有同ASIN MFN申报库存；41条无可售库存或零库存草稿。',
'23条“不能匹配”全部是Incomplete、MFN申报0；62条在11/1报告中均仍有精确SKU记录。确认已不存在=0，不能仅凭回执删除或重建。','',
'先核这5条有FBA库存的商品：']
for r in rows:
 if priority[r['inventory_group']]<=1:
  amount=f"本SKU {r['exact_fba_available']:g}件"if r['exact_fba_available']else f"同ASIN另SKU {','.join(r['active_fba_aliases'])} 共{r['same_asin_fba_available']:g}件"
  sales=r['same_asin_order_snapshot']
  lines.append(f"- {r['sku']} / {r['asin']}：{amount}；字段{','.join(r['conflicting_fields'])}；历史导出有效{sales['valid_nonpending_orders']}单/{sales['units']}件。")
lines+=['','按字段处理：',
'- 20条color冲突：先看实物/包装、实际颜色/图案、UPC。目录正确且确为同货才纠正卖家值；目录错误则备证据，不盲目跟目录。',
'- 13条item_classification：涉及base_product、目录身份或父子；列入家族暂缓，当前不改父子关系。',
'- 3条manufacturer：核包装/发票中的真实制造商；不能以China或未经证明的公司名称填值过检。',
'- 3条standard_product_id：先核条码、实际型号与装量、原SKU映射，不猜ASIN/UPC。',
'- 23条不能匹配的零库存草稿：先留证及核历史条码/别名；不占有货FBA优先队列，不删除重建。','',
'三项真实资料阻塞：',
'- CR012 / B0822QC8Z2：冻结面板要求ps_toys_dv_us相关文件。准备与实物型号/ASIN对应的包装标签、制造商信息及已有真实检测/合规材料；具体文件类别现有证据未列全，须以对应入口请求为准。改文案不能替代文件。',
'- 305Y / B01N0R4QI8：18370详情页商标提示。准备完整侵权/绩效通知、被指向内容、实物/包装/UPC、真实商标授权或来源凭证（若确有）；现有回执未给权利人明细，不代写权属声明。',
'- 024 / B01MEBRJQE：100227版权、19083商品商标、19084限制。准备通知全文、被投诉图文或图案的原始来源/授权、实物包装及采购来源，分别核版权与商标，不以换SKU绕过。','',
'0146推荐用途与6035x2枚举由主线程独占，本清单未操作。逐SKU证据与安全下一步保存在residual62-closeout.json。']
(P/'residual-closeout-brief.txt').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps({k:v for k,v in out.items()if k not in['rows','compliance_blockers']},ensure_ascii=False,indent=2))
print('FBA PRIORITY')
for r in rows:
 if priority[r['inventory_group']]<=1:print(r['sku'],r['asin'],r['inventory_group'],r['exact_fba_available'],r['same_asin_fba_available'],r['conflicting_fields'],r['same_asin_order_snapshot'])
