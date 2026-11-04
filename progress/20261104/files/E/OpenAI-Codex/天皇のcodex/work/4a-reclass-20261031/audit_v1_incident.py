import json,re,html
from pathlib import Path
from collections import Counter
import openpyxl
root=Path(__file__).parent
load=lambda n:json.loads((root/n).read_text(encoding='utf-8-sig'))
data=load('urgent-batches-data.json')
cat=load('category-report-audit.json')['rows']
coupon=load('coupon-fullscan-parsed.json')['rows']
source=Path('C:/Users/24243/Documents/Codex/2026-08-11/7-30-slack-plugin-slack-openai/4A_Amazon_Operations/source_workbooks/亚马逊供应商和开店总表-2026 (1).xlsx')
w=openpyxl.load_workbook(source,read_only=True,data_only=True)
wbrows={s.title:list(s.values) for s in w}
by_sku={r['sku']:r for r in cat}
live={r['sku']:r for r in coupon}
records=[]
for p in data['price_updates']:
 if 'MJ' not in p['cells']:continue
 c=by_sku.get(p['sku'],{});l=live.get(p['sku'],{});old=p['before']['price'];new=p['cells']['MJ']
 sources=[]
 for st in p['sources']:
  m=re.search(r'(Sheet\d+) 行(\d+)',st)
  if m:
   sheet,row=m.group(1),int(m.group(2));v=wbrows[sheet][row-1]
   sources.append(dict(sheet=sheet,row=row,sku=v[0],freight_code=v[7],freight_header=wbrows[sheet][0][7],list=v[11],sale=v[12],title=v[6]))
 drop=round((1-new/old)*100,3)
 fba=l.get('channel')=='AFN' or ('AMAZON' in str(c.get('channel')).upper())
 qty=l.get('units_current',c.get('available10_30') if fba else c.get('quantity'))
 flags=[]
 if drop>=30:flags.append('降幅至少30%')
 if fba and sources and any(s['freight_code'] for s in sources):flags.append('FBA价格直接取另列物流的表价，须复核包邮口径')
 if not l:flags.append('完整Coupon扫描未出现该SKU，不等于已停售；须单独核验')
 if c.get('offer_stop_passed'):flags.append('改价前目录报价终止日已过')
 if c.get('sale_active_by_dates'):flags.append('改价前已有有效Sale Price，须按实际成交价比较')
 status='待复核：有货FBA且降幅至少30%' if fba and qty and drop>=30 else '待复核：FBA运费口径' if fba and qty else '待复核：有货MFN大降幅' if l and l.get('channel')=='MFN' and drop>=30 else '未发现相同高降幅FBA模式；并非核准价格'
 if p['sku']=='4A 5082-Y-L-GM':status='已确认错误：主代理正在回退'
 others=[dict(sku=r['sku'],price=r['price'],status=r.get('status_report'),channel=r.get('channel'),offer_stop_passed=r.get('offer_stop_passed')) for r in cat if r['asin']==p['asin'] and r['sku']!=p['sku']]
 records.append(dict(sku=p['sku'],asin=p['asin'],old=old,new=new,drop_pct=drop,old_effective=p['before']['effective'],old_b2b=p['before']['b2b'],new_b2b=p['cells'].get('MS'),old_channel=c.get('channel'),channel=l.get('channel'),quantity=qty,sales_ui=l.get('sales_units_ui'),sales_30_snapshot=c.get('sold30_10_30'),snapshot_price=l.get('price'),coupon_page=l.get('page'),source=sources,status=status,flags=flags,other_same_asin=others))
records.sort(key=lambda x:(not (x['status'].startswith('待复核：') and 'FBA' in x['status'] or '确认错误' in x['status']),-x['drop_pct']))
assert len(records)==82,len(records)
# Check authored upload actually contains the same numeric regular prices.
up=Path('outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/01-price-title-fixes.xlsm')
uw=openpyxl.load_workbook(up,read_only=True,data_only=True)
ur=list(uw['Template'].values);mi=openpyxl.utils.column_index_from_string('MJ')-1
actual={v[2]:v[mi] for v in ur[6:] if len(v)>mi and v[2]}
errors=[r['sku'] for r in records if actual.get(r['sku'])!=r['new']]
summary=dict(total_upload_rows=len(actual),regular_changes=len(records),upload_mismatches=errors,drop_ge30=sum(r['drop_pct']>=30 for r in records),classifications=dict(Counter(r['status'] for r in records)),scope='只读审查。未更改线上或上传文件。现价/数量来自本次会话保存的34页Coupon快照，非本子代理重新读取后台。')
b2b=[]
for p in data['price_updates']:
 if 'MS' not in p['cells']:continue
 l=live.get(p['sku'],{})
 b2b.append(dict(sku=p['sku'],asin=p['asin'],old_b2b=p['before']['b2b'],new_b2b=p['cells']['MS'],old_regular=p['before']['price'],new_regular=p['cells'].get('MJ'),channel=l.get('channel'),quantity=l.get('units_current'),note='跟随本批普通降价联动，若回退普通价需回退企业价' if 'MJ' in p['cells'] else '仅将企业价从高于普通价改为等于原普通有效价，未新增低于普通价的优惠'))
summary['b2b_changes']=len(b2b)
summary['b2b_following_regular_drop']=sum(r['new_regular'] is not None for r in b2b)
out=dict(summary=summary,records=records,b2b_changes=b2b)
(root/'v1-price-incident-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['V1价格审查','',json.dumps(summary,ensure_ascii=False,indent=2),'','重点：不能把这些待复核项全部宣称为错误；更不能把其余项宣称为安全。FBA运费口径的系统性问题适用于小幅降价项。','']
for r in records:
 lines += [f"{r['sku']} | {r['asin']} | ${r['old']:.2f} -> ${r['new']:.2f} | -{r['drop_pct']:.1f}% | {r['channel'] or r['old_channel']} | qty={r['quantity']} | sales={r['sales_ui']} | {r['status']}", '  '+ '; '.join(r['flags']), '  源表 '+json.dumps(r['source'],ensure_ascii=False)]
lines+=['','企业价29条附录（其中联动普通降价的需一并回退审查）']
for r in b2b:lines.append(json.dumps(r,ensure_ascii=False))
(root/'v1-price-incident-audit.txt').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
for r in records:
 if r['status'].startswith('待复核：') and 'FBA' in r['status'] or '确认错误' in r['status']:print(r['sku'],r['old'],r['new'],r['quantity'],r['sales_ui'],[(s['freight_code'],s['sheet'],s['row']) for s in r['source']])
