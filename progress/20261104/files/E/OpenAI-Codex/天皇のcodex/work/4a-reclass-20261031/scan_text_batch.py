import json,csv,re,collections
from pathlib import Path
import openpyxl
P=Path(__file__).parent
O=P.parents[1]/'outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes'
raw=json.loads((P/'category-report-raw.json').read_text(encoding='utf8'))
rows={r['contribution_sku#1.value']:dict(r) for r in raw['rows']}
current={r['seller-sku']:r for r in csv.DictReader(Path('D:/下载文件/所有商品报告_11-01-2026.txt').open(encoding='utf-8-sig'),delimiter='\t')}
text_prefixes=('item_name','title_differentiation','product_description','bullet_point')
sent=[]
for f in sorted(O.glob('*.xlsm')):
 if f.name[:2] not in ['01','03','04','06','11']:continue
 w=openpyxl.load_workbook(f,read_only=True,data_only=True);s=w['Template'];h=[c.value for c in s[5]]
 if 'contribution_sku#1.value' not in h:continue
 ix=h.index('contribution_sku#1.value')
 for vs in s.iter_rows(min_row=7,values_only=True):
  sku=vs[ix]
  if not sku:continue
  edits={k:v for k,v in zip(h,vs) if k and k.startswith(text_prefixes) and v not in (None,'')}
  if not edits:continue
  sent.append({'sku':sku,'file':f.name,'edits':edits})
  if sku in rows:rows[sku].update(edits)
 w.close()
for sku in rows:
 if sku in current:rows[sku]['current_report_title']=current[sku]['item-name']
 # 012 independently verified cleared through visible UI.
 if sku=='4A 012':
  for k in rows[sku]:
   if k.startswith('title_differentiation'):rows[sku][k]=''
patterns={
 'commercial':r'free\s*shipping|orders?\s*over|good\s*price|high\s*quality|best\s*quality|best .*world|search\s*4a|amazon\.com|guarantee|money.?back|satisfaction|buy\s*now|christmas\s*gifts',
 'environmental':r'recycl|certif|forest|eco.?friendly|sustainab|non.?toxic|acid.?free',
 'comparative':r'longer\s*and\s*stronger|stronger\s*than|twice\s*as|\b[23]x\s+(?:the\s+)?(?:stick|adhesi)',
 'external_link':r'https?://|www\.'}
issues=[];groups=collections.Counter()
for sku,r in rows.items():
 for k,v in r.items():
  if not k.startswith(text_prefixes) or not isinstance(v,str) or not v:continue
  reasons=[n for n,pat in patterns.items() if re.search(pat,v,re.I)]
  if k.startswith('title_differentiation') and re.fullmatch(r'B[A-Z0-9]{9}',v):reasons.append('asin_in_highlight')
  if k.startswith('item_name') and len(v)>200:reasons.append('title_over_200')
  if reasons:
   issue={'sku':sku,'asin':r.get('amzn1.volt.ca.product_id_value'),'field':k,'value':v,'reasons':reasons,'exact_sku_in_latest_report':sku in current,'status':current.get(sku,{}).get('status'),'product_type':r.get('product_type#1.value')}
   issues.append(issue);groups[(k.split('[')[0],v)]+=1
out={'source_rows':len(raw['rows']),'current_rows':len(current),'matched_exact_skus':len(rows.keys()&current.keys()),'submitted_text_rows':sent,'issue_counts':dict(collections.Counter(x for i in issues for x in i['reasons'])),'issues':issues,'overlay_warning':'Submitted text overlaid to avoid duplicate writes; upload processing alone does not prove live acceptance. 11 remains pending until receipt.'}
(P/'12-text-scan.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
(P/'12-text-value-review.txt').write_text('\n\n'.join(f'{n} | {k}\n{v}' for (k,v),n in groups.most_common() if k!='title_differentiation'),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k not in ['submitted_text_rows','issues']},ensure_ascii=False))
print('Unique suspect values',len(groups),'issues',len(issues))
