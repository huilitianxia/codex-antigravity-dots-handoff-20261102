import openpyxl
import sys

sys.stdout.reconfigure(encoding='utf-8')

wb = openpyxl.load_workbook(r"D:\下载文件\14-proven-catalog-conflicts-only-processing-summary.xlsm", data_only=True)
ws = wb['Template']

for c in range(1, ws.max_column + 1):
    col_letter = openpyxl.utils.get_column_letter(c)
    h4 = str(ws.cell(4, c).value or '')
    h5 = str(ws.cell(5, c).value or '')
    if 'color' in h4.lower() or 'color' in h5.lower() or col_letter in ('BG', 'BH', 'BI', 'BJ', 'BK', 'BL', 'BM', 'HN', 'IU', 'IV', 'IW', 'LT', 'LV', 'LX'):
        print(f"{col_letter:3s} (1-based {c:3d}) | {h4:30s} | {h5:65s} | Row25(GM40624*2)={ws.cell(25, c).value!r} | Row10(0166)={ws.cell(10, c).value!r}")
