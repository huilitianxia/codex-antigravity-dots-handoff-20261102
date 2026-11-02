import openpyxl

file_path = r'd:\下载文件\4A_全店21大家族精细化变体清洗_终极纯净版-processing-summary (1).xlsm'
wb = openpyxl.load_workbook(file_path, data_only=True)
ws_fps = wb['Feed Processing Summary']

print("--- Errors for 30315 in Feed Processing Summary ---")
for r in range(45, ws_fps.max_row + 1):
    vals = [ws_fps.cell(r, c).value for c in range(1, ws_fps.max_column + 1)]
    row_str = " ".join([str(v) for v in vals if v is not None])
    if '30315' in row_str or '169' in str(vals[1]) or '170' in str(vals[1]):
        print(f"Row {r}: {vals}")
