import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

folders = [
    r"C:\Users\24243\Desktop",
    r"C:\Users\24243\Downloads",
    r"E:\Desktop",
    r"D:\4A\01_便签店运营_2026-10\4A便签店运营归档_终版_20261101.zip",
    r"D:\4A\Codex给Gemini_已处理未处理交接与D盘复核_20261101.zip"
]

for f in folders:
    if os.path.exists(f):
        print("EXISTS:", f)
        if os.path.isdir(f):
            for x in os.listdir(f):
                if any(k in x for k in ['库存', '订单', '10-31', '11-01', 'FBA', 'Order', 'Inventory', '14-']):
                    print("  ->", x)
