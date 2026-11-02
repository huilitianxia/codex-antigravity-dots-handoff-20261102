import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk(r"D:\4A"):
    for f in files:
        if any(k in f.lower() for k in ['batch14', 'batch 14', '14-proven']):
            print(os.path.join(root, f))
