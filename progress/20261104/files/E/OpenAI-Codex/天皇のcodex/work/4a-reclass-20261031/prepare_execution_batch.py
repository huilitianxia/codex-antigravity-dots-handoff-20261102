"""Prepare reviewed partial-update cells and a complete Coupon exception ledger."""
import collections
import json
import re
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).parent
def read(name):
    return json.loads((ROOT/name).read_text(encoding='utf-8'))
raw = read('category-report-raw.json')
audit = read('category-report-audit.json')['rows']
scan = read('coupon-fullscan-parsed.json')['rows']
fees = read('fba-live-fees.json')
orders = read('fba-potential-from-orders.json')['rows']
raw_by = {r['contribution_sku#1.value']:r for r in raw['rows']}
aud_by = {r['sku']:r for r in audit}
fee_by = {r['sku']:r for r in fees}
order_by = {r['asin']:r for r in orders}
headers = raw['headers']
col_key = {get_column_letter(i):key for i,(_,key) in enumerate(headers,1)}
assert 'bullet_point' in col_key['AW'] and '#5.value' in col_key['AW']
assert 'discounted_price' in col_key['MN'] and 'start_at' in col_key['MO']
assert 'quantity_discount_plan' in col_key['MX']

def money(x):
    return float(Decimal(str(x)).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))

operations = {}
def op_for(sku, asin):
    if sku not in operations:
        product_type = aud_by.get(sku,{}).get('product_type')
        if not product_type:
            types = {r['product_type'] for r in audit if r['asin']==asin}
            assert types == {'SELF_STICK_NOTE'}, (sku,asin,types)
            product_type = 'SELF_STICK_NOTE'
        operations[sku] = {'sku':sku,'asin':asin,'cells':{'C':sku,'D':product_type,'E':'Edit (Partial Update)','L':'ASIN','M':asin},'before':{},'reasons':[],'sources':[]}
    return operations[sku]

receipt = openpyxl.load_workbook('D:/下载文件/03-catalog-errors-consolidated-processing-summary.xlsm',data_only=False)['Template']
deleted_skus = set()
flagged_bullet_skus = set()
for row in receipt.iter_rows(min_row=7):
    sku = row[3].value
    for cell in row:
        msg = cell.comment.text if cell.comment else ''
        if 'SKU is not in the catalog or has been deleted' in msg:
            deleted_skus.add(sku)
        if 'Bullet Point contains false/promotional claims' in msg:
            flagged_bullet_skus.add(sku)

ui_asins = {'B07FKJNNHP','B07FK8ML41','B01N6J0VZO','B07F2FCHLK','B07F2CWVQ7','B07FKL115P'}
promo_pattern = re.compile(r'free.*shipping|orders? over|high quality.*good price', re.I)
def fifth_bullet(title):
    t = title.lower()
    if 'coloring' in t:
        return 'Continuous paper rolls for coloring and drawing.'
    if 'label' in t and ('chalkboard' in t or 'circle' in t or 'dot label' in t):
        return 'Use the labels to identify and organize items.'
    if 'whiteboard' in t or 'dry erase' in t:
        return 'A writing surface for notes, planning and presentations.'
    if 'easel' in t or 'flip chart' in t or 'meeting pad' in t:
        return 'Use the large sheets to write and display meeting notes.'
    if 'roll' in t or 'tape' in t:
        return 'Cut a section from the roll for notes and page marking.'
    if 'flag' in t or 'file tab' in t or 'page marker' in t or 'page maker' in t:
        return 'Use the tabs to mark pages and organize documents.'
    if 'holder' in t or 'dispenser' in t and 'pop-up notes' not in t:
        return 'Keep note pads organized and within reach on your desk.'
    return 'Use these note pads for written reminders, lists and messages.'

copy_exclusions=[]
for sku,r in raw_by.items():
    old = r.get(col_key['AW'])
    if not promo_pattern.search(str(old or '')):
        continue
    a=aud_by[sku]
    if sku in deleted_skus or a['asin'] in ui_asins:
        copy_exclusions.append({'sku':sku,'asin':a['asin'],'reason':'旧回执SKU不存在警告，待核实' if sku in deleted_skus else '此前Chrome已处理的ASIN，本批避免覆盖'})
        continue
    assert a['asin'] and a['parentage']!='Parent'
    op=op_for(sku,a['asin'])
    op['before']['AW']=old
    op['cells']['AW']=fifth_bullet(a['title'] or '')
    op['reasons'].append('移除第5要点中的免运费、优质低价等促销性声明')
    op['sources'].append('10/31分类商品报告同SKU第5要点')

rewrites={
 '4A 4013':[
  'Includes 18 sticky note pads with 1,900 sheets in total.',
  'Assorted note sizes are supplied together in one PP storage box.',
  'Neon assorted colors help separate different notes and reminders.',
  'Use the note pads for written messages, lists and planning.',
  'Keep the assorted pads together in the included storage box.'],
 '4A 404SL-15':[
  'Each note measures 4 x 4 inches and has printed writing lines.',
  'Includes 15 pads with 80 sheets per pad, 1,200 sheets in total.',
  'Five colors: purple, green, yellow, light orange and orange.',
  'Self-stick sheets for notes, reminders and written messages.',
  'Lined pages provide a guide for lists and handwritten notes.'],
 '4A 406SL-10':[
  'Each note measures 4 x 6 inches and has printed writing lines.',
  'Includes 10 pads with 80 sheets per pad, 800 sheets in total.',
  'Five colors: purple, green, yellow, light orange and orange.',
  'Self-stick sheets for notes, reminders and written messages.',
  'Lined pages provide a guide for lists and handwritten notes.'],
 '4A 60121-10x2':[
  'Each page flag measures 0.5 x 1.75 inches.',
  'Includes two sets of 10 flag pads with 35 flags per pad, 700 flags total.',
  'Neon assorted colors help distinguish marked sections.',
  'Writable transparent flags for marking pages in books and documents.',
  'Pop-up dispensers keep the flags together for page marking.'],
 '4A 60174-Sign Herex2':[
  'Includes two packs with eight dispensers per pack.',
  'Each dispenser contains 50 flags, for 800 flags in total.',
  'Neon assorted colors help distinguish marked sections.',
  'Writable transparent flags for marking pages and paperwork.',
  'Use the flags to draw attention to signature locations and reference pages.'],
 '4A 6032x5':[
  'Each divider tab measures 1.5 x 2 inches.',
  'Includes 120 tabs in four assorted colors.',
  'Writable transparent tabs for labeling documents and folders.',
  'Use different colors to distinguish sections and reference pages.',
  'Repositionable tabs help organize books, paperwork and files.'],
}
assert set(rewrites)==flagged_bullet_skus-deleted_skus
for sku,bullets in rewrites.items():
    r=aud_by[sku];op=op_for(sku,r['asin'])
    for col,value in zip(['AS','AT','AU','AV','AW'],bullets):
        op['before'][col]=raw_by[sku].get(col_key[col])
        op['cells'][col]=value
    op['reasons'].append('回执将Bullet Point整体标为促销/不实声明，重写全部5点为现有资料支持的产品事实')
    op['sources'].append('03处理报告及同SKU原有标题、要点')

# Sale price decisions retain real ordinary prices and never manufacture a list price.
# None sale = preserve existing sale; business tiers can still be improved.
sale_specs={
 'B07QXJWDPL':(None,18.49,'保留前台已显示的18.99划线促销及原结束日，补企业阶梯'),
 'B0FBG138ND':(10.44,9.49,'427件但近30天123件，采用约5%温和促销并保留较低企业价'),
 'B07FK975YB':(11.04,10.99,'372件、近30天49件，约15%促销及企业批量优惠'),
 'B0F2TKL2P5':(16.19,15.99,'338件、近30天75件，约10%促销及企业阶梯'),
 'B07QXJZKHC':(18.69,18.49,'180件、近30天11件，约15%促销及企业阶梯'),
 'B07FK9BYHW':(12.74,12.49,'60件且56件库龄超过365天，约15%促销'),
 'B01LVXOCU2':(7.99,7.99,'24本装清仓；与同装量301双盒协调，保留原ASIN'),
 'B07FK8LN8D':(7.99,7.99,'真实24本2400张；修正同装量价格差，非12本单包价'),
 'B0F7LW38FX':(14.99,14.99,'48本装低于两份24本7.99的合计15.98'),
 'B0DYNL5SMR':(20.39,19.99,'33件、近期未出单，约15%促销，同步最低价'),
 'B01MSZM8IC':(12.74,12.74,'23件且近期未出单，按当前同SKU普通价约15%促销'),
 'B07RQ7G57D':(16.14,16.14,'23件均为365天以上库龄，约15%促销'),
 'B07QXJX2BV':(14.44,14.44,'两个原FBA SKU合计32件，按同ASIN统一约15%促销；家族错误另修'),
 'B0DY12Y8FK':(24.69,24.69,'22件且近30天9件，采用约5%温和促销'),
 'B01MU0JZHU':(9.34,9.34,'21件均为365天以上库龄，约15%促销'),
 'B07RP9MSSG':(16.14,16.14,'21件均为365天以上库龄，约15%促销'),
 'B07RT4GTLZ':(54.39,54.39,'19件均为365天以上库龄，约15%促销；FBM运费另查'),
 'B01N9LOE7P':(9.34,9.34,'18件均为365天以上库龄，约15%促销'),
 'B0F28LXKKF':(30.59,30.59,'真实四包24本横线款，17件均为365天以上库龄，约15%促销'),
 'B07RP8HYCJ':(16.99,16.99,'16件均为365天以上库龄，约15%促销'),
 'B07RQ7JMV9':(11.04,11.04,'16件中14件为365天以上库龄，约15%促销'),
 'B07FKGPCQM':(11.04,11.04,'真实三包24本，13件365天以上库龄，约15%促销'),
 'B07M855HVB':(33.99,33.99,'真实四包48本循环色，12件365天以上库龄，约15%促销'),
 'B07WDWY3B2':(16.14,16.14,'8件中7件365天以上库龄，约15%促销'),
 'B0756ZY4F8':(10.19,10.19,'8件365天以上库龄，按现有商品报价约15%促销'),
 'B07RQ7B9QR':(20.39,20.39,'真实12本横线款，6件365天以上库龄，约15%促销'),
 'B0CPM4CP6T':(14.27,14.27,'3件小库存，按实时最低报价14.27修复竞争力；不同ASIN配置仍单独保留'),
}
holds={
 'B07FK7PBHJ':'SKU写NGGrid但当前标题写NYNR双卷套装，先核实实物配置和页面身份，暂不促销放量',
 'B00SMEEVKQ':'售价4.99、企业价4.49及已有数量优惠，保留低价，不为达到Coupon门槛涨价',
 'B07QXJYTZ7':'近30天179件、当前约60件，保留现有价格及企业优惠，优先补货',
 'B07F295DPC':'30315已有15.99促销，目录合并Case 22923307871待审，本批保留价格',
 'B08DKFCQBB':'双包装描述、原始总张数及FBM报价不一致，先核实包装后定价',
 'B07TSD57BD':'同ASIN存在单双包价格来源冲突，保留现价待核实',
 'B00SMEDVEI':'只余4件且低价4.49，保留现价，避免过度压缩回款',
 'B01MATRHXM':'只余3件、无365天以上库龄，保留当前10.49及8.73最低价',
}
price_fix={'B07QWKYQV7':27.39}
blocked_fba=[r for r in scan if r['channel']=='AFN' and r['units_current']>0 and not r['selectable']]
assert {r['asin'] for r in blocked_fba} == set(sale_specs)|set(holds)|set(price_fix)
assert not (set(sale_specs)&set(holds))
price_rows=[]
for r in blocked_fba:
    sku,asin=r['sku'],r['asin'];f=fee_by[sku]
    if asin in holds:
        continue
    op=op_for(sku,asin)
    if asin in price_fix:
        new=price_fix[asin]
        op['cells']['MJ']=new;op['before']['MJ']=f['price']
        op['reasons'].append('Coupon明确要求普通价不高于27.39，先修报价，上传生效后重试资格')
        op['sources'].append('本轮Coupon全扫及当前FBA报价')
        price_rows.append({'sku':sku,'asin':asin,'qty':f['available'],'regular':f['price'],'sale_before':f['sale_visible'],'sale_new':None,'regular_new':new,'business_before':f['b2b'],'business_new':None,'tiers':[], 'fba_fee':f['fba_fee'],'cash_after_platform':money(new-money(new*.15)-f['fba_fee']),'minimum_cash':money(new-money(new*.15)-f['fba_fee']),'reason':op['reasons'][-1]})
        continue
    new,biz,reason=sale_specs[asin]
    effective=new if new is not None else (f['sale_visible'] or f['price'])
    if new is not None:
        assert new<f['price']
        for col,v in [('MN',new),('MO','2026-10-31'),('MP','2026-11-30')]:
            op['cells'][col]=v;op['before'][col]=raw_by.get(sku,{}).get(col_key[col])
        if f['minimum'] is not None and f['minimum']>new:
            op['cells']['ML']=new;op['before']['ML']=f['minimum']
    # Retain any genuinely lower live business price.
    biz=min(biz,f['b2b']) if f['b2b'] is not None else biz
    assert biz<=effective
    op['cells']['MS']=biz;op['before']['MS']=f['b2b']
    if f['available']>=50 or asin in {'B07QXJX2BV','B07FK8LN8D'}:
        tiers=[(2,3),(5,5),(10,8)]
    elif f['available']>=10:
        tiers=[(3,2),(5,4)]
    else:
        tiers=[(2,2)]
    if asin=='B0CPM4CP6T':
        tiers=[]
    if tiers:
        op['cells']['MX']='Percent';op['before']['MX']=raw_by.get(sku,{}).get(col_key['MX'])
        for level,(quantity,pct) in enumerate(tiers):
            for col,v in [(get_column_letter(363+level*2),quantity),(get_column_letter(364+level*2),pct)]:
                op['cells'][col]=v;op['before'][col]=raw_by.get(sku,{}).get(col_key[col])
        # No unseen old tiers may be left outside the explicitly written levels.
        for level in range(len(tiers)+1,6):
            old=raw_by.get(sku,{}).get(col_key[get_column_letter(361+level*2)])
            assert old is None,(sku,level,old)
    worst=money(biz*(1-max((pct for _,pct in tiers),default=0)/100))
    cash=money(effective-money(effective*.15)-f['fba_fee'])
    worst_cash=money(worst-money(worst*.15)-f['fba_fee'])
    assert worst_cash>=.75,(sku,worst_cash)
    op['reasons'].append(reason)
    op['sources'].append('当前FBA报价/费用；10月订单；10/30库龄；同SKU及同ASIN装量资料')
    price_rows.append({'sku':sku,'asin':asin,'qty':f['available'],'regular':f['price'],'sale_before':f['sale_visible'],'sale_new':new,'regular_new':None,'business_before':f['b2b'],'business_new':biz,'tiers':tiers,'fba_fee':f['fba_fee'],'cash_after_platform':cash,'minimum_business_unit_price':worst,'minimum_cash':worst_cash,'reason':reason})

all_asins=collections.defaultdict(list)
for r in scan:
    all_asins[r['asin']].append(r)
exception_rows=[]
for asin,offers in all_asins.items():
    if any(r['selectable'] and r['units_current']>0 for r in offers) or not any(r['units_current']>0 for r in offers):
        continue
    fa=[r for r in offers if r['channel']=='AFN' and r['units_current']>0]
    mf=[{'sku':r['sku'],'reported_qty':r['units_current'],'price':r['price']} for r in offers if r['channel']=='MFN' and r['units_current']>0]
    current=[x for x in price_rows if x['asin']==asin]
    action='本批写入促销/企业报价' if current and asin not in price_fix else '本批修报价后重试Coupon' if asin in price_fix else holds.get(asin,'FBM专项：核实真实装量、运费和美国仓成本后配置；本批不盲目改价')
    exception_rows.append({'asin':asin,'fba_units':sum(fee_by[r['sku']]['available'] for r in fa), 'fba_skus':[r['sku'] for r in fa],'fbm_offers':mf,
                           'reason':list(dict.fromkeys(z for r in offers for z in r['reasons'])), 'action':action,
                           'units_order_report':order_by.get(asin,{}).get('units30')})
exception_rows.sort(key=lambda r:(-r['fba_units'],r['asin']))
assert len(exception_rows)==88

operations=list(operations.values())
operations.sort(key=lambda r:(0 if any(c in r['cells'] for c in ['MN','MJ','MS']) else 1,r['sku']))
allowed={'C','D','E','L','M','AS','AT','AU','AV','AW','MJ','ML','MN','MO','MP','MS','MX','MY','MZ','NA','NB','NC','ND','NE','NF','NG','NH'}
assert all(set(r['cells'])<=allowed for r in operations)
assert all(not promo_pattern.search(str(r['cells'].get('AW',''))) for r in operations)
assert all(r['sku'] not in deleted_skus for r in operations)
out={'operations':operations,'pricing':price_rows,'exceptions':exception_rows,'copy_exclusions':copy_exclusions,
     'holds':holds,'coupon_scan_stats':{'offers':333,'asins':274,'in_stock_eligible_asins':185,'in_stock_blocked_asins':88,'fba_eligible_asins':92,'fba_blocked_asins':36,'fba_scan_units':6030,'fba_fee_snapshot_units':sum(f['available'] for f in fees)},
     'stats':{'rows':len(operations),'asins':len({r['asin']for r in operations}),
              'bullet5_rows':sum('AW'in r['cells'] for r in operations),'full_bullet_rewrites':len(rewrites),
              'sale_rows':sum('MN'in r['cells']for r in operations),'regular_price_rows':sum('MJ'in r['cells']for r in operations),
              'business_rows':sum('MS'in r['cells']for r in operations),'tier_rows':sum('MX'in r['cells']for r in operations),
              'minimum_rows':sum('ML'in r['cells']for r in operations),'pricing_asins':len({r['asin']for r in price_rows}),
              'pricing_fba_units':sum(r['qty']for r in price_rows)},
     'terms':{'sale_start':'2026-10-31','sale_end_exclusive':'2026-11-30','business_expiry':'企业价和数量阶梯无自动到期，持续至售罄或另行调整',
              'cash_model':'消费者促销价或最低企业阶梯价－按15%估算佣金－当前FBA配送费；未扣采购、头程、仓储、退货、广告等，也不含新增Coupon。',
              'strikethrough':'目标为真实划线价，但参考价由Amazon验证；本批不写List Price/MSRP，不保证展示',
              'coupon_sequence':'用户先上传本批；Coupon具体5%/15%划分及新增随后进行',
              'page_target':'PSS32x6同ASIN双报价为目标结构；不同ASIN真实同款须核实及目录合并，301十二本先保持并行例外'}}
(ROOT/'execution-batch-data.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out['stats'],ensure_ascii=False))
for r in price_rows:
    print(r['sku'],r['regular'],'->',r['sale_new'] or r['regular_new'] or r['sale_before'],'B2B',r['business_new'],'tiers',r['tiers'],'min cash',r['minimum_cash'])
