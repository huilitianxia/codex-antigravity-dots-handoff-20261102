import json,re,hashlib
from pathlib import Path
from collections import Counter
import openpyxl
P=Path(__file__).parent
receipt=Path('D:/下载文件/04-reviewed-nonincident-fixes-processing-summary (2).xlsm')
upload=Path('outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/04-reviewed-nonincident-fixes.xlsm')
source=Path('D:/下载文件/分类商品报告_10-31-2026.xlsm')
def read(p,sku_col):
 w=openpyxl.load_workbook(p,data_only=False);s=w['Template'];h={i:s.cell(5,i).value for i in range(1,s.max_column+1)}
 return s,h,{str(s.cell(r,sku_col).value):{h[c]:s.cell(r,c).value for c in h if h[c]} for r in range(7,s.max_row+1) if s.cell(r,sku_col).value}
rs,rh,rr=read(receipt,4);us,uh,ur=read(upload,3);ss,sh,sr=read(source,3)
old=json.loads((P/'v4-processing-receipt-audit.json').read_text(encoding='utf8'))
oldmap={}
for x in old['errors']:oldmap.setdefault((x['sku_or_count'],re.search(r'\(([A-Z]+\d+)\)',x['field']).group(1)),[]).append(x)
def prefix(row,p):return {k:v for k,v in row.items() if k.startswith(p)}
records=[];counts=Counter();unmatched=[]
for rn in range(7,rs.max_row+1):
 sku=rs.cell(rn,4).value
 if not sku:continue
 before=sr.get(sku,{});sent={k:v for k,v in ur[sku].items() if v not in (None,'')};issues=[]
 matches=[]
 for c in rs[rn]:
  if not c.comment or c.column==1:continue
  msg=c.comment.text.replace('_x000d_','').strip();oms=oldmap.get((sku,c.coordinate),[])
  found=[om for om in oms if om['message'] in msg]
  if not found:unmatched.append((sku,c.coordinate,msg))
  matches.extend((c,om,msg) for om in found)
 for c,om,msg in matches:
  code=om['code'];counts[code]+=1;key=rh[c.column];family=key.split('[')[0].split('#')[0]
  cause='preexisting_unsent_attribute';action='manual_identity_review';detail=''
  if code=='100476':
   action='delete_only_optional_title_differentiation';detail='v4未写item_name/title_differentiation；源表已有highlight，空白Partial Update未执行删除。优先按选择器删除可选highlight，保留长标题。不得批量缩97标题。'
  elif code=='8541':
   action='verify_identity_then_correct_conflicting_attribute';detail='v4未写颜色/制造商；历史贡献与目录冲突。逐ASIN核实真实产品、颜色/图案及制造商，再用匹配目录的真实值或申诉。不能无条件照抄目录值。'
  elif code=='99300':
   action='replace_complete_five_bullets_with_factual_copy';cause='touched_bullet_array_with_legacy_other_members';detail='回执AT是第一条bullet；v4只改第五条，整组校验仍被旧条目触发。需要核五条完整数组，不重复只改第五条。'
  elif code=='18155':
   action='verify_latest_price_floor_repair';cause='introduced_price_floor_inconsistency';detail='本批最低价20.39未覆盖企业基础19.99及最深19.19，为本次联动遗漏。主代理已处理19.19，先读取实际结果，不再次覆盖。'
  elif code=='13013':
   action='verify_exact_sku_exists_do_not_recreate';detail='确切SKU不存在/已删除警告，本次写入不能以SUCCESS行状态推断生效；先核精确空格SKU，不自动重建。'
  elif code in ['100390','100477']:
   action='genuine_compliance_documents_required';detail='需真实合规资料或政策判断，改文案不能替代审核。'
  elif code in ['100893','100899','8801']:
   action='verify_real_variation_identity_then_repair';detail='父子关系/必填变体字段/重复组合的旧问题；须按真实尺寸颜色装量核实全家族后处理，不编造区分值。'
  elif code=='100095':
   action='replace_invalid_enumeration_after_schema_check';detail='旧推荐用途值办公室无效；先查该productType有效值，若Office有效才替换；不能直接按中文翻译猜枚举。'
  elif code=='100720':
   action='verify_language_tag_and_real_brand_manufacturer';detail='美国站品牌/制造商语言数据无效；核en_US语种及真实权属，禁止把国家China当制造商或为过检乱改品牌。'
  elif code=='100470':
   action='repair_repeated_title_words_after_live_readback';detail='旧标题词重复；仅去重复保留事实，不顺带重写全店标题。源标题已不复现重复的，先查当前贡献及目录值。'
  elif code=='101265':
   action='no_repair_required_sales_forecast_notice';cause='informational_suggestion_not_failure';detail='这是模型预测转FBA销售额的建议，不是错误，不授权转换履约。'
  issues.append(dict(code=code,severity=om['severity'],receipt_cell=c.coordinate,semantic_key=key,message=om['message'],classification=cause,action=action,detail=detail,field_written_in_v4=key in sent))
 proposed=[]
 if any(i['code']=='100476' for i in issues):proposed.append(dict(attribute='title_differentiation',operation='selector_scoped_delete',marketplace_id='ATVPDKIKX0DER',language_tag='en_US',reason='源highlight为ASIN等无效摘要；优先移除可选highlight，不批量缩原标题',precondition='读取当前贡献并核对productType schema和可用授权连接'))
 records.append(dict(sku=sku,asin=next((v for k,v in sent.items() if k=='amzn1.volt.ca.product_id_value'),None),status=rs.cell(rn,1).value,sent_fields=sent,source_title=prefix(before,'item_name'),source_highlight=prefix(before,'title_differentiation'),source_bullets=prefix(before,'bullet_point'),source_color=prefix(before,'color['),source_manufacturer=prefix(before,'manufacturer'),issues=issues,proposed_changes=proposed,verification='回执表明提交已处理；不等同买家页面/全部字段生效。需后续逐字段回读。'))
assert len(records)==146
out=dict(receipt=str(receipt),upload=str(upload),source=str(source),sha256_frozen_upload=hashlib.sha256(upload.read_bytes()).hexdigest(),summary=dict(rows=len(records),statuses=dict(Counter(r['status'] for r in records)),issue_occurrences=dict(counts),unmatched_comments=unmatched),attribute_delete_method=dict(attribute='title_differentiation',not_item_highlight='模板Item Highlight的API属性是title_differentiation',official_docs=['https://developer-docs.amazon/sp-api/docs/submit-modular-titles','https://developer-docs.amazon/sp-api/docs/partially-update-a-listing','https://developer-docs.amazon/sp-api/reference/patchlistingsitem'],draft_patch={'op':'delete','path':'/attributes/title_differentiation','value':[{'marketplace_id':'ATVPDKIKX0DER','language_tag':'en_US'}]},conditions='仅卖家现存SKU；先取现有属性与对应productType schema验证selectors；需已授权SP-API Product Listing连接，当前未确认可用。此处不执行，不以SKU Delete/整行删除替代；未证实XLSM通用delete单元格语法，不能把价格模板delete规则套用highlight。'),records=records)
drafts={
'4A 189':['Lined sticky note pads for written notes and lists.','Each note measures 6 x 8 inches.','Assorted bright colors help separate notes by topic.','Use the notes for reminders at home, school or the office.','Write tasks, messages and meeting notes on the lined paper.'],
'4A001':['Small sticky note pads for brief notes and reminders.','Each note measures 1.5 x 2 inches.','Adhesive is positioned along the shorter edge.','Use the notes to label tasks and organize written reminders.','Compact notes for use at a desk, study area or workstation.'],
'4A078':['Red sticky note paper in a roll format.','The roll measures 2 inches wide and 315 inches long.','Cut sections to suit the length of your notes.','Writable paper for reminders, lists and page marking.','Keep the roll at a desk or study area for everyday note taking.']}
for r in records:
 if r['sku'] in drafts:r['proposed_changes'].append(dict(attribute='bullet_point',operation='replace_all_five',draft=drafts[r['sku']],precondition='先核当前页面与源尺寸/形态一致；189与001装量身份待核，不写3包600张或25包30000张；不改变颜色制造商价格',unverified_claims_removed=['recyclable','holds longer and stronger than original','no residue','high quality/good price','free shipping']))
 if r['sku']=='4A Meeting-51':r['proposed_changes'].append(dict(attribute='item_name',operation='replace_after_current_readback',draft='4A Tabletop Easel Pad and Dry Erase Board, 20 x 23 in, 20 Sheets',basis='源表已有尺寸/20张/2合1桌面支架事实，去掉重复pad及premium等修饰'))
 if r['sku']=='4A SCPOPUP303':r['proposed_changes'].append(dict(attribute='item_name',operation='hold_until_current_readback',reason='源表标题只出现一次4A，不能依据旧报错重复改同一标题；另item_classification冲突需查商品身份'))
out['summary']['unique_skus_by_code']={k:len({r['sku'] for r in records if any(i['code']==k for i in r['issues'])}) for k in counts}
out['summary']['effect_on_v4']='20 SUCCESS无回执列出错误；126 OTHER ERROR仍为已应用变更并有其他错误。具体上架展示与字段生效需回读；13013与18155须专项核验。'
(P/'v4-receipt-repair-plan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
lines=['V4回执逐SKU修复准备（只读，未修改线上与冻结上传文件）',json.dumps(out['summary'],ensure_ascii=False,indent=2),'','97 Item Highlight属性名title_differentiation；当前连接未验证可执行SP-API，不承诺可直接批量删。官方方法与selector草案见JSON。','27条8541是错误出现次数，涉及26个SKU，其中NRGrid同一冲突重复。','3条bullet仅改第五不充分，建议安全五条文案见下；装量与颜色冲突单独保留。','']
for r in records:
 lines.append(f"{r['sku']} | {r['asin']} | {r['status']} | codes={','.join(i['code'] for i in r['issues']) or 'none'}")
 for i in r['issues']:lines.append('  '+i['code']+' '+i['action']+'：'+i['detail'])
 for v in r['proposed_changes']:lines.append('  具体准备：'+json.dumps(v,ensure_ascii=False))
lines+=['','官方依据：']+out['attribute_delete_method']['official_docs']
(P/'v4-receipt-repair-plan.txt').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps(out['summary'],ensure_ascii=False))
for r in records:
 if any(i['code']=='99300' for i in r['issues']):print(json.dumps(r,ensure_ascii=False,indent=2))
