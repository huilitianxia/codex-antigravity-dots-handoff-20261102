import openpyxl

file_path = r'd:\下载文件\4A_全店21大家族精细化变体清洗_终极纯净版-processing-summary (1).xlsm'
wb = openpyxl.load_workbook(file_path, data_only=True)
ws_fps = wb['Feed Processing Summary']

for r in range(1, 15):
    vals = [ws_fps.cell(r, c).value for c in range(1, ws_fps.max_column + 1)]
    print(f"Row {r}: {vals}")
