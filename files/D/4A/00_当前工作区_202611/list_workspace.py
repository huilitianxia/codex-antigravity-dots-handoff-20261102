import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

p = r"D:\4A\00_当前工作区_202611"
for f in sorted(os.listdir(p)):
    fp = os.path.join(p, f)
    if os.path.isfile(fp):
        print(f"{os.path.getsize(fp):>10}  {f}")
