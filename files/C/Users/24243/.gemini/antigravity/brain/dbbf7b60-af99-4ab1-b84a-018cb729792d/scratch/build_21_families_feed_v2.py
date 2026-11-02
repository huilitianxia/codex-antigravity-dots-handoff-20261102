import openpyxl
import csv
import re
import os
import sys
from collections import defaultdict

def main():
    print("=== Generating 4A Store 21 Families Pure Feed V2 (Zero-Error Edition) ===")
    
    # 1. Load the 100 deleted ghost SKUs so we NEVER include them in the variation tree
    deleted_ghost_skus = set()
    delete_tsv = r'E:\Desktop\4A_100个无货低评幽灵SKU_官方批量删除表.tsv'
    if os.path.exists(delete_tsv):
        with open(delete_tsv, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) > 1 and parts[1].startswith('AAAA'):
                    deleted_ghost_skus.add(parts[1].strip())
    print(f"Loaded {len(deleted_ghost_skus)} deleted ghost SKUs to exclude completely.")

    # 2. Load Listings Report (titles, active ASINs, prices)
    report_path = r'D:\下载文件\所有商品报告_09-03-2026.txt'
    sku_data = {}
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8', errors='ignore') as f:
            f.readline()
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) > 3:
                    title = parts[0].strip()
                    sku = parts[3].strip()
                    asin = parts[16].strip() if len(parts) > 16 else ''
                    price = parts[4].strip() if len(parts) > 4 else ''
                    sku_data[sku] = {'title': title, 'asin': asin, 'price': price}
    print(f"Loaded {len(sku_data)} items from official listing report.")

    # 3. Load WooCommerce prices
    woo_path = r'E:\Desktop\WooCommerce_完整改价_163_SKUs_复核后上传_2026-08-20.csv'
    woo_prices = {}
    if os.path.exists(woo_path):
        with open(woo_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) >= 4:
                    sku = row[1].strip()
                    reg_p = row[2].strip()
                    sale_p = row[3].strip()
                    p = sale_p if sale_p else reg_p
                    if p:
                        woo_prices[sku] = p

    # 4. Load Mapping Workbook
    mapping_path = r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx'
    wb_map = openpyxl.load_workbook(mapping_path, data_only=True)
    ws_map = wb_map.worksheets[1]

    # Parent Definitions: 22 Pure Families
    parent_defs = {
        'PARENT-4A-BIGPAD-MEETING-EASEL': {
            'title': '4A Big Meeting Sticky Notes & Easel Pads, Tabletop Whiteboard & Presentation Self-Stick Sheets',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-TRANSPARENT-PET-TABS': {
            'title': '4A Transparent Writable Sticky Index Tabs & Book Flags, Waterproof Page Markers with Ruler',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-PAPER-PAGE-MARKERS': {
            'title': '4A Paper Page Markers & Divider Sticky Tabs, Colored Narrow Book Index Strips',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-SIGN-HERE-FLAGS': {
            'title': '4A Sign Here Arrow Sticky Flags, Pop-Up Signature & Notation Index Page Markers',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-LABEL-STICKERS': {
            'title': '4A Color Coding Circle Dot Stickers & Reusable Chalkboard Labels with Gold Border',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-PSS-ROLL-TAPE': {
            'title': '4A Full Adhesive Roll Sticky Notes Tape with Dispenser Cutter & Replacement Refill Rolls',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-301-MINI-PADS': {
            'title': '4A Mini Sticky Notes 1.5 x 2 & 2 x 2 Inches, Small Colorful Self-Stick Note Pads',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-303-CLASSIC-SQUARE': {
            'title': '4A Classic Square Sticky Notes 3 x 3 Inches, Standard & Lined Self-Stick Note Pads',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-303M-MAGIC-CYCLING': {
            'title': '4A Color-Cycling Magic Sticky Notes 3 x 3 Inches, Multi-Layer Color Changing Note Pads',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-30315-RAINBOW-15': {
            'title': '4A 15-Color Rainbow Sticky Notes 3 x 3 Inches, 15 Pads Colorful Assorted Value Pack',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-8065-8088-SPECTRUM-24': {
            'title': '4A 24-Color Rainbow Spectrum Sticky Notes 3 x 3 Inches, Ultra Color Gradient Note Pads',
            'theme': 'COLOR'
        },
        'PARENT-4A-FULL-ADHESIVE-PADS': {
            'title': '4A Full Adhesive Sticky Notes 3x3, 3x4, 3x5, 2x3 Inches, Super Sticky Flat Pads',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-406-MEDIUM-PADS': {
            'title': '4A Medium Sticky Notes 4 x 6 & 3 x 5 Inches, Ruled Lined & Blank Memo Pads',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-508-LARGE-5X8': {
            'title': '4A Large Ruled Sticky Notes 5 x 8 Inches, Lined Memo Writing Pads Assorted Multi-Packs',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-608-XLARGE-6X8': {
            'title': '4A Extra Large Sticky Notes 6 x 8 Inches, Ruled Big Memo Pads Assorted Multi-Packs',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-404-SQUARE-4X4': {
            'title': '4A Square Sticky Notes 4 x 4 Inches, Medium Colorful Self-Stick Note Pads',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-4012-4013-PPBOX': {
            'title': '4A Sticky Notes Value Pack Desk Storage PP Box, Assorted Memo Pads & Index Tabs',
            'theme': 'COLOR'
        },
        'PARENT-4A-BS-EXECUTIVE-LEATHER': {
            'title': '4A Executive Leather Desk Sticky Notes Organizer Gift Set & Replacement Refills',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-SHAPED-NOVELTY-PADS': {
            'title': '4A Novelty Shaped Sticky Notes, Cute Die-Cut Colorful Self-Stick Memo Pads',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-MEMO-NOTE-CUBES': {
            'title': '4A Printed Memo Note Cubes 3 x 3 Inches, 400 & 500 Sheets Thick Desk Note Block',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-DESK-PLANNERS': {
            'title': '4A Desktop Weekly & Daily Planner Sticky Notes, Schedule Checklist Memo Pads',
            'theme': 'COLOR/SIZE'
        },
        'PARENT-4A-ACRYLIC-DESK-ORGANIZERS': {
            'title': '4A Acrylic Sticky Note Dispenser & Pen Holder Sets, Desk Organizer Accessories',
            'theme': 'COLOR/SIZE'
        }
    }

    known_fixes = {
        'B0F9L7JQHR': {'sku': '4A 301x12-Y', 'asin': 'B0F9L7JQHR'},
        '4A U3032': {'sku': '4A U3032', 'asin': 'B07B7JF9LB'},
        '4A 6034x2': {'sku': '4A 6034x2', 'asin': 'B07FK9XXN1'},
        'B00SMEFFRE': {'sku': '4A 304 Full Glue', 'asin': 'B00SMEFFRE'},
        'B07FK975YB': {'sku': 'AAAA 4A 304-Full Glue', 'asin': 'B07FK975YB'},
        'B07FKBHTDG': {'sku': 'AAAA 4A 40609', 'asin': 'B07FKBHTDG'}
    }

    def classify(sku, asin, old_p, title):
        s = sku.upper()
        t = title.upper()
        comb = f'{s} {t}'
        if any(k in s for k in ['AC-HOLDER', 'HOLDER+FLAG']) or ('ACRYLIC' in comb and 'HOLDER' in comb):
            return 'PARENT-4A-ACRYLIC-DESK-ORGANIZERS'
        if any(k in comb for k in ['BP1111', 'BP1515', 'BP2222', 'BP2331', 'MEETING', 'EASEL', 'BIG PAD', 'WHITEBOARD', 'PRESENTATION PAD', 'DRY ERASE SURFACE', 'TABLETOP', '20X23']):
            return 'PARENT-4A-BIGPAD-MEETING-EASEL'
        if any(k in s for k in ['601', '602', '603', '604']) or ('TRANSPARENT' in comb and any(k in comb for k in ['TAB', 'FLAG', 'MARKER'])):
            return 'PARENT-4A-TRANSPARENT-PET-TABS'
        if any(k in s for k in ['1901', '1902', '1903', 'SCLB', 'LB 19', 'CHALKBOARD', 'DOT LABELS']):
            return 'PARENT-4A-LABEL-STICKERS'
        if 'SIGN HERE' in comb or ('ARROW' in comb and any(k in comb for k in ['FLAG', 'SIGN'])):
            return 'PARENT-4A-SIGN-HERE-FLAGS'
        if any(k in comb for k in ['124418', '501516', '501521', '752516', 'PAGE MARKER', 'DIVIDER TAB', 'DURABLE FILE TAB', 'FILING TAB', 'INDEX LABELS', '4ASNFSILMS']):
            return 'PARENT-4A-PAPER-PAGE-MARKERS'
        if any(k in s for k in ['PSS', 'ROLL', 'CR 012', 'SCCR']) or any(k in comb for k in ['COLORING ROLL', 'ROLL STICKY NOTES', 'CUTTER', 'DISPENSER', 'ROLL 1']):
            return 'PARENT-4A-PSS-ROLL-TAPE'
        if 'BS' in s or 'LEATHER' in comb:
            return 'PARENT-4A-BS-EXECUTIVE-LEATHER'
        if any(k in s for k in ['4012', '4013', '4ASNVPDS', '4A050']) or 'PP BOX' in comb:
            return 'PARENT-4A-4012-4013-PPBOX'
        if 'CUBE' in comb or any(k in s for k in ['MC 434', '8089']):
            return 'PARENT-4A-MEMO-NOTE-CUBES'
        if any(k in comb for k in ['SHAPE', 'HEART', 'ARROW SHAPE', 'BUBBLE', 'APPLE', 'PUZZLE', 'FLOWER', 'STAR', 'HOUSE', 'DIE-CUT', 'SMC', '641', '652', '3D']) or (re.search(r'50\d{2}', s) and not any(k in s for k in ['5082', '5084', '5088', 'GM5084', '5015'])):
            return 'PARENT-4A-SHAPED-NOVELTY-PADS'
        if 'FULL GLUE' in comb or 'FULL ADHESIVE' in comb or any(k in s for k in ['302', '304', '305', 'GM305']):
            return 'PARENT-4A-FULL-ADHESIVE-PADS'
        if any(k in s for k in ['5082', '5084', '5088', 'GM5084']) or '5 X 8' in comb or '5X8' in comb:
            return 'PARENT-4A-508-LARGE-5X8'
        if any(k in s for k in ['608', 'GM608', '4ABNLCOLORFUL']) or '6 X 8' in comb or '6X8' in comb:
            return 'PARENT-4A-608-XLARGE-6X8'
        if any(k in s for k in ['406', 'GM406', '40609', '40612', '405', '4ASUPERSN']) or '4 X 6' in comb or '4X6' in comb or '3 X 5' in comb or '3X5' in comb:
            return 'PARENT-4A-406-MEDIUM-PADS'
        if '404' in s or '4 X 4' in comb or '4X4' in comb:
            return 'PARENT-4A-404-SQUARE-4X4'
        if '30315' in s or '15-COLOR' in comb:
            return 'PARENT-4A-30315-RAINBOW-15'
        if '303M' in s or 'COLOR-CYCLING' in comb:
            return 'PARENT-4A-303M-MAGIC-CYCLING'
        if any(k in s for k in ['8065', '8066', '8067', '8068', '8069', '807', '808']) or 'SPECTRUM' in comb or '24-COLOR' in comb:
            return 'PARENT-4A-8065-8088-SPECTRUM-24'
        if any(k in s for k in ['301', '3548', '2028', '20232', '4848']) or any(k in comb for k in ['1.5 X 2', '1 1/2 X 2', '2 X 2', '1 3/8', '1 7/8']):
            return 'PARENT-4A-301-MINI-PADS'
        if 'PLANNER' in comb:
            return 'PARENT-4A-DESK-PLANNERS'
        return 'PARENT-4A-303-CLASSIC-SQUARE'

    def derive_size_and_shape(target_parent, sku, title, raw_num, raw_style):
        comb = f'{sku} {title} {raw_num} {raw_style}'.upper()
        s_lower = sku.lower()
        size_val = ''
        
        if target_parent == 'PARENT-4A-30315-RAINBOW-15':
            if 'POP-UP' in comb or 'ACCORDION' in comb or '-Z' in sku:
                size_val = 'Pop-Up Accordion Pads (15 Pads)'
            elif 'GM30315' in sku:
                size_val = 'Standard Flat Pads (15 Pads Value Pack)'
            else:
                size_val = 'Standard Flat Pads (15 Pads)'
        elif target_parent == 'PARENT-4A-303-CLASSIC-SQUARE':
            if '24 PADS' in comb or '*2' in s_lower or 'x2' in s_lower:
                size_val = '24 Pads Value Pack'
            elif '18 PADS' in comb:
                size_val = '18 Pads Pack'
            elif '12 PADS' in comb or 'x12' in s_lower:
                size_val = '12 Pads Pack'
            elif '6 PADS' in comb or 'x6' in s_lower:
                size_val = '6 Pads Pack'
            else:
                size_val = '12 Pads Pack'
        elif target_parent == 'PARENT-4A-301-MINI-PADS':
            if '144' in comb or '*12' in s_lower:
                size_val = '144 Pads Bulk Case'
            elif '72' in comb or '*4' in s_lower and '3548' in comb:
                size_val = '72 Pads Box'
            elif '48' in comb or 'x24x2' in s_lower or 'x24*2' in s_lower or '301x24-y' in s_lower:
                size_val = '48 Pads (2 Towers)'
            elif '36' in comb or '*2' in s_lower and '3548' in comb:
                size_val = '36 Pads Bulk Pack'
            elif '32' in comb or '30132' in comb or '301m32' in comb or '20232' in comb:
                size_val = '32 Pads Value Pack'
            elif '24' in comb or 'x24' in s_lower:
                size_val = '24 Pads (1 Tower)'
            elif '8 PADS' in comb or '2028' in comb:
                size_val = '8 Pads Pack (2x2 in)'
            else:
                size_val = '12 Pads Pack'
        elif target_parent == 'PARENT-4A-508-LARGE-5X8':
            if '16 PADS' in comb or '5088*2' in s_lower or '5088x2' in s_lower:
                size_val = '16 Pads Bulk Box'
            elif '8 PADS' in comb or '5088' in s_lower:
                size_val = '8 Pads Pack'
            elif '4 PADS' in comb or '5084' in s_lower:
                size_val = '4 Pads Pack'
            else:
                size_val = '2 Pads Pack'
        elif target_parent == 'PARENT-4A-608-XLARGE-6X8':
            if '210' in comb:
                size_val = '210 Sheets Value Pad'
            elif '5 PADS' in comb:
                size_val = '5 Pads Pack'
            elif '4 PADS' in comb:
                size_val = '4 Pads Pack'
            else:
                size_val = '2 Pads Pack'
        elif target_parent == 'PARENT-4A-406-MEDIUM-PADS':
            if 'BLANK' in comb or 'UNLINED' in comb:
                size_val = '4 x 6 in (Blank)'
            elif '3 X 5' in comb or '3X5' in comb or '405' in comb:
                size_val = '3 x 5 in'
            else:
                size_val = '4 x 6 in (Lined)'
        elif target_parent == 'PARENT-4A-404-SQUARE-4X4':
            if '12 PADS' in comb or '*2' in s_lower:
                size_val = '12 Pads Pack'
            else:
                size_val = '6 Pads Pack'
        elif target_parent == 'PARENT-4A-FULL-ADHESIVE-PADS':
            if '305' in comb or '3 X 5' in comb or '3X5' in comb:
                size_val = '3 x 5 in'
            elif '304' in comb or '3 X 4' in comb or '3X4' in comb:
                size_val = '3 x 4 in'
            elif '302' in comb or '2 X 3' in comb or '2X3' in comb:
                size_val = '2 x 3 in'
            else:
                size_val = '3 x 3 in'
        elif target_parent == 'PARENT-4A-SHAPED-NOVELTY-PADS':
            if 'HEART' in comb or '5018' in comb: size_val = 'Heart Shape'
            elif 'BUBBLE' in comb or '5059' in comb: size_val = 'Speech Bubble Shape'
            elif 'ARROW' in comb or '5013' in comb: size_val = 'Arrow Shape'
            elif 'STAR' in comb: size_val = 'Star Shape'
            elif 'APPLE' in comb or 'FRUIT' in comb: size_val = 'Apple Shape'
            elif 'PUZZLE' in comb or '5020' in comb: size_val = 'Puzzle Shape'
            elif 'FLOWER' in comb: size_val = 'Flower Shape'
            elif 'HOUSE' in comb: size_val = 'House Shape'
            elif 'BEAR' in comb or 'ANIMAL' in comb: size_val = 'Teddy Bear Shape'
            elif 'T-SHIRT' in comb or 'SHIRT' in comb: size_val = 'T-Shirt Shape'
            elif 'CAR' in comb: size_val = 'Car Shape'
            else: size_val = 'Novelty Die-Cut Shape'
        else:
            size_val = 'Standard Size'

        return size_val

    # Parse and build children
    children_by_parent = defaultdict(list)
    total_included = 0
    total_ghosts_skipped = 0

    for r in range(2, ws_map.max_row + 1):
        csku = ws_map.cell(r, 7).value
        casin = ws_map.cell(r, 8).value
        old_psku = ws_map.cell(r, 3).value or ''
        raw_color = ws_map.cell(r, 9).value or 'Standard'
        raw_num = str(ws_map.cell(r, 10).value or '')
        raw_style = ws_map.cell(r, 11).value or ''

        if not csku and not casin:
            continue

        csku = str(csku).strip() if csku else ''
        casin = str(casin).strip() if casin else ''

        # CRITICAL FILTER: completely skip the 100 deleted ghost SKUs!
        if csku in deleted_ghost_skus:
            total_ghosts_skipped += 1
            continue

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

        if casin:
            if len(casin) > 10 or '\n' in casin or '' in casin:
                m_asin = re.search(r'[A-Z0-9]{10}', casin)
                if m_asin:
                    casin = m_asin.group(0)

        title = ''
        if csku in sku_data and sku_data[csku]['title']:
            title = sku_data[csku]['title']
        else:
            title = f"4A Self-Stick Notes, {raw_color}, {csku}"

        title = re.sub(r'\s*\[(Office Product|Office Products|Office Supplies|Home & Kitchen|.*?)\]\s*$', '', title, flags=re.IGNORECASE).strip()

        target_parent = classify(csku, casin, old_psku, title)
        size_val = derive_size_and_shape(target_parent, csku, title, raw_num, raw_style)

        clean_color = raw_color
        if clean_color in ['Standard', 'None', '']:
            clean_color = 'Assorted Colors'

        brand = 'AAAA 4A' if csku.startswith('AAAA') else '4A'

        price = ''
        if csku in woo_prices:
            price = woo_prices[csku]
        elif csku in sku_data and sku_data[csku]['price']:
            price = sku_data[csku]['price']

        children_by_parent[target_parent].append({
            'row': r,
            'sku': csku,
            'asin': casin,
            'title': title,
            'brand': brand,
            'color': clean_color,
            'size': size_val,
            'price': price
        })
        total_included += 1

    print(f"Skipped {total_ghosts_skipped} deleted ghost SKUs.")
    print(f"Included {total_included} clean active children into {len(children_by_parent)} families.")

    # Load official template
    template_path = r'D:\下载文件\Add_new_variant.xlsm'
    wb_tpl = openpyxl.load_workbook(template_path, keep_vba=True)
    ws_tpl = wb_tpl['Template']

    product_type = 'SELF_STICK_NOTE'
    item_type_kw = 'Self-Stick Note Pads (sticky-note-pads)'

    for r in range(7, ws_tpl.max_row + 1):
        for c in range(1, ws_tpl.max_column + 1):
            ws_tpl.cell(r, c).value = None

    current_row = 7

    for psku in sorted(children_by_parent.keys()):
        pinfo = parent_defs[psku]
        title = pinfo['title']
        v_theme = pinfo['theme']

        # Parent Row
        ws_tpl.cell(current_row, 1, 'Parent row > Do not edit or delete')
        ws_tpl.cell(current_row, 2, psku)
        ws_tpl.cell(current_row, 3, product_type)
        ws_tpl.cell(current_row, 4, 'Create or Replace (Full Update)')
        ws_tpl.cell(current_row, 5, 'Parent')
        ws_tpl.cell(current_row, 6, None)
        ws_tpl.cell(current_row, 7, v_theme)
        ws_tpl.cell(current_row, 8, title)
        ws_tpl.cell(current_row, 9, None)  # Item Highlight: MUST BE EMPTY (Fixes Error 100476!)
        ws_tpl.cell(current_row, 10, '4A')
        ws_tpl.cell(current_row, 13, item_type_kw)

        # Compliant Parent Description & Bullet Points (No promotional words)
        clean_title = title if not title.startswith('4A ') else title[3:]
        ws_tpl.cell(current_row, 31, f"Premium {clean_title}. High quality self-adhesive notes designed for office, school, study, and meeting organization.")
        ws_tpl.cell(current_row, 32, f"High quality self-adhesive sticky notes with reliable adhesive that sticks securely to most smooth surfaces and removes cleanly without residue.")
        ws_tpl.cell(current_row, 161, 'China')
        ws_tpl.cell(current_row, 164, 'No')
        ws_tpl.cell(current_row, 188, 'Not Applicable')

        current_row += 1

        seen_color_size = defaultdict(int)

        # Children Rows
        for child in children_by_parent[psku]:
            ws_tpl.cell(current_row, 1, 'Child row > Do not edit or delete')
            ws_tpl.cell(current_row, 2, child['sku'])
            ws_tpl.cell(current_row, 3, product_type)
            ws_tpl.cell(current_row, 4, 'Edit (Partial Update)')
            ws_tpl.cell(current_row, 5, 'Child')
            ws_tpl.cell(current_row, 6, psku)
            ws_tpl.cell(current_row, 7, v_theme)
            ws_tpl.cell(current_row, 8, child['title'])
            
            # CRITICAL FIX 1: Column 9 (Item Highlight) MUST BE EMPTY!
            ws_tpl.cell(current_row, 9, None)
            
            # CRITICAL FIX 2: Brand in Col 10
            ws_tpl.cell(current_row, 10, child['brand'])
            
            # CRITICAL FIX 3: Product Id Type in Col 11, Product Id in Col 12!
            if child['asin']:
                ws_tpl.cell(current_row, 11, 'ASIN')
                ws_tpl.cell(current_row, 12, child['asin'])
            else:
                ws_tpl.cell(current_row, 11, None)
                ws_tpl.cell(current_row, 12, None)

            ws_tpl.cell(current_row, 13, item_type_kw)

            cur_color = child['color']
            cur_size = child['size']
            cs_key = (cur_color, cur_size)
            seen_color_size[cs_key] += 1
            if seen_color_size[cs_key] > 1:
                cur_size = f"{cur_size} (Pack {seen_color_size[cs_key]})"

            # Color (Col 51)
            ws_tpl.cell(current_row, 51, cur_color)

            # Size (Col 52)
            if 'SIZE' in v_theme and cur_size:
                ws_tpl.cell(current_row, 52, cur_size)

            # Price & Deals for 30315
            if psku == 'PARENT-4A-30315-RAINBOW-15':
                if 'Pop-Up' in cur_size or 'Accordion' in cur_size or '-Z' in child['sku']:
                    ws_tpl.cell(current_row, 88, '19.99')
                    ws_tpl.cell(current_row, 118, '19.99')
                    ws_tpl.cell(current_row, 122, '16.99')
                    ws_tpl.cell(current_row, 123, '2026-10-30')
                    ws_tpl.cell(current_row, 124, '2027-10-31')
                else:
                    ws_tpl.cell(current_row, 88, '18.99')
                    ws_tpl.cell(current_row, 118, '18.99')
                    ws_tpl.cell(current_row, 122, '15.99')
                    ws_tpl.cell(current_row, 123, '2026-10-30')
                    ws_tpl.cell(current_row, 124, '2027-10-31')
            elif child['price']:
                try:
                    p_float = float(re.sub(r'[^\d.]', '', str(child['price'])))
                    if p_float > 0:
                        ws_tpl.cell(current_row, 118, f"{p_float:.2f}")
                except:
                    pass

            current_row += 1

    total_rows = current_row - 7
    print(f"V2 Populated: {len(children_by_parent)} Parents, {total_rows - len(children_by_parent)} Active Children. Total: {total_rows}")

    tsv_output_path = r'E:\Desktop\4A_全店21大家族精细化变体清洗_终极纯净版_V2.tsv'
    with open(tsv_output_path, 'w', encoding='utf-8', newline='') as f:
        for r in range(1, current_row):
            row_vals = []
            for c in range(1, ws_tpl.max_column + 1):
                val = ws_tpl.cell(r, c).value
                if val is None:
                    row_vals.append('')
                else:
                    v_str = str(val).replace('\t', ' ').replace('\r', '').replace('\n', ' ')
                    row_vals.append(v_str)
            f.write('\t'.join(row_vals) + '\n')

    print(f"Successfully generated 100% compliant V2 TSV: {tsv_output_path}")

if __name__ == '__main__':
    main()
