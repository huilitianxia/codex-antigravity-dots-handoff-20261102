import glob
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

for p in glob.glob(r"D:\4A\**\*", recursive=True):
    if p.endswith((".json", ".md", ".txt", ".py", ".csv")) and "网站备份" not in p:
        try:
            txt = open(p, "r", encoding="utf-8", errors="ignore").read()
            if "8898" in txt or "8,898" in txt or "4947" in txt or "4,947" in txt:
                print("Matched in:", p)
        except Exception:
            pass
