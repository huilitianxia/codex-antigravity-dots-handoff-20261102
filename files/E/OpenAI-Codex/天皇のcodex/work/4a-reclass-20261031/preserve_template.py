from pathlib import Path
import zipfile, re, hashlib, json
import openpyxl
from xml.sax.saxutils import escape

root=Path(__file__).parent
src=Path('D:/下载文件/restore-batch-01-New_Version.xlsm')
authored=root/'restore-batch-01-cells.xlsx'
dest=root/'restore-batch-01-fixed.xlsm'
aw=openpyxl.load_workbook(authored,read_only=True,data_only=True)
ow=openpyxl.load_workbook(src,read_only=True,data_only=False)
changes={f'{col}{r}':aw['Template'][f'{col}{r}'].value for col in ['CF','DC'] for r in range(7,14)}
assert set(changes.values())=={'No','Not Applicable'}
with zipfile.ZipFile(src) as z:
    sheet='xl/worksheets/sheet5.xml'
    xml=z.read(sheet).decode('utf-8')
    assert 'AAAA 4A' not in xml or 'sheetData' in xml
    for addr,value in changes.items():
        pattern=rf'<c\b([^>]*\br="{addr}"[^>]*)(?:/>|>.*?</c>)'
        match=re.search(pattern,xml)
        cell=f'<c r="{addr}" t="inlineStr"><is><t>{escape(value)}</t></is></c>'
        if match:
            attrs=match.group(1)
            attrs=re.sub(r'\s+t="[^"]*"','',attrs)
            cell=f'<c{attrs} t="inlineStr"><is><t>{escape(value)}</t></is></c>'
            xml=xml[:match.start()]+cell+xml[match.end():]
        else:
            rownum=int(re.search(r'\d+',addr).group())
            rowpat=rf'(<row\b[^>]*\br="{rownum}"[^>]*>)(.*?)(</row>)'
            rm=re.search(rowpat,xml)
            assert rm
            cells=re.findall(r'<c\b[^>]*(?:/>|>.*?</c>)',rm.group(2))
            cells.append(cell)
            from openpyxl.utils.cell import coordinate_from_string,column_index_from_string
            cells.sort(key=lambda c:column_index_from_string(coordinate_from_string(re.search(r'\br="([A-Z]+\d+)"',c).group(1))[0]))
            xml=xml[:rm.start()]+rm.group(1)+''.join(cells)+rm.group(3)+xml[rm.end():]
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
        for item in z.infolist():out.writestr(item,xml.encode('utf-8') if item.filename==sheet else z.read(item.filename))
nw=openpyxl.load_workbook(dest,read_only=True,data_only=False)
diff=[]
for sn in ow.sheetnames:
    from openpyxl.utils.cell import get_column_letter
    for rn,(oldrow,newrow) in enumerate(zip(ow[sn].iter_rows(values_only=True),nw[sn].iter_rows(values_only=True)),1):
        for cn,(before,after) in enumerate(zip(oldrow,newrow),1):
            if before!=after:diff.append((sn,f'{get_column_letter(cn)}{rn}',before,after))
assert {(sn,addr) for sn,addr,_,_ in diff}=={('Template',a) for a in changes},diff
with zipfile.ZipFile(src) as a,zipfile.ZipFile(dest) as b:
    changed_parts=[n for n in a.namelist() if a.read(n)!=b.read(n)]
assert changed_parts==[sheet],changed_parts
print(json.dumps({'file':str(dest),'changed_cells':len(diff),'changed_parts':changed_parts,'original_macro_and_all_other_parts_preserved':True},ensure_ascii=False))
