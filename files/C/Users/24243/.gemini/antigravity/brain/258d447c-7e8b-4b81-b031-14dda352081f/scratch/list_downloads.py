import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

dl = r"C:\Users\24243\Downloads"
for f in os.listdir(dl):
    if "4A" in f or "4a" in f:
        print(repr(f), os.path.getsize(os.path.join(dl, f)))
