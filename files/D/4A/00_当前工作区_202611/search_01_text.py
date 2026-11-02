import sys

sys.stdout.reconfigure(encoding='utf-8')

fp = r"D:\4A\00_Codex交接给Gemini_20261101\01_已处理与未处理_完整运营交接.txt"
with open(fp, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l for k in ['PSS 9-5', '40606', '8541', '03-catalog', '12-catalog', '14-']):
        print(f"Line {i+1}: {l.strip()[:140]}")
