import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

steps_dir = r"C:\Users\24243\.gemini\antigravity\brain\f1367eb9-fa19-4a11-abf4-4dc63e32dd4b\.system_generated\steps"
for s in sorted(os.listdir(steps_dir), key=lambda x: int(x) if x.isdigit() else 999999):
    op = os.path.join(steps_dir, s, "output.txt")
    if os.path.exists(op):
        sz = os.path.getsize(op)
        if sz > 2000:
            with open(op, 'r', encoding='utf-8', errors='ignore') as fp:
                c = fp.read(500)
                if "asin" in c.lower() or "sku" in c.lower() or "manage" in c.lower() or "inventory" in c.lower():
                    print(f"Step {s}: {sz} bytes")
