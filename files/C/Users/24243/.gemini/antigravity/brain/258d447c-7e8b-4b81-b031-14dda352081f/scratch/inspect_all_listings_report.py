import sys
import csv

sys.stdout.reconfigure(encoding='utf-8')

p = r"D:\下载文件\所有商品报告_09-03-2026.txt"
print("Reading:", p)

with open(p, 'r', encoding='ansi', errors='ignore') as f:
    reader = csv.reader(f, delimiter='\t')
    header = next(reader)
    print("Header:", header)
    rows = list(reader)
    print(f"Total rows in 所有商品报告_09-03-2026.txt: {len(rows)}")
    
    # check sample rows
    for r in rows[:5]:
        print("  Sample row:", r[:7])

    # check status breakdown
    statuses = {}
    for r in rows:
        st = r[4] if len(r) > 4 else "UNKNOWN"
        statuses[st] = statuses.get(st, 0) + 1
    print("Statuses:", statuses)
