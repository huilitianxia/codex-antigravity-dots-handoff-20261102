"""Read-only preparation: inventory, unit economics, and precise-ad drafts."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import math
import re
import sys
import openpyxl

sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).parent
DATA = ROOT / 'full-coverage'
MASTER_PATH = Path(r'D:/4A/01_便签店运营_2026-10/01_官方上传表格_核心在用/【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx')

def read(name, base=DATA):
    return json.loads((base / name).read_text(encoding='utf-8-sig'))

def num(v):
    if v is None or v == '': return None
    try: return float(str(v).replace(',', ''))
    except (ValueError, TypeError): return None

def canon(v):
    v = str(v or '').upper().replace('×', 'X')
    v = re.sub(r'^AAAA\s*', '', v)
    v = re.sub(r'^4A\s*', '', v)
    v = re.sub(r'(?:-?FBA|-?FBM|-GM)$', '', v)
    v = re.sub(r'-B[0-9A-Z]{3,9}$', '', v)
    while re.match(r'^(GM|SC|SN|VC|FBM)[ -]*', v):
        v = re.sub(r'^(GM|SC|SN|VC|FBM)[ -]*', '', v)
    v = v.replace('LINE', 'L').replace('REFIL', 'REFILL')
    return re.sub(r'[^A-Z0-9]', '', v)

def asins(v): return re.findall(r'B[0-9A-Z]{9}', str(v or '').upper())

def pack(title):
    t = re.sub(r'(?<=\d),(?=\d{3}\b)', '', str(title or '').lower()).replace(',', ' ')
    pads = [int(x) for x in re.findall(r'(\d+)\s*pads?\b', t)]
    pad = max(pads) if pads else None
    per_pack = re.search(r'(\d+)\s*pads?\s*/\s*(?:pack|box)', t)
    packs = [int(x) for x in re.findall(r'(\d+)\s*(?:packs|boxes)\b', t)]
    if per_pack and packs:
        pad = max(pad or 0, int(per_pack[1]) * max(packs))
    sheets = [int(x) for x in re.findall(r'(\d+)\s*sheets?\s*total', t)]
    sheets += [int(x) for x in re.findall(r'total\s*(\d+)\s*sheets?', t)]
    total = max(sheets) if sheets else None
    if total is None:
        per_pack_sheets = re.search(r'(\d+)\s*sheets?\s*/\s*pack', t)
        if per_pack_sheets: total = int(per_pack_sheets[1]) * (max(packs) if packs else 1)
    if total is None and pad:
        unit = re.search(r'(\d+)\s*sheets?\s*/\s*(?:pad|color)', t)
        if unit: total = int(unit[1]) * pad
    return {'pads':pad, 'sheets':total}

sc = read('current-sc-with-fba.json')
fba = read('fba-current-20261103.json')
hist = read('vc-sales-historical-current-source.json')['rows']
cross = read('historical-current-crosswalk.json')['rows']
bulk = read('advertising-bulk-current.json')
sp = bulk['商品推广活动']
fees = read('fba-live-fees.json', ROOT.parent / '4a-reclass-20261031')
scope = read('ads-102-asins-aggregated.json', ROOT)
coupons = read('coupon-coverage.json', ROOT)['coupons']
final = read('execution-final.json', ROOT)
live_prices = read('priority-live-prices.json', ROOT)
cashflow = json.loads(Path(r'D:/4A/00_当前工作区_202611/high_stock_cashflow_plan.json').read_text(encoding='utf-8-sig'))
with Path(r'D:/下载文件/284701020757.txt').open(encoding='utf-8-sig',newline='') as f:
    age_rows=[r for r in csv.DictReader(f,delimiter='\t') if r.get('marketplace')=='US']
age_by_fn=collections.defaultdict(list)
for r in age_rows: age_by_fn[r['fnsku']].append(r)

book = openpyxl.load_workbook(MASTER_PATH, read_only=True, data_only=True)
masters = []
for row_number, r in enumerate(book['Sheet1'].iter_rows(values_only=True), 1):
    if row_number == 1 or not r[0] or not str(r[0]).strip().startswith('4A'): continue
    masters.append({'row':row_number, 'sku':r[0], 'vc_asins':asins(r[2]), 'sc_asins':asins(r[4]),
        'title':r[6], 'shipping_class':r[7], 'fob':num(r[9]), 'amazon_cost':num(r[10]),
        'list_price':num(r[11]), 'sale_2026':num(r[12]), 'weight_lb':num(r[14]),
        'pads_source':num(r[32]), 'pack':pack(r[6]), 'norm':canon(r[0])})
book.close()

fb = {r['sku']:r for r in fba}
fee_by = {r['sku']:r for r in fees}
scope_by = {r['asin']:r for r in scope}
coupon_by = {a:c['pct']/100 for c in coupons for a in c['asins']}
promo_by = {r['sku']:r for r in final['promotion']['items']}
campaigns = {r['广告活动编号']:r for r in sp if r['实体层级']=='广告活动'}
groups = {r['广告组编号']:r for r in sp if r['实体层级']=='广告组'}

def active(r):
    return bool(r and r.get('状态')=='已启用'
        and (not r.get('开始日期') or str(r['开始日期'])<='20261103')
        and (not r.get('结束日期') or str(r['结束日期'])>='20261103'))

exact_groups = {r['广告组编号'] for r in sp if r['实体层级']=='关键词' and r.get('匹配类型')=='精准'
    and active(r) and active(campaigns.get(r['广告活动编号'])) and active(groups.get(r['广告组编号']))}
ads_by_sku = collections.defaultdict(list)
perf_by_asin = collections.defaultdict(lambda:collections.defaultdict(float))
for r in sp:
    if r['实体层级']!='商品广告': continue
    ads_by_sku[r['SKU']].append(r)
    for key in ['展示量','点击量','花费','销量','订单数量']:
        perf_by_asin[r['ASIN（仅供参考）']][key] += num(r.get(key)) or 0

history_by_sku = collections.defaultdict(list)
for h in cross:
    for key in ['stocked_exact_asin','stocked_aliases','stocked_master_candidates']:
        for r in h[key]: history_by_sku[r['seller-sku']].append((h,key))
for r in sc:
    if '*' not in r['seller-sku'] or history_by_sku.get(r['seller-sku']): continue
    base=canon(r['seller-sku'].split('*')[0])
    for h in hist:
        if canon(h['sku'])==base:
            history_by_sku[r['seller-sku']].append((h,'model_multipack'))

shipping_by_sku = {}
for group in live_prices:
    for r in group['rows']:
        m = re.search(r'运费\s*\n\+ \$([\d.]+)', r['text'])
        if m: shipping_by_sku[r['sku']] = {'amount':float(m[1]),'date':group['checked_at']}

stocked = [r for r in sc if r['currently_stocked']]
stocked_by_asin = collections.defaultdict(list)
for r in stocked: stocked_by_asin[r['asin1']].append(r)

def match_master(row):
    norm = canon(row['seller-sku'])
    current_pack = pack(row['item-name'])
    candidates = []
    for m in masters:
        asin_match = row['asin1'] in m['vc_asins']+m['sc_asins']
        model_match = norm == m['norm']
        linked = any(h['asin'] in m['vc_asins']+m['sc_asins'] or canon(h['sku'])==m['norm']
                     for h,key in history_by_sku.get(row['seller-sku'],[]))
        if not (asin_match or model_match or linked): continue
        score = 80*model_match + 60*asin_match + 20*linked
        if current_pack['pads'] and m['pack']['pads']:
            score += 15 if current_pack['pads']==m['pack']['pads'] else -10
        if current_pack['sheets'] and m['pack']['sheets']:
            score += 15 if current_pack['sheets']==m['pack']['sheets'] else -10
        candidates.append((score,m))
    if not candidates: return None, None, '未匹配成本表'
    candidates.sort(key=lambda x:(-x[0],x[1]['row']))
    chosen = candidates[0][1]
    multiplier = 1.0
    note = '型号或ASIN匹配'
    mp = chosen['pack']
    ratios=[]
    if current_pack['pads'] and mp['pads']: ratios.append(current_pack['pads']/mp['pads'])
    if current_pack['sheets'] and mp['sheets']: ratios.append(current_pack['sheets']/mp['sheets'])
    if ratios and any(abs(x-1)>0.01 for x in ratios):
        ratio = max(ratios)
        if all(abs(x-ratio)<0.01 for x in ratios) and ratio >= 1 and abs(ratio-round(ratio))<0.01:
            multiplier=ratio
            note='当前标题为主表'+str(int(ratio))+'倍包装，成本折算待实物核对'
        else:
            multiplier=None
            note='当前与主表包装数量冲突'
    if len(candidates)>1 and candidates[1][0]==candidates[0][0] and candidates[1][1]['fob']!=chosen['fob']:
        multiplier=None
        note='多个成本行同分且成本不一致'
    sku_multiplier=re.search(r'\*(\d+)$',row['seller-sku'])
    if sku_multiplier and multiplier==1 and canon(row['seller-sku'].split('*')[0])==chosen['norm']:
        multiplier=float(sku_multiplier[1])
        note='SKU声明'+sku_multiplier[1]+'倍包装，实物和标题须核对'
    return chosen,multiplier,note

def choose_history(row, master):
    matches=history_by_sku.get(row['seller-sku'],[])
    if not matches: return None, '未匹配VC销量'
    def key(v):
        h,relation=v
        exact = h['asin']==row['asin1']
        model = canon(h['sku'])==canon(row['seller-sku'])
        master_model = master and canon(h['sku'])==master['norm']
        return (-int(exact),-int(model),-int(bool(master_model)),h['rank_original'])
    h,relation=sorted(matches,key=key)[0]
    labels={'stocked_exact_asin':'VC原ASIN','stocked_aliases':'同型号另页面','stocked_master_candidates':'主表关联页面','model_multipack':'历史型号的倍数包装'}
    return h, labels[relation]

def contribution(price, cost, fba_fee, coupon):
    if any(v is None for v in [price,cost,fba_fee]): return None
    net=price*(1-coupon)
    return net-max(0.30,net*0.15)-cost-fba_fee-net*(0.025 if coupon else 0)

rows=[]
for r in stocked:
    m,mult,cost_match=match_master(r)
    h,history_match=choose_history(r,m)
    sku=r['seller-sku']; a=r['asin1']; is_fba=r['fulfillment-channel']=='AMAZON_NA'
    fi=fb.get(sku); fee=fee_by.get(sku)
    valid_ads=[d for d in ads_by_sku[sku] if active(d) and active(campaigns.get(d['广告活动编号']))
        and active(groups.get(d['广告组编号'])) and d['资格状态（仅供参考）']=='符合条件']
    old = bool(h or a in scope_by)
    # Existing promotion is represented separately; the base price is not silently overwritten.
    promo=promo_by.get(sku)
    price=num(r['price']); effective_price=min(price,promo['price']) if promo else price
    cost_fob=m['fob']*mult if m and m['fob'] is not None and mult is not None else None
    cost_amazon=m['amazon_cost']*mult if m and m['amazon_cost'] is not None and mult is not None else None
    ff=num(fee.get('fba_fee')) if is_fba and fee else None
    coupon=coupon_by.get(a,0)
    c=contribution(effective_price,cost_fob,ff,coupon) if is_fba else None
    proposed_price=price
    if is_fba and c is not None and c<0.50 and not promo:
        # Aim for one dollar of ad-before-other-cost contribution, respecting price review.
        required=(cost_fob+ff+1.0)/((1-coupon)*(0.85-(0.025 if coupon else 0)))
        proposed_price=math.ceil(required+0.01)-0.01
    if sku=='4A 301x12-N': proposed_price=7.99
    if promo: proposed_price=price
    proposed_contribution=contribution(min(proposed_price,promo['price']) if promo else proposed_price,cost_fob,ff,coupon) if is_fba else None
    explicit_holds=[]
    if cost_fob is None: explicit_holds.append(cost_match)
    if mult and mult!=1: explicit_holds.append('包装倍数待核')
    if a=='B01MZ1PQQ8': explicit_holds.append('两盒规格须回读确认，不能按单盒成本')
    if a=='B01N9HHKRM': explicit_holds.append('当前为48包整箱，不能当单包24本')
    if a=='B01N2YLQ23': explicit_holds.append('广告商品名300本与库存页12本不一致')
    if is_fba and not fee: explicit_holds.append('缺FBA费用')
    if not is_fba: explicit_holds.append('缺实际发货成本')
    perf=perf_by_asin[a]
    demand_rows=age_by_fn.get(fi['fnsku'],[]) if fi else []
    shipped_set={num(x['units-shipped-t30']) for x in demand_rows if num(x['units-shipped-t30']) is not None}
    shipped_30=next(iter(shipped_set)) if len(shipped_set)==1 else None
    existing_exact=any(d['广告组编号'] in exact_groups for d in valid_ads)
    current_ad_eligible=any(d['资格状态（仅供参考）']=='符合条件' for d in ads_by_sku[sku])
    row={
        'sku':sku,'asin':a,'title':r['item-name'],'fulfillment':'FBA' if is_fba else 'FBM',
        'old_candidate':old,'history_rank':h['rank_original'] if h else None,'history_sku':h['sku'] if h else None,
        'history_units':h['total_units'] if h else None,'history_2023':h['years'].get('2023') if h else None,
        'history_2024':h['years'].get('2024') if h else None,'history_match':history_match,
        'fba_available':num(fi['afn-fulfillable-quantity']) if fi else None,
        'fba_buyable':num(fi['afn-onhand-buyable-quantity']) if fi else None,
        'fba_reserved':num(fi['afn-reserved-quantity']) if fi else None,
        'fba_transfer':num(fi['afn-fc-transfer-quantity']) if fi else None,
        'fba_t30_shipped':shipped_30,'fba_t30_snapshot':'2026-10-30' if demand_rows else None,
        'fbm_declared':r['quantity_numeric'] if not is_fba else None,
        'price':price,'effective_price':effective_price,'shipping_template':r['merchant-shipping-group'],
        'shipping_confirmed':0.0 if is_fba else shipping_by_sku.get(sku,{}).get('amount'),
        'shipping_reference':0.0 if is_fba else {'N':4.99,'B':9.99,'H':11.99,'2H':22.99}.get(str(m['shipping_class']) if m else ''),
        'shipping_actual_cost':None,'extra_unit_cost':None,'master_row':m['row'] if m else None,
        'master_sku':m['sku'] if m else None,'master_sale':m['sale_2026'] if m else None,
        'master_weight_lb':m['weight_lb']*mult if m and m['weight_lb'] is not None and mult is not None else None,
        'pack_multiplier':mult,'cost_match':cost_match,'fob_cost':cost_fob,'amazon_cost':cost_amazon,
        'fba_fee':ff,'fee_date':'2026-10-31' if fee else None,'business_price_snapshot':num(fee.get('b2b')) if fee else None,
        'coupon_pct':coupon,'coupon_variable_fee':0.025 if coupon else 0,
        'scheduled_promo':promo['price'] if promo else None,
        'promo_warning':'4012需≤10.03/404评分预警，待回读' if a in ['B01M3N310M','B01MXYQPE1'] and promo else None,
        'existing_sp':bool(valid_ads),'existing_exact':existing_exact,
        'existing_campaigns':sorted({d['广告活动名称（仅供参考）'] for d in valid_ads}),
        'last_known_ad_eligible':current_ad_eligible,'ad_impressions':perf['展示量'],'ad_clicks':perf['点击量'],
        'ad_spend':perf['花费'],'ad_sales':perf['销量'],'ad_orders':perf['订单数量'],
        'proposed_price':proposed_price,'fob_contribution_current':c,'fob_contribution_proposed':proposed_contribution,
        'holds':explicit_holds,'asin_url':'https://www.amazon.com/dp/'+a,
        'shipping_origin':'Dallas warehouse' if not is_fba else 'Amazon FBA',
    }
    rows.append(row)

# Advertising is a page-level decision; SKU-level inventory/cost remains separate.
by_asin=collections.defaultdict(list)
for r in rows: by_asin[r['asin']].append(r)

plans=[]
for a,offers in by_asin.items():
    if not any(r['old_candidate'] for r in offers): continue
    offers.sort(key=lambda r:(r['fob_cost'] is None, bool(r['holds']) and r['fulfillment']=='FBA',
        r['fulfillment']!='FBA',-(r['fba_available'] or 0),-(r['fbm_declared'] or 0)))
    target=offers[0]
    stock=max([r['fbm_declared'] or 0 for r in offers]+[r['fba_available'] or 0 for r in offers])
    rank=min([r['history_rank'] for r in offers if r['history_rank'] is not None] or [999])
    if any(r['existing_exact'] for r in offers):
        action='修复已有精准利润' if any(r['fob_contribution_current'] is not None and r['fob_contribution_current']<0.50 for r in offers) else '维护已有精准'
    elif target['fob_cost'] is None or any('包装' in t or '整箱' in t or '不一致' in t or '规格' in t for t in target['holds']): action='先核规格或成本'
    elif target['fulfillment']=='FBM': action='核运费后新增精准'
    elif target['proposed_price']>target['price']: action='调价后新增精准'
    else: action='回读后新增精准'
    launch_stock=(target['fba_available'] or 0) if target['fulfillment']=='FBA' else (target['fbm_declared'] or 0)
    daily=10 if rank<=10 and launch_stock>=100 else 6 if rank<=25 and launch_stock>=50 else 4 if launch_stock>=20 else 2
    c=target['fob_contribution_proposed']
    planned_cvr=(target['ad_orders']/target['ad_clicks']) if target['ad_clicks']>=20 and target['ad_orders']>0 else 0.10
    bid=round(min(0.45,max(0.02,(c or 0)*planned_cvr*0.7)),2) if c is not None and c>0 else None
    if action in ['维护已有精准','修复已有精准利润']: daily=0;bid=None
    plans.append({'asin':a,'target_sku':target['sku'],'history_rank':None if rank==999 else rank,
        'history_sku':target['history_sku'],'history_units':target['history_units'],'action':action,
        'skus':[r['sku'] for r in offers],'daily_draft':daily,'bid_draft':bid,'planned_cvr':planned_cvr,
        'cvr_basis':'该ASIN导出期SP订单/点击' if target['ad_clicks']>=20 and target['ad_orders']>0 else '测试假设10%，不是已证实转化率',
        'stock_sort':stock,'test_days':7,'status':'草案未上传',
        'history_original':any(o['history_match']=='VC原ASIN' for o in offers)})
plans.sort(key=lambda r:(r['history_rank'] is None,r['history_rank'] or 999,not r['history_original'],-r['stock_sort'],r['asin']))

summary={
    'historical_styles':len(hist),'stocked_skus':len(rows),'stocked_fba_skus':sum(r['fulfillment']=='FBA' for r in rows),
    'stocked_fbm_skus':sum(r['fulfillment']=='FBM' for r in rows),'stocked_asins':len(by_asin),
    'old_candidate_asins':len(plans),'old_candidate_skus':sum(r['old_candidate'] for r in rows),
    'actions':dict(collections.Counter(r['action'] for r in plans)),
    'fba_fee_matched':sum(r['fulfillment']=='FBA' and r['fba_fee'] is not None for r in rows),
    'cost_matched':sum(r['fob_cost'] is not None for r in rows),
    'fba_current_contribution_calculated':sum(r['fob_contribution_current'] is not None for r in rows),
    'fba_current_negative_foB':sum(r['fob_contribution_current'] is not None and r['fob_contribution_current']<0 for r in rows),
    'source_asof_beijing':'2026-11-03 08:38库存、08:41广告导出',
}
output={'summary':summary,'sku_rows':rows,'plans':plans,'history':hist,'masters':masters,
    'fee_rules':{'referral_rate':0.15,'minimum_referral':0.30,'coupon_variable_rate':0.025,'coupon_fixed_per_campaign':5,
        'referral_source':'https://sell.amazon.com/pricing',
        'coupon_source':'https://sellercentral.amazon.com/seller-forums/discussions/t/05d936ee-b79d-451d-b03c-827df41df300'},
    'cost_basis_status':'FOB和Amazon Cost均为原表参考列，尚未确认实际单套货本。未含未提供的头程、仓储、退货和税费。',
    'shipping_facts':{'fbm_origin':'美国达拉斯仓','sea_lead_days':30,'air_lead_days':7,
        'source':'用户本轮明确：FBM从达拉斯发货；非急缺海运约一个月，急货空运预留七天。',
        'actual_unit_cost_status':'未找到实际货本、海空运单套分摊、达拉斯出库包材派送账单。'},
    'source_files':{
        'master':str(MASTER_PATH),'inventory':read('current-source-provenance.json'),
        'advertising':str(Path(r'D:/下载文件/4A_ALL_OLD_PREMIUM_AUDIT_20261103_30D.xlsx')),
        'fba_fee':'10月31日逐SKU后台费用快照，执行前需回读',
    }}
(DATA/'vc-execution-preparation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
for p in plans[:32]:
    t=next(r for r in rows if r['sku']==p['target_sku'])
    print(p['history_rank'],p['history_sku'],p['asin'],p['target_sku'],p['action'],
          'FBA',t['fba_available'],'FBM',t['fbm_declared'],'cost',t['fob_cost'],
          'margin',None if t['fob_contribution_current'] is None else round(t['fob_contribution_current'],2),
          'price',t['price'],'draft',t['proposed_price'],'holds',t['holds'])
