import json
import re
import sys
from datetime import datetime
from decimal import Decimal as D, ROUND_HALF_UP
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
P = Path(__file__).parent
batch = int(sys.argv[1])
rows = json.loads((P / f'coupon-audit-agent-batch{batch}-assigned.json').read_text(encoding='utf-8'))
for row in rows:
    evidence = f'audit{batch}-live-{row["asin"]}.txt'
    snapshot = (P / evidence).read_text(encoding='utf-8')
    block = next(b for b in snapshot.split('- checkbox') if f'link "{row["sku"]}"' in b)
    def number(pattern):
        match = re.search(pattern, block)
        return float(match[1].replace(',', '')) if match else None
    row.update(
        price=number(r'- generic: 价格\n- generic: USD\n- generic: USD\n- textbox: "([\d.]+)"'),
        units_current=int(number(r'- generic: 可售\n- generic: "([\d,]+)"')),
        b2b=number(r'- generic: 企业商品价格\n- generic: \$([\d.]+)'),
        fba_fee=number(r'- generic: 亚马逊物流费用\n- generic: \$([\d.]+)'),
        total_fee=number(r'- generic: 总费用\n- generic: 总费用\n- generic: \$([\d.]+)'),
        minimum=number(r'- generic: 最低价格\n- generic: USD\n- generic: USD\n- textbox: "([\d.]+)"'),
        live_evidence=evidence,
    )
    assert row['price'] is not None and row['fba_fee'] is not None, row['asin']
    tier_file = P / f'audit{batch}-tiers-{row["asin"]}.txt'
    row['tiers'] = []
    if tier_file.exists():
        panel = tier_file.read_text(encoding='utf-8').split('- dialog')[1]
        assert '购买数量折扣类型' in panel, row['asin']
        assert 'radio "% 优惠" [checked]' in panel, 'Manual review needed for fixed-price tiers'
        row['tiers'] = [[int(q), float(v)] for q, v in re.findall(
            r'- spinbutton: "(\d+)"\n  - paragraph: 单位获得优惠\n  - textbox: "([\d.]+)"', panel)]
        row['tier_evidence'] = tier_file.name
    assert row['b2b'] is None or tier_file.exists(), 'Missing business evidence: ' + row['asin']
    row['audit_state'] = 'live_fba_price_stock_fee_and_business_discount_verified'
    row['coupon_scenarios'] = []
    for coupon in [5, 15]:
        regular = D(str(row['price']))
        base = D(str(min(row['price'], row['b2b'] or row['price'])))
        tier = D(str(max([v for q, v in row['tiers']] or [0])))
        unit = (base * (1-tier/100) * (1-D(coupon)/100)).quantize(D('.01'), rounding=ROUND_HALF_UP)
        cash = (unit*D('.85') - D(str(row['fba_fee'])) - regular*D('.025')).quantize(D('.01'), rounding=ROUND_HALF_UP)
        row['coupon_scenarios'].append({
            'coupon_percent': coupon,
            'regular_coupon_price': float((regular*(1-D(coupon)/100)).quantize(D('.01'), rounding=ROUND_HALF_UP)),
            'deepest_coupon_stacked_unit': float(unit),
            'cash_before_goods_inbound_storage_ads_refunds_fixed_fee': float(cash),
        })
    row['suggested_coupon_percent'] = 15 if row['age365plus'] > 0 or row['units_current']/max(row['units30_fba'] or 0, 1)>6 else 5
    row['suggested_reason'] = 'Aged or slow stock; provisional grouping for parent review' if row['suggested_coupon_percent']==15 else 'Mild coupon; preserve restored ordinary price'
    if row['coupon_scenarios'][1]['cash_before_goods_inbound_storage_ads_refunds_fixed_fee'] < 1.5:
        row['suggested_coupon_percent'] = 5
        row['suggested_reason'] = '15% leaves under1.50 before goods and other costs;5% is more conservative'
    if row['coupon_scenarios'][0]['cash_before_goods_inbound_storage_ads_refunds_fixed_fee'] < 1.5:
        row['suggested_coupon_percent'] = None
        row['suggested_reason'] = 'Even5% leaves under1.50; retain existing promotion and parent decide alternatives; no automatic additional coupon'
    row['selected_scenario'] = next((s for s in row['coupon_scenarios'] if s['coupon_percent']==row['suggested_coupon_percent']), None)
    print(row['asin'], row['price'], row['b2b'], row['tiers'], row['fba_fee'], row['units_current'], 'suggest', row['suggested_coupon_percent'], 'cash5/15', [s['cash_before_goods_inbound_storage_ads_refunds_fixed_fee'] for s in row['coupon_scenarios']])
result = {
    'scope': f'Batch{batch} additional ASINs; read-only; no coupon or price changes',
    'asof': datetime.now().isoformat(), 'rows': rows, 'count': len(rows),
    'stock': sum(r['units_current'] for r in rows),
    'assumptions': ['15% estimated referral + live FBA fee + coupon variable2.5% ordinary price',
        'Coupon conservatively stacked on deepest current business tier',
        'Not profit: excludes goods,inbound,storage,ads,refunds,fixed fee',
        '1.50 caution line is audit recommendation,not a user-imposed threshold',
        'Parent checks coupon eligibility; never lower ordinary price to unlock coupon'],
}
(P / f'coupon-expansion-batch{batch}-readonly-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
(P / f'coupon-expansion-batch{batch}-readonly-review.txt').write_text('\n'.join(
    f"{r['asin']} | {r['sku']} | stock {r['units_current']} | price {r['price']} | b2b {r['b2b']} | tiers {r['tiers']} | FBA {r['fba_fee']} | suggested {r['suggested_coupon_percent']}% | cash5/15 {[s['cash_before_goods_inbound_storage_ads_refunds_fixed_fee'] for s in r['coupon_scenarios']]}" for r in rows), encoding='utf-8')
all_rows = json.loads((P/'coupon-expansion-candidates-current-work.json').read_text(encoding='utf-8-sig'))
excluded = {'B00SMEFFRE'}
for file in P.glob('coupon-expansion-batch*-*review.json'):
    excluded.update(r['asin'] for r in json.loads(file.read_text(encoding='utf-8-sig'))['rows'])
remaining = [r for r in all_rows if r['asin'] not in excluded]
following = remaining[:12]
(P/f'coupon-audit-agent-batch{batch+1}-assigned.json').write_text(json.dumps(following, ensure_ascii=False, indent=2), encoding='utf-8')
print('TOTAL', result['stock'], 'REMAINING',len(remaining),'NEXT',[(r['asin'],r['sku']) for r in following])
