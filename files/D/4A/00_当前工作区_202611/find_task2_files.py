import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

targets = [
    '所有商品报告',
    '亚马逊物流库存',
    '订单报告',
    'coupon-fullscan-parsed.json',
    '【官方定价基准_终版】亚马逊供应商和开店总表-2026(3).xlsx'
]

print("Searching D:\\4A ...")
for root, dirs, files in os.walk(r"D:\4A"):
    for f in files:
        for t in targets:
            if t in f:
                print(f"MATCH [{t}]: {os.path.join(root, f)}")
