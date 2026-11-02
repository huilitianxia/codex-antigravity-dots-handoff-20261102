import json
from pathlib import Path
from openpyxl.utils import column_index_from_string as ix
p=Path(__file__).parent
rd=lambda n:json.loads((p/n).read_text(encoding='utf8'))
review=rd('v4-price-independent-review.json');e=rd('execution-batch-data.json');raw=rd('category-report-raw.json')
oldrows={r['contribution_sku#1.value']:r for r in raw['rows']};ops={r['sku']:r for r in e['operations']};prices={r['sku']:r for r in e['pricing']}
approved=[]
for r in review['excluded_price_rows']:
 if len(r['reasons'])!=1 or r['sku']=='AAAA 4A 2028-N':continue
 q=prices[r['sku']];o=ops[r['sku']];rr=oldrows.get(r['sku'],{});old_tiers={k:rr.get(raw['headers'][ix(k)-1][1]) for k in ['MX','MY','MZ','NA','NB','NC','ND','NE','NF','NG','NH']}
 for k,v in old_tiers.items():
  assert v in (None,'') or k in o['cells'],(r['sku'],k,v)
 cells={k:v for k,v in o['cells'].items() if k not in ['C','D','E','L','M'] and ix(k)>=ix('ML') and ix(k)<=ix('NH')}
 assert 'MJ' not in cells and 'MK' not in cells
 assert q['business_new']<=q['sale_new']
 assert q['sale_new']/q['regular']>=.849
 assert r['checks']['same_sku_fee_match'] and r['checks']['standalone_cash_after_estimated15percent_commission_and_fba']>0
 approved.append(dict(sku=r['sku'],asin=r['asin'],allowed_price_cells=cells,regular_price_unchanged=q['regular'],sale_price=q['sale_new'],business_price=q['business_new'],minimum_business_unit_price=q['minimum_business_unit_price'],maximum_stack_cash=r['checks']['standalone_cash_after_estimated15percent_commission_and_fba'],cash_definition='最深本批企业阶梯价扣15%估算佣金和当前FBA费；现有券无ASIN交集，统一促销总览及品牌定制活动由主代理现场核验；未扣采购、头程、仓储、广告、退货',evidence=[r['checks']['source'],'category-report-raw.json 全五档阶梯无未覆盖残留','promotion-active-dashboard-v4.txt','主代理品牌定制入口现场核验结果'],old_tiers=old_tiers))
assert len(approved)==16,len(approved)
for a in approved:
 q=prices[a['sku']]
 a.update(ordinary_base=q['regular'],effective_after=q['sale_new'],sale_before=q['sale_before'],sale_new=q['sale_new'],sale_drop_percent=round(100*(1-q['sale_new']/q['regular']),2),sale_start='2026-11-01',sale_end_exclusive='2026-11-30',business_tiers=q['tiers'],maximum_cumulative_business_discount_percent=round(100*(1-q['minimum_business_unit_price']/q['regular']),2))
 a['evidence'][-1]='brand-promotions-v4.txt 全部五项2025完成或取消；promotion-types-and-active-v4.txt 仅两券'
(p/'v4-approved-price-rows.json').write_text(json.dumps(approved,ensure_ascii=False,indent=2),encoding='utf8')
approved_skus={a['sku'] for a in approved}
review['decision']='最终16条价格/企业阶梯获批，其余13条价格排除；仅保留非事故的已核实非价格字段'
review['approved_price_rows']=approved
review['excluded_price_rows']=[r for r in review['excluded_price_rows'] if r['sku'] not in approved_skus]
for r in review['excluded_price_rows']:
 r['reasons']=[x for x in r['reasons'] if not x.startswith('既有购物车')]
 if r['sku']=='AAAA 4A 2028-N':r['reasons'].append('02恢复前同SKU历史19.99，02设12.99，本批再11.04；累计44.8%且包装/原价尚未复核，新增事故排除')
review['note']='当前促销叠加核验已完成：两券均不含获批16ASIN；品牌定制无现在/未来活动。获批16条不改普通基价、不改包装；最低企业阶梯现金按估算15%佣金和当前FBA费计算。'
(p/'v4-price-independent-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf8')
lines=[review['decision'],review['note'],'','批准16条：']
for a in approved:lines.append(f"{a['sku']} | 原普通{a['ordinary_base']} | 促销{a['sale_new']} | 降幅{a['sale_drop_percent']}% | 企业最低{a['minimum_business_unit_price']} | 企业最大累计折扣{a['maximum_cumulative_business_discount_percent']}% | 费用后最低现金{a['maximum_stack_cash']} | 2026-11-01至11-30零点")
lines+=['','排除13条：']
for r in review['excluded_price_rows']:lines.append(r['sku']+' | '+'; '.join(r['reasons']))
(p/'v4-price-independent-review.txt').write_text('\n'.join(lines),encoding='utf8')
print('Approved rows',len(approved),'minimum cash',min(r['maximum_stack_cash'] for r in approved))
