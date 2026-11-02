import zipfile
import xml.etree.ElementTree as ET

path_13 = r'D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\13-0146-office-only.xlsm'

with zipfile.ZipFile(path_13, 'r') as z:
    s5_xml = z.read('xl/worksheets/sheet5.xml')
    root = ET.fromstring(s5_xml)
    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    sheetData = root.find('main:sheetData', ns)
    
    row7 = None
    for r in sheetData.findall('main:row', ns):
        if r.get('r') == '7':
            row7 = r
            break
    
    if row7 is not None:
        print("Row 7 XML:")
        print(ET.tostring(row7, encoding='utf-8').decode('utf-8'))
    
    # check sharedStrings if present
    if 'xl/sharedStrings.xml' in z.namelist():
        ss_xml = z.read('xl/sharedStrings.xml').decode('utf-8')
        print(f"sharedStrings.xml exists! Length: {len(ss_xml)} chars")
