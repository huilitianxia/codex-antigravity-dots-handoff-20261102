import json
import sys
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\family_mapping_export.json", 'r', encoding='utf-8') as f:
    family_buckets = json.load(f)

from generate_family_mapping import FAMILIES_META

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Styles
header_font = Font(name="微软雅黑", size=11, bold=True, color="FFFFFF")
header_fill_blue = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
header_fill_gold = PatternFill(start_color="C65911", end_color="C65911", fill_type="solid")
header_fill_navy = PatternFill(start_color="2F3542", end_color="2F3542", fill_type="solid")

data_font = Font(name="微软雅黑", size=10)
bold_font = Font(name="微软雅黑", size=10, bold=True)
small_font = Font(name="微软雅黑", size=9, color="555555")

master_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid") # soft blue
merge_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") # soft yellow
child_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")

thin_border = Border(
    left=Side(style='thin', color='D9D9D9'),
    right=Side(style='thin', color='D9D9D9'),
    top=Side(style='thin', color='D9D9D9'),
    bottom=Side(style='thin', color='D9D9D9')
)

align_center = Alignment(horizontal='center', vertical='center', wrap_text=True)
align_left = Alignment(horizontal='left', vertical='center', wrap_text=True)
align_right = Alignment(horizontal='right', vertical='center')

# ==========================================================
# TAB 1: 【全店15大家族总览】
# ==========================================================
ws_summary = wb.create_sheet(title="全店15大家族总览")
summary_headers = [
    "家族编号", "超级品类家族名称", "父体 SKU (Parent SKU)", "变体主题 (Variation Theme)", 
    "主力保留 ASIN (Master ASIN)", "主力保留 SKU", "纳入成员数", "在售 FBA 现货", 
    "工厂实物库存", "可聚合历史好评数", "核心改善指标与作战收益"
]
ws_summary.append(summary_headers)
for col_idx, h in enumerate(summary_headers, 1):
    cell = ws_summary.cell(row=1, column=col_idx)
    cell.font = header_font
    cell.fill = header_fill_blue
    cell.alignment = align_center
    cell.border = thin_border
ws_summary.row_dimensions[1].height = 28

total_members = 0
total_fba = 0
total_wh = 0
total_reviews = 0

for fam_key in sorted(FAMILIES_META.keys()):
    meta = FAMILIES_META[fam_key]
    items = family_buckets.get(fam_key, [])
    
    fba_sum = sum(it.get('fba_qty', 0) for it in items)
    wh_sum = sum(it.get('wh_qty', 0) for it in items if isinstance(it.get('wh_qty', 0), (int, float)))
    rev_sum = sum(it.get('reviews', 0) for it in items if isinstance(it.get('reviews', 0), (int, float)))
    
    total_members += len(items)
    total_fba += fba_sum
    total_wh += wh_sum
    total_reviews += rev_sum
    
    row_data = [
        f"Hero-{meta['id']:02d}",
        meta['name'],
        meta['parent_sku'],
        meta['theme'],
        meta['master_asin'],
        meta['master_sku'],
        len(items),
        fba_sum,
        wh_sum,
        rev_sum,
        meta['benefit']
    ]
    ws_summary.append(row_data)
    curr_row = ws_summary.max_row
    ws_summary.row_dimensions[curr_row].height = 36
    for c_idx in range(1, len(row_data) + 1):
        cell = ws_summary.cell(row=curr_row, column=c_idx)
        cell.font = data_font
        cell.border = thin_border
        if c_idx in [1, 4, 5, 6]:
            cell.alignment = align_center
        elif c_idx in [7, 8, 9, 10]:
            cell.alignment = align_right
            cell.font = bold_font
        else:
            cell.alignment = align_left

# Add Total Row
total_row = [
    "合计", "全店15大超级家族大变体总计", "--", "--", "--", "--", 
    total_members, total_fba, total_wh, total_reviews, 
    "彻底统合全店 700+ 历史散碎 Listing 与 163 款现货，消除同店竞价内耗，汇聚上万真实评价！"
]
ws_summary.append(total_row)
r_total = ws_summary.max_row
ws_summary.row_dimensions[r_total].height = 32
for c_idx in range(1, len(total_row) + 1):
    cell = ws_summary.cell(row=r_total, column=c_idx)
    cell.font = Font(name="微软雅黑", size=11, bold=True, color="9C0006")
    cell.fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
    cell.border = thin_border
    if c_idx in [7, 8, 9, 10]:
        cell.alignment = align_right
    else:
        cell.alignment = align_center if c_idx < 7 else align_left

# ==========================================================
# TAB 2: 【全量变体合并与挂载映射总表】(939 rows)
# ==========================================================
ws_all = wb.create_sheet(title="全量变体合并与挂载总表")
all_headers = [
    "家族编号", "超级品类家族", "父体 SKU (Parent SKU)", "变体主题", "主力目标 ASIN",
    "合并/挂载角色", "子体 SKU", "子体 ASIN", "ColorName (颜色属性)", "NumberOfItems (包装数量)",
    "StyleName (款式风格)", "FBA 在售现货", "历史好评数", "星级", "官方售价 ($)", "WooCommerce 售价 ($)",
    "官方状态", "推荐执行操作", "商品标题"
]
ws_all.append(all_headers)
for col_idx, h in enumerate(all_headers, 1):
    cell = ws_all.cell(row=1, column=col_idx)
    cell.font = header_font
    cell.fill = header_fill_navy
    cell.alignment = align_center
    cell.border = thin_border
ws_all.row_dimensions[1].height = 26

for fam_key in sorted(FAMILIES_META.keys()):
    meta = FAMILIES_META[fam_key]
    items = family_buckets.get(fam_key, [])
    # Sort: Master first, then Merge Duplicates with high reviews, then Children
    def sort_key(x):
        r = x.get('role', '')
        score = 0
        if r == 'MASTER_TARGET': score = 1000000
        elif r == 'MERGE_DUPLICATE': score = 500000 + (x.get('reviews') or 0)
        else: score = (x.get('fba_qty') or 0)
        return score
    items.sort(key=sort_key, reverse=True)
    
    for it in items:
        role = it.get('role', 'VARIATION_CHILD')
        role_label = ""
        exec_action = ""
        if role == 'MASTER_TARGET':
            role_label = "【保留主力】Master Target"
            exec_action = "主力页面保留 (吸收其他链接评价与库存)"
        elif role == 'MERGE_DUPLICATE':
            role_label = "【合并重复】Merge ASIN"
            exec_action = "卖家助手 -> 合并重复商品 (无损转移库存与好评)"
        else:
            role_label = "【变体挂载】Variation Child"
            exec_action = "变体向导 / 批量模板 (PartialUpdate 无损挂载)"
            
        row_vals = [
            f"Hero-{meta['id']:02d}",
            meta['name'].split()[0],
            meta['parent_sku'],
            meta['theme'],
            meta['master_asin'],
            role_label,
            it.get('sku', ''),
            it.get('asin', ''),
            it.get('color_name', ''),
            it.get('number_of_items', ''),
            it.get('style_name', ''),
            it.get('fba_qty', 0),
            it.get('reviews', 0),
            it.get('stars', ''),
            it.get('price', ''),
            it.get('woo_price', ''),
            it.get('status', ''),
            exec_action,
            it.get('title', '')
        ]
        ws_all.append(row_vals)
        c_row = ws_all.max_row
        ws_all.row_dimensions[c_row].height = 20
        for col_idx in range(1, len(row_vals) + 1):
            cell = ws_all.cell(row=c_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if role == 'MASTER_TARGET':
                cell.fill = master_fill
            elif role == 'MERGE_DUPLICATE':
                cell.fill = merge_fill
                
            if col_idx in [1, 4, 5, 6, 7, 8, 14, 17]:
                cell.alignment = align_center
            elif col_idx in [12, 13, 15, 16]:
                cell.alignment = align_right
            else:
                cell.alignment = align_left

# ==========================================================
# TABS 3~17: INDIVIDUAL FAMILY SHEETS
# ==========================================================
for fam_key in sorted(FAMILIES_META.keys()):
    meta = FAMILIES_META[fam_key]
    items = family_buckets.get(fam_key, [])
    tab_title = f"H{meta['id']:02d}_{meta['name'].split()[0][:8]}"
    ws_fam = wb.create_sheet(title=tab_title)
    
    # Title info banner
    ws_fam.merge_cells("A1:J1")
    banner = ws_fam.cell(row=1, column=1)
    banner.value = f"【超级家族 Hero-{meta['id']:02d}】{meta['name']} —— 变体架构与映射执行表"
    banner.font = Font(name="微软雅黑", size=13, bold=True, color="FFFFFF")
    banner.fill = header_fill_gold
    banner.alignment = Alignment(horizontal='left', vertical='center', indent=1)
    ws_fam.row_dimensions[1].height = 32
    
    ws_fam.merge_cells("A2:J2")
    sub_banner = ws_fam.cell(row=2, column=1)
    sub_banner.value = f"父体 SKU: {meta['parent_sku']}  |  变体主题: {meta['theme']}  |  主力保留: {meta['master_asin']} ({meta['master_sku']})  |  收益: {meta['benefit']}"
    sub_banner.font = Font(name="微软雅黑", size=10, italic=True)
    sub_banner.fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    sub_banner.alignment = Alignment(horizontal='left', vertical='center', indent=1)
    ws_fam.row_dimensions[2].height = 24
    
    fam_headers = [
        "挂载/合并角色", "子体 SKU", "子体 ASIN", "ColorName", "NumberOfItems", 
        "StyleName", "FBA 在售现货", "历史好评数", "星级", "官方售价 ($)", "WooCommerce 价", "执行指引", "商品标题"
    ]
    ws_fam.append(fam_headers)
    ws_fam.row_dimensions[3].height = 24
    for c_idx, h in enumerate(fam_headers, 1):
        cell = ws_fam.cell(row=3, column=c_idx)
        cell.font = header_font
        cell.fill = header_fill_blue
        cell.alignment = align_center
        cell.border = thin_border
        
    for it in items:
        role = it.get('role', 'VARIATION_CHILD')
        role_label = "【保留主力】Master Target" if role == 'MASTER_TARGET' else ("【合并重复】Merge ASIN" if role == 'MERGE_DUPLICATE' else "【变体挂载】Variation Child")
        exec_guide = "保留为父体锚点" if role == 'MASTER_TARGET' else ("卖家助手 -> 合并重复 ASIN" if role == 'MERGE_DUPLICATE' else "变体向导 / 表格挂载")
        row_vals = [
            role_label,
            it.get('sku', ''),
            it.get('asin', ''),
            it.get('color_name', ''),
            it.get('number_of_items', ''),
            it.get('style_name', ''),
            it.get('fba_qty', 0),
            it.get('reviews', 0),
            it.get('stars', ''),
            it.get('price', ''),
            it.get('woo_price', ''),
            exec_guide,
            it.get('title', '')
        ]
        ws_fam.append(row_vals)
        c_row = ws_fam.max_row
        ws_fam.row_dimensions[c_row].height = 20
        for col_idx in range(1, len(row_vals) + 1):
            cell = ws_fam.cell(row=c_row, column=col_idx)
            cell.font = data_font
            cell.border = thin_border
            if role == 'MASTER_TARGET': cell.fill = master_fill
            elif role == 'MERGE_DUPLICATE': cell.fill = merge_fill
            if col_idx in [1, 2, 3, 9, 12]: cell.alignment = align_center
            elif col_idx in [7, 8, 10, 11]: cell.alignment = align_right
            else: cell.alignment = align_left

# Auto-adjust column widths for all sheets
for ws in wb.worksheets:
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val_str = str(cell.value or '')
            if cell.row in [1, 2] and ws.title.startswith('H'): continue # ignore merged banner
            # count double-width chars
            length = sum(2 if ord(c) > 127 else 1 for c in val_str[:50])
            if length > max_len: max_len = length
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 11), 50)

excel_out = r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\4A_全店变体合并全量大排查与挂载映射总表.xlsx"
wb.save(excel_out)
print(f"Excel successfully saved to: {excel_out}")
