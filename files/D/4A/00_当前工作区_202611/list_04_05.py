import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

base = r"D:\4A\01_便签店运营_2026-10"
for x in ['04_运营复盘与审计报告', '05_历史版本与中间过程']:
    p = os.path.join(base, x)
    print("=== ", p, " ===")
    if os.path.exists(p):
        for root, dirs, files in os.walk(p):
            for f in files:
                print(os.path.join(root, f))
