import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

p = r"D:\4A\00_Codex交接给Gemini_20261101"
for f in os.listdir(p):
    if f.endswith('.txt'):
        print(f)
        with open(os.path.join(p, f), 'r', encoding='utf-8', errors='ignore') as fp:
            print("--- FIRST 500 CHARS ---")
            print(fp.read(500))
            print("-----------------------")
