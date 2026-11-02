import os
import time
import shutil
import json

watch_dirs = [
    r"E:\OpenAI-Codex\CodexHome\generated_images",
    r"E:\Desktop\待上架_新图文素材库",
    r"C:\Users\24243\Documents\ChatGPT\天皇のcodex 2\outputs"
]

log_file = r"E:\Desktop\通宵自动监听与提取日志.txt"

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    print(line, end="")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line)

log("4A 通宵自动资产监听守护进程已启动...")
for d in watch_dirs:
    log(f"监控目标目录: {d} (存在: {os.path.exists(d)})")
