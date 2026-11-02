import shutil
import hashlib
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

desktop_file = r"E:\Desktop\14-proven-catalog-conflicts-only.xlsm"
work_file = r"D:\4A\00_当前工作区_202611\14-proven-catalog-conflicts-only.xlsm"

if os.path.exists(desktop_file):
    dt_sha = hashlib.sha256(open(desktop_file, 'rb').read()).hexdigest()
    print("Desktop SHA256:", dt_sha)
    shutil.copy2(desktop_file, work_file)
    wk_sha = hashlib.sha256(open(work_file, 'rb').read()).hexdigest()
    print("Work SHA256 after copy from desktop:", wk_sha)
else:
    print("Desktop file not found!")
