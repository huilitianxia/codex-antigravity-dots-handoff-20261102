import sys

sys.stdout.reconfigure(encoding='utf-8')

for fname in ['175793876516020757.txt', '284701020757.txt', '284753020757.txt', '284774020757.txt']:
    p = rf"D:\下载文件\{fname}"
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        first_line = f.readline().strip()
        second_line = f.readline().strip()
        print(f"=== {fname} ===")
        print("Line 1:", first_line[:120])
        print("Line 2:", second_line[:120])
