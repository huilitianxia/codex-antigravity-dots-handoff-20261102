import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

p = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据"
for f in sorted(os.listdir(p)):
    fp = os.path.join(p, f)
    if os.path.isfile(fp):
        print(f"{os.path.getsize(fp):>10}  {f}")
