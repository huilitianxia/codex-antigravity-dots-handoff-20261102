import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\下载文件\175793876516020757.txt", "r", encoding="utf-8", errors="ignore") as f:
    headers = f.readline().strip().split("\t")
    print("Order report headers:", headers)
    print("Number of orders:")
    count = 0
    min_date, max_date = None, None
    for line in f:
        count += 1
        parts = line.strip().split("\t")
        if len(parts) > 2:
            pdate = parts[2]
            if min_date is None or pdate < min_date:
                min_date = pdate
            if max_date is None or pdate > max_date:
                max_date = pdate
    print(f"Total rows: {count}, min_date: {min_date}, max_date: {max_date}")

with open(r"D:\下载文件\284701020757.txt", "r", encoding="utf-8", errors="ignore") as f:
    headers = f.readline().strip().split("\t")
    print("\nFBA inventory headers:", headers)
    count = 0
    for line in f:
        count += 1
    print(f"Total FBA inventory rows: {count}")
