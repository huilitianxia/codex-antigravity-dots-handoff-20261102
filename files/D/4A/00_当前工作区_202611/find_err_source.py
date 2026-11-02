import openpyxl
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

dir_path = r"D:\下载文件"
for fname in os.listdir(dir_path):
    if fname.endswith("processing-summary.xlsm"):
        fp = os.path.join(dir_path, fname)
        wb = openpyxl.load_workbook(fp, data_only=True)
        # check sheet names
        for sname in wb.sheetnames:
            ws = wb[sname]
            for r in range(1, min(ws.max_row+1, 250)):
                for c in range(1, min(ws.max_column+1, 15)):
                    val = str(ws.cell(r, c).value or '')
                    if "4A PSS 9-5 NB" in val or "4A 40606" in val:
                        print(f"Found in {fname} sheet {sname} row {r}: {val}")
                        # print row
                        row_vals = [ws.cell(r, col).value for col in range(1, 15)]
                        print("  Row:", row_vals)
                        break
