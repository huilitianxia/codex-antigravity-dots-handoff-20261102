import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\下载文件\所有商品报告_09-03-2026.txt", 'r', encoding='utf-8-sig', errors='ignore') as f:
    reader = csv.DictReader(f, delimiter='\t')
    first = next(reader)
    print("Keys with utf-8-sig:", list(first.keys())[:5])
    print("item-name:", first.get('item-name'))
