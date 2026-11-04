import csv,json,re
from pathlib import Path
from datetime import datetime,timezone,timedelta
from decimal import Decimal,ROUND_HALF_UP
P=Path(__file__).parent
original=json.loads((P/'coupon-original15-demand-recheck.json').read_text('utf8'))
ledger={r['asin']:r for r in json.loads((P/'coupon-audit-ledger.json').read_text('utf8'))['rows']}
fees={r['sku']:r for r in json.loads((P/'fba-live-fees.json').read_text('utf8'))}
raw={r['contribution_sku#1.value']:r for r in json.loads((P/'category-report-raw.json').read_text('utf8'))['rows']}
listing={r['seller-sku']:r for r in csv.DictReader(open('D:/下载文件/所有商品报告_11-01-2026.txt',encoding='utf-8-sig'),delimiter='\t')}
orders=[]
for r in csv.DictReader(open('D:/下载文件/175793876516020757.txt',encoding='utf-8-sig'),delimiter='\t'):
    d=datetime.fromisoformat(r['purchase-date']).astimezone(timezone(timedelta(hours=-7))).date().isoformat()
    if '2026-10-02'<=d<='2026-10-30' and r['ship-country']=='US' and r['currency']=='USD' and r['order-status']!='Cancelled':orders.append((r,d))
def cash(v):return float(Decimal(str(v)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))
decisions={
'B07RN7WQ81':('REMOVE15_HEALTHY_DEMAND','51件，29日10单23件，近7日5单。库存约2.2个月；181+50件但AIS仅1.42/月，当前销量优先于单纯库龄标记。建议停止此ASIN普惠15，保留普通/企业方案。'),
'B01N1U9USQ':('DEPRIORITIZE_MFN_ONLY','本期未查到FBA库存/AIS。MFN显示1609不是已核实物理积压；与本轮优先清理收费FBA目标不一致。'),
'B07FKHHTYG':('KEEP15_AGED_SLOW','44件且44件365+，29日仅1单1件，AIS15.40/月。保留15清库，不再降普通价或追加Sale。'),
'B07QZR9Z3P':('KEEP15_AGED_SLOW','28件全365+，29日零单，AIS10.04/月、普通仓储12.78/月。现企业27.98及2件2%需计入总折让，不加第二重Sale。'),
'B07B8RBCKT':('REDUCE15_TO5_NO_AIS','24件，29日1单1件，181+0、AIS0、普通仓储1.39/月。可做轻量5%测试，但不属于优先15%收费滞留清库；不因旧券存在就继续强促。'),
'B07FKBHTDG':('REDUCE15_TO5_EXCESS_WITH_DEMAND','612件库存高、约27.8个月当前销量，但29日20单22件、近7日4单，持续有订单。181+0、AIS0、普通仓储10.13/月。建议轻券5%或观察现价，不称无订单/滞留附加费商品。'),
'B07T79KGWM':('DEPRIORITIZE_MFN_ONLY','未查到FBA库存/AIS，MFN显示1027件且物理库存未核；按新的FBA费用优先级后排。'),
'B07T42D4GL':('DEPRIORITIZE_MFN_ONLY','未查到FBA库存/AIS，MFN显示1018件且物理库存未核；按新的FBA费用优先级后排。'),
'B01N6IT5IG':('DEPRIORITIZE_MFN_ONLY','未查到FBA库存/AIS，MFN显示1404件不证明FBA费用压力；原企业配置需另核，不以旧模板值当当前实况。'),
'B07QWKWWP2':('KEEP15_AGED_SLOW','162件可售，181+163件（库龄口径含非可售，不能相加），AIS6.06/月，29日仅2单2件。虽365+0仍存在超龄附加费，应保留15清库存。'),
'B00SMEENOU':('KEEP15_AGED_SLOW','140件可售，181+139/365+138，AIS48.36/月，为原券最高。29日零单，保留15作为现金回收清库；低价扣费后现金薄，不加Sale，不能称有利润。'),
'B07R2KSW34':('KEEP15_AGED_SLOW','130件，181+129但365+0，AIS11.25/月，29日仅1单1件。是收费的超龄低销库存，保留15。'),
'B07RP9K6KV':('REVIEW_HIGH_AIS_DEEP_BUSINESS_STACK','77件全365+、29日零单、AIS26.90/月，清库优先级高；但现企业9.49及2件2%，再叠15券累计34.07%让利。建议单列核准总让利，优先改轻5%（累计26.31%）或保留15作为明确深清仓例外，不额外加Sale/改普通价。'),
'B0F2YHTD8T':('KEEP15_AGED_SLOW','52件，181+52/365+49，AIS17.23/月，29日零单。保留15清库，不重复叠新促销价。'),
'B0F2TJ7ZL7':('KEEP15_AGED_SLOW','44件全365+，AIS15.40/月，29日零单。保留15清库，不追加Sale。')}
rows=[];differences=[]
for o in original:
    asin=o['asin'];sku=o['sku']; l=ledger.get(asin,{}); f=fees.get(sku,{}); rr=raw.get(sku,{})
    same=[(r,d) for r,d in orders if r['asin']==asin];afn=[(r,d) for r,d in same if r['fulfillment-channel']=='Amazon']
    st={'fba_orders29':len({r['amazon-order-id'] for r,d in afn}),'fba_units29':sum(int(r['quantity']) for r,d in afn),
      'all_orders29':len({r['amazon-order-id'] for r,d in same}),'all_units29':sum(int(r['quantity']) for r,d in same),
      'orders7':len({r['amazon-order-id'] for r,d in same if d>='2026-10-24'})}
    for k,v in st.items():
        if v!=o[k]:differences.append({'asin':asin,'key':k,'raw':v,'parent':o[k]})
    price=float(listing[sku]['price']);b2b=f.get('b2b')
    tiers=[]
    for i in range(1,6):
        pref=f'purchasable_offer[marketplace_id=ATVPDKIKX0DER][audience=B2B]#1.quantity_discount_plan#1.schedule#1.levels#{i}.'
        if rr.get(pref+'lower_bound') is not None and rr.get(pref+'value') is not None:tiers.append([int(rr[pref+'lower_bound']),float(rr[pref+'value'])])
    tier=max([r[1] for r in tiers],default=0);deep=(b2b or price)*(1-tier/100)
    # This is a conservative sensitivity case, not confirmation that every buyer can stack discounts.
    p15=deep*.85;p5=deep*.95
    unitcash=p15-f['fba_fee']-price*.15-price*.025 if f.get('fba_fee') is not None else None
    decision,reason=decisions[asin]
    rows.append({**o,'age181plus':l.get('age181plus'),'estimated_aged_surcharge_monthly':l.get('estimated_aged_surcharge'),
      'estimated_ordinary_storage_monthly':l.get('estimated_month_storage'),'fee_source_stock_snapshot':'2026-10-30','fee_basis_stock':l.get('available10_30'),
      'regular_price_latest11_01_report':price,'business_price_last_saved_ui':b2b,'business_tiers_from10_31_template':tiers,
      'business_evidence':f.get('source'),'business_not_freshly_reread_this_review':True,'fba_fee_last_saved_ui':f.get('fba_fee'),
      'all_stack_15_unit_price':cash(p15) if f else None,'all_stack_15_total_discount_percent':round((1-p15/price)*100,2) if f else None,
      'all_stack_5_unit_price':cash(p5) if f else None,'all_stack_5_total_discount_percent':round((1-p5/price)*100,2) if f else None,
      'conservative_cash_after_15_before_goods_inbound_storage_ads_refunds_fixedcoupon':cash(unitcash) if unitcash is not None else None,
      'no_new_v4_sale_for_these_original15':True,'decision':decision,'reason':reason})
assert not differences,differences
summary={}
for k in sorted({r['decision'] for r in rows}):
    items=[r for r in rows if r['decision']==k]
    summary[k]={'asins':len(items),'fba_stock':sum(r['fba_stock'] or 0 for r in items),'monthly_estimated_aged_surcharge':cash(sum(r['estimated_aged_surcharge_monthly'] or 0 for r in items)) if any(r['estimated_aged_surcharge_monthly'] is not None for r in items) else None,'asins_list':[r['asin'] for r in items]}
out={'status':'READ_ONLY_RECOMMENDATION_NOT_APPLIED','scope':'Original15 already-running ASINs; excludes later8 approved additions and new draft additions',
 'principle':'Prioritize actual estimated AIS fee pressure, low real demand, then total concession. Age365 is not the sole trigger. Positive age181 alone is not decisive.',
 'authorization_distinction':'The original15 were previously approved and running. Removal or migration is a new recommendation under the latest inventory/demand/fee-priority instruction; do not describe it as an unauthorized original action. Parent decides and performs final campaign edit.',
 'order_period':'29 complete PDT days2026-10-02..30; last7=10-24..30; US/USD noncancelled',
 'independent_order_check':{'rows':15,'fields':5,'mismatches':differences},'summary':summary,
 'limitations':['AIS and ordinary storage are separate estimated monthly amounts, not settled charges or guaranteed avoidable savings.','Current sellable stock and dated age units differ; do not sum available and aged counts.','B2B last saved UI and10/31 tiers require final readback before changing price policy; corrected regular prices use11/1 report, not older incident prices.','Estimated cash excludes goods/inbound/storage/ads/refunds/fixed coupon fee and is not profit.','MFN reported counts are not verified physical warehouse inventory and do not establish FBA aged fees.'],
 'rows':rows}
(P/'coupon-original15-aged-demand-final-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),'utf8')
lines=['原运行15款：AIS压力、真实订单及总让利复核（只读）','保留15建议7款；6031x4深叠加单列；5020x3建议退出15；40609及608建议轻5%；4款仅MFN后排。',
 '这是按用户最新目标调整既有许可活动，非把原审批描述为错误。库存/费用来源分开，AIS非普通仓储费。','',
 'ASIN | SKU | FBA库存 | 181+/365+ | AIS/月 | 普通仓储/月 | 实际29日单/件 | 近7日单 | 普通/企业/阶梯 | 最深15总让利 | 建议']
for r in rows:
    lines.append(f"{r['asin']} | {r['sku']} | {r['fba_stock']} | {r['age181plus']}/{r['age365plus']} | {r['estimated_aged_surcharge_monthly']} | {r['estimated_ordinary_storage_monthly']} | {r['all_orders29']}/{r['all_units29']} | {r['orders7']} | {r['regular_price_latest11_01_report']}/{r['business_price_last_saved_ui']}/{r['business_tiers_from10_31_template']} | {r['all_stack_15_total_discount_percent']}% | {r['decision']}")
    lines.append(r['reason'])
(P/'coupon-original15-aged-demand-final-review.txt').write_text('\n'.join(lines),'utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
