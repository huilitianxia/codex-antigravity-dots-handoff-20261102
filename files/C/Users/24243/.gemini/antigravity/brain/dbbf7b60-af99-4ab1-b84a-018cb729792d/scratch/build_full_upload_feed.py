import openpyxl
import re
import os
import sys

def main():
    print("Starting Amazon Bulk Upload Template generation for ALL 15 Families...")
    
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
                    pid = parts[22].strip() if len(parts) > 22 else ''
                    sku_data[sku] = {'title': title, 'asin': asin, 'pid': pid}
    print(f"Loaded {len(sku_data)} records from official listing report.")

    # 2. Load Mapping Workbook
    mapping_path = r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx'
    wb_map = openpyxl.load_workbook(mapping_path, data_only=True)
    ws_map = wb_map['全量变体合并与挂载总表']

    # Parent definitions
    parent_info = {
        'PARENT-4A-30315-RAINBOW-3X3': {
            'title': '4A 3x3 Inches Sticky Notes 15-Color Rainbow Value Pack, Assorted Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'High quality 3x3 inch self-stick notes in 15 vibrant rainbow colors. Strong adhesive sticks securely and removes cleanly.'
        },
        'PARENT-4A-BS-EXECUTIVE-LEATHER': {
            'title': '4A Executive Leather Desk Sticky Notes Organizer Gift Set & Replacement Refills',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Deluxe executive faux leather desk organizer with colored memo pads, index flags, and 2-year reference calendar.'
        },
        'PARENT-4A-4012-4013-PPBOX': {
            'title': '4A Sticky Notes Value Pack Desk Storage PP Box, Assorted Sizes & Pads',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Convenient clear PP desk organizer storage box containing multiple assorted sizes of sticky note pads and page flags.'
        },
        'PARENT-4A-508-LARGE-5X8': {
            'title': '4A Large Ruled Sticky Notes 5 x 8 Inches, Lined Memo Pads Assorted Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Generous 5x8 inch large sticky notes with ruled lines for detailed task lists, meeting minutes, and study notes.'
        },
        'PARENT-4A-608-XLARGE-6X8': {
            'title': '4A Extra Large Sticky Notes 6 x 8 Inches, Lined Big Writing Pads Assorted Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Extra large 6x8 inch ruled memo pads with ample writing space for classroom, office presentations, and brainstorms.'
        },
        'PARENT-4A-406-LARGE-4X6': {
            'title': '4A Large Sticky Notes 4 x 6 & 3 x 5 Inches, Lined & Blank Memo Pads Assorted Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Versatile 4x6 and 3x5 inch note pads in vibrant neon and soft pastel colors for daily office, home, and school reminders.'
        },
        'PARENT-4A-406XX-INDEX-TABS': {
            'title': '4A Index Tabs & Sticky Notes Bookmarks, Page Markers for Notebooks & Planners',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Eye-catching index tabs and bookmark sticky notes with ruler scale and lined sections for planners, textbooks, and files.'
        },
        'PARENT-4A-301-MINI-SMALL': {
            'title': '4A Mini Sticky Notes 1.5 x 2 & 2 x 2 Inches, Small Memo Pads Assorted Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Compact 1.5x2 and 2x2 inch small sticky notes for brief annotations, calendar markings, quick tabs, and desktop tags.'
        },
        'PARENT-4A-FULL-ADHESIVE-PADS': {
            'title': '4A Full Adhesive Sticky Notes 3x3, 3x4, 3x5 Inches, Super Sticky Pads Assorted Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Full adhesive sticky pads with 100% surface tackiness. Stays flat without edge curling on laptops, whiteboards, and walls.'
        },
        'PARENT-4A-303-CLASSIC-3X3': {
            'title': '4A Classic Square Sticky Notes 3 x 3 Inches, Standard & Lined Pads Assorted Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Classic 3x3 inch standard and lined square memo pads in cheerful pastel and bright neon hues for all desktop note-taking.'
        },
        'PARENT-4A-SIGN-HERE-FLAGS': {
            'title': '4A Document Sticky Flags & Page Markers, Sign Here Arrows & Colored Tabs Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Professional Sign Here arrow flags and index tabs for legal contracts, accounting ledgers, and document signatures.'
        },
        'PARENT-4A-PSS-ROLL-TAPE': {
            'title': '4A Full Adhesive Roll Sticky Notes Tape with Dispenser & Replacement Refill Rolls',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Continuous full adhesive sticky note paper roll with reusable desktop dispenser cutter. Cut any custom length on demand.'
        },
        'PARENT-4A-8065-8088-SPECTRUM-24': {
            'title': '4A 24-Color Rainbow Spectrum Sticky Notes 3 x 3 Inches, Single Color & Assorted Multi-Packs',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Comprehensive 24-color rainbow spectrum collection of 3x3 inch self-stick notes for color-coded organization.'
        },
        'PARENT-4A-SHAPES-CUBE-NOVELTY': {
            'title': '4A Novelty Shaped Sticky Notes & Printed Note Cubes, Assorted Die-Cut Pads',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Creative die-cut novelty memo shapes including puzzles, leaves, hearts, and 4-sided printed note memo cubes.'
        },
        'PARENT-4A-BP-MEETING-PLANNERS': {
            'title': '4A Big Meeting Sticky Notes, Desktop Planners & Acrylic Holder Office Series',
            'theme': 'COLOR/NUMBER_OF_ITEMS',
            'bullet': 'Large format meeting whiteboard sticky pads, weekly planning memo pads, and heavy-duty crystal acrylic stationery organizers.'
        }
    }

    # Extract all rows from mapping workbook
    children_rows = []
    parents_ordered = []
    
    # Specific known fixes for missing data
    known_fixes = {
        'B0F9L7JQHR': {'sku': '4A 301x12-Y', 'asin': 'B0F9L7JQHR'},
        '4A U3032': {'sku': '4A U3032', 'asin': 'B07B7JF9LB', 'upc': '702877124574'},
        '4A 6034x2': {'sku': '4A 6034x2', 'asin': 'B07FK9XXN1'},
        'B00SMEFFRE': {'sku': '4A 304 Full Glue', 'asin': 'B00SMEFFRE'},
        'B07FK975YB': {'sku': 'AAAA 4A 304-Full Glue', 'asin': 'B07FK975YB'},
        'B07FKBHTDG': {'sku': 'AAAA 4A 40609', 'asin': 'B07FKBHTDG'}
    }

    for r in range(2, ws_map.max_row + 1):
        psku = ws_map.cell(r, 3).value
        csku = ws_map.cell(r, 7).value
        casin = ws_map.cell(r, 8).value
        color = ws_map.cell(r, 9).value or 'Standard'
        num_str = str(ws_map.cell(r, 10).value or '1')
        style = ws_map.cell(r, 11).value or ''
        
        # Apply known fixes
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

        if psku not in parents_ordered and psku in parent_info:
            parents_ordered.append(psku)

        # Parse number of items integer
        m = re.search(r'\d+', num_str)
        num_int = int(m.group(0)) if m else 1

        # Extract title from report or fallback
        title = ''
        if csku in sku_data and sku_data[csku]['title']:
            title = sku_data[csku]['title']
        else:
            title = f"4A Self-Stick Notes, {color}, {num_str}, {csku}"

        # Combine style into color if style has rich differentiation
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

    # 3. Load official Amazon template
    template_path = r'D:\下载文件\Self-stick_Note_Pads_2026-10-29T13_06.xlsm'
    wb_tpl = openpyxl.load_workbook(template_path, keep_vba=True)
    ws_tpl = wb_tpl['Template-SELF_STICK_NOTE']

    # Remove existing sample data rows 7 to max_row
    if ws_tpl.max_row >= 7:
        ws_tpl.delete_rows(7, ws_tpl.max_row - 6)

    vendor_code = '4A（USA）LIMITED -- Dropship, us_office_products, 4AUSA'
    product_type = 'SELF_STICK_NOTE'
    variation_theme = 'COLOR/NUMBER_OF_ITEMS'

    current_row = 7

    # Insert Parents first
    for psku in parents_ordered:
        p = parent_info[psku]
        ws_tpl.cell(current_row, 1, vendor_code)                      # Vendor Code
        ws_tpl.cell(current_row, 2, psku)                             # Vendor SKU
        ws_tpl.cell(current_row, 3, product_type)                     # Product Type
        ws_tpl.cell(current_row, 4, 'Parent')                         # Parentage Level
        ws_tpl.cell(current_row, 5, None)                             # Child Relationship Type
        ws_tpl.cell(current_row, 6, None)                             # Parent SKU
        ws_tpl.cell(current_row, 7, variation_theme)                  # Variation Theme Name
        ws_tpl.cell(current_row, 8, p['title'])                       # Item Name
        ws_tpl.cell(current_row, 10, '4A')                            # Brand Name
        ws_tpl.cell(current_row, 34, p['bullet'])                     # Bullet Point 1
        ws_tpl.cell(current_row, 103, 'No')                           # Are batteries required?
        ws_tpl.cell(current_row, 127, 'Not Applicable')               # Dangerous Goods Regulations
        current_row += 1

    # Insert Children
    for ch in children_rows:
        ws_tpl.cell(current_row, 1, vendor_code)                      # Vendor Code
        ws_tpl.cell(current_row, 2, ch['sku'])                        # Vendor SKU
        ws_tpl.cell(current_row, 3, product_type)                     # Product Type
        ws_tpl.cell(current_row, 4, 'Child')                          # Parentage Level
        ws_tpl.cell(current_row, 5, 'Variation')                      # Child Relationship Type
        ws_tpl.cell(current_row, 6, ch['parent_sku'])                 # Parent SKU
        ws_tpl.cell(current_row, 7, variation_theme)                  # Variation Theme Name
        ws_tpl.cell(current_row, 8, ch['title'])                      # Item Name
        ws_tpl.cell(current_row, 10, ch['brand'])                     # Brand Name
        if ch['asin']:
            ws_tpl.cell(current_row, 11, 'ASIN')                      # External Product ID Type
            ws_tpl.cell(current_row, 12, ch['asin'])                  # External Product ID
            ws_tpl.cell(current_row, 13, ch['asin'])                  # Merchant Suggested ASIN
        ws_tpl.cell(current_row, 34, f"Standard office self-stick memo notes. Color: {ch['color']}, Quantity: {ch['num_items']} pads.")
        ws_tpl.cell(current_row, 45, ch['num_items'])                 # Number of Items
        ws_tpl.cell(current_row, 47, ch['color'])                     # Color
        ws_tpl.cell(current_row, 103, 'No')                           # Are batteries required?
        ws_tpl.cell(current_row, 127, 'Not Applicable')               # Dangerous Goods Regulations
        current_row += 1

    # Save official .xlsm template
    out_xlsm = r'E:\Desktop\4A_全店15大家族全量变体合并_亚马逊官方批量上传表.xlsm'
    wb_tpl.save(out_xlsm)
    print(f"Successfully generated XLSM: {out_xlsm} (Total rows: {current_row - 1})")

    # Also export TSV flat file
    out_tsv = r'E:\Desktop\4A_全店15大家族全量变体合并_亚马逊官方批量上传表.tsv'
    with open(out_tsv, 'w', encoding='utf-8', errors='ignore') as f_out:
        for r in range(1, current_row):
            row_vals = []
            for c in range(1, ws_tpl.max_column + 1):
                val = ws_tpl.cell(r, c).value
                val_str = '' if val is None else str(val).replace('\t', ' ').replace('\n', ' ')
                row_vals.append(val_str)
            # trim trailing empty cells
            while row_vals and row_vals[-1] == '':
                row_vals.pop()
            f_out.write('\t'.join(row_vals) + '\n')
    print(f"Successfully generated TSV: {out_tsv}")

if __name__ == '__main__':
    main()
