import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

brain_root = r"C:\Users\24243\.gemini\antigravity\brain"
print("=== Brain folders ===")
for d in os.listdir(brain_root):
    dp = os.path.join(brain_root, d)
    if os.path.isdir(dp):
        print(d)

print("\n=== Check 675d7e41-2d41-4b28-b1f5-b2ca4c6c75c7 ===")
old_conv = os.path.join(brain_root, "675d7e41-2d41-4b28-b1f5-b2ca4c6c75c7")
if os.path.exists(old_conv):
    for f in os.listdir(old_conv):
        fp = os.path.join(old_conv, f)
        if os.path.isfile(fp):
            print(" ", f, os.path.getsize(fp))
