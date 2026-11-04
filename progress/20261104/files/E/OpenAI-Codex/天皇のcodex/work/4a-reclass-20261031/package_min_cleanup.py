import json,re,zipfile,copy,hashlib,csv
from pathlib import Path
from xml.sax.saxutils import escape
import openpyxl
from openpyxl.utils import get_column_letter

root=Path(__file__).parent
spec=json.loads((root/'05-min-cleanup-spec.json').read_text(encoding='utf8'))
source=Path(spec['source']); dest=Path(spec['final'])
authored=openpyxl.load_workbook(root/'05-min-cleanup-authored-cells.xlsx',read_only=True,data_only=True)['Template']
report={r['seller-sku']:r for r in csv.DictReader(Path('D:/下载文件/所有商品报告_11-01-2026.txt').read_text(encoding='utf-8-sig').splitlines(),delimiter='\t')}
expected=[]
for n,(sku,price) in enumerate(spec['rows'],7):
    assert float(report[sku]['price'])==price,(sku,report[sku]['price'],price)
    assert report[sku]['status']=='Active',sku
    cells={'A':sku,'G':price,'I':spec['deletion']}
    assert all(authored[f'{c}{n}'].value==v for c,v in cells.items())
    expected.append(cells)
with zipfile.ZipFile(source) as z:
    part='xl/worksheets/sheet5.xml'; xml=z.read(part).decode('utf8')
    sd=re.search(r'<sheetData>(.*?)</sheetData>',xml,re.S); assert sd
    assert not re.search(r'<row\b[^>]*\br="(?:[7-9]|[1-9][0-9]+)"',sd[1])
    extra=[]
    for n,cells in enumerate(expected,7):
        cs=[]
        for c,v in cells.items():
            if isinstance(v,(int,float)):
                cs.append(f'<c r="{c}{n}"><v>{v}</v></c>')
            else:
                cs.append(f'<c r="{c}{n}" s="1" t="inlineStr"><is><t xml:space="preserve">{escape(v)}</t></is></c>')
        extra.append(f'<row r="{n}" ht="42" customHeight="1">'+''.join(cs)+'</row>')
    xml=xml[:sd.end(1)]+''.join(extra)+xml[sd.end(1):]
    xml=re.sub(r'(<dimension\b[^>]*ref=")[^"]+("[^>]*/>)',r'\g<1>A1:AF10\2',xml,count=1)
    def adjust_col(m):
        tag=m[0]; n=re.search(r'\bmin="(\d+)"',tag)
        if not n or int(n[1]) not in (1,9):return tag
        width='38' if int(n[1])==1 else '65'
        tag=re.sub(r'\bwidth="[^"]*"',f'width="{width}"',tag)
        tag=re.sub(r'\bhidden="[^"]*"','hidden="0"',tag)
        return tag
    xml=re.sub(r'<col\b[^>]*/>',adjust_col,xml)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as out:
        for info in z.infolist():out.writestr(copy.copy(info),xml.encode('utf8') if info.filename==part else z.read(info.filename))
    with zipfile.ZipFile(dest) as out:
        changed=[n for n in z.namelist() if z.read(n)!=out.read(n)]
        assert changed==[part],changed
original=openpyxl.load_workbook(source,read_only=True,data_only=False)
result=openpyxl.load_workbook(dest,read_only=True,data_only=False)
assert original.sheetnames==result.sheetnames
assert list(original['Template'].iter_rows(max_row=6,values_only=True))==list(result['Template'].iter_rows(max_row=6,values_only=True))
actual=[]
for r in result['Template'].iter_rows(min_row=7,values_only=True):
    values={get_column_letter(i):v for i,v in enumerate(r,1) if v is not None}
    if values: actual.append(values)
assert actual==expected,(actual,expected)
assert all(set(r)=={'A','G','I'} for r in actual)
valid=[c.value for row in original['Valid Values'] for c in row]
assert spec['deletion'] in valid
check={'file':str(dest),'rows':4,'only_nonempty_columns':['A:SKU','G:verified unchanged regular price','I:official deletion enum for ordinary minimum'],'quantity_fulfillment_business_sale_maximum_blank':True,'changed_zip_parts':changed,'headers_macros_other_sheets_preserved':True,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
(root/'05-min-cleanup-verification.json').write_text(json.dumps(check,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(check,ensure_ascii=False,indent=2))
