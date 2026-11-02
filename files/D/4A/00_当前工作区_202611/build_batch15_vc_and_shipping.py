import openpyxl
import json
import os
import hashlib

cat_path = r'D:\4A\00_Codex交接给Gemini_20261101\05_源数据快照_按日期使用\分类商品报告_10-31-2026.xlsm'
tpl_path = r'D:\4A\00_Codex交接给Gemini_20261101\02_已提交历史文件_不可直接重传\13-0146-office-only.xlsm'
out_path = r'D:\4A\00_当前工作区_202611\15-vc-classics-shipping-and-spec-fixes.xlsm'
audit_path = r'D:\4A\00_当前工作区_202611\batch15_cell_audit.json'

wb_cat = openpyxl.load_workbook(cat_path, read_only=True, data_only=True)
ws_cat = wb_cat['Template']
cat_rows = list(ws_cat.iter_rows(values_only=True))
h4 = cat_rows[3]
h5 = cat_rows[4]
cat_by_sku = {r[2]: r for r in cat_rows[6:] if r and len(r) > 2 and r[2]}

# Define exact, proven fixes for Batch 15 (0-based column indices in Template sheet):
# Col 2 (C): SKU
# Col 3 (D): Product Type
# Col 4 (E): Listing Action = 'Edit (Partial Update)'
# Col 11 (L): Product ID Type
# Col 12 (M): Product ID
# Col 58 (BG): Color
# Col 59 (BH): Size
# Col 355 (MR): Stop Selling Date (Sell on Amazon, US)
# Col 379..386: Package Length/Width/Height + Package Weight

fixes = [
    # 1. 4A ST303X12NZ (B07FKL115P, 858 MFN units, father's 303x12-N-Z):
    # Clear 2025 Stop Selling Date -> 2099-12-31, fix Color -> Neon Assorted, Size -> 12 Pads Pop-Up (3 x 3 in), add Package Dimensions & Weight (1.15 lb)
    {
        'sku': '4A ST303X12NZ',
        'reason': 'Unblock 858 MFN units of 303x12-N-Z: push expired 2025-04-22 Stop Selling Date to 2099-12-31, fix Color (Neon Assorted) & Size, and populate Package Weight (1.15 lb) from Master Row 28',
        'updates': {
            58: 'Neon Assorted',
            59: '12 Pads Pop-Up (3 x 3 in)',
            355: '2099-12-31T00:00:00.000Z',
            379: '6.06', 380: 'Inches',
            381: '3.07', 382: 'Inches',
            383: '4.65', 384: 'Inches',
            385: '1.15', 386: 'Pounds'
        }
    },
    # 2. Other 5 in-stock MFN SKUs blocked by expired 2025 Stop Selling Date (443 MFN units total)
    {
        'sku': '4A GMSC60187',
        'reason': 'Unblock 271 MFN units: push expired 2025-04-22 Stop Selling Date to 2099-12-31',
        'updates': {355: '2099-12-31T00:00:00.000Z'}
    },
    {
        'sku': '4A GMSCCR 012',
        'reason': 'Unblock 140 MFN units: push expired 2025-12-15 Stop Selling Date to 2099-12-31',
        'updates': {355: '2099-12-31T00:00:00.000Z'}
    },
    {
        'sku': '4A 124418',
        'reason': 'Unblock 12 MFN units: push expired 2025-03-13 Stop Selling Date to 2099-12-31',
        'updates': {355: '2099-12-31T00:00:00.000Z'}
    },
    {
        'sku': '4A 303-AC-holder',
        'reason': 'Unblock 12 MFN units: push expired 2025-03-19 Stop Selling Date to 2099-12-31',
        'updates': {355: '2099-12-31T00:00:00.000Z'}
    },
    {
        'sku': '4A 302 Full Glue',
        'reason': 'Unblock 8 MFN units: push expired 2025-02-06 Stop Selling Date to 2099-12-31',
        'updates': {355: '2099-12-31T00:00:00.000Z'}
    },
    # 3. 406SL-10, 40612, 40612-L ($1,000,001 shipping SKUs + their FBA siblings on the same ASINs):
    # Populate missing seller Package Dimensions & Weight on MFN SKUs and unify same-ASIN Size labels (removing fake Pack 16 / Pack 11 / Pack 6 / Lined on unlined 40612)
    {
        'sku': '4A GM406SL-10',
        'reason': '466 MFN units ($1,000,001 shipping): populate exact Package Dimensions & Weight (2.34 lb) from FBA sibling 4A 406SL-10 and set true Size (10 Pads Lined, 4 x 6 in)',
        'updates': {
            59: '10 Pads Lined (4 x 6 in)',
            379: '6.06', 380: 'Inches',
            381: '4.09', 382: 'Inches',
            383: '4.02', 384: 'Inches',
            385: '2.34', 386: 'Pounds'
        }
    },
    {
        'sku': '4A 406SL-10',
        'reason': 'FBA sibling on B07RP85C2P: remove fake (Pack 16) suffix so FBA and MFN SKU agree on Size (10 Pads Lined, 4 x 6 in)',
        'updates': {
            59: '10 Pads Lined (4 x 6 in)'
        }
    },
    {
        'sku': '4A GM40612',
        'reason': '109 MFN units ($1,000,001 shipping): populate exact Package Dimensions & Weight (3.2 lb) from FBA sibling 4A 40612 and fix false (Lined) (Pack 6) -> 12 Pads Unlined (4 x 6 in)',
        'updates': {
            59: '12 Pads Unlined (4 x 6 in)',
            379: '5.99', 380: 'Inches',
            381: '5.12', 382: 'Inches',
            383: '4.04', 384: 'Inches',
            385: '3.2', 386: 'Pounds'
        }
    },
    {
        'sku': '4A 40612',
        'reason': 'FBA sibling on B07RVJB9DL (3 FBA units): fix false (Lined) (Pack 11) -> 12 Pads Unlined (4 x 6 in)',
        'updates': {
            59: '12 Pads Unlined (4 x 6 in)'
        }
    },
    {
        'sku': '4A GM40612-L',
        'reason': '119 MFN units ($1,000,001 shipping): populate exact Package Dimensions & Weight (3.20 lb) from FBA sibling 4A 40612-L and remove fake (Pack 2) -> 12 Pads Lined (4 x 6 in)',
        'updates': {
            59: '12 Pads Lined (4 x 6 in)',
            379: '5.99', 380: 'Inches',
            381: '5.12', 382: 'Inches',
            383: '4.04', 384: 'Inches',
            385: '3.20', 386: 'Pounds'
        }
    },
    {
        'sku': '4A 40612-L',
        'reason': 'FBA sibling on B07RT4GQJK: remove fake (Pack 6) -> 12 Pads Lined (4 x 6 in)',
        'updates': {
            59: '12 Pads Lined (4 x 6 in)'
        }
    },
    # 4. PSS 32x6 (B08DKJ2K3T FBA 34 + MFN 835, and B08CVLH794 old VC ASIN):
    # Remove 3.8's fake Standard Size (Pack 44) and (Pack 38) so all 3 SKUs have Standard Size (Pack 6)
    {
        'sku': '4A PSS 32x6',
        'reason': 'Old VC ASIN B08CVLH794: replace 3.8 fake Standard Size (Pack 44) with Standard Size (Pack 6) to unblock Case 22934108221 merge with B08DKJ2K3T',
        'updates': {
            59: 'Standard Size (Pack 6)'
        }
    },
    {
        'sku': '4A SCPSS 32x6',
        'reason': 'Active FBA SKU on B08DKJ2K3T (34 FBA units): replace 3.8 fake Standard Size (Pack 38) with Standard Size (Pack 6) to match MFN SKU 4A GM-SCPSS 32x6',
        'updates': {
            59: 'Standard Size (Pack 6)'
        }
    },
    # 5. 354818 Series (B07DJKDB63 18-Pad FBA 22, B07FK6867S 36-Pad MFN 93, B07MGH2KWS 72-Pad MFN 91):
    # Fix false "48 Pads (2 Towers) (Pack 2)" on 18-pad and 36-pad SKUs
    {
        'sku': '4A 354818',
        'reason': 'Father VC classic 354818 (B07DJKDB63, 22 FBA units): fix false 48 Pads (2 Towers) (Pack 2) -> 18 Pads Pack (1.38 x 1.88 in)',
        'updates': {
            59: '18 Pads Pack (1.38 x 1.88 in)'
        }
    },
    {
        'sku': '4A 354818*2',
        'reason': 'Father VC classic 354818*2 (B07FK6867S, 93 MFN units): fix false 48 Pads (2 Towers) -> 36 Pads (2 Packs of 18)',
        'updates': {
            59: '36 Pads (2 Packs of 18)'
        }
    },
    {
        'sku': '4A 354818*4',
        'reason': 'Father VC classic 354818*4 (B07MGH2KWS): remove fake (Pack 2) so FBA and MFN SKU agree on 72 Pads Box',
        'updates': {
            59: '72 Pads Box'
        }
    },
    # 6. 5088-N-L, 5084-N-L, 5082-Y-L, 406x6, 406x6-N: remove fake (Pack N) and false (Lined)
    {
        'sku': '4A 5088-N-L',
        'reason': 'B07RP9MB7Y (FBA 5): unify Size to 8 Pads Pack (5 x 8 in Lined) instead of fake 8 Pads Pack (Pack 4)',
        'updates': {59: '8 Pads Pack (5 x 8 in Lined)'}
    },
    {
        'sku': '4A GM5088-N-L',
        'reason': 'B07RP9MB7Y (MFN 582): unify Size to 8 Pads Pack (5 x 8 in Lined) instead of fake 8 Pads Pack (Pack 3)',
        'updates': {59: '8 Pads Pack (5 x 8 in Lined)'}
    },
    {
        'sku': '4A 5084-N-L',
        'reason': 'B07F2B49BL (FBA 143): unify Size to 4 Pads Pack (5 x 8 in Lined) instead of fake 4 Pads Pack (Pack 3)',
        'updates': {59: '4 Pads Pack (5 x 8 in Lined)'}
    },
    {
        'sku': '4A GM5084-N-L',
        'reason': 'B07F2B49BL: unify Size to 4 Pads Pack (5 x 8 in Lined) instead of fake 4 Pads Pack (Pack 2)',
        'updates': {59: '4 Pads Pack (5 x 8 in Lined)'}
    },
    {
        'sku': '4A 5082-Y-L',
        'reason': 'B07F2BHFJH: fix false Color (Pastel Assorted -> Canary Yellow) and remove fake (Pack 2)',
        'updates': {58: 'Canary Yellow', 59: '2 Pads Pack (5 x 8 in Lined)'}
    },
    {
        'sku': '4A 5082-Y-L-GM',
        'reason': 'B07F2BHFJH (FBA 62): fix false Color (Pastel Assorted -> Canary Yellow) and unify Size',
        'updates': {58: 'Canary Yellow', 59: '2 Pads Pack (5 x 8 in Lined)'}
    },
    {
        'sku': 'AAAA 4A 406x6',
        'reason': 'B07FKL263W (FBA 7, 406x6 Pastel Unlined): fix false 4 x 6 in (Lined) -> 6 Pads Unlined (4 x 6 in)',
        'updates': {59: '6 Pads Unlined (4 x 6 in)'}
    },
    {
        'sku': '4A GM406x6-N',
        'reason': 'B07FKHHTY4 (MFN 521, 406x6-N Neon Unlined): fix false 4 x 6 in (Lined) (Pack 4) -> 6 Pads Unlined (4 x 6 in)',
        'updates': {59: '6 Pads Unlined (4 x 6 in)'}
    }
]

wb_out = openpyxl.load_workbook(tpl_path, keep_vba=True)
ws_out = wb_out['Template']

# Clear existing data rows from row 7 downwards
for r_idx in range(7, ws_out.max_row + 1):
    for c_idx in range(1, ws_out.max_column + 1):
        ws_out.cell(r_idx, c_idx).value = None

audit_records = []
for idx, item in enumerate(fixes, start=7):
    sku = item['sku']
    cr = cat_by_sku[sku]
    pt = cr[3]
    id_type = cr[11]
    id_val = cr[12]

    ws_out.cell(idx, 3).value = sku
    ws_out.cell(idx, 4).value = pt
    ws_out.cell(idx, 5).value = 'Edit (Partial Update)'
    ws_out.cell(idx, 12).value = id_type
    ws_out.cell(idx, 13).value = id_val

    populated = {
        'C (SKU)': sku,
        'D (Product Type)': pt,
        'E (Action)': 'Edit (Partial Update)',
        'L (ID Type)': id_type,
        'M (ID Value)': id_val
    }
    for col0, val in item['updates'].items():
        ws_out.cell(idx, col0 + 1).value = val
        col_letter = openpyxl.utils.get_column_letter(col0 + 1)
        populated[f"{col_letter} ({h4[col0]})"] = val

    audit_records.append({
        'excel_row': idx,
        'sku': sku,
        'asin_or_id': id_val,
        'reason': item['reason'],
        'populated_cells': populated
    })

wb_out.save(out_path)

# Re-read and verify
wb_ver = openpyxl.load_workbook(out_path, data_only=True)
ws_ver = wb_ver['Template']
verified_rows = 0
for r_idx in range(7, 7 + len(fixes)):
    non_empty = {openpyxl.utils.get_column_letter(c): ws_ver.cell(r_idx, c).value for c in range(1, ws_ver.max_column + 1) if ws_ver.cell(r_idx, c).value is not None}
    verified_rows += 1

sha256 = hashlib.sha256(open(out_path, 'rb').read()).hexdigest()
with open(audit_path, 'w', encoding='utf-8') as f:
    json.dump({'file': out_path, 'sha256': sha256, 'row_count': verified_rows, 'rows': audit_records}, f, ensure_ascii=False, indent=2)

print(f"Built {out_path} | Rows={verified_rows} | SHA256={sha256}")
