import json, re
from pathlib import Path

base = Path(__file__).parent
load = lambda n: json.loads((base / n).read_text(encoding='utf-8-sig'))
all_records = load('precision-ad-execution.json') + load('approved-ad-execution-20261103.json')
records = {r['group']: r for r in all_records if r.get('status') == 'launched'}
b4 = load('optimization-30315-current-keywords.json')['rows']
rows, changes = [], []

def terms(g):
    if g == 'B4': return b4
    v = records[g]['verification']
    return v.get('targets', v.get('dom_targets', {}).get('rows', []))

def group_id(g):
    m = re.search(r'/ad-groups/(\d+)/', records[g]['verification']['ads_url'])
    if m: return m[1]
    ids = set()
    for f in base.glob(g + '-*adgroups*.txt'):
        ids.update(re.findall(r'/ad-groups/(\d+)/(?:ads|targeting)', f.read_text(encoding='utf-8-sig')))
    assert len(ids) == 1, (g, ids)
    return next(iter(ids))

def add(g, entity, operation, **fields):
    row = {'Product': 'Sponsored Products', 'Entity': entity, 'Operation': operation,
           'Campaign ID': str(records[g]['publicCampaignId'])}
    if entity == 'Keyword': row['Ad Group ID'] = group_id(g)
    row.update(fields)
    rows.append(row)

def keyword(g, text):
    matches = [t for t in terms(g) if t.get('cells', {}).get('target', '').split('\n')[0] == text]
    assert len(matches) == 1, (g, text)
    return matches[0]

budgets = {'B5': 1, 'B6': 1, 'RE302': 1, 'B12': 6, 'B4': 7, 'R002': 5, 'B2': 5, 'RE303': 4, 'R006': 4}
for g, after in budgets.items():
    add(g, 'Campaign', 'Update', **{'Daily Budget': after})
    changes.append({'group': g, 'type': 'budget', 'before': records[g]['daily'], 'after': after, 'asin': records[g]['asin']})

bids = {
    'B4': {'3x3 sticky notes bulk': .65, 'colored sticky notes 3x3': .65, 'sticky notes 3x3 assorted colors': .65},
    'B12': {'0.6 inch sticky note roll': .50, 'full adhesive sticky note roll 0.6 inch': .50, '6 color sticky note rolls with dispenser': .45},
    'R002': {'desktop sticky notes organizer set': .40, 'sticky notes and index flags organizer': .40},
    'B2': {'full adhesive sticky notes': .55, 'sticky notes full back adhesive': .55, 'fully adhesive sticky notes': .50, 'full sticky notes': .40},
    'RE303': {'full sticky back post it notes': .70},
    'B1': {'lined sticky notes 5x8': .55, 'large yellow lined sticky notes': .60},
    'R006': {'1.5x2 sticky notes 24 pads': .35, '1.5 x 2 sticky notes assorted colors': .35},
}
for g, values in bids.items():
    for text, after in values.items():
        t = keyword(g, text)
        assert t['cells']['status'] == '进行中'
        before = float(re.search(r'US\$([\d.]+)', t['cells']['bid'])[1])
        add(g, 'Keyword', 'Update', **{'Keyword ID': str(t['id']), 'Bid': after})
        changes.append({'group': g, 'type': 'bid', 'keyword': text, 'keyword_id': str(t['id']), 'before': before, 'after': after})

pauses = {
    'B5': ['mini sticky notes bulk', 'small colored sticky notes'],
    'B6': ['mini sticky notes', 'mini sticky notes assorted colors', 'small sticky notes bulk', 'sticky notes 32 pads'],
    'RE302': ['full stick post it notes'],
    'R008': ['large lined sticky notes 5 x 8'],
}
for g, texts in pauses.items():
    for text in texts:
        t = keyword(g, text)
        add(g, 'Keyword', 'Update', **{'Keyword ID': str(t['id']), 'State': 'paused'})
        changes.append({'group': g, 'type': 'pause-keyword', 'keyword': text, 'keyword_id': str(t['id'])})

new_terms = [
    ('B4', '3x3 sticky notes assorted colors', 'phrase', .50),
    ('B12', 'sticky note roll dispenser', 'phrase', .50),
    ('R002', 'sticky note organizer set', 'phrase', .40),
    ('B2', 'fully adhesive sticky notes', 'phrase', .40),
    ('R006', 'mini sticky notes', 'phrase', .30),
    ('RE303', 'full stick post it notes', 'exact', .55),
    ('RE302', 'full adhesive sticky notes 2x3', 'phrase', .25),
    ('B1', 'lined sticky notes', 'exact', .55),
    ('B6', 'small sticky notes 1 3/8 x 1 7/8', 'exact', .30),
]
for g, text, match, bid in new_terms:
    assert not any(t.get('cells', {}).get('target', '').split('\n')[0] == text
                   and (t['cells'].get('matchType') == '精准') == (match == 'exact') for t in terms(g)), (g, text)
    add(g, 'Keyword', 'Create', **{'State': 'enabled', 'Bid': bid, 'Keyword Text': text, 'Match Type': match})
    changes.append({'group': g, 'type': 'new-keyword', 'keyword': text, 'match': match, 'bid': bid})

ui = [{'group': 'R008', 'type': 'budget', 'before': 3, 'after': 1}, {'group': 'R007', 'type': 'budget', 'before': 3, 'after': 1}]
new_total = 97 + sum(c['after'] - c['before'] for c in changes + ui if c['type'] == 'budget')
assert new_total == 100
assert len({(r['Entity'], r['Operation'], r['Campaign ID'], r.get('Keyword ID'), r.get('Keyword Text')) for r in rows}) == len(rows)
assert all(r['Campaign ID'].isdigit() for r in rows)
assert all(not r.get('Bid') or 0 < r['Bid'] <= .70 for r in rows)
result = {'status': 'prepared-not-submitted', 'US_period': '2026-11-03',
          'historical_period': '2026-10-04 through2026-11-03', 'budget_before': 97, 'budget_after': new_total,
          'ui_already_applied': ui, 'changes': changes, 'rows': rows,
          'scope': 'Existing US campaigns only. No offer, inventory, dates, bidding-strategy or placement changes.',
          'notes': ['Multi-ASIN search-term sales are not attributed to each member ASIN.',
                    '5082/5084/5088 share a retail variation family. Main5082 remains5/day.',
                    '301x24/30132/354832 share a retail family. Main24pads4/day, secondary1/day.',
                    '302/303/305Full family shared. Retain specific302 and emphasize converting303exact terms.',
                    '4012 contribution using FOB3.25, reference outbound9.99,15%referral,.50misc is only.693 before ads at11.99+4.99. No increase pending actual costs.',
                    'Budget increases are bounded acquisition experiments, not proof of positive profit.']}
(base / 'optimization-approved-plan-US20261103.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'rows': len(rows), 'budget_rows': len(budgets), 'bid_updates': sum(map(len, bids.values())),
                  'pauses': sum(map(len, pauses.values())), 'creates': len(new_terms), 'before': 97, 'after': new_total}))
