import json,collections,datetime
from pathlib import Path
P=Path(__file__).parent
def load(n):return json.loads((P/n).read_text('utf-8-sig'))
audit=load('coupon-expansion-77-complete-readonly-audit.json')
demand=load('coupon77-demand-and-aged-fee-recheck.json')
f15=load('coupon15-final22-expected.json');f5=load('coupon5-12-final-review.json')
dec15={r['asin']:r for r in load('coupon15-demand-revised-decisions.json')['rows']}
dec5={r['asin']:r for r in load('coupon5-38-demand-final-review.json')['rows']}
original={r['asin']:r for r in load('coupon-original15-aged-demand-final-review.json')['rows']}
auditMap={r['asin']:r for r in audit['rows']};dm={r['asin']:r for r in demand['rows']}
final15=set(f15['expected_asins']);final5=set(f5['asins'])
live15=set(f15['live23_basis']['asins']);live5=set(load('coupon-expanded-execution-ledger.json')['existing5_before'])
f15rows={r['asin']:r for r in f15['rows']}
assert len(dm)==77 and set(dm)==set(auditMap)
assert len(final15)==22 and len(final5)==12 and not(final15&final5)
assert len(live15)==23 and len(live5)==4 and not(live15&live5)
def reason_list(v):return v if isinstance(v,list)else[v]if v else[]
def state_for(a):
 old=15 if a in live15 else 5 if a in live5 else None
 new=15 if a in final15 else 5 if a in final5 else None
 transition='KEEP_IN_EXISTING_COUPON'if old==new and new else'ADD_TO_COUPON'if new and old is None else'MOVE_COUPON_15_TO_5'if old==15 and new==5 else'REMOVE_FROM_COUPON'if old and new is None else'NO_COUPON_ADDITION'
 return {'last_verified_live_coupon_percent':old,'last_verified_live_basis':'Saved prior running23/4 campaign evidence; no new UI check in this ledger','planned_coupon_percent':new,'planned_change':transition,'planned_campaign_update_status':'UNSUBMITTED_DRAFT'if new or old else'NOT_PLANNED','final_campaign_live_verified':False}
def candidate(a):
 d=dm[a];ad=auditMap[a];r={'asin':a,'sku':d['sku'],'scope':'AUDITED_77','metrics':{k:d.get(k)for k in ['stock','orders29','units29','orders7','units7','asin_orders29','asin_units29','age181plus','age365plus','estimated_aged_surcharge','estimated_month_storage','months_cover','price','b2b','tiers']},**state_for(a)}
 if a in final15:
  r['decision_group']='PLANNED_COUPON_15'
  r['reasons']=reason_list(dec15.get(a,{}).get('reason'))or['最终15%名单保留；按已存库存、需求和超龄费压力审核。']
  r['decision_source']='coupon15-final22-expected.json'
 elif a in final5:
  r['decision_group']='PLANNED_COUPON_5'
  if a in dec5:r['reasons']=reason_list(dec5[a]['reason'])
  elif dec15.get(a,{}).get('decision')=='MOVE_TO_5':r['reasons']=reason_list(dec15[a]['reason'])
  else:r['reasons']=['最终审核将原15%候选调整为5%轻券；最终名单优先于早期KEEP_15建议。',f"库存{d['stock']}件，29日{d['orders29']}单/{d['units29']}件，预估超龄附加费{d.get('estimated_aged_surcharge')}美元/月。"]
  r['decision_source']='coupon5-12-final-review.json'
 elif a=='B00SMEFFRE':
  r['decision_group']='PROTECTED_STAR_KEEP_CURRENT'
  r['reasons']=['明星满胶商品；保留普通及现有企业方案，不叠加Coupon。',f"29日{d['orders29']}单/{d['units29']}件，近7日{d['orders7']}单，预估超龄附加费{d.get('estimated_aged_surcharge')}美元/月。"]
  r['decision_source']='coupon-expansion-77-complete-readonly-audit.json'
 elif ad.get('audit_decision')=='PARENT_REVIEW_LOW_STACKED_CASH':
  r['decision_group']='HOLD_DEEP_BUSINESS_NO_EXTRA_COUPON'
  r['reasons']=reason_list(ad.get('suggested_reason'))
  r['cash_estimates_are_not_profit']=True
  r['decision_source']='coupon-expansion-77-complete-readonly-audit.json'
 elif a in dec15:
  q=dec15[a];r['decision_group']='KEEP_EXISTING_BUSINESS_REMOVE_COUPON'if q['decision']=='REMOVE_15_KEEP_EXISTING_BUSINESS'else'HOLD_LOW_REMAINING_STOCK'
  r['reasons']=reason_list(q['reason']);r['decision_source']='coupon15-demand-revised-decisions.json'
 elif a in dec5:
  q=dec5[a]
  r['decision_group']='HOLD_AGED_SMALL_STOCK_EXCEPTION'if q['decision']=='REVIEW_AGED_EXCEPTION_DEFAULT_REMOVE'else'HOLD_LOW_REMAINING_STOCK'if q['fba_sellable']<20 else'KEEP_CURRENT_ONGOING_DEMAND'
  r['reasons']=reason_list(q['reason']);r['decision_source']='coupon5-38-demand-final-review.json'
 else:raise AssertionError('Unmapped '+a)
 r['all_reason_evidence_preserved']=True
 return r
rows=[candidate(r['asin'])for r in demand['rows']]
supplement=[]
for a in sorted((live15|live5|final15|final5)-set(dm)):
 src=f15rows.get(a,{});orig=original.get(a,{})
 reason=reason_list(orig.get('reason'))
 if a in final15 and orig.get('decision')=='REVIEW_HIGH_AIS_DEEP_BUSINESS_STACK':reason=['最终名单明确保留该深企业优惠例外，早期仅待审状态已由最终22名单覆盖。']+reason
 if a in live5:reason=['原已运行5%四款保留；本轮最终12名单未移除。']
 if a=='B07QWKYQV7':reason=['当前27.39已符合Coupon选品资格，无需继续降价；25件FBA、24件超365天。无企业价和数量阶梯，最终纳15%。','29日US订单0与平台近30日显示3件存在口径差异，已保留该差异。']
 supplement.append({'asin':a,'sku':src.get('sku')or orig.get('sku'),'scope':'EXISTING_CAMPAIGN_OR_ADDED_BP_OUTSIDE_77',**state_for(a),'reasons':reason,'metrics':src or orig,'decision_source':'coupon15-final22-expected.json / coupon5-12-final-review.json'})
proposal=load('restricted-noncoupon-five-proposal.json')
noncoupon=[]
for r in proposal['rows']:
 if r['asin']=='B00SMEEVKQ':continue
 noncoupon.append({'asin':r['asin'],'sku':r['sku'],'scope':'FOUR_NONCOUPON_OUTSIDE_77','last_verified_live_coupon_percent':None,'planned_route':'SALE_PRICE_AND_BUSINESS_TIERS','planned_status':'FILE_10_PREPARED_NOT_LIVE_VERIFIED','live_submission_verified':False,'reason':'独立当前Coupon选品仍因销售历史限制，采用已批准备用Sale及企业价方案。','coupon_restriction':'NO_SALES_HISTORY_IN_COUPON_UI','ordinary_price_write':False,'ordinary_price':r['current_ordinary_price'],'fba_stock':r['current_sellable'],'sale_price':r['proposed_sale_price'],'business_price':r['proposed_business_price'],'tiers':r['proposed_business_tiers'],'sale_start':'2026-11-02','sale_end_exclusive':'2026-11-16 00:00','business_tiers_persist_after_sale':True,'source':'10-four-spec.json / restricted-noncoupon-five-proposal.json / saved current eligibility evidence'})
held073={'asin':'B00SMEEVKQ','sku':'4A073','scope':'PRICE_RESTRICTED_RECHECK_OUTSIDE_77','coupon_eligible_current':True,'last_verified_live_coupon_percent':None,'planned_coupon_percent':None,'planned_target_after_prerequisite':15,'status':'HOLD_09_BUSINESS_CORRECTION_NOT_LIVE_VERIFIED','reason':'旧价格限制消失，但09企业价及阶梯尚未传播，暂不入券、不加Sale。','last_verified_business_price':4.49,'last_verified_tiers':[[10,8]],'target_business_price':9.49,'target_tiers':[[3,2],[5,3],[10,5]],'ordinary_price':10.99,'fba_stock':60,'receipt':'Parent verified upload processed with only inherited100476; not live acceptance','evidence':['09-073-final-independent-inventory.txt','09-073-final-independent-tiers.txt']}
receipt10=load('10-processing-receipt-audit.json') if (P/'10-processing-receipt-audit.json').exists() else None
if receipt10:
 receipt_rows={r['sku']:r for r in receipt10['rows']}
 for r in noncoupon:
  r['planned_status']='UPLOAD_PROCESSED_LIVE_CONFIGURATION_PENDING'
  r['live_submission_verified']=True
  r['live_configuration_verified']=False
  r['receipt_status']=receipt_rows[r['sku']]['status']
  r['receipt_price_errors']=receipt10['price_errors']
  r['receipt_source']='10-processing-receipt-audit.json'
groups=collections.Counter(r['decision_group']for r in rows)
out={'created':datetime.datetime.now().astimezone().isoformat(),'status':'OFFLINE_COVERAGE_LEDGER_PLANNED_VS_LAST_VERIFIED_LIVE','source_precedence':['Final22 and final12 membership','Saved final demand decisions','Original77 audit'], 'basis':demand['basis'],'important_limits':['所有AIS金额均为库存报表预估月费，不是实际账单收费。','Last verified live23/4是此前已运行证据；本台账未访问UI重新确认，不能当作当前最终运行验收。','最终22/12仍记未提交草稿，由主代理完成提交后更新live状态。','77候选、既有活动、另加BP、非券4款和073分开列示，避免混淆母集。','无新增选品或价格决定；保持已有最终分流。','低库存20件是已用筛选经验阈值，不是用户硬性规则；例外按既有最终名单。'], 'campaigns':{'15_percent':{'last_verified_live_count':23,'last_verified_live_asins':sorted(live15),'planned_final_count':22,'planned_final_asins':sorted(final15),'remove_pending':sorted(live15-final15),'add_pending':sorted(final15-live15),'status':'UNSUBMITTED_DRAFT'},'5_percent':{'last_verified_live_count':4,'last_verified_live_asins':sorted(live5),'planned_final_count':12,'planned_final_asins':sorted(final5),'add_pending':sorted(final5-live5),'status':'UNSUBMITTED_DRAFT'}},'coverage_summary':{'audited_candidates':77,'mapped_candidates':len(rows),'candidate_decision_groups':dict(groups),'candidate_planned15':sum(r['planned_coupon_percent']==15 for r in rows),'candidate_planned5':sum(r['planned_coupon_percent']==5 for r in rows),'candidate_no_new_coupon':sum(r['planned_coupon_percent']is None for r in rows),'additional_campaign_rows_outside77':len(supplement),'noncoupon4_count':4,'noncoupon4_units':sum(r['fba_stock']for r in noncoupon),'held073_units':60},'audited77':rows,'additional_campaign_rows':supplement,'noncoupon4':noncoupon,'held073':held073,'validation':{'all77_mapped_once':len(rows)==77 and len({r['asin']for r in rows})==77,'no_final_coupon_overlap':not(final15&final5),'coupon15_transition':'23 - 9 + 8 =22','coupon5_transition':'4 + 8 =12','no_claim_new_campaign_live':True,'no_added_price_fields_or_actions':True}}
(P/'promotion-final-coverage-ledger.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf-8')
lines=['促销最终覆盖台账（离线汇总；计划与已运行分开）',out['created'],'','此前已验运行：15% 23 ASIN；5% 4 ASIN。','本轮最终草稿：15% 22 ASIN（23减9加8）；5% 12 ASIN（4加8），均未按新名单完成运行验收。','77候选已逐一映射；其余原活动商品、BP、非券4款和073另列。','AIS为预估月度附加费，非实际账单。','']
for group,n in groups.items():lines.append(f'{group}: {n}款')
lines+=['','77候选逐条：']
for r in rows:
 m=r['metrics'];live=r['last_verified_live_coupon_percent'];planned=r['planned_coupon_percent']
 lines.append(f"{r['asin']} | {r['sku']} | 已验券={live or '无'} | 计划券={planned or '不新增'} | {r['decision_group']} | 库存{m['stock']} | 29日{m['orders29']}单/{m['units29']}件 | 近7日{m['orders7']}单 | 181+{m['age181plus']} | 365+{m['age365plus']} | AIS预估${m['estimated_aged_surcharge']} | {'；'.join(r['reasons'])}")
lines+=['','既有活动及BP（77之外）：']
for r in supplement:lines.append(f"{r['asin']} | {r['sku']or '原5%保留商品'} | 已验券={r['last_verified_live_coupon_percent']or '无'} | 计划券={r['planned_coupon_percent']or '移除'} | {'；'.join(r['reasons'])}")
lines+=['',('非券4款：文件10上传已处理，1条SUCCESS及3条SUCCESS OTHER ERROR，仅旧100476、无价格错误；仍待现场配置验收。' if receipt10 else '非券4款：文件10已准备，未完成生效验收。')+'普通价不写。Sale覆盖11/2–11/15，结束值11/16 00:00；企业阶梯不自动随Sale到期。']
for r in noncoupon:lines.append(f"{r['asin']} | {r['sku']} | {r['fba_stock']}件 | Sale {r['sale_price']} | B2B {r['business_price']} | 3/5/10件减2/3/5% | 销售历史限制仍在")
lines+=['','073：B00SMEEVKQ / 4A073，60件。当前Coupon可选，但企业仍4.49及10件8%；09目标9.49+3/5/10件2/3/5%尚未验收，先不纳券。','', '最终22及12清单：','15%: '+','.join(sorted(final15)),'5%: '+','.join(sorted(final5))]
(P/'promotion-final-coverage-ledger.txt').write_text('\n'.join(lines)+'\n','utf-8')
print(json.dumps({'coverage':out['coverage_summary'],'validation':out['validation']},ensure_ascii=False,indent=2))
