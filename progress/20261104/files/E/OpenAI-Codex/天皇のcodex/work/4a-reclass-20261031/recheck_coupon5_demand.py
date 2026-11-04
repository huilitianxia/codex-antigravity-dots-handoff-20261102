from pathlib import Path
from datetime import datetime, timezone, timedelta
from collections import defaultdict, Counter
from decimal import Decimal, ROUND_HALF_UP
import csv,json

P=Path(__file__).parent
assigned=json.loads((P/'coupon5-final-38-assigned.json').read_text('utf-8'))
parent={r['asin']:r for r in json.loads((P/'coupon77-demand-recheck.json').read_text('utf-8'))['rows']}
source=Path('D:/下载文件/175793876516020757.txt')
orders=list(csv.DictReader(source.open(encoding='utf-8-sig',newline=''),delimiter='\t'))
pdt=timezone(timedelta(hours=-7))
usable=[]
for r in orders:
    day=datetime.fromisoformat(r['purchase-date']).astimezone(pdt).date().isoformat()
    if r['ship-country']=='US' and r['currency']=='USD' and r['order-status']!='Cancelled' and '2026-10-02'<=day<='2026-10-30':
        usable.append((r,day))

def stats(items):
    return {'orders29':len({r['amazon-order-id'] for r,d in items}),
      'units29':sum(int(r['quantity'] or 0) for r,d in items),
      'orders7':len({r['amazon-order-id'] for r,d in items if d>='2026-10-24'}),
      'units7':sum(int(r['quantity'] or 0) for r,d in items if d>='2026-10-24'),
      'active_days29':len({d for r,d in items}),
      'last_order_day':max([d for r,d in items],default=None),
      'business_orders29':len({r['amazon-order-id'] for r,d in items if r['is-business-order'].lower()=='true'}),
      'b2c_orders29':len({r['amazon-order-id'] for r,d in items if r['is-business-order'].lower()!='true'}),
      'promotion_orders29':len({r['amazon-order-id'] for r,d in items if Decimal(r['item-promotion-discount'] or '0')>0}),
      'observed_fulfillment':sorted({r['fulfillment-channel'] for r,d in items})}

def money(n):return float(Decimal(str(n)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))
rows=[];mismatches=[]
keep={'B07QVKPZXX','B07QXJYKJN'}
for a in assigned:
    same_sku=stats([(r,d) for r,d in usable if r['sku']==a['sku']])
    same_asin=stats([(r,d) for r,d in usable if r['asin']==a['asin']])
    for k in ['orders29','units29','orders7','units7','active_days29','last_order_day']:
        if same_sku[k]!=parent[a['asin']][k]:mismatches.append({'asin':a['asin'],'field':k,'independent':same_sku[k],'parent':parent[a['asin']][k]})
    for k,pk in [('orders29','asin_orders29'),('units29','asin_units29')]:
        if same_asin[k]!=parent[a['asin']][pk]:mismatches.append({'asin':a['asin'],'field':pk,'independent':same_asin[k],'parent':parent[a['asin']][pk]})
    regular=Decimal(str(a['price'])); b2b=Decimal(str(a['b2b'] or a['price'])); tier=max([float(t[1]) for t in a['tiers']],default=0)
    prior_deep=b2b*(1-Decimal(str(tier))/100)
    coupon_deep=prior_deep*Decimal('0.95')
    reason=[]
    if a['asin']=='B07QVKPZXX':
        decision='KEEP_NEW_5_PERCENT';reason=['67件FBA库存，29完整日仅4单9件、4个销售日；库存约7.4个月的过去销量。','近7日2单7件有回升，因此只保留5%轻券，不再降价；当前无企业价/阶梯叠加。']
    elif a['asin']=='B07QXJYKJN':
        decision='KEEP_NEW_5_PERCENT';reason=['33件FBA库存，29完整日6单6件、近7日2单2件；库存约5.5个月销量。','当前无企业价/阶梯，保留5%轻券即可，不追加降价。']
    elif a['asin']=='B07F2BHFJH':
        decision='REMOVE_NEW_KEEP_EXISTING';reason=['61件库存但29完整日15单16件，14个销售日，近7日4单5件，仍有持续自然需求。','企业9.49较普通11.99已低20.85%；2件再2%后累计22.43%，再叠5%券约26.31%。保留企业方案，不再加普惠券。']
    elif a['asin']=='B07FKHNTRK':
        decision='REMOVE_NEW_KEEP_EXISTING';reason=['26件库存，29完整日17单19件、12个销售日，库存约1.4个月；并非近期无订单堆货。','已有企业14.99，普通15.99；保留现价与企业价。']
    elif a['asin']=='B07FKJGDJR':
        decision='REVIEW_AGED_EXCEPTION_DEFAULT_REMOVE';reason=['仅3件库存，29完整日零订单；3件均库龄365天以上。','可作为清理一年老库的小量例外单独决定；本轮默认先撤新增5%券，不把它纳入普遍堆货降价。']
    else:
        decision='REMOVE_NEW_KEEP_EXISTING'
        if a['units_current']<20:reason.append(f"仅{a['units_current']}件FBA库存，低于本次建议优先处理的规模；20件为筛选参考，不是用户硬性标准。")
        if same_sku['orders29']:
            reason.append(f"29完整日{same_sku['orders29']}单{same_sku['units29']}件，近7日{same_sku['orders7']}单{same_sku['units7']}件；保留已有需求与价格。")
        else:reason.append('29完整日零订单，但库存少且没有365天以上库龄证据；先处理页面/曝光，不直接扩大普惠让利。')
        if a['asin'] in ['B077QLHHVH','B0784GHSVJ']:
            reason.append('普通/企业5.99，10件阶梯8%已在；叠5%券总折让12.6%。低库存低单价，不再加券。')
        elif a['b2b'] is not None:reason.append('保留现有企业价及阶梯，不再额外叠加本轮优惠券。')
    scenarios=a.get('coupon_scenarios') or []
    cash=next((s['cash_before_goods_inbound_storage_ads_refunds_fixed_fee'] for s in scenarios if s['coupon_percent']==5),a.get('cash_before_goods_inbound_storage_ads_refunds_fixed_fee'))
    rows.append({'asin':a['asin'],'sku':a['sku'],'fba_sellable':a['units_current'],'fba_units30':a['units30_fba'],
       'age365plus':a['age365plus'],'actual_order_source':str(source),'orders30':None,'orders30_note':'No complete30-day order export; exact29 complete PDT days reported separately.',
       **same_sku,'same_asin_all_fulfillment':same_asin,'regular_price':a['price'],'sale_visible':a.get('sale_visible'),'business_price':a['b2b'],'business_tiers':a['tiers'],
       'deepest_existing_business_price':money(prior_deep),'deepest_existing_discount_percent':round(float((1-prior_deep/regular)*100),2),
       'deepest_with_5_coupon_price':money(coupon_deep),'deepest_with_5_coupon_discount_percent':round(float((1-coupon_deep/regular)*100),2),
       'estimated_cash_with_5_coupon_before_goods_and_other_costs':cash,
       'months_cover_at29day_velocity':round(a['units_current']/same_sku['units29'],1) if same_sku['units29'] else None,
       'decision':decision,'remove_from_current_unsubmitted_draft':a['asin'] not in keep,'reason':reason,
       'audit_source':a['source_audit_file']})
assert not mismatches,mismatches
groups={}
for decision in sorted({r['decision'] for r in rows}):
    rr=[r for r in rows if r['decision']==decision]
    groups[decision]={'asins':len(rr),'fba_sellable':sum(r['fba_sellable'] for r in rr),'asin_list':[r['asin'] for r in rr]}
result={'status':'READ_ONLY_RECOMMENDATIONS_NO_DRAFT_CHANGES','scope':'38 proposed additions to existing5% coupon; original4 retained outside this review',
 'period':{'order_complete_PDT':'2026-10-02..2026-10-30 (29days)','last7_PDT':'2026-10-24..2026-10-30','FBA_units30':'Dated FBA stock snapshot rolling30day units; not equivalent to29day US order count'},
 'count':len(rows),'fba_sellable_total':sum(r['fba_sellable'] for r in rows),'inventory_under20_count':sum(r['fba_sellable']<20 for r in rows),
 'independent_raw_order_validation':{'fields_compared':8,'candidate_rows':len(rows),'mismatches':mismatches},'groups':groups,
 'proposed_new_coupon_asins':sorted(keep),'proposed_total_with_original4':6,'default_remove_additions':36,
 'principle':'Prioritize substantial stock with slow real demand. Preserve small stocks and ongoing-demand offers. No ordinary-price changes. Age365 exception for3 units is separate for parent judgment. Threshold20 is a screening heuristic, not a user requirement.',
 'rows':rows}
(P/'coupon5-38-demand-final-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
lines=['5%新增38款真实订单/库存复核（只读，未改变草稿）',
 '建议新增仅2款：PSS9-1Refill 67件、PSS9-5NANBx2 33件，共100件。原4款不在本次撤券范围。',
 '35款建议撤本次新增，246件；Meeting6仅3件但全部一年老库，列独立例外待决定，默认先撤。合计38款349件。',
 '订单为PDT10月2日至30日29个完整日，近7日10月24日至30日；缺完整30日订单，不能将29日标作30日。FBA units30沿用库存报告真实滚动30天。',
 '已从原订单文件独立核验38款8项统计，全部与主表一致。订单ID及客户信息未输出。',
 '', 'ASIN | SKU | FBA库存 | FBA30日件 | 实际29日单/件 | 近7日单/件 | 365天以上 | 普通/企业 | 阶梯 | 建议']
for r in rows:
    lines.append(f"{r['asin']} | {r['sku']} | {r['fba_sellable']} | {r['fba_units30']} | {r['orders29']}/{r['units29']} | {r['orders7']}/{r['units7']} | {r['age365plus']} | {r['regular_price']}/{r['business_price']} | {r['business_tiers']} | {r['decision']}")
    lines.append('理由：'+' '.join(r['reason']))
(P/'coupon5-38-demand-final-review.txt').write_text('\n'.join(lines),'utf-8')
print(json.dumps({k:result[k] for k in ['count','fba_sellable_total','inventory_under20_count','groups','proposed_total_with_original4','independent_raw_order_validation']},ensure_ascii=False,indent=2))
