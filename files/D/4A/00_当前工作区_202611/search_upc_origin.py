import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

for root, dirs, files in os.walk(r"D:\4A"):
    for f in files:
        if f.endswith(('.txt', '.json', '.tsv', '.csv', '.xlsm', '.xlsx')):
            fp = os.path.join(root, f)
            try:
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fp_in:
                    txt = fp_in.read()
                    if '702877119600' in txt:
                        print("Match 702877119600 in:", fp)
            except:
                pass
