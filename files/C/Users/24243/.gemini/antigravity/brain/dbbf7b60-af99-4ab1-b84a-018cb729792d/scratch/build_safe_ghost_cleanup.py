import openpyxl
from collections import defaultdict
import csv

def build_safe_ghost_cleanup():
    mapping_path = r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx'
    wb_map = openpyxl.load_workbook(mapping_path, data_only=True)
    ws_map = wb_map.worksheets[1]

    # Map all ASINs to their SKUs
    asin_to_skus = defaultdict(list)
    for r in range(2, ws_map.max_row + 1):
        sku = str(ws_map.cell(r, 7).value or '').strip()
        asin = str(ws_map.cell(r, 8).value or '').strip()
        stock = ws_map.cell(r, 12).value
        rating = ws_map.cell(r, 14).value
        status = ws_map.cell(r, 17).value
        title = ws_map.cell(r, 19).value or ''
        if sku and asin:
            asin_to_skus[asin].append({
                'row': r,
                'sku': sku,
                'asin': asin,
                'stock': stock,
                'rating': rating,
                'status': status,
                'title': title
            })

    to_delete = []
    keep_stock = []
    keep_high_rating = []

    for asin, skus in asin_to_skus.items():
        aaaa_in_asin = [s for s in skus if s['sku'].startswith('AAAA') or s['sku'].startswith('AA ')]
        non_aaaa = [s for s in skus if not (s['sku'].startswith('AAAA') or s['sku'].startswith('AA '))]

        for a_sku in aaaa_in_asin:
            s_val = a_sku['stock']
            has_stock = s_val not in [None, 0, '0', '', 'None']
            try:
                if float(str(s_val).strip()) > 0:
                    has_stock = True
                else:
                    has_stock = False
            except:
                pass

            if has_stock:
                keep_stock.append(a_sku)
                continue

            # It has 0 stock. Now check rating.
            rating_val = None
            try:
                if a_sku['rating'] not in [None, 'None', '']:
                    rating_val = float(str(a_sku['rating']).strip())
            except:
                pass

            other_sku_names = [o['sku'] for o in non_aaaa]

            info = {
                'sku': a_sku['sku'],
                'asin': asin,
                'stock': 0,
                'rating': rating_val if rating_val is not None else '无评分',
                'status': a_sku['status'],
                'other_skus': ", ".join(other_sku_names) if other_sku_names else '无其他SKU',
                'title': a_sku['title']
            }

            # User strict criteria: "既没货评分又不高的"
            # Low or no rating: rating is None or rating < 4.0
            if rating_val is None or rating_val < 4.0:
                to_delete.append(info)
            else:
                keep_high_rating.append(info)

    print(f"Total AAAA SKUs examined: {len(to_delete) + len(keep_stock) + len(keep_high_rating)}")
    print(f"  - Safe To Delete (0 Stock & Low/No Rating): {len(to_delete)}")
    print(f"  - Protected Keep (In-Stock > 0): {len(keep_stock)}")
    print(f"  - Protected Keep (High Rating >= 4.0): {len(keep_high_rating)}")

    # 1. Create Detailed Excel Audit Workbook
    wb_out = openpyxl.Workbook()
    
    # Sheet 1: To Delete
    ws1 = wb_out.active
    ws1.title = "待删除100个无货低评幽灵SKU"
    headers1 = ["序号", "幽灵SKU", "对应ASIN", "当前库存", "前台评分", "在售状态", "同ASIN其他活跃SKU", "商品标题"]
    ws1.append(headers1)
    for i, it in enumerate(to_delete, 1):
        ws1.append([i, it['sku'], it['asin'], it['stock'], it['rating'], it['status'], it['other_skus'], it['title']])

    # Sheet 2: Keep Stock
    ws2 = wb_out.create_sheet(title="严格保护保留的8个现货SKU")
    headers2 = ["序号", "SKU", "对应ASIN", "FBA在库现货", "前台评分", "在售状态", "商品标题"]
    ws2.append(headers2)
    for i, it in enumerate(keep_stock, 1):
        ws2.append([i, it['sku'], it['asin'], it['stock'], it['rating'], it['status'], it['title']])

    # Sheet 3: Keep High Rating
    ws3 = wb_out.create_sheet(title="严格保护保留的高分评SKU")
    headers3 = ["序号", "SKU", "对应ASIN", "当前库存", "前台评分", "在售状态", "同ASIN其他活跃SKU", "商品标题"]
    ws3.append(headers3)
    for i, it in enumerate(keep_high_rating, 1):
        ws3.append([i, it['sku'], it['asin'], it['stock'], it['rating'], it['status'], it['other_skus'], it['title']])

    excel_path = r'E:\Desktop\4A_100个无货低评幽灵SKU_安全审计明细表.xlsx'
    wb_out.save(excel_path)
    print(f"Saved audit workbook to: {excel_path}")

    # 2. Build Official Amazon Delete TSV Feed based on Add_new_variant.xlsm Template
    tpl_path = r'D:\下载文件\Add_new_variant.xlsm'
    wb_tpl = openpyxl.load_workbook(tpl_path, keep_vba=True)
    ws_tpl = wb_tpl['Template']

    # Clear template data rows from row 7 onwards
    for r in range(7, ws_tpl.max_row + 1):
        for c in range(1, ws_tpl.max_column + 1):
            ws_tpl.cell(r, c).value = None

    curr_r = 7
    for it in to_delete:
        ws_tpl.cell(curr_r, 1, 'Child row > Do not edit or delete')
        ws_tpl.cell(curr_r, 2, it['sku'])
        ws_tpl.cell(curr_r, 3, 'SELF_STICK_NOTE')
        ws_tpl.cell(curr_r, 4, 'Delete')  # Official Amazon Delete Instruction!
        curr_r += 1

    tsv_path = r'E:\Desktop\4A_100个无货低评幽灵SKU_官方批量删除表.tsv'
    with open(tsv_path, 'w', encoding='utf-8', newline='') as f:
        for r in range(1, curr_r):
            row_vals = []
            for c in range(1, ws_tpl.max_column + 1):
                v = ws_tpl.cell(r, c).value
                if v is None:
                    row_vals.append('')
                else:
                    v_str = str(v).replace('\t', ' ').replace('\r', '').replace('\n', ' ')
                    row_vals.append(v_str)
            f.write('\t'.join(row_vals) + '\n')

    print(f"Generated official delete TSV: {tsv_path} with {len(to_delete)} rows.")

if __name__ == '__main__':
    build_safe_ghost_cleanup()
