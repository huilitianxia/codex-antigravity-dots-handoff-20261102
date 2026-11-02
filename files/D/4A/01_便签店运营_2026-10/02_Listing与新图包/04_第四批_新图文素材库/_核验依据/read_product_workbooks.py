from pathlib import Path
import json,re
from openpyxl import load_workbook
base=Path('C:/Users/24243/Documents/Codex/2026-08-11/7-30-slack-plugin-slack-openai/4A_Amazon_Operations/source_workbooks')
out=[]
for name in ['亚马逊供应商和开店总表-2026 (1).xlsx','亚马逊供应商和开店总表-2023.xlsx']:
    p=base/name
    wb=load_workbook(p,read_only=True,data_only=True)
    for ws in wb:
        headers=[];hits=[]
        for row_number,row in enumerate(ws.iter_rows(),1):
            vals=[{'cell':c.coordinate,'value':str(c.value)} for c in row if c.value is not None]
            if row_number<=6:headers.append(vals)
            if any(re.search(r'(?i)(\b4012\b|303M.?PN.?x?12|124418|B01M3N310M|B07B7JF9LB|B07F2CWVQ7)',str(c.value or '')) for c in row):hits.append(vals)
        if hits:out.append({'file':str(p),'sheet':ws.title,'headers':headers,'rows':hits})
    wb.close()
dest=Path('E:/Desktop/待上架_新图文素材库_第四批/_核验依据/C盘产品表_对应行.json')
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
