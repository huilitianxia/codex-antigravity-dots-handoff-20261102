import openpyxl
import shutil
import hashlib
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

SRC_XLSM = r"D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm"
WORK_DIR = r"D:\4A\00_当前工作区_202611"
DESKTOP_DIR = r"E:\Desktop"

wb = openpyxl.load_workbook(SRC_XLSM, keep_vba=True)
ws = wb['Template']
max_col = ws.max_column

sku_to_row = {}
for r in range(7, ws.max_row + 1):
    s = ws.cell(r, 3).value
    if s:
        sku_to_row[str(s).strip()] = r

def extract_row_values(r):
    return [ws.cell(r, c).value for c in range(1, max_col + 1)]

specs = [
    {"sku": "4A 0166",     "mfg": "4A",              "color": "White-polar Bear", "colormap": "White",      "fix_in_units": True,  "note": "Fix 90244 Package Length/Width/Height Unit 'IN' -> 'Inches' + clear Item Highlight (549 FBA units)"},
    {"sku": "4A 039",      "mfg": "4A",              "color": "Orange&pink",      "colormap": "Multicolor", "fix_in_units": True,  "note": "Match exact Amazon catalog Color='Orange&pink' revealed after Mfg fix (1,073 FBA units)"},
    {"sku": "4A 040",      "mfg": "4A",              "color": "Red&pink",         "colormap": "Multicolor", "fix_in_units": True,  "note": "Match exact Amazon catalog Color='Red&pink' revealed after Mfg fix (917 FBA units)"},
    {"sku": "4A 037",      "mfg": "4A（USA）LIMITED", "color": "Green&yellow",     "colormap": "Multicolor", "fix_in_units": True,  "note": "Match exact Amazon catalog Color='Green&yellow' revealed in 8541 message (553 FBA units)"},
    {"sku": "4A 60238",    "mfg": "4A（USA）LIMITED", "color": "Colors-60238",     "colormap": "Multicolor", "fix_in_units": True,  "note": "Match exact Amazon catalog Color='Colors-60238' revealed after Mfg fix (5 MFN units)"},
    {"sku": "4A SF-60238", "mfg": "4A（USA）LIMITED", "color": "Colors-60238",     "colormap": "Multicolor", "fix_in_units": True,  "note": "Align same-ASIN B01MATR9TE Color='Colors-60238' (381 MFN units)"},
]

rows_to_write = []
for spec in specs:
    sku = spec["sku"]
    src_r = sku_to_row[sku]
    vals = extract_row_values(src_r)
    vals[4] = "Edit (Partial Update)"
    # Clear Col 9 (0-based, 1-based 10, J: Item Highlight) so 100476 never triggers
    vals[9] = None
    vals[19] = spec["mfg"]
    vals[58] = spec["color"]
    vals[254] = spec["colormap"]
    # Replace any 'IN' with 'Inches' in dimension unit columns
    fixed_units = []
    for c_idx in range(len(vals)):
        if vals[c_idx] == "IN":
            h4 = str(ws.cell(4, c_idx + 1).value or '')
            vals[c_idx] = "Inches"
            fixed_units.append((c_idx, h4))
    rows_to_write.append({
        "vals": vals,
        "audit": {
            "sku": sku,
            "source_row": src_r,
            "mfg": vals[19],
            "color": vals[58],
            "colormap": vals[254],
            "fixed_in_units": fixed_units,
            "note": spec["note"]
        }
    })

# Clear rows 7..max_row
for r in range(7, ws.max_row + 1):
    for c in range(1, max_col + 1):
        ws.cell(r, c).value = None

audit_list = []
for idx, item in enumerate(rows_to_write):
    target_r = 7 + idx
    for c_idx, v in enumerate(item["vals"]):
        ws.cell(target_r, c_idx + 1).value = v
    audit_list.append(item["audit"])

out_work = os.path.join(WORK_DIR, "18-batch14-residual-followup.xlsm")
out_desk = os.path.join(DESKTOP_DIR, "18-batch14-residual-followup.xlsm")
out_audit = os.path.join(WORK_DIR, "batch18_cell_audit.json")

wb.save(out_work)
shutil.copy2(out_work, out_desk)
with open(out_audit, "w", encoding="utf-8") as f:
    json.dump(audit_list, f, ensure_ascii=False, indent=2)

sha = hashlib.sha256(open(out_work, "rb").read()).hexdigest()
print(f"Batch 18 built & copied to Desktop! Rows={len(rows_to_write)}, SHA256={sha}")
for a in audit_list:
    print(" ", a)
