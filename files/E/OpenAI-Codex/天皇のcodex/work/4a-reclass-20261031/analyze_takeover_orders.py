import csv,json
from pathlib import Path
from collections import defaultdict
from datetime import datetime,timezone,timedelta
from decimal import Decimal

ROOT=Path(__file__).parent
catalog={r['asin']:r for r in json.loads((ROOT/'fba-potential-from-orders.json').read_text(encoding='utf8'))['rows']}
pt=timezone(timedelta(hours=-7))
def bucket():
    return {'ids':set(),'units':0,'sales':Decimal(0),'discount':Decimal(0),'discount_ids':set(),'promo_ids':set(),'promo_labels':set()}
stats=defaultdict(lambda:defaultdict(bucket))
daily=defaultdict(lambda:defaultdict(bucket))
def add(b,r):
    b['ids'].add(r['amazon-order-id']);b['units']+=int(r['quantity'] or 0)
    b['sales']+=Decimal(r['item-price'] or 0)
    d=Decimal(r['item-promotion-discount'] or 0)
    b['discount']+=d
    if d>0:b['discount_ids'].add(r['amazon-order-id'])
    if r['promotion-ids'].strip():
        b['promo_ids'].add(r['amazon-order-id']);b['promo_labels'].add(r['promotion-ids'])
def clean(b):
    return {('orders' if k=='ids' else k):len(v) if isinstance(v,set) and k!='promo_labels' else sorted(v) if isinstance(v,set) else float(v) if isinstance(v,Decimal) else v for k,v in b.items()}
with open('D:/下载文件/175793876516020757.txt',encoding='utf-8-sig',newline='') as f:
    for r in csv.DictReader(f,delimiter='\t'):
        if r['ship-country']!='US' or r['currency']!='USD' or r['order-status']=='Cancelled' or r['fulfillment-channel']!='Amazon':continue
        day=datetime.fromisoformat(r['purchase-date']).astimezone(pt).date().isoformat()
        period='before28' if day<'2026-10-28' else '28transition' if day=='2026-10-28' else '29to30' if day<'2026-10-31' else '31partial'
        a=r['asin'];add(stats[a][period],r);add(daily[a][day],r)
rows=[]
for a,ps in stats.items():
    c=catalog.get(a,{})
    rows.append({'asin':a,'skus':c.get('order_skus',[]),'category':c.get('category'),'stock10_30':c.get('available10_30'),
                 'periods':{p:clean(ps[p]) for p in ['before28','28transition','29to30','31partial']},
                 'daily':{d:clean(b) for d,b in sorted(daily[a].items())}})
rows.sort(key=lambda r:-(r['periods']['28transition']['sales']+r['periods']['29to30']['sales']))
out={'basis':'US,USD,noncancelled,FBA; PDT calendar dates;28 transition;29-30 complete;31 partial through08:14; pending included; item-price before refunds; discounts separately reported','rows':rows}
(ROOT/'takeover-order-analysis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
    if not str(r['category']).startswith('满胶'):
        print(json.dumps({**r,'daily':{d:v for d,v in r['daily'].items() if d>='2026-10-24'}},ensure_ascii=False))
