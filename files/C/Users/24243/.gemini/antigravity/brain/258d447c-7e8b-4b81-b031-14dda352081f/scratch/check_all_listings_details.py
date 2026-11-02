import csv
import sys

sys.stdout.reconfigure(encoding='utf-8')

p = r"D:\下载文件\所有商品报告_09-03-2026.txt"
with open(p, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f, delimiter='\t')
    count = 0
    fba_count = 0
    fbm_count = 0
    active_count = 0
    inactive_count = 0
    for r in reader:
        count += 1
        sku = r.get('seller-sku', '')
        asin = r.get('asin1', '')
        qty = r.get('quantity', '')
        status = r.get('status', '')
        fc = r.get('fulfillment-channel', '')
        if fc == 'AMAZON_NA':
            fba_count += 1
        else:
            fbm_count += 1
        if status == 'Active':
            active_count += 1
        else:
            inactive_count += 1

    print(f"Total rows: {count}")
    print(f"Active: {active_count}, Inactive: {inactive_count}")
    print(f"FBA: {fba_count}, FBM: {fbm_count}")
