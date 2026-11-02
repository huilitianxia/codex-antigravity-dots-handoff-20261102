import csv
import glob
import shutil
import openpyxl
import sys

sys.stdout.reconfigure(encoding="utf-8")

# 1. Inspect Batch 19 (21-row) processing summary receipt
rcpt_src = r"d:\下载文件\19-voc-copy-and-pack-clarity-fixes-processing-summary (1).xlsm"
rcpt_dst = r"D:\4A\00_Codex交接给Gemini_20261101\04_正式处理回执\19-voc-copy-and-pack-clarity-fixes-processing-summary.xlsm"
shutil.copy2(rcpt_src, rcpt_dst)

wb_r = openpyxl.load_workbook(rcpt_dst, read_only=True, data_only=True)
print("=== 1. BATCH 19 (21-ROW) PROCESSING SUMMARY ===")
for name in wb_r.sheetnames:
    if "Summary" in name or "汇总" in name or "Template" in name or "处理" in name:
        ws = wb_r[name]
        print(f"--- Sheet: {name} ---")
        for i, row in enumerate(ws.iter_rows(values_only=True), 1):
            if any(row) and i <= 35:
                non_empty = [f"C{j}:{str(v)[:60]}" for j, v in enumerate(row, 1) if v is not None]
                print(f"  Row {i:2d}: {' | '.join(non_empty[:10])}")
wb_r.close()
