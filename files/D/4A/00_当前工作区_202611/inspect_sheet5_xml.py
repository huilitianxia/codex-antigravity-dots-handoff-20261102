import zipfile
import xml.etree.ElementTree as ET

path_13 = r'D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\13-0146-office-only.xlsm'

with zipfile.ZipFile(path_13, 'r') as z:
    s5_xml = z.read('xl/worksheets/sheet5.xml')
    root = ET.fromstring(s5_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheetData = root.find('main:sheetData', ns)
    
    rows = sheetData.findall('main:row', ns)
    print(f"Total <row> elements in sheet5.xml: {len(rows)}")
    for r in rows:
        r_num = r.get('r')
        cells = r.findall('main:c', ns)
        if int(r_num) >= 7:
            cell_refs = [c.get('r') for c in cells]
            print(f"Row {r_num} has {len(cells)} cells: {cell_refs}")
