import os

with open(r"D:\4A\00_当前工作区_202611\files_found.txt", "w", encoding="utf-8") as out:
    for root, dirs, files in os.walk(r"D:\4A"):
        for f in files:
            p = os.path.join(root, f)
            out.write(p + "\n")

print("Done writing files_found.txt")
