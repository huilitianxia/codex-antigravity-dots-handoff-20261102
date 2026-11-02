import openpyxl
import os
import json
from collections import defaultdict

# 1. Check 21-Family V2 TSV for the MFN shipping SKUs
tsv_path = r'D:\4A\01_便签店运营_2026-10\01_官方上传表格_核心在用\4A_全店21大家族精细化变体清洗_终极纯净版_V2.tsv'
with open(tsv_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = [l.rstrip('\n').split('\t') for l in f]

h4 = lines[3]
h5 = lines[4]
targets = {'4A ST303X12NZ', '4A GM406SL-10', '4A GM40612-L', '4A GM40612', '4A GM608SL-5', '4A GM404SL-15', '4A 000', '4A GMBP2222 NGPOY'}
print("=== 1. 21-FAMILY V2 TSV ROWS FOR TARGETS ===")
for r in lines[6:]:
    for cell in r[:5]:
        if cell in targets:
            non_empty = {f"{i}:{h5[i] if i<len(h5) else ''}": v for i, v in enumerate(r) if v != ''}
            print(cell, json.dumps(non_empty, ensure_ascii=False))

# 2. Check Amazon Bulk order 2023 & 2024 + 周订单总表 2023 & 2024
print("\n=== 2. VC BULK ORDER 2023 & 2024 TOP SELLERS ===")
vc_totals = defaultdict(lambda: {'qty': 0, 'cost': 0.0, 'orders': 0})
for fn in [r'D:\4A\02_老资料_表格与订单\Amazon Bulk order-2023总表.xlsx', r'D:\4A\02_老资料_表格与订单\Amazon Bulk order-2024总表.xlsx']:
    if os.path.exists(fn):
        wb = openpyxl.load_workbook(fn, read_only=True, data_only=True)
        for s in wb.sheetnames:
            ws = wb[s]
            for r in ws.iter_rows(min_row=2, values_only=True):
                if r and len(r) >= 7 and r[2] and isinstance(r[4], (int, float)):
                    model = str(r[2]).strip()
                    vc_totals[model]['qty'] += int(r[4])
                    vc_totals[model]['cost'] += float(r[6] or 0)
                    vc_totals[model]['orders'] += 1

for model, d in sorted(vc_totals.items(), key=lambda x: -x[1]['cost'])[:35]:
    print(f"  {model:25s} | Orders={d['orders']:3d} | Qty={d['qty']:6d} | Wholesale=${d['cost']:10.2f}")

# 3. Read 4A_暑期要回老品_工厂排产复产推荐清单.xlsx and 4A-SL缺货评分好款_父体已修正.xlsx
print("\n=== 3. 暑期要回老品 & 被低估好款 ===")
for fn in [r'D:\4A\02_老资料_表格与订单\4A_暑期要回老品_工厂排产复产推荐清单.xlsx', r'D:\4A\02_老资料_表格与订单\4A-SL缺货评分好款_父体已修正.xlsx']:
    wb = openpyxl.load_workbook(fn, read_only=True, data_only=True)
    for s in wb.sheetnames:
        ws = wb[s]
        rows = list(ws.iter_rows(values_only=True))
        print(f"File={os.path.basename(fn)} | Sheet={s} | Rows={len(rows)}")
        for r in rows[:20]:
            if any(x is not None for x in r):
                print("  ", [x for x in r[:12] if x is not None][:10])
