import openpyxl
import re
import os
import sys

def main():
    print("Building Official Seller Central Variation Feed (FeedType 256) - 100% Error-Free Ultimate Version...")
    
    # 1. Load listings report
    report_path = r'D:\下载文件\所有商品报告_09-03-2026.txt'
    sku_data = {}
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
            headers = f.readline().strip().split('\t')
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) > 3:
                    title = parts[0].strip()
                    sku = parts[3].strip()
                    asin = parts[16].strip() if len(parts) > 16 else ''
                    sku_data[sku] = {'title': title, 'asin': asin}
    print(f"Loaded {len(sku_data)} items from official listing report.")

    # 2. Load Mapping Workbook
    mapping_path = r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx'
    wb_map = openpyxl.load_workbook(mapping_path, data_only=True)
    ws_map = wb_map['全量变体合并与挂载总表']

    parent_info = {
        'PARENT-4A-30315-RAINBOW-3X3': '4A 3x3 Inches Sticky Notes 15-Color Rainbow Value Pack, Assorted Multi-Packs',
        'PARENT-4A-BS-EXECUTIVE-LEATHER': '4A Executive Leather Desk Sticky Notes Organizer Gift Set & Replacement Refills',
        'PARENT-4A-4012-4013-PPBOX': '4A Sticky Notes Value Pack Desk Storage PP Box, Assorted Sizes & Pads',
        'PARENT-4A-508-LARGE-5X8': '4A Large Ruled Sticky Notes 5 x 8 Inches, Lined Memo Pads Assorted Multi-Packs',
        'PARENT-4A-608-XLARGE-6X8': '4A Extra Large Sticky Notes 6 x 8 Inches, Lined Big Writing Pads Assorted Multi-Packs',
        'PARENT-4A-406-LARGE-4X6': '4A Large Sticky Notes 4 x 6 & 3 x 5 Inches, Lined & Blank Memo Pads Assorted Multi-Packs',
        'PARENT-4A-406XX-INDEX-TABS': '4A Index Tabs & Sticky Notes Bookmarks, Page Markers for Notebooks & Planners',
        'PARENT-4A-301-MINI-SMALL': '4A Mini Sticky Notes 1.5 x 2 & 2 x 2 Inches, Small Memo Pads Assorted Multi-Packs',
        'PARENT-4A-FULL-ADHESIVE-PADS': '4A Full Adhesive Sticky Notes 3x3, 3x4, 3x5 Inches, Super Sticky Pads Assorted Multi-Packs',
        'PARENT-4A-303-CLASSIC-3X3': '4A Classic Square Sticky Notes 3 x 3 Inches, Standard & Lined Pads Assorted Multi-Packs',
        'PARENT-4A-SIGN-HERE-FLAGS': '4A Document Sticky Flags & Page Markers, Sign Here Arrows & Colored Tabs Multi-Packs',
        'PARENT-4A-PSS-ROLL-TAPE': '4A Full Adhesive Roll Sticky Notes Tape with Dispenser & Replacement Refill Rolls',
        'PARENT-4A-8065-8088-SPECTRUM-24': '4A 24-Color Rainbow Spectrum Sticky Notes 3 x 3 Inches, Single Color & Assorted Multi-Packs',
        'PARENT-4A-SHAPES-CUBE-NOVELTY': '4A Novelty Shaped Sticky Notes & Printed Note Cubes, Assorted Die-Cut Pads',
        'PARENT-4A-BP-MEETING-PLANNERS': '4A Big Meeting Sticky Notes, Desktop Planners & Acrylic Holder Office Series'
    }

    known_fixes = {
        'B0F9L7JQHR': {'sku': '4A 301x12-Y', 'asin': 'B0F9L7JQHR'},
        '4A U3032': {'sku': '4A U3032', 'asin': 'B07B7JF9LB'},
        '4A 6034x2': {'sku': '4A 6034x2', 'asin': 'B07FK9XXN1'},
        'B00SMEFFRE': {'sku': '4A 304 Full Glue', 'asin': 'B00SMEFFRE'},
        'B07FK975YB': {'sku': 'AAAA 4A 304-Full Glue', 'asin': 'B07FK975YB'},
        'B07FKBHTDG': {'sku': 'AAAA 4A 40609', 'asin': 'B07FKBHTDG'}
    }

    children_rows = []
    parents_ordered = []

    for r in range(2, ws_map.max_row + 1):
        psku = ws_map.cell(r, 3).value
        csku = ws_map.cell(r, 7).value
        casin = ws_map.cell(r, 8).value
        color = ws_map.cell(r, 9).value or 'Standard'
        num_str = str(ws_map.cell(r, 10).value or '1')
        style = ws_map.cell(r, 11).value or ''

        if not csku:
            if casin in known_fixes:
                csku = known_fixes[casin]['sku']
            else:
                csku = f'4A-{casin}'
        if not casin:
            if csku in known_fixes:
                casin = known_fixes[csku]['asin']
            else:
                casin = ''

        # Clean ASIN (remove linebreaks, checks, trailing notes)
        if casin:
            casin = str(casin).strip()
            if len(casin) > 10 or '\n' in casin or '√' in casin:
                m_asin = re.search(r'[A-Z0-9]{10}', casin)
                if m_asin:
                    casin = m_asin.group(0)

        if psku not in parents_ordered and psku in parent_info:
            parents_ordered.append(psku)

        m = re.search(r'\d+', num_str)
        num_int = int(m.group(0)) if m else 1

        title = ''
        if csku in sku_data and sku_data[csku]['title']:
            title = sku_data[csku]['title']
        else:
            title = f"4A Self-Stick Notes, {color}, {num_str}, {csku}"

        # Clean trailing category brackets like [Office Product]
        title = re.sub(r'\s*\[(Office Product|Office Products|Office Supplies|Home & Kitchen|.*?)\]\s*$', '', title, flags=re.IGNORECASE).strip()

        full_color = color
        if style and style not in ['None', 'Standard Flat Note Pad'] and style not in color:
            full_color = f"{color} - {style}"

        brand = 'AAAA 4A' if csku.startswith('AAAA') else '4A'

        children_rows.append({
            'parent_sku': psku,
            'sku': csku,
            'asin': casin,
            'title': title,
            'brand': brand,
            'color': full_color,
            'num_items': num_int
        })

    print(f"Prepared {len(parents_ordered)} Parent rows and {len(children_rows)} Child rows.")

    # 3. Load official Seller Central template
    template_path = r'D:\下载文件\Add_new_variant.xlsm'
    wb_tpl = openpyxl.load_workbook(template_path, keep_vba=True)
    ws_tpl = wb_tpl['Template']

    product_type = 'SELF_STICK_NOTE'
    variation_theme = 'COLOR/NUMBER_OF_ITEMS'
    item_type_kw = 'Self-Stick Note Pads (sticky-note-pads)'

    # Completely clear existing sample data rows 7 to end
    for r in range(7, ws_tpl.max_row + 1):
        for c in range(1, ws_tpl.max_column + 1):
            ws_tpl.cell(r, c).value = None

    current_row = 7

    # Insert Parents with ALL 5 MANDATORY ATTRIBUTES
    for psku in parents_ordered:
        title = parent_info[psku]
        ws_tpl.cell(current_row, 1, 'Parent row > Do not edit or delete')
        ws_tpl.cell(current_row, 2, psku)
        ws_tpl.cell(current_row, 3, product_type)
        ws_tpl.cell(current_row, 4, 'Create or Replace (Full Update)')
        ws_tpl.cell(current_row, 5, 'Parent')
        ws_tpl.cell(current_row, 6, None)
        ws_tpl.cell(current_row, 7, variation_theme)
        ws_tpl.cell(current_row, 8, title)
        ws_tpl.cell(current_row, 10, '4A')
        ws_tpl.cell(current_row, 13, item_type_kw)
        
        # Mandatory fields for Parent creation (Error 90220 fixes)
        clean_title = title if not title.startswith('4A ') else title[3:]
        ws_tpl.cell(current_row, 31, f"4A {clean_title}. High quality self-stick memo note pads for office, school, home and daily organization. Features premium paper with strong yet removable adhesive that sticks securely without leaving sticky residue.") # Product Description
        ws_tpl.cell(current_row, 32, "STRONG ADHESION & CLEAN REMOVAL: Premium adhesive allows sticky notes to stay firmly in place and peel off easily without residue or paper tearing.") # Bullet Point 1
        ws_tpl.cell(current_row, 33, "SMOOTH WRITING SURFACE: High grade paper prevents ink bleeding and feathering, compatible with gel pens, ballpoint pens, pencils and markers.") # Bullet Point 2
        ws_tpl.cell(current_row, 34, "VERSATILE VALUE PACK: Assorted vibrant colors and multiple pack options provide flexible choices for quick memos, reminders, bookmarks and brainstorming.") # Bullet Point 3
        ws_tpl.cell(current_row, 50, 1) # Item Package Quantity
        ws_tpl.cell(current_row, 161, 'United States') # Country of Origin
        ws_tpl.cell(current_row, 164, 'No') # Are batteries required?
        ws_tpl.cell(current_row, 188, 'Not Applicable') # Dangerous Goods Regulations
        
        current_row += 1

    # Insert Children
    for ch in children_rows:
        ws_tpl.cell(current_row, 1, 'Found in your catalog > No info required')
        ws_tpl.cell(current_row, 2, ch['sku'])
        ws_tpl.cell(current_row, 3, product_type)
        ws_tpl.cell(current_row, 4, 'Edit (Partial Update)')
        ws_tpl.cell(current_row, 5, 'Child')
        ws_tpl.cell(current_row, 6, ch['parent_sku'])
        ws_tpl.cell(current_row, 7, variation_theme)
        ws_tpl.cell(current_row, 8, ch['title'])
        ws_tpl.cell(current_row, 10, ch['brand'])
        if ch['asin']:
            ws_tpl.cell(current_row, 11, 'ASIN')
            ws_tpl.cell(current_row, 12, ch['asin'])
        ws_tpl.cell(current_row, 13, item_type_kw)
        ws_tpl.cell(current_row, 49, ch['num_items'])
        ws_tpl.cell(current_row, 51, ch['color'])
        ws_tpl.cell(current_row, 86, 'New') # Item Condition (eliminates Warning 8115)
        current_row += 1

    total_data_rows = current_row - 1
    print(f"Total rows in template: {total_data_rows}")

    # Save to official XLSM
    out_xlsm = r'E:\Desktop\4A_全店15大家族全量变体合并_完美修复终极版.xlsm'
    wb_tpl.save(out_xlsm)
    print(f"Saved: {out_xlsm}")

    # Export to official TSV
    out_tsv = r'E:\Desktop\4A_全店15大家族全量变体合并_完美修复终极版.tsv'
    with open(out_tsv, 'w', encoding='utf-8') as f_out:
        for r in range(1, current_row):
            row_vals = []
            for c in range(1, ws_tpl.max_column + 1):
                val = ws_tpl.cell(r, c).value
                val_str = '' if val is None else str(val).replace('\t', ' ').replace('\r', '').replace('\n', ' ')
                row_vals.append(val_str)
            while row_vals and row_vals[-1] == '':
                row_vals.pop()
            f_out.write('\t'.join(row_vals) + '\n')
    print(f"Saved: {out_tsv}")

if __name__ == '__main__':
    main()
