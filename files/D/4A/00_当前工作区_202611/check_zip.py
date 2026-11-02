import zipfile
import sys

sys.stdout.reconfigure(encoding='utf-8')

zip_path = r"D:\4A\Codex给Gemini_已处理未处理交接与D盘复核_20261101.zip"
with zipfile.ZipFile(zip_path, 'r') as z:
    for name in z.namelist():
        # Try decoding CP437 or GBK if needed
        print(name)
