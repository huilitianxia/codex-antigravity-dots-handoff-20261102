"""Read only the visible inventory page captures saved during this audit."""
import json
import re
from pathlib import Path
from urllib.parse import unquote_plus

ROOT = Path(__file__).parent
rows = []
for path in sorted(ROOT.glob('fba-fees-page[0-9].txt')):
    text = path.read_text(encoding='utf-8')
    for block in re.split(r'\n- checkbox\n', text):
        asin = re.search(r'- generic: ASIN\n- generic: (B[A-Z0-9]{9})', block)
        sku = re.search(r'/url: /skucentral\?mSku=([^&\n]+)', block)
        if not asin:
            continue
        assert sku, path
        def num(pattern):
            m = re.search(pattern, block)
            return float(m[1].replace(',', '')) if m and m[1] else None
        def price(label):
            return num(r'- generic: '+label+r'\n(?:- generic: [^\n]*\n){0,6}- textbox(?:: "([\d.]+)")?')
        fnsku = re.search(r'- generic: FNSKU\n- generic: (\w+)', block)
        title = re.search(r'- link ["\'](.+)["\']:\n  - /url: https://www.amazon.com/dp/'+asin[1], block)
        r = {'asin':asin[1], 'sku':unquote_plus(sku[1]), 'fnsku':fnsku[1] if fnsku else None,
             'title':title[1] if title else None,
             'available':num(r'- generic: 可售\n- generic: "?([\d,]+)"?'),
             'price':price('价格'), 'minimum':price('最低价格'), 'maximum':price('最高价格'),
             'sale_visible':num(r'- generic: 促销价格\n- generic: \$([\d,.]+)'),
             'b2b':num(r'- generic: 企业商品价格\n- generic: \$([\d,.]+)'),
             'fba_fee':num(r'- generic: 亚马逊物流费用\n- generic: \$([\d,.]+)'),
             'total_fee':num(r'- generic: 总费用\n(?:- generic: 总费用\n)?- generic: \$([\d,.]+)'),
             'sales_units_ui':num(r'- generic: 售出件数\n- generic: "?([\d,]+)"?'),
             'source':path.name}
        assert r['price'] is not None and r['available'] is not None, r
        rows.append(r)
assert len({r['sku'] for r in rows}) == len(rows)
(ROOT/'fba-live-fees.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'rows':len(rows), 'positive_rows':sum(r['available']>0 for r in rows),
                  'unique_positive_fnsku':len({r['fnsku'] for r in rows if r['available']>0}),
                  'available_sum':sum(r['available'] for r in rows),
                  'missing_fees':[r['sku'] for r in rows if r['fba_fee'] is None]},ensure_ascii=False))
