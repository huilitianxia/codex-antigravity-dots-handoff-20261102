import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

d = r"D:\4A"
for x in os.listdir(d):
    if "01_" in x:
        sub = os.path.join(d, x)
        print("Subdir:", sub)
        for y in os.listdir(sub):
            print("  ", repr(y))
