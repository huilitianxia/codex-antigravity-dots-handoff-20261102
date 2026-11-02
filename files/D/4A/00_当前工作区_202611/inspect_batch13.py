import zipfile
import openpyxl
import xml.etree.ElementTree as ET

path_13 = r'D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\13-0146-office-only.xlsm'

print("=== INSPECTING 13-0146-office-only.xlsm VIA OPENPYXL ===")
wb = openpyxl.load_workbook(path_13, data_only=True, read_only=True)
print("Sheet names:", wb.sheetnames)

for sname in wb.sheetnames:
    ws = wb[sname]
    print(f"Sheet '{sname}': max_row={ws.max_row}, max_col={ws.max_column}")
    if sname == 'Template':
        # Let's inspect populated rows and columns
        for r_idx, row in enumerate(ws.iter_rows(values_only=True), 1):
            populated = [(openpyxl.utils.get_column_letter(c_idx), c_idx, val) for c_idx, val in enumerate(row, 1) if val is not None]
            if populated:
                # show first 10 columns or all
                pop_summary = [f"{col}({idx}): '{val}'" for col, idx, val in populated]
                print(f"  Row {r_idx} ({len(populated)} populated cells): {', '.join(pop_summary[:10])}")
                if len(pop_summary) > 10:
                    print(f"    ... +{len(pop_summary)-10} more cells")
wb.close()

print("\n=== INSPECTING ZIP STRUCTURE & sheet5.xml ===")
with zipfile.ZipFile(path_13, 'r') as z:
    print("ZIP File List:")
    for info in z.infolist():
        print(f"  {info.filename} ({info.file_size} bytes)")
    
    # Check sheet5.xml or relevant worksheet
    # Let's find which sheet is Template
    # check xl/workbook.xml
    wb_xml = z.read('xl/workbook.xml').decode('utf-8')
    print("\nxl/workbook.xml snippet:")
    print(wb_xml[:1000])

    # Check sheet5.xml or whatever sheet maps to Template
    if 'xl/worksheets/sheet5.xml' in z.namelist():
        s5_xml = z.read('xl/worksheets/sheet5.xml').decode('utf-8')
        print(f"\nxl/worksheets/sheet5.xml length: {len(s5_xml)} chars")
        print("sheet5.xml head snippet:")
        print(s5_xml[:1500])
        print("sheet5.xml tail snippet:")
        print(s5_xml[-1500:])
