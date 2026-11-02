import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for root_dir in [r"E:\Desktop", r"C:\Users\24243\Downloads", r"D:\下载文件", r"C:\Users\24243\Documents"]:
    if os.path.exists(root_dir):
        for root, dirs, files in os.walk(root_dir):
            for f in files:
                if "所有商品" in f or "all+listings" in f.lower() or "merchant" in f.lower() or "inventory" in f.lower():
                    print(os.path.join(root, f))
