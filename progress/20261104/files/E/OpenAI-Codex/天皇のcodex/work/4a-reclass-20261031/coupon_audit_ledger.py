import json
from pathlib import Path
R=Path(__file__).parent
data=json.loads((R/'fba-potential-from-orders.json').read_text(encoding='utf8'))['rows']
existing15=['B07RN7WQ81','B01N1U9USQ','B07FKHHTYG','B07QZR9Z3P','B07B8RBCKT','B07FKBHTDG','B07T79KGWM','B07T42D4GL','B01N6IT5IG']
new15=['B07QWKWWP2','B00SMEENOU','B07R2KSW34','B07RP9K6KV','B0F2YHTD8T','B0F2TJ7ZL7']
existing5=['B08DKJ2K3T','B01LVTWP7Q','B07F2B49BL']
new5=['B0F9L5G6XQ']
blocked={'B07QXJWDPL':'评分门槛','B0FBG138ND':'评分门槛','B07QXJZKHC':'评分门槛','B07FK9BYHW':'评分门槛',
 'B0F28LXKKF':'评分门槛及销售历史','B07RT4GTLZ':'销售历史','B01LVXOCU2':'销售历史',
 'B07FK8LN8D':'销售历史','B0F7LW38FX':'销售历史','B00SMEEVKQ':'价格4.99低于优惠券门槛'}
reviewed=set(existing15+new15+existing5+new5+list(blocked))
rows=[]
for x in data:
    if x['available10_30']<=0:continue
    a=x['asin']
    status='15%券已提交并运行' if a in existing15+new15 else '5%券已提交待回读' if a in existing5+new5 else 'Coupon受限:'+blocked[a] if a in blocked else '待筛查'
    rows.append({k:x[k] for k in ['asin','title','category','available10_30','units30','age365plus','age181plus','estimated_aged_surcharge','estimated_month_storage']}|{'coupon_status':status})
rows.sort(key=lambda r:-r['available10_30'])
out={'asof':'2026-11-01 CST','source_inventory_date':'2026-10-30','source_order_period':'Oct1-31 08:14 PDT',
 'coupon15_asins':existing15+new15,'coupon5_asins':existing5+new5,'coupon5_removed':'B07FKG29KB',
 'newly_screened':17,'new15':new15,'new5':new5,'blocked':blocked,'rows':rows}
(R/'coupon-audit-ledger.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
pending=[r for r in rows if r['coupon_status']=='待筛查']
print('FBApositiveASIN',len(rows),'totalqty',sum(r['available10_30'] for r in rows),'pending',len(pending),'pendingqty',sum(r['available10_30'] for r in pending))
print(json.dumps(pending[:35],ensure_ascii=False,indent=2))
