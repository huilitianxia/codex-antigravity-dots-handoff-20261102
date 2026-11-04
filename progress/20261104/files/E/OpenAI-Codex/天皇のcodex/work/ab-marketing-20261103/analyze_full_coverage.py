from pathlib import Path
import collections
import json
import re

ROOT = Path(__file__).parent
DATA = ROOT / 'full-coverage'

def read(name):
    return json.loads((DATA / name).read_text(encoding='utf-8-sig'))

def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def norm(value):
    value = str(value).upper().replace('×', 'X')
    value = re.sub(r'^(?:AAAA\s*)?(?:4A\s*)?', '', value)
    value = re.sub(r'^(?:GM|SC|SN)+', '', value)
    value = re.sub(r'(?:-?FBA|-?FBM)$', '', value)
    value = value.replace('LINEX', 'LX').replace('LINE X', 'LX')
    value = value.replace('REFILL', 'REFIL').replace('REFIL', 'REFILL')
    return re.sub(r'[^A-Z0-9]', '', value)

sc = read('source-sc-current-20261103.json')
fba = read('fba-current-20261103.json')
hist = read('vc-sales-historical-current-source.json')['rows']
vc = read('source-vc309.json')
masters = read('source-master-rows.json')
fba_by_sku = {row['sku']: row for row in fba}

for row in sc:
    row['quantity_numeric'] = number(row['quantity'])
    fba_row = fba_by_sku.get(row['seller-sku'])
    row['available_fba'] = number(fba_row['afn-fulfillable-quantity']) if fba_row else None
    row['buyable_fba'] = number(fba_row['afn-onhand-buyable-quantity']) if fba_row else None
    row['currently_stocked'] = (
        row['status'] == 'Active'
        and (
            (row['fulfillment-channel'] == 'DEFAULT' and (row['quantity_numeric'] or 0) > 0)
            or (row['fulfillment-channel'] == 'AMAZON_NA' and (row['buyable_fba'] or 0) > 0)
        )
    )
    row['model_norm'] = norm(row['seller-sku'])

models = []
for historical in hist:
    direct = [row for row in sc if row['asin1'] == historical['asin']]
    aliases = [row for row in sc if row not in direct and row['model_norm'] == norm(historical['sku'])]
    master_candidates = []
    for master in masters:
        master_asins = master['vc_asins'] + master['sc_asins']
        if historical['asin'] in master_asins or norm(historical['sku']) == norm(master['sku']):
            for row in sc:
                if row['asin1'] in master_asins and row not in direct + aliases + master_candidates:
                    master_candidates.append(row)
    models.append({
        **historical,
        'exact_asin_offers': direct,
        'exact_model_alias_offers': aliases,
        'official_master_candidates': master_candidates,
        'stocked_exact_asin': [row for row in direct if row['currently_stocked']],
        'stocked_aliases': [row for row in aliases if row['currently_stocked']],
        'stocked_master_candidates': [row for row in master_candidates if row['currently_stocked']],
    })

summary = {
    'historical_styles': len(hist),
    'current_sc_rows': len(sc),
    'current_active_rows': sum(row['status'] == 'Active' for row in sc),
    'current_stocked_rows': sum(row['currently_stocked'] for row in sc),
    'historical_styles_stocked_exact_asin': sum(bool(row['stocked_exact_asin']) for row in models),
    'historical_styles_stocked_model_or_master': sum(
        bool(row['stocked_exact_asin'] + row['stocked_aliases'] + row['stocked_master_candidates'])
        for row in models
    ),
    'old_asin_stocked': len({offer['asin1'] for row in models for offer in row['stocked_exact_asin']}),
    'all_linked_candidate_stocked_asins': len({
        offer['asin1'] for row in models
        for offer in row['stocked_exact_asin'] + row['stocked_aliases'] + row['stocked_master_candidates']
    }),
}

(DATA / 'historical-current-crosswalk.json').write_text(
    json.dumps({'summary': summary, 'rows': models}, ensure_ascii=False, indent=2), encoding='utf8'
)
(DATA / 'current-sc-with-fba.json').write_text(json.dumps(sc, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps(summary, ensure_ascii=False))
for row in models[:60]:
    print(json.dumps({
        'rank': row['rank_original'], 'sku': row['sku'], 'units': row['total_units'],
        'exact_stock': [offer['seller-sku'] + '@' + offer['asin1'] for offer in row['stocked_exact_asin']],
        'alias_stock': [offer['seller-sku'] + '@' + offer['asin1'] for offer in row['stocked_aliases']],
        'master_stock': [offer['seller-sku'] + '@' + offer['asin1'] for offer in row['stocked_master_candidates']],
    }, ensure_ascii=False))
