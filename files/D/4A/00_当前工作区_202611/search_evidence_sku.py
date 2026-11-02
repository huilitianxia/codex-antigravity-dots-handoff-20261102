import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

bdir = r"D:\4A\00_Codex交接给Gemini_20261101\03_验收与待办证据"
for fname in os.listdir(bdir):
    fp = os.path.join(bdir, fname)
    if os.path.isfile(fp) and fname.endswith(('.txt', '.json')):
        with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if '4A PSS 9-5 NB' in content or '4A 40606' in content:
                print(f"Match in {fname}")
                for line in content.splitlines():
                    if '4A PSS 9-5 NB' in line or '4A 40606' in line:
                        print("  ", line[:150])
