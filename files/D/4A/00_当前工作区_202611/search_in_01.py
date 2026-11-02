import sys

sys.stdout.reconfigure(encoding='utf-8')

fp = r"D:\4A\00_Codex交接给Gemini_20261101\01_已处理与未处理_完整运营交接.txt"
with open(fp, "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

for line in text.splitlines():
    if any(k in line for k in ['库存', '订单', '10-31', '11-01', 'FBA', 'MFN', '304-Full Adhesive-400', '303-Full Adhesive-400']):
        print(line[:120])
