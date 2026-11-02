import openpyxl
import shutil
import hashlib
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

# First check AAAA 4A 305-Full Glue price in All Listings Report
with open(r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\商品报告_11-01-2026.txt", "r", encoding="utf-8", errors="replace") as f:
    lines = f.readlines()

headers = lines[0].strip().split("\t")
for line in lines[1:]:
    parts = line.strip().split("\t")
    if len(parts) > 4 and ("305-Full Glue" in line or "B07FK9BYHW" in line):
        row_dict = dict(zip(headers, parts))
        print("Found in All Listings:", row_dict.get("seller-sku"), "ASIN:", row_dict.get("asin1"), "Price:", row_dict.get("price"), "Qty:", row_dict.get("quantity"), "Channel:", row_dict.get("fulfillment-channel"))
