import json,re
from pathlib import Path
from datetime import datetime

root=Path(__file__).parent
audit=json.loads((root/'v1-price-incident-audit.json').read_text(encoding='utf8'))
rows=[r for r in audit['records'] if r['status']=='待复核：有货MFN大降幅']
assert len(rows)==8
mapping={
 '4A ST303X12NZ':('303','Big size delivery',1000001,0.522,'Kilograms'),
 '4A GM406SL-10':('406sl','Heavy delivery',1000001,1.066,'Kilograms'),
 '4A GM40612-L':('40612l','Heavy delivery',1000001,1.406,'Kilograms'),
 '4A GM40612':('40612','Heavy delivery',1000001,1.43,'Kilograms'),
 '4A GM608SL-5':('608sl','Heavy delivery',26.35,1.061,'Kilograms'),
 '4A GM404SL-15':('404sl','Heavy delivery',27.12,2.45,'Pounds'),
 '4A GM6031x4':('6031','Migrated Template',5.49,None,None),
 '4A GM6032x5':('6032','Migrated Template',5.64,None,None),
}
rates={'Heavy delivery':(9.99,6.99),'Big size delivery':(10.99,8.99),'Migrated Template':(4.99,4.99)}
freight={'N':4.99,'B':9.99,'H':11.99,'2H':22.99}
outrows=[]
for r in rows:
    tag,template,ship,weight,unit=mapping[r['sku']]
    src=r['source'][0]
    assert abs(float(src['sale'])-r['new'])<.001
    evidence=(root/f'mfn-incident-{tag}-before.txt').read_text(encoding='utf8')
    assert r['sku'] in evidence
    assert f'+ ${ship:,.2f}' in evidence
    d=dict(sku=r['sku'],asin=r['asin'],old_base_price=r['old'],current_base_price=r['new'],base_matches_excel_sale=True,source=src,shipping_template=template,shipping_display=ship,shipping_source=f'mfn-incident-{tag}-before.txt',shipping_verified_again=(tag=='406sl'),reported_quantity=r['quantity'],excel_freight_code=src['freight_code'],excel_freight_amount=freight[src['freight_code']],excel_base_plus_freight=round(r['new']+freight[src['freight_code']],2),base_price_decision='保留当前基础价；符合已选Excel折后价/另收运费口径，不因降幅大自动回退',shipping_decision='报价/运费异常待修复' if ship==1000001 else '实际收运费；未发现百万异常，Heavy费率偏高另审',catalog_package_weight=weight,catalog_package_weight_unit=unit)
    if weight:
        lbs=weight*2.20462262185 if unit=='Kilograms' else weight
        base,perlb=rates[template]
        d.update(catalog_weight_pounds=round(lbs,6),formula_shipping_estimate_raw_weight=round(base+perlb*lbs,2),formula_shipping_estimate_rounded_lb=round(base+perlb*round(lbs,2),2),weight_evidence=f'mfn8-{tag}-offer'+('-all' if tag=='406sl' else '')+'.txt',seller_package_weight_input='blank; platform catalog value shown separately')
    if ship!=1000001:d['current_base_plus_displayed_shipping']=round(r['new']+ship,2)
    if tag=='6031':d['source_caution']='Excel list 9.99 < sale 11.99; preserve selected sale column, do not silently replace with lower list value.'
    outrows.append(d)

out=dict(generated_local=datetime.now().isoformat(),scope='只读诊断；未修改共享配送模板、SKU库存、价格、重量，也未提交编辑页。',base_price_finding='8/8基础价逐一匹配原Excel折后列，另有N/B/H运费代码；没有证据将8条都归为FBA式误降价。',template_live_checks={
 'Heavy delivery':dict(mainland48='9.99/order + 6.99/lb; street and PO box; SSA standard shipping',AK_HI_PR='49.99/order + 8.99/lb',weight_tiers='none visible; linear rate',evidence='mfn8-heavy-template-live.txt'),
 'Big size delivery':dict(mainland48='10.99/order + 8.99/lb; street and PO box; CA/TX 2-3 days, others 2-4 days',AK_HI_PR='not present in displayed coverage',weight_tiers='none visible; linear rate',evidence='mfn8-big-template-live.txt'),
 'Migrated Template':dict(mainland48='4.99/order + 4.99/lb',AK_HI_PR='9.99/order + 9.99/lb',weight_tiers='none visible; linear rate',evidence='mfn8-migrated-template-live.txt')},rows=outrows,
 confirmed=['All three shipping templates display finite linear shipping rates, no million-dollar rate or threshold.', 'All four million-shipping SKUs have plausible platform catalog package weights, not a catalog weight of zero or hundreds of thousands of pounds.', 'Both normal Heavy controls have blank seller weight contribution boxes too, so blank seller input alone does not distinguish the failure.', 'GM404SL-15: 9.99+6.99*2.45=27.12 exactly matches display. GM608SL-5: 1.061kg approximately 2.34lb, gives 26.35 after 2dp lb rounding, matching display.', 'Current GM406SL-10 inventory: active MFN quantity466/base17.49/shipping1000001; corresponding FBA quantity0. SKU Central shipping --. Buyer page at existing NY10001 destination says currently unavailable.'],
 diagnosis='已确认报价/运费输出异常；不能归因为共享模板直接设百万费率、目录无包装重量或kg单位本身。失败占位/报价可配送性链路异常是符合多页面证据的推测，具体内部原因尚未确定。买家页缺货与异常并存，不证明两者因果。',
 limitations=['Only GM406SL-10 shipping display was refreshed again in this subtask; other seven shipping values use saved same-session evidence.', 'Catalog weights are platform values, not newly weighed warehouse measurements.', 'No authenticated quote-engine internal status/error code available from the visible UI.', 'No checkout performed. No proof buyers are actually asked to pay 1000001.', 'No shipping repair has been executed or verified.'],
 minimal_next_steps=['保留8条已匹配Excel折后基础价，不回退为旧的疑似含运费总价，也不把运费清零。', '针对4个百万异常SKU，先核后台报价/配送资格诊断及SKU模板关联；GM406SL-10优先，保存现有库存、价格、模板与目录重量证据。', '若诊断明确指出缺卖家包装重量，先用实际发货包裹称重复核，仅补该SKU重量和单位；正常SKU也为空，不能仅据空框批量补。', '若诊断明确指向SKU模板映射或缓存，先仅对一个异常SKU重新关联已核准模板/或等费率独立副本，验证纽约10001可购和真实运费恢复后再扩至其余3款；不要改共享模板费率。', '对于608/404的26.35/27.12高但可计算运费，另做实际运费成本核算后才调整独立模板。Excel H11.99与当前Heavy线性费率并不相同，不能宣称现有运费已按Excel执行。', '若可见诊断仍无错误码，准备GM406SL-10 support case事实附件：库存466，价格17.49，模板9.99+6.99/lb，目录1.066kg，理论约26.42，库存显示1000001，SKU Central --，前台不可售。联系卖家支持需要主流程明确授权后再发送。'])
(root/'mfn8-shipping-diagnosis.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
lines=['8款MFN价格与运费只读诊断',out['scope'],'结论：'+out['base_price_finding'],'根因边界：'+out['diagnosis'],'','SKU | 当前基础价 | 运费显示 | 模板 | 目录包装重量 | 判断']
for r in outrows:lines.append(f"{r['sku']} | ${r['current_base_price']:.2f} | ${r['shipping_display']:,.2f} | {r['shipping_template']} | {r['catalog_package_weight']} {r['catalog_package_weight_unit']} | 保留基础价；{r['shipping_decision']}")
lines+=['','已确认证据',*out['confirmed'],'','下一步最小范围',*out['minimal_next_steps'],'','局限',*out['limitations']]
(root/'mfn8-shipping-diagnosis.txt').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps({'rows':len(outrows),'keep_base_prices':8,'million_shipping':sum(r['shipping_display']==1000001 for r in outrows),'estimates':[(r['sku'],r.get('formula_shipping_estimate_rounded_lb')) for r in outrows]},ensure_ascii=False,indent=2))
