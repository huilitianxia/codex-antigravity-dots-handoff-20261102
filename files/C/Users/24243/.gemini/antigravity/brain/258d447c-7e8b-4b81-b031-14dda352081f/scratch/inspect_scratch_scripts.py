import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

scratch = r"C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch"

for fname in os.listdir(scratch):
    if fname.endswith(('.py', '.js', '.mjs')):
        fpath = os.path.join(scratch, fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as fp:
            content = fp.read()
            # print if mentions inventory or manage or pages or 854
            print(f"=== {fname} ({len(content)} chars) ===")
            lines = content.split('\n')
            for l in lines[:15]:
                print(" ", l)
