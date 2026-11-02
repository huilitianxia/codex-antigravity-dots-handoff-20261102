"""Summarize saved, visible Coupon eligibility rows without hidden browser data."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
rows = []
pages = []
for path in sorted(ROOT.glob('coupon-fullscan-page[0-9][0-9].txt')):
    text = path.read_text(encoding='utf-8')
    page = int(re.search(r'page(\d+)', path.name)[1])
    pages.append(page)
    starts = list(re.finditer(r"^    - 'row .*?ASIN:.*$", text, re.M))
    for i, match in enumerate(starts):
        block = text[match.start():starts[i+1].start() if i+1 < len(starts) else text.index('- \'heading "已选择', match.start())]
        header = match[0]
        identity = re.search(r'generic: "ASIN: ([A-Z0-9]{10})"', block)
        sku_match = re.search(r'generic: "SKU: (.+)"', block)
        assert identity and sku_match, (page, header)
        asin, sku = identity[1], sku_match[1]
        stock = re.search(r'gridcell "([\d,]+) 件数 (AFN|MFN)"', block)
        prices = re.findall(r'gridcell "\$([\d,]+\.\d{2})"', block)
        assert stock and prices, (page, sku)
        reason = header.split('SKU: ' + sku, 1)[1].split(' 销量 :', 1)[0].strip()
        reasons = [reason] if reason else []
        checked = bool(re.search(r'checkbox \[checked\]', block))
        disabled = bool(re.search(r'checkbox.*\[disabled\]', block))
        units = re.search(r'售出商品数量 : ([\d,]+|[-])', header)
        rows.append({'page': page, 'asin': asin, 'sku': sku, 'price': float(prices[-1].replace(',', '')),
                     'units_current': int(stock[1].replace(',', '')), 'channel': stock[2],
                     'sales_units_ui': int(units[1].replace(',', '')) if units and units[1] != '-' else None,
                     'selected': checked, 'disabled': disabled, 'reasons': reasons,
                     'selectable': not disabled and not reasons,
                     'visible_row': header.strip()})
keys = [(x['asin'], x['sku']) for x in rows]
assert len(keys) == len(set(keys)), 'Duplicate offer across saved pages; pagination may have shifted'
out = {'pages': pages, 'rows': rows, 'offer_rows': len(rows), 'asins': len({x['asin'] for x in rows}),
       'fba_rows': sum(x['channel'] == 'AFN' for x in rows),
       'fba_units': sum(x['units_current'] for x in rows if x['channel'] == 'AFN')}
(ROOT / 'coupon-fullscan-parsed.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k != 'rows'}, ensure_ascii=False))
print('Unselected FBA candidates:', json.dumps([{k:v for k,v in x.items() if k not in {'visible_row','reasons'}} for x in rows if x['channel']=='AFN' and x['selectable'] and not x['selected']], ensure_ascii=False))
