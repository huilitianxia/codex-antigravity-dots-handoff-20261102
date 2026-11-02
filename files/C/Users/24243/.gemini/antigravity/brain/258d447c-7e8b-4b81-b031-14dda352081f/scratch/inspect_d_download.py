import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

d_down = r"D:\下载文件"
if os.path.exists(d_down):
    print(f"=== {d_down} ===")
    for f in os.listdir(d_down):
        p = os.path.join(d_down, f)
        if os.path.isfile(p):
            print(f, os.path.getsize(p))
