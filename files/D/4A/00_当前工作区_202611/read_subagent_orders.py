import sys

sys.stdout.reconfigure(encoding='utf-8')

fp = r"D:\4A\01_便签店运营_2026-10\05_历史版本与中间过程\调试日志与中间数据\subagent_orders_step5336.txt"
with open(fp, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
    print("Total lines:", len(lines))
    for l in lines[:20]:
        print(l.rstrip())
