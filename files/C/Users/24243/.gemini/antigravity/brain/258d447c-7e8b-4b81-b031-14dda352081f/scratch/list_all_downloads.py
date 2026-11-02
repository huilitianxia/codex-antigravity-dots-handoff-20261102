import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

dl = r"C:\Users\24243\Downloads"
for f in os.listdir(dl):
    print(repr(f), os.path.getsize(os.path.join(dl, f)))
