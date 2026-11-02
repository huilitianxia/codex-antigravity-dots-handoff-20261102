import os

files = [
    r"D:\4A\00_Codex交接给Gemini_20261101\00_先读我_给Gemini的交接说明.txt",
    r"D:\4A\00_Codex交接给Gemini_20261101\01_已做与未做_及运营全貌.txt",
    r"D:\4A\00_Codex交接给Gemini_20261101\02_D盘判断根据.txt"
]

for fp in files:
    print(f"=== {fp} ===")
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for line in lines[:35]:
                print(line.rstrip())
    else:
        print("Not found")
