import json, re, collections
from pathlib import Path

root=Path(__file__).parent
audit=json.loads((root/'category-report-audit.json').read_text(encoding='utf-8'))
catalog=json.loads((root/'excel-price-authority.json').read_text(encoding='utf-8'))
raw=json.loads((root/'category-report-raw.json').read_text(encoding='utf-8'))
old=json.loads((root/'analysis.json').read_text(encoding='utf-8'))
old_by={x['sku']:x for x in old['master']}
raw_by={r['contribution_sku#1.value']:r for r in raw['rows']}
def number(v):
    try:return float(v)
    except (TypeError,ValueError):return None
by_asin=collections.defaultdict(list)
for c in catalog:
    target=number(c['sale']) or number(c['list'])
    if target and target>0:
        for asin in set(re.findall(r'B0[A-Z0-9]{8}',str(c['vc'])+' '+str(c['sc']))):
            by_asin[asin].append((target,c))

operations=[];holds=[]
# Individually reviewed pack conflicts. ASIN identity alone does not establish pack size.
pack_conflicts={
 'B07B8JFJZY','B07B8DSVRB','B07B9W62T2','B01N6KX8DW','B01N6KXLJ5',
 'B01MZ1PQQ8','B07B8CP97S','B07TSD57BD','B07FD3X3NM',
 'B07KSX2V6M', # current 25 sheets versus source 20 sheets
 'B01MU5BGNQ', # x2 contribution cannot yet be reconciled with source pack
 'B07RP9BW5Z', # current pastel-only versus source pastel + neon
}
for r in audit['rows']:
    if r['parentage']=='Parent' or not r['asin']:continue
    changes={};reasons=[];sources=[]
    target=None
    candidates=by_asin[r['asin']]
    if len(set(p for p,c in candidates))==1:
        proposed,c=candidates[0]
        if r['price'] and r['effective_before_coupons'] and r['effective_before_coupons']>proposed+0.005:
            title=(r['title'] or '')
            suspect=(r['asin'] in pack_conflicts or r['sku']=='4A000' or len(title)<65 or title.startswith('4A Self-Stick Notes,') or r['price']>proposed*3 or re.search(r'1152\s*Pads|115200\s*Sheets|25\s*Packs',title,re.I))
            # A matched ASIN with a clearly conflicting bulk title needs manual identity review.
            if suspect:
                holds.append({'sku':r['sku'],'asin':r['asin'],'reason':'装量/规格冲突或当前描述不足，保留普通售价待核实','current':r['price'],'excel':proposed,'title':title,'source_title':c['title']})
            else:
                target=proposed;changes['MJ']=target
                if r['sale_active_by_dates'] and r['sale'] and r['sale']>target:changes['MN']=target
                reasons.append('同ASIN且当前标题的型号、装量与2026总表复核一致，下调偏高有效售价')
                sources.append(f"2026总表 {c['sheet']} 行{c['row']}; {c['sku']}")
    elif len(set(p for p,c in candidates))>1:
        holds.append({'sku':r['sku'],'asin':r['asin'],'reason':'同ASIN对应多个Excel价格，待核实','excel':[p for p,c in candidates]})
    effective=target if target is not None else r['effective_before_coupons']
    if effective is not None and r['b2b'] is not None and r['b2b']>effective+0.005:
        changes['MS']=effective;reasons.append('企业基础价不得高于当前普通有效价；暂不新增折扣')
    if effective is not None and r['minimum'] is not None and r['minimum']>effective+0.005:
        changes['ML']=effective;reasons.append('同步下调高于售价的自设最低价')
    if changes:
        operations.append({'sku':r['sku'],'asin':r['asin'],'product_type':r['product_type'],
             'cells':{'C':r['sku'],'D':r['product_type'],'E':'Edit (Partial Update)','L':'ASIN','M':r['asin'],**changes},
             'before':{'price':r['price'],'effective':r['effective_before_coupons'],'b2b':r['b2b'],'minimum':r['minimum']},
             'reasons':reasons,'sources':sources or ['2026-10-31 19:31分类商品报告当前价格']})

# Two diagnosed copy fixes. Both preserve product identity, quantity, and fulfillment.
title_fixes={
 '4A 60122×6-N':('4A Pop-up Page Flags, 6 Neon Colors, 6 Dispensers', 'Writable transparent flags for marking pages.'),
 '4A GMSCCR 012':('4A Self-Adhesive Coloring Paper Rolls, 30 x 500 cm, 2 Rolls','Continuous patterned coloring paper.'),
 '4A SCCR 012':('4A Self-Adhesive Coloring Paper Rolls, 30 x 500 cm, 2 Rolls','Continuous patterned coloring paper.')
}
current={x['sku']:x for x in audit['rows']}
for sku,(title,highlight) in title_fixes.items():
    if sku not in current:continue
    r=current[sku];op=next((x for x in operations if x['sku']==sku),None)
    if op is None:
        op={'sku':sku,'asin':r['asin'],'product_type':r['product_type'],'cells':{'C':sku,'D':r['product_type'],'E':'Edit (Partial Update)','L':'ASIN','M':r['asin']},'before':{},'reasons':[],'sources':['实时后台诊断面板及现有商品描述']};operations.append(op)
    op['cells'].update({'I':title,'J':highlight});op['reasons'].append('修正超长标题或禁用措词；文件审核要求仍须另行完成')
    assert len(title)<=75

# Original SKU/ASIN restoration, using documented prior offer prices where no exact pack price exists.
restore_specs=[
 ('AAAA 4A PSS 9-1 NYGrid','B07FKB3BRZ',15.99,'原SKU历史售价；2026总表无对应单卷价格，未冒用4卷价'),
 ('AAAA 4A PSS 9-1 NRGrid','B07FKF5V92',19.99,'4卷网格替芯；2026总表行117，且与原SKU历史售价一致'),
 ('AAAA 4A 305-Full Glue','B07FK9BYHW',14.99,'真实双包装；原SKU历史售价与同ASIN现有报价一致'),
 ('AAAA 4A PSS 9-1 NBGrid','B07FK8MF91',15.99,'原SKU历史售价；2026总表无对应单卷价格，未冒用4卷价'),
 ('AAAA 4A 2028-N','B07FKGPCQM',12.99,'24本三包装；同ASIN现有GM报价，低于三份单包表价合计14.97'),
 ('AAAA 4A 303-AC-holder','B07FKHHTYG',10.99,'2026总表行101及同ASIN现有GM报价；含便签标签的笔筒套装'),
 ('AAAA 4A 40622','B07FKFMJTL',9.99,'原SKU历史双包装售价；先恢复，最终多包装折扣另行核算'),
 ('AAAA 4A 6032','B07FK81CQ7',14.99,'现有同ASIN标题为6032x5；2026总表行150五套装'),
 ('AAAA 4A 40607','B07FK8CJ76',12.99,'原SKU历史三包装售价；未套用单包价或四包装价')]
restore=[]
missing=json.loads((root/'category-fba-coverage.json').read_text(encoding='utf-8'))['missing']
missing_map={s:f for f in missing for s in f['skus']}
for sku,asin,price,basis in restore_specs:
    assert missing_map[sku]['asin']==asin
    restore.append({'sku':sku,'asin':asin,'price':price,'units10_30':missing_map[sku]['available'],'basis':basis,
        'cells':{'A':sku,'B':'Create or Edit','E':asin,'M':'New','AL':'Fulfillment by Amazon (NA)','AQ':price,'CF':'No','DC':'Not Applicable'}})
assert len({x['sku'] for x in operations})==len(operations)
# Correct the diagnosed inverted percentage ladder; retain the existing 5/30-unit thresholds.
pss=next(x for x in operations if x['sku']=='4A PSS 9-3 2 Sets')
pss['cells'].update({'MX':'Percent','MY':5,'MZ':2,'NA':30,'NB':5})
pss['before']['quantity_tiers']='Percent: 5 units 24.99%; 30 units 22.49%'
pss['reasons'].append('企业数量优惠原值为百分比24.99/22.49，越买越贵；改为5件2%、30件5%，减少过度折扣')
assert sum(x['units10_30'] for x in restore)==298
result={'price_updates':operations,'price_holds':holds,'restore':restore,'counts':{
 'price_rows':len(operations),'base_price_changes':sum('MJ' in x['cells'] for x in operations),
 'business_price_changes':sum('MS' in x['cells'] for x in operations),'minimum_price_changes':sum('ML' in x['cells'] for x in operations),
 'title_changes':sum('I' in x['cells'] for x in operations),'restore_rows':len(restore),'restore_units_snapshot':298}}
(root/'urgent-batches-data.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result['counts'],ensure_ascii=False))
for o in operations:
    if 'MJ' in o['cells']:print(o['sku'],o['asin'],o['before']['effective'],'->',o['cells']['MJ'],o['sources'][0])
print('HOLDS',len(holds))
