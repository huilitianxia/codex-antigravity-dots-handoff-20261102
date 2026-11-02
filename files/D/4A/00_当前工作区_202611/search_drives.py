import os

for drive in ['C:\\', 'D:\\', 'E:\\']:
    if not os.path.exists(drive):
        continue
    print(f"Scanning drive {drive}...")
    try:
        for root, dirs, files in os.walk(drive):
            # Skip some large system dirs on C
            if drive == 'C:\\' and any(x in root for x in ['Windows', 'Program Files', 'AppData\\Local\\Microsoft', 'node_modules', '.git']):
                continue
            for f in files:
                if '10-31-2026' in f or '11-01-2026' in f or '亚马逊物流库存' in f or '订单报告' in f:
                    p = os.path.join(root, f)
                    try:
                        print("FOUND:", p)
                    except:
                        print("FOUND (raw):", repr(p))
    except Exception as e:
        print("Error on drive", drive, e)
