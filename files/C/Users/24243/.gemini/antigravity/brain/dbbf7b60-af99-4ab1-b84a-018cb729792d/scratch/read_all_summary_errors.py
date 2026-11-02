import openpyxl

file_path = r'd:\下载文件\4A_全店21大家族精细化变体清洗_终极纯净版-processing-summary (1).xlsm'
wb = openpyxl.load_workbook(file_path, data_only=True)
ws_fps = wb['Feed Processing Summary']

print("--- Summary Block ---")
for r in range(3, 9):
    print([ws_fps.cell(r, c).value for c in range(1, 9) if ws_fps.cell(r, c).value is not None])

print("\n--- Error Summary Table ---")
for r in range(11, 45):
    code = ws_fps.cell(r, 3).value
    cat = ws_fps.cell(r, 4).value
    msg = ws_fps.cell(r, 6).value
    col = ws_fps.cell(r, 7).value
    cnt = ws_fps.cell(r, 8).value
    if code is not None:
        print(f"Code: {code} | Type: {cat} | Count: {cnt} | Field: {col}")
        print(f"  Msg: {str(msg)[:150]}")
