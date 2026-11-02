import os

keywords = ['库存', '订单', '10-31', '11-01', 'fba', 'order', 'all+listings', 'inventory']
matches = []

with open(r"D:\4A\00_当前工作区_202611\files_found.txt", "r", encoding="utf-8") as f:
    for line in f:
        line_clean = line.strip()
        low = line_clean.lower()
        if any(k in low for k in keywords):
            # exclude wp-content website stuff
            if 'wp-content' not in low and 'wp-includes' not in low:
                matches.append(line_clean)

for m in matches:
    print(m)
