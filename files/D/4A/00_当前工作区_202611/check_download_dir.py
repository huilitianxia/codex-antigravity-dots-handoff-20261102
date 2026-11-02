import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

paths = [
    r"D:\下载文件",
    r"C:\Users\24243\Downloads"
]

for p in paths:
    print("Checking:", p)
    if os.path.exists(p):
        for f in os.listdir(p):
            print("  ", f)
