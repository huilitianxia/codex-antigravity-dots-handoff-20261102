import json,collections
from pathlib import Path
import openpyxl
P=Path(__file__).parent
f=Path('D:/下载文件/12-catalog-text-repairs-only-processing-summary.xlsm')
if not f.exists():raise SystemExit('12 receipt not downloaded yet')
ops=json.loads((P/'12-text-operations-draft.json').read_text(encoding='utf8'))['operations']
source=P.parents[1]/'outputs/01a18a7c-7953-7b83-b51d-1a7f216ae7e1/20261031-urgent-fixes/12-catalog-text-repairs-only.xlsm'
sw=openpyxl.load_workbook(source,read_only=True,data_only=True)['Template']
sh={c.column_letter:c.value for c in sw[5] if c.value}
rw=openpyxl.load_workbook(f,data_only=True);rs=rw['Template'];rh={c.value:c.column for c in rs[5]if c.value}
sku_col=rh['contribution_sku#1.value'];receipt_rows={rs.cell(n,sku_col).value:n for n in range(7,rs.max_row+1)if rs.cell(n,sku_col).value}
assert set(receipt_rows)=={o['sku']for o in ops},'Receipt SKU population differs'
results=[];mismatches=[];comments=[]
for o in ops:
 n=receipt_rows[o['sku']]
 for col,expected in o['cells'].items():
  key=sh[col]
  actual=rs.cell(n,rh[key]).value if key in rh else None
  if actual!=expected:mismatches.append({'sku':o['sku'],'field':key,'expected':expected,'actual':actual})
 issues=[]
 for cell in rs[n]:
  if cell.comment and cell.column!=1:issues.append({'cell':cell.coordinate,'semantic_key':rs.cell(5,cell.column).value,'message':cell.comment.text.replace('_x000d_','')})
 results.append({'sku':o['sku'],'asin':o['asin'],'status':rs.cell(n,1).value,'issues':issues})
summary=rw['Feed Processing Summary'];per_code=[];per_sku=[];section=None
for row in summary.iter_rows(values_only=True):
 vals=list(row)
 if len(vals)>1 and vals[1]=='Errors and Warnings per Error Code':section='codes';continue
 if len(vals)>1 and vals[1]=='Errors and Warnings per SKU':section='skus';continue
 if len(vals)>7 and isinstance(vals[2],(str,int,float)) and str(vals[2]).isdigit():
  issue={'code':str(vals[2]),'severity':vals[3],'marketplace':vals[4],'message':vals[5],'field':vals[6],'count_or_sku':vals[7]}
  (per_code if section=='codes'else per_sku).append(issue)
out={'receipt':str(f),'batch_id':'285175020758','rows':len(results),'statuses':dict(collections.Counter(r['status']for r in results)),'checked_submitted_cells':sum(len(o['cells'])for o in ops),'mismatches':mismatches,'error_overview':per_code,'sku_errors':per_sku,'rows_detail':results,'source_upload_unchanged':True,'public_page_complete_acceptance':False}
(P/'12-processing-receipt-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items()if k not in ['rows_detail','sku_errors']},ensure_ascii=False,indent=2))
