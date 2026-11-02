import os
import sys

def list_files(dir_path):
    print("Listing:", dir_path)
    if not os.path.exists(dir_path):
        print("Does not exist!")
        return
    for item in os.listdir(dir_path):
        p = os.path.join(dir_path, item)
        if os.path.isdir(p):
            print(f"[DIR]  {item}")
        else:
            print(f"[FILE] {item} ({os.path.getsize(p)} bytes)")

print("=== 05_源数据快照_按日期使用 ===")
list_files(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用")

print("\n=== 00_Codex交接给Gemini_20261101 ===")
list_files(r"D:\4A\00_Codex交接给Gemini_20261101")

print("\n=== 02_老资料_表格与订单 ===")
list_files(r"D:\4A\02_老资料_表格与订单")

print("\n=== 01_便签店运营_2026-10 ===")
list_files(r"D:\4A\01_便签店运营_2026-10")

print("\n=== 01_便签店运营_2026-10/01_官方上传表格_核心在用 ===")
list_files(r"D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用")
