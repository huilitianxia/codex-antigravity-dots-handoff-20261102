"""Read-only evidence join for stocked FBA routing and six factual copy repairs."""
import json, re, collections
from pathlib import Path
P=Path(__file__).parent
def rd(n): return json.loads((P/n).read_text(encoding='utf-8'))
aud=rd('category-report-audit.json')['rows']; scan=rd('coupon-fullscan-parsed.json')['rows']; fees=rd('fba-live-fees.json')
orders={x['asin']:x for x in rd('fba-potential-from-orders.json')['rows']}
pairs=rd('page-identity-excel-pairs.json'); draft=rd('execution-batch-data.json')
priority={x['sku'] for x in draft['operations'] if any(k in x['cells'] for k in ('MJ','MN','MS'))}
fee={x['sku']:x for x in fees}; ab=collections.defaultdict(list); sb=collections.defaultdict(list)
for x in aud: ab[x['asin']].append(x)
for x in scan: sb[x['asin']].append(x)
pairby=collections.defaultdict(list)
for p in pairs:
    aa=set(re.findall(r'B[A-Z0-9]{9}',str(p.get('vc_asin'))+' '+str(p.get('sc_asin'))))
    if len(aa)>1:
        for a in aa: pairby[a].append((p,aa))
rows=[]
for s in scan:
    if s['channel']!='AFN' or s['units_current']<=0: continue
    a=s['asin']; f=fee.get(s['sku'],{}); o=orders.get(a,{})
    m=[x for x in sb[a] if x['channel']=='MFN' and x['units_current']>0]
    dormant=[x for x in ab[a] if 'Merchant' in str(x.get('channel')) and x['sku'] not in {z['sku'] for z in m}]
    candidates=[]
    for p,aa in pairby[a]:
        for other in sorted(aa-{a}):
            of=[x for x in fees if x['asin']==other]; oo=orders.get(other,{})
            candidates.append({'asin':other,'source_excel_row':p['row'],'source_title':p['title'],'upc_equal':p.get('vc_upc')==p.get('sc_upc'),'vc_upc':p.get('vc_upc'),'sc_upc':p.get('sc_upc'),'active_offers':[{'sku':x['sku'],'channel':x['channel'],'quantity':x['units_current'],'sales_units_ui':x['sales_units_ui']} for x in sb[other]],'fba_units':sum(x['available'] for x in of),'units30_fba':oo.get('units30'),'historical_ratings_unverified':oo.get('historic_ratings_unverified',[])})
    route='KEEP_CURRENT_ASIN_DUAL_OFFER' if m else 'KEEP_CURRENT_ASIN_VERIFY_EXISTING_MFN' if dormant else 'KEEP_CURRENT_ASIN_MFN_IDENTITY_REQUIRED'
    action='保留原FBA SKU/FNSKU；同ASIN有货MFN已在扫描中，核对两报价买家可买及包装一致' if m else '保留原FBA SKU/FNSKU；同ASIN存在目录MFN记录但未见本次有货报价，核查库存与启售' if dormant else '保留原FBA SKU/FNSKU；没有同ASIN有货MFN证据，先核实实物配置后决定是否新增MFN报价'
    blockers=['实时子ASIN评分与评论归属尚未全量核实；历史评分不得直接用于迁移决策','所有新增价格/优惠冻结；本清单不授权迁移FBA库存或修改ASIN']
    if candidates: blockers.append('存在Excel同款候选但UPC/装量/胶型须验证；当前不据此合并或宣称最佳页')
    if a=='B01LVTWP7Q': route='301_PARALLEL_EXCEPTION';action='保留FBA老页与B07KPF9PFX的FBM并行；遵循用户例外，暂不强并'
    if a in ('B07F295DPC','B07FKG29KB'): route='30315_CASE_PENDING';action='保留原报价并跟进case22923307871；不得直接改FBA ASIN'
    if a=='B08DKJ2K3T': action='PSS32x6同ASIN双报价作为目标结构；保留两履约，另修错误变体标签'
    if a=='B07QXJWDPL': action='保留当前有货页与18.99既有促销；旧页B07T42DY5K缺货且约3.0分不足以支持迁移'
    if a in draft.get('holds',{}): blockers.append(draft['holds'][a])
    rows.append({'priority04':s['sku'] in priority,'sku':s['sku'],'asin':a,'fnsku':f.get('fnsku'),'fba_units_scan':s['units_current'],'fba_units_fee_snapshot':f.get('available'),'title_current':f.get('title'),'catalog_titles':[x['title'] for x in ab[a]],'catalog_label_issues':[{'sku':x['sku'],'size':x['size'],'parent':x['parent']} for x in ab[a] if re.search(r'\(Pack \d+\)',str(x.get('size')))],'price_snapshot':f.get('price'),'fba_fee':f.get('fba_fee'),'total_fee':f.get('total_fee'),'units30_fba':o.get('units30'),'age365plus':o.get('age365plus'),'historical_ratings_unverified':o.get('historic_ratings_unverified',[]),'coupon_selectable':s['selectable'],'coupon_reasons':s['reasons'],'active_same_asin_mfn':[{'sku':x['sku'],'quantity':x['units_current'],'price':x['price'],'sales_units_ui':x['sales_units_ui']} for x in m],'catalog_mfn_unverified':[{'sku':x['sku'],'status':x.get('status_report'),'quantity':x.get('quantity'),'offer_stop_passed':x.get('offer_stop_passed')} for x in dormant],'other_asin_identity_candidates':candidates,'route':route,'retain_asin':a,'action':action,'blockers':blockers,'evidence':['category-report-audit.json','coupon-fullscan-page%02d.txt'%s['page'],f.get('source'),'fba-potential-from-orders.json']})
rows.sort(key=lambda r:(not r['priority04'],-r['fba_units_scan'],r['sku']))
stats={'rows':len(rows),'asins':len({r['asin'] for r in rows}),'priority04_rows':sum(r['priority04'] for r in rows),'fba_units_scan':sum(r['fba_units_scan'] for r in rows),'routes':dict(collections.Counter(r['route'] for r in rows)),'with_active_same_asin_mfn':sum(bool(r['active_same_asin_mfn']) for r in rows),'with_cross_asin_candidates':sum(bool(r['other_asin_identity_candidates']) for r in rows)}
out={'scope':'本地全量证据对应，不是全量实时最佳页面认证；价格方案冻结','stats':stats,'rows':rows}
(P/'samepage-stocked-fba-execution.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['有货FBA逐SKU页面与双报价执行台账','统计：'+json.dumps(stats,ensure_ascii=False),'扫描129有货FBA报价覆盖全部128 ASIN。优先列04草案29条；所有新增价格方案冻结。','同ASIN报价存在由本次完整快照支持；跨ASIN只列身份候选，不自动认定同款/最佳页。','']
for r in rows:
    lines += [f"{'[04优先] ' if r['priority04'] else ''}{r['sku']} | {r['asin']} | FBA {r['fba_units_scan']} | 近30天FBA {r['units30_fba']} | {r['route']}",r['action'],'同ASIN有货MFN：'+json.dumps(r['active_same_asin_mfn'],ensure_ascii=False),'跨ASIN候选：'+json.dumps(r['other_asin_identity_candidates'],ensure_ascii=False),'阻碍：'+'；'.join(r['blockers']),'证据：'+', '.join(x for x in r['evidence'] if x),'']
(P/'samepage-stocked-fba-execution.txt').write_text('\n'.join(lines),encoding='utf-8')
# Six residual errors: validate each factual sentence against saved source fields.
raw=rd('category-report-raw.json'); rb={x['contribution_sku#1.value']:x for x in raw['rows']}
cols={c:k for c,k in zip(('AS','AT','AU','AV','AW'),[f'bullet_point[marketplace_id=ATVPDKIKX0DER][language_tag=en_US]#{i}.value' for i in range(1,6)])}
six=[x for x in draft['operations'] if all(c in x['cells'] for c in cols)]
copy=[]
for x in six:
    source=rb[x['sku']]; cat=next(a for a in aud if a['sku']==x['sku'])
    copy.append({'sku':x['sku'],'asin':x['asin'],'source_title':cat['title'],'source_bullets':{c:source.get(k) for c,k in cols.items()},'proposed_bullets':{c:x['cells'][c] for c in cols},'review':'原标题/第一点支持数量尺寸颜色；去掉无证据可回收、比较黏性、免运费及价格声明。未提交。','attribute_conflicts':{'size':cat['size'],'number_of_items':source.get('number_of_items[marketplace_id=ATVPDKIKX0DER]#1.value')},'blocker':'标题与现有number_of_items/假Pack标签语义冲突；本轮仅改五点，属性另列核实。'})
(P/'six-bullet-factual-review.json').write_text(json.dumps(copy,ensure_ascii=False,indent=2),encoding='utf-8')
assert len(rows)==129 and len({r['fnsku'] for r in rows})==129
assert sum(r['priority04'] for r in rows)==29 and len(six)==6
print(json.dumps(stats,ensure_ascii=False))
