import json
from pathlib import Path
from decimal import Decimal as D
R=Path(__file__).parent
source={x['asin']:x for x in json.loads((R/'fba-potential-from-orders.json').read_text(encoding='utf8'))['rows']}
items=[
('B07QWKWWP2','PSS 9-1 NYNRx2',162,'19.99','7.36','6.25'),
('B00SMEENOU','5037树形',140,'6.99','4.31','2'),
('B07R2KSW34','PSS 9-1 Grid-NYNGx2',130,'22.99','7.81','6.875'),
('B07RP9K6KV','6031x4',77,'11.99','5.43','6'),
('B0F2YHTD8T','彩虹便签',52,'12.99','5.58',None),
('B0F2TJ7ZL7','笔筒+便签',44,'19.99','7.64',None)]
rows=[]
for a,n,q,p,f,c in items:
    p,f=D(p),D(f);c=D(c) if c else None
    s=source[a]
    discount=p*D('.15');fee=p*D('.025')
    # Conservative: retain currently displayed Amazon total fee rather than
    # assuming referral fees fall with discounted proceeds. Coupon variable
    # fee is conservatively applied to undiscounted item price.
    cash=p-discount-f-fee
    monthly=D(str(s['estimated_month_storage']))+D(str(s['estimated_aged_surcharge']))
    rows.append({'asin':a,'name':n,'qty':q,'price':float(p),'coupon_price':float((p-discount).quantize(D('.01'))),
                 'current_amazon_fee':float(f),'coupon_variable_fee_conservative':float(fee),
                 'cash_before_goods_inbound_refunds_ads_fixed':float(cash),
                 'fob_proxy':float(c) if c is not None else None,
                 'margin_after_fob_before_inbound_other':float(cash-c) if c is not None else None,
                 'discount_for_all':float(discount*q),'cash_for_all_before_goods_etc':float(cash*q),
                 'monthly_storage_plus_aged_estimate':float(monthly),
                 'monthly_carry_per_unit':float(monthly/q),
                 'months_carry_equivalent_coupon_increment':float((discount+fee)/(monthly/q)) if monthly else None,
                 'units30':s['units30']})
out={'assumptions':['15% customer discount; no other discount stacking in this scenario',
 'Coupon variable fee conservatively 2.5% of pre-discount price',
 'Current Amazon total per-unit estimated fee retained unchanged, conservative',
 'FOB from 2026 workbook is only proxy, not actual landed inventory cost',
 'Exclude inbound/customs/refunds/ads/fixed coupon fee; never label cash as profit',
 'Storage/aged estimates from10-30 are approximate reference, not actual deducted or guaranteed avoidable'],
 'rows':rows,'total_qty':sum(r['qty'] for r in rows),
 'discount_all':sum(r['discount_for_all'] for r in rows),
 'cash_all_before_goods_etc':sum(r['cash_for_all_before_goods_etc'] for r in rows),
 'monthly_carry_estimate_all':sum(r['monthly_storage_plus_aged_estimate'] for r in rows),
 'units_last30_all':sum(r['units30'] for r in rows)}
(R/'coupon-economics.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(out,ensure_ascii=False,indent=2))
