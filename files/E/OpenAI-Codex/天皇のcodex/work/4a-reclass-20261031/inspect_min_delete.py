from pathlib import Path
import openpyxl,json,re
root=Path(__file__).parent
files=[Path('D:/下载文件/PriceAndQuantity.xlsm'),Path('D:/下载文件/05-remove-temporary-minimums-processing-summary.xlsm')]
out=[]
for p in files:
 w=openpyxl.load_workbook(p,read_only=True,data_only=False)
 data={'file':str(p),'sheets':w.sheetnames,'template':[],'relevant_definitions':[],'summary':[]}
 for s in w:
  if s.title=='Template':
   for row in s.iter_rows(max_row=12):
    data['template'].append([(c.coordinate,c.value) for c in row if c.value is not None])
  else:
   for row in s:
    vals=[(c.coordinate,c.value) for c in row if c.value is not None]
    text=' '.join(str(v) for _,v in vals)
    if re.search(r'Delete Minimum|minimum.*allowed|minimum_seller|delete.*min|删除最低|最低.*删除',text,re.I):data['relevant_definitions'].append({'sheet':s.title,'cells':vals})
    elif 'summary' in s.title.lower() or '摘要' in s.title:data['summary'].append(vals)
 out.append(data)
(root/'05-min-delete-template-inspection.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str),encoding='utf8')
for d in out:
 print('\nFILE',d['file'],'SHEETS',d['sheets'])
 print('TEMPLATE')
 for row in d['template']:print(json.dumps(row,ensure_ascii=False,default=str))
 print('DEFINITIONS')
 for row in d['relevant_definitions']:print(json.dumps(row,ensure_ascii=False,default=str))
 print('SUMMARY',json.dumps(d['summary'],ensure_ascii=False,default=str))
