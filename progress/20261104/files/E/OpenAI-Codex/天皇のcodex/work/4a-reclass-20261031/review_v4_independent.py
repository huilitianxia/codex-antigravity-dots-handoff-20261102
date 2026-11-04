import json
from pathlib import Path
from collections import Counter
p=Path(__file__).parent
rd=lambda n:json.loads((p/n).read_text(encoding='utf-8-sig'))
e=rd('execution-batch-data.json');v1=rd('v1-price-incident-audit.json');fees={r['sku']:r for r in rd('fba-live-fees.json')};cat={r['sku']:r for r in rd('category-report-audit.json')['rows']}
ops={r['sku']:r for r in e['operations']};bad_asins={r['asin'] for r in v1['records']};coupons=rd('coupon-audit-ledger.json');coupon_asins=set(coupons['coupon15_asins']+coupons['coupon5_asins'])
reviews=[]
for r in e['pricing']:
 f=fees.get(r['sku'],{});c=cat.get(r['sku'],{});op=ops[r['sku']];cells=op['cells'];why=[]
 current=r['regular'];effective=r['sale_new'] or r['regular_new'] or r['sale_before'] or current
 business=r['business_new'] or r['business_before'] or effective
 min_b=round(business*(1-max([x[1] for x in r['tiers']] or [0])/100),2)
 cash=round(min(effective,min_b)*.85-r['fba_fee'],2)
 if r['asin'] in bad_asins:why.append('与V1普通降价事故复核ASIN重叠，基础报价未经事故复核关闭')
 if r['sku'] in ['AAAA 4A 301x12-N','4A 301x24x2']:why.append('为协调004错误基价而派生的大幅降价，不能以此作为多包装定价依据')
 if effective/current<.8:why.append('折扣超过20%，未见该最终幅度的单款明确决定')
 if not f:why.append('无同SKU实时费用快照')
 elif f['price']!=current:why.append('拟定基价与同SKU费用快照不一致')
 if f and f['fba_fee']!=r['fba_fee']:why.append('FBA配送费与快照不一致')
 if f and f['asin']!=r['asin']:why.append('费用快照ASIN不匹配')
 if r['asin'] in coupon_asins:why.append('已存在Coupon，拟稿现金模型未计券及券费')
 if c and c.get('sale_active_by_dates') and r['sale_new']:why.append('已有有效限时促销，需复核覆盖日期及现价')
 if business>effective:why.append('拟定企业价高于有效消费者价')
 if cash<=0:why.append('单独计算平台费用后现金非正')
 if 'MO' in cells and (cells['MO']!='2026-11-01' or cells['MP']!='2026-11-30'):why.append('限时价日期不符合本批约定')
 checks=dict(same_sku_fee_match=bool(f and f['price']==current and f['fba_fee']==r['fba_fee'] and f['asin']==r['asin']),standalone_min_unit=min(effective,min_b),standalone_cash_after_estimated15percent_commission_and_fba=cash,source=f.get('source'),title=f.get('title'),source_channel=c.get('channel'),sale_start=cells.get('MO'),sale_end_exclusive=cells.get('MP'),in_existing_coupon=r['asin'] in coupon_asins)
 why.append('既有购物车/企业/其他促销叠加未完成全量核验；正的单独现金测算不等于最差叠加现金下界已确认')
 reviews.append(dict(sku=r['sku'],asin=r['asin'],decision='EXCLUDE_PRICE_FIELDS_THIS_V4',allowed_price_cells={},original_regular=current,proposed_effective=effective,proposed_min_business=min_b,checks=checks,reasons=why))
assert len(reviews)==29
out=dict(decision='本次可上传V4仅非价格修复；29条价格方案全部暂缓，不对旧促销作任何清除',approved_price_rows=[],excluded_price_rows=reviews,scope='独立逐行检查全部29SKU/28ASIN；与V1、同SKUFBA价费、源目录、现有券清单、日期及算术交叉。未使用源表单独运费价重新定FBA售价。',remove_columns=['MJ','MK','ML','MM','MN','MO','MP','MQ','MR','MS','MT','MU','MV','MW','MX','MY','MZ','NA','NB','NC','ND','NE','NF','NG','NH'],note='这是本次交付排除，不表示29条全部定价错误。已核实非价格字段可独立交付；保留ASIN/SKU和现有线上价。',standalone_checks_pass_count=sum(x['checks']['same_sku_fee_match'] and x['checks']['standalone_cash_after_estimated15percent_commission_and_fba']>0 for x in reviews))
(p/'v4-price-independent-review.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
lines=[out['decision'],out['scope'],out['note'],'独立单价与费用一致且单独现金正：'+str(out['standalone_checks_pass_count'])+'/29','']
for r in reviews:lines.extend([f"{r['sku']} | {r['asin']} | 普通{r['original_regular']} -> 有效{r['proposed_effective']} / 企业最低{r['proposed_min_business']} | 单独现金 {r['checks']['standalone_cash_after_estimated15percent_commission_and_fba']}",'; '.join(r['reasons'])])
(p/'v4-price-independent-review.txt').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps(dict(rows=len(reviews),standalone_pass=out['standalone_checks_pass_count'],direct_issues=[(r['sku'],r['reasons'][:-1]) for r in reviews if len(r['reasons'])>1]),ensure_ascii=False))
