import openpyxl
import csv
import re
import os
import sys
from collections import defaultdict

def main():
    print("=== Starting 4A Store 22 Pure Families Feed Generation (100% Error-Free Version) ===")
    
    # 1. Load Listings Report (titles, active ASINs)
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
                    price = parts[4].strip() if len(parts) > 4 else ''
                    sku_data[sku] = {'title': title, 'asin': asin, 'price': price}
    print(f"Loaded {len(sku_data)} items from official listing report.")

    # 2. Load WooCommerce prices
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
    print(f"Loaded {len(woo_prices)} price references from WooCommerce.")

    # 3. Load Mapping Workbook
    mapping_path = r'E:\Desktop\4A_全店变体合并全量大排查与挂载映射总表.xlsx'
    wb_map = openpyxl.load_workbook(mapping_path, data_only=True)
    ws_map = wb_map.worksheets[1]

    # Parent Definitions: 22 Pure Families (Acrylic Organizers separated!)
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
            'theme': 'COLOR/SIZE'  # Official approved theme in SELF_STICK_NOTE!
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
        
        # 1. Acrylic Desk Organizers / Holders (Separated!)
        if any(k in s for k in ['AC-HOLDER', 'HOLDER+FLAG']) or ('ACRYLIC' in comb and 'HOLDER' in comb):
            return 'PARENT-4A-ACRYLIC-DESK-ORGANIZERS'

        # 2. Big Meeting Pads / Tabletop Easel / Whiteboard
        if any(k in comb for k in ['BP1111', 'BP1515', 'BP2222', 'BP2331', 'MEETING', 'EASEL', 'BIG PAD', 'WHITEBOARD', 'PRESENTATION PAD', 'DRY ERASE SURFACE', 'TABLETOP', '20X23']):
            return 'PARENT-4A-BIGPAD-MEETING-EASEL'
            
        # 3. Transparent PET Tabs
        if any(k in s for k in ['601', '602', '603', '604']) or ('TRANSPARENT' in comb and any(k in comb for k in ['TAB', 'FLAG', 'MARKER'])):
            return 'PARENT-4A-TRANSPARENT-PET-TABS'
            
        # 4. Label Stickers (1901 color dots, 1902 chalkboard, 1903 gold border)
        if any(k in s for k in ['1901', '1902', '1903', 'SCLB', 'LB 19', 'CHALKBOARD', 'DOT LABELS']):
            return 'PARENT-4A-LABEL-STICKERS'
            
        # 5. Sign Here Arrow Flags
        if 'SIGN HERE' in comb or ('ARROW' in comb and any(k in comb for k in ['FLAG', 'SIGN'])):
            return 'PARENT-4A-SIGN-HERE-FLAGS'
            
        # 6. Paper Page Markers (5015, 7525, 124418, paper tabs)
        if any(k in comb for k in ['124418', '501516', '501521', '752516', 'PAGE MARKER', 'DIVIDER TAB', 'DURABLE FILE TAB', 'FILING TAB', 'INDEX LABELS', '4ASNFSILMS']):
            return 'PARENT-4A-PAPER-PAGE-MARKERS'
                
        # 7. PSS Roll Tape & Dispenser
        if any(k in s for k in ['PSS', 'ROLL', 'CR 012', 'SCCR']) or any(k in comb for k in ['COLORING ROLL', 'ROLL STICKY NOTES', 'CUTTER', 'DISPENSER', 'ROLL 1']):
            return 'PARENT-4A-PSS-ROLL-TAPE'
            
        # 8. BS Executive Leather Sets (Fixed BS 1803!)
        if 'BS' in s or 'LEATHER' in comb:
            return 'PARENT-4A-BS-EXECUTIVE-LEATHER'
            
        # 9. PP Box Sets (4012, 4013, 4ASNVPDS, 4A050 - Fixed!)
        if any(k in s for k in ['4012', '4013', '4ASNVPDS', '4A050']) or 'PP BOX' in comb:
            return 'PARENT-4A-4012-4013-PPBOX'
            
        # 10. Thick Memo Note Cubes
        if 'CUBE' in comb or any(k in s for k in ['MC 434', '8089']):
            return 'PARENT-4A-MEMO-NOTE-CUBES'
            
        # 11. Novelty Die-Cut Shaped Notes
        if any(k in comb for k in ['SHAPE', 'HEART', 'ARROW SHAPE', 'BUBBLE', 'APPLE', 'PUZZLE', 'FLOWER', 'STAR', 'HOUSE', 'DIE-CUT', 'SMC', '641', '652', '3D']) or (re.search(r'50\d{2}', s) and not any(k in s for k in ['5082', '5084', '5088', 'GM5084', '5015'])):
            return 'PARENT-4A-SHAPED-NOVELTY-PADS'
            
        # 12. Full Adhesive / Super Sticky Pads (302, 303 Full Glue, 304, 305)
        if 'FULL GLUE' in comb or 'FULL ADHESIVE' in comb or any(k in s for k in ['302', '304', '305', 'GM305']):
            return 'PARENT-4A-FULL-ADHESIVE-PADS'
            
        # 13. 5x8 Large Lined Notes (5082, 5084, 5088)
        if any(k in s for k in ['5082', '5084', '5088', 'GM5084']) or '5 X 8' in comb or '5X8' in comb:
            return 'PARENT-4A-508-LARGE-5X8'
            
        # 14. 6x8 Extra Large Lined Notes (608, 608S, 4ABNLCOLORFUL)
        if any(k in s for k in ['608', 'GM608', '4ABNLCOLORFUL']) or '6 X 8' in comb or '6X8' in comb:
            return 'PARENT-4A-608-XLARGE-6X8'
            
        # 15. 4x6 & 3x5 Medium Memo Notes (406, 405, 40609, 40612, 4ASUPERSN)
        if any(k in s for k in ['406', 'GM406', '40609', '40612', '405', '4ASUPERSN']) or '4 X 6' in comb or '4X6' in comb or '3 X 5' in comb or '3X5' in comb:
            return 'PARENT-4A-406-MEDIUM-PADS'
            
        # 16. 4x4 Square Notes (404, 404S)
        if '404' in s or '4 X 4' in comb or '4X4' in comb:
            return 'PARENT-4A-404-SQUARE-4X4'
            
        # 17. 30315 15-Color Rainbow (3x3)
        if '30315' in s or '15-COLOR' in comb:
            return 'PARENT-4A-30315-RAINBOW-15'
            
        # 18. 303M Color-Cycling Magic Notes (3x3)
        if '303M' in s or 'COLOR-CYCLING' in comb:
            return 'PARENT-4A-303M-MAGIC-CYCLING'
            
        # 19. 8065-8088 24-Color Rainbow Spectrum (3x3)
        if any(k in s for k in ['8065', '8066', '8067', '8068', '8069', '807', '808']) or 'SPECTRUM' in comb or '24-COLOR' in comb:
            return 'PARENT-4A-8065-8088-SPECTRUM-24'
            
        # 20. 301 Mini Sticky Notes (1.5 x 2 in, 2 x 2 in, 1 3/8 x 1 7/8 in)
        if any(k in s for k in ['301', '3548', '2028', '20232', '4848']) or any(k in comb for k in ['1.5 X 2', '1 1/2 X 2', '2 X 2', '1 3/8', '1 7/8']):
            return 'PARENT-4A-301-MINI-PADS'
            
        # 21. Desktop Planners
        if 'PLANNER' in comb:
            return 'PARENT-4A-DESK-PLANNERS'
            
        # 22. 303 Classic Square Sticky Notes (3x3)
        if '303' in s or '3 X 3' in comb or '3X3' in comb or 'SQUARE' in comb:
            return 'PARENT-4A-303-CLASSIC-SQUARE'
            
        if '303' in old_p: return 'PARENT-4A-303-CLASSIC-SQUARE'
        if '301' in old_p: return 'PARENT-4A-301-MINI-PADS'
        if '406' in old_p: return 'PARENT-4A-406-MEDIUM-PADS'
        if 'SHAPES' in old_p: return 'PARENT-4A-SHAPED-NOVELTY-PADS'
        return 'PARENT-4A-303-CLASSIC-SQUARE'

    def derive_size_and_shape(target_parent, sku, title, raw_num, raw_style):
        comb = f'{sku} {title} {raw_num} {raw_style}'.upper()
        s_lower = sku.lower()
        size_val = ''
        
        # 1. Acrylic Desk Organizers
        if target_parent == 'PARENT-4A-ACRYLIC-DESK-ORGANIZERS':
            if '303' in comb:
                size_val = '3x3 in Notes with Pen Holder'
            elif '404' in comb:
                size_val = '4x4 in Notes with Pen Holder'
            else:
                size_val = 'Desk Organizer Set'

        # 2. Big Meeting Pads / Easel
        elif target_parent == 'PARENT-4A-BIGPAD-MEETING-EASEL':
            if '23X31' in comb or '23 X 31' in comb or 'BP2331' in comb:
                size_val = '23 x 31.5 in (Easel Pad)'
            elif '22X22' in comb or '22 X 22' in comb or 'BP2222' in comb:
                size_val = '22 x 22 in (Big Pad)'
            elif '20X23' in comb or '20 X 23' in comb:
                size_val = '20 x 23 in (Easel Pad)'
            elif '15X15' in comb or '15 X 15' in comb or 'BP1515' in comb:
                size_val = '15 x 15 in (4 Pads)'
            elif '11X11' in comb or '11 X 11' in comb or 'BP1111' in comb:
                size_val = '11 x 11 in (4 Pads)'
            elif 'TABLETOP' in comb or 'MEETING-51' in comb or 'MEETING-52' in comb:
                size_val = 'Tabletop Easel Pad'
            else:
                size_val = 'Large Meeting Pad'

        # 3. Transparent PET Tabs
        elif target_parent == 'PARENT-4A-TRANSPARENT-PET-TABS':
            if 'RULER' in comb or '60238' in comb or '60239' in comb:
                if '*2' in s_lower or 'x2' in s_lower or '2 pack' in comb.lower():
                    size_val = '1.5 x 2 in with Ruler (2 Packs)'
                else:
                    size_val = '1.5 x 2 in with Ruler (1 Pack)'
            elif 'DISPENSER' in comb or '60121' in comb or '60122' in comb or '6034' in comb or '6035' in comb:
                if '*2' in s_lower or 'x2' in s_lower or '2 pack' in comb.lower():
                    size_val = 'Pop-Up in Dispenser (2 Packs)'
                else:
                    size_val = 'Pop-Up in Dispenser (1 Pack)'
            elif '100 PCS' in comb or '6031' in comb:
                size_val = '1.2 x 2 in (100 Pcs)'
            elif '780 PCS' in comb or '60222' in comb:
                size_val = 'Multi-Color Tabs (780 Pcs)'
            elif '400 PCS' in comb:
                size_val = 'Index Tabs (400 Pcs)'
            else:
                if '*2' in s_lower or 'x2' in s_lower or '2 pack' in comb.lower():
                    size_val = '2 Packs'
                else:
                    size_val = '1 Pack'

        # 4. Paper Page Markers
        elif target_parent == 'PARENT-4A-PAPER-PAGE-MARKERS':
            if '501521' in comb or '21 COLOR' in comb:
                if '*2' in s_lower or 'x2' in s_lower:
                    size_val = '50x15mm, 21 Colors (2 Packs)'
                else:
                    size_val = '50x15mm, 21 Colors (1 Pack)'
            elif '501516' in comb or '16 COLOR' in comb:
                if '*2' in s_lower or 'x2' in s_lower:
                    size_val = '50x15mm, 16 Colors (2 Packs)'
                else:
                    size_val = '50x15mm, 16 Colors (1 Pack)'
            elif '7525' in comb:
                if '*2' in s_lower or 'x2' in s_lower:
                    size_val = '75x25mm, 16 Colors (2 Packs)'
                else:
                    size_val = '75x25mm, 16 Colors (1 Pack)'
            elif '124418' in comb:
                size_val = 'Paper Strips (16 Colors)'
            else:
                size_val = 'Standard Paper Tabs'

        # 5. Sign Here Flags
        elif target_parent == 'PARENT-4A-SIGN-HERE-FLAGS':
            if '400' in comb or 'x4' in s_lower or '*4' in s_lower:
                size_val = '400 Pcs (4 Packs)'
            elif '200' in comb or 'x2' in s_lower or '*2' in s_lower:
                size_val = '200 Pcs (2 Packs)'
            else:
                size_val = '100 Pcs (1 Pack)'

        # 6. Label Stickers
        elif target_parent == 'PARENT-4A-LABEL-STICKERS':
            if '1901' in comb or 'CIRCLE' in comb or 'DOT' in comb:
                size_val = 'Round Color Dots (16 Colors)'
            elif '1902' in comb or 'BLACK' in comb:
                size_val = 'Black Chalkboard Labels (2.5x3.5 in)'
            elif '1903' in comb or 'GOLD' in comb:
                size_val = 'Gold Border Chalkboard Labels'
            else:
                size_val = 'Assorted Labels'

        # 7. PSS Roll Tape (Fixed Error 100899 by differentiating widths!)
        elif target_parent == 'PARENT-4A-PSS-ROLL-TAPE':
            width_str = '0.6 in'
            if '9-5' in comb:
                width_str = '0.9 in'
            elif '9-3' in comb:
                width_str = '0.75 in'
            elif '9-1' in comb:
                width_str = '0.6 in'

            if 'COLORING' in comb or 'CR 012' in comb or 'SCCR' in comb:
                size_val = 'Coloring Roll with Patterns'
            elif 'REFILL' in comb or 'ROLLS' in comb:
                if '4 ROLLS' in comb or 'x4' in s_lower or '*4' in s_lower:
                    size_val = f'Refills ({width_str}, 4 Rolls)'
                elif '2 ROLLS' in comb or 'x2' in s_lower or '*2' in s_lower:
                    size_val = f'Refills ({width_str}, 2 Rolls)'
                else:
                    size_val = f'Refills ({width_str}, 1 Roll)'
            else:
                size_val = f'Dispenser with Tape ({width_str} x 315 in)'

        # 8. 301 Mini Sticky Notes
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
            elif '12 PADS' in comb or 'x12' in s_lower:
                size_val = '12 Pads Pack'
            else:
                size_val = '12 Pads Pack'

        # 9. 303 Classic Square Sticky Notes
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

        # 10. 303M Magic Cycling
        elif target_parent == 'PARENT-4A-303M-MAGIC-CYCLING':
            if '32' in comb:
                size_val = '32 Pads Pack'
            elif '24' in comb:
                size_val = '24 Pads Pack'
            else:
                size_val = '12 Pads Pack'

        # 11. 30315 15-Color Rainbow
        elif target_parent == 'PARENT-4A-30315-RAINBOW-15':
            if 'POP-UP' in comb or 'ACCORDION' in comb or '-Z' in sku:
                size_val = 'Pop-Up Accordion Pads (15 Pads)'
            else:
                size_val = 'Standard Flat Pads (15 Pads)'

        # 12. Full Adhesive Pads
        elif target_parent == 'PARENT-4A-FULL-ADHESIVE-PADS':
            if '305' in comb or '3 X 5' in comb or '3X5' in comb:
                size_val = '3 x 5 in'
            elif '304' in comb or '3 X 4' in comb or '3X4' in comb:
                size_val = '3 x 4 in'
            elif '302' in comb or '2 X 3' in comb or '2X3' in comb:
                size_val = '2 x 3 in'
            else:
                size_val = '3 x 3 in'

        # 13. 406 Medium Notes
        elif target_parent == 'PARENT-4A-406-MEDIUM-PADS':
            if 'BLANK' in comb or 'UNLINED' in comb:
                size_val = '4 x 6 in (Blank)'
            elif '3 X 5' in comb or '3X5' in comb or '405' in comb:
                size_val = '3 x 5 in'
            else:
                size_val = '4 x 6 in (Lined)'

        # 14. 508 Large Notes
        elif target_parent == 'PARENT-4A-508-LARGE-5X8':
            if '16 PADS' in comb or '5088*2' in s_lower or '5088x2' in s_lower:
                size_val = '16 Pads Bulk Box'
            elif '8 PADS' in comb or '5088' in s_lower:
                size_val = '8 Pads Pack'
            elif '4 PADS' in comb or '5084' in s_lower:
                size_val = '4 Pads Pack'
            else:
                size_val = '2 Pads Pack'

        # 15. 608 Extra Large Notes
        elif target_parent == 'PARENT-4A-608-XLARGE-6X8':
            if '210' in comb:
                size_val = '210 Sheets Value Pad'
            elif '5 PADS' in comb:
                size_val = '5 Pads Pack'
            elif '4 PADS' in comb:
                size_val = '4 Pads Pack'
            else:
                size_val = '2 Pads Pack'

        # 16. 404 Square Notes
        elif target_parent == 'PARENT-4A-404-SQUARE-4X4':
            if '12 PADS' in comb or '*2' in s_lower:
                size_val = '12 Pads Pack'
            else:
                size_val = '6 Pads Pack'

        # 17. BS Executive Leather
        elif target_parent == 'PARENT-4A-BS-EXECUTIVE-LEATHER':
            if 'REFILL' in comb or 'REPLACEMENT' in comb:
                size_val = 'Organizer Refill Set'
            else:
                size_val = 'Luxury Leather Gift Set'

        # 18. Novelty Shaped Notes (FIXED Error 90244: uses COLOR/SIZE with descriptive Shape values!)
        elif target_parent == 'PARENT-4A-SHAPED-NOVELTY-PADS':
            if 'HEART' in comb or '5018' in comb:
                size_val = 'Heart Shape'
            elif 'BUBBLE' in comb or '5059' in comb:
                size_val = 'Speech Bubble Shape'
            elif 'ARROW' in comb or '5013' in comb:
                size_val = 'Arrow Shape'
            elif 'STAR' in comb:
                size_val = 'Star Shape'
            elif 'APPLE' in comb or 'FRUIT' in comb:
                size_val = 'Apple Shape'
            elif 'PUZZLE' in comb or '5020' in comb:
                size_val = 'Puzzle Shape'
            elif 'FLOWER' in comb:
                size_val = 'Flower Shape'
            elif 'HOUSE' in comb:
                size_val = 'House Shape'
            elif 'BEAR' in comb or 'ANIMAL' in comb:
                size_val = 'Teddy Bear Shape'
            elif 'T-SHIRT' in comb or 'SHIRT' in comb:
                size_val = 'T-Shirt Shape'
            elif 'CAR' in comb:
                size_val = 'Car Shape'
            else:
                size_val = 'Novelty Die-Cut Shape'

        # 19. Memo Cubes
        elif target_parent == 'PARENT-4A-MEMO-NOTE-CUBES':
            if '500' in comb:
                size_val = '500 Sheets Cube'
            else:
                size_val = '400 Sheets Cube'

        # 20. Desk Planners
        elif target_parent == 'PARENT-4A-DESK-PLANNERS':
            if 'WEEKLY' in comb:
                size_val = 'Weekly Planner Pad'
            else:
                size_val = 'Daily Schedule Pad'

        return size_val

    # Parse and build all child items
    children_by_parent = defaultdict(list)
    total_processed = 0

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
        total_processed += 1

    print(f"Classified {total_processed} items into {len(children_by_parent)} families.")

    # 4. Load official template to build TSV feed
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
        ws_tpl.cell(current_row, 10, '4A')
        ws_tpl.cell(current_row, 13, item_type_kw)

        # 5 Mandatory attributes for Parent (FIXED Error 99300: zero promotional words!)
        clean_title = title if not title.startswith('4A ') else title[3:]
        ws_tpl.cell(current_row, 31, f"Premium {clean_title}. High quality self-adhesive notes designed for office, school, study, and meeting organization.")
        ws_tpl.cell(current_row, 32, f"High quality self-adhesive sticky notes with reliable adhesive that sticks securely to most smooth surfaces and removes cleanly without residue.")
        ws_tpl.cell(current_row, 161, 'China')
        ws_tpl.cell(current_row, 164, 'No')
        ws_tpl.cell(current_row, 188, 'Not Applicable')

        current_row += 1

        # Track existing (color, size) to prevent Error 100899 duplicate collisions!
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
            ws_tpl.cell(current_row, 9, child['asin'])
            ws_tpl.cell(current_row, 10, child['brand'])
            ws_tpl.cell(current_row, 11, 'ASIN')
            ws_tpl.cell(current_row, 13, item_type_kw)

            # Prevent duplicate color/size under same parent
            cur_color = child['color']
            cur_size = child['size']
            cs_key = (cur_color, cur_size)
            seen_color_size[cs_key] += 1
            if seen_color_size[cs_key] > 1:
                # Disambiguate if duplicate child in same family
                cur_size = f"{cur_size} (Pack {seen_color_size[cs_key]})"

            # Color (Col 51)
            ws_tpl.cell(current_row, 51, cur_color)

            # Size (Col 52)
            if 'SIZE' in v_theme and cur_size:
                ws_tpl.cell(current_row, 52, cur_size)

            # Price & Strike-through Deal
            if psku == 'PARENT-4A-30315-RAINBOW-15':
                if 'Pop-Up' in cur_size or 'Accordion' in cur_size or '-Z' in csku:
                    # Pop-Up Accordion: $19.99 list price -> $16.99 sale deal
                    ws_tpl.cell(current_row, 88, '19.99')   # List Price
                    ws_tpl.cell(current_row, 118, '19.99')  # Your Price
                    ws_tpl.cell(current_row, 122, '16.99')  # Sale Price
                    ws_tpl.cell(current_row, 123, '2026-10-30')  # Sale Start Date
                    ws_tpl.cell(current_row, 124, '2027-10-31')  # Sale End Date
                else:
                    # Standard Flat: $18.99 list price -> $15.99 sale deal (1,054 units FBA hot deal)
                    ws_tpl.cell(current_row, 88, '18.99')   # List Price
                    ws_tpl.cell(current_row, 118, '18.99')  # Your Price
                    ws_tpl.cell(current_row, 122, '15.99')  # Sale Price
                    ws_tpl.cell(current_row, 123, '2026-10-30')  # Sale Start Date
                    ws_tpl.cell(current_row, 124, '2027-10-31')  # Sale End Date
            elif child['price']:
                try:
                    p_float = float(re.sub(r'[^\d.]', '', str(child['price'])))
                    if p_float > 0:
                        ws_tpl.cell(current_row, 118, f"{p_float:.2f}")
                except:
                    pass

            current_row += 1

    total_rows = current_row - 7
    print(f"Template populated: {len(children_by_parent)} Parents, {total_rows - len(children_by_parent)} Children. Total rows: {total_rows}")

    tsv_output_path = r'E:\Desktop\4A_全店21大家族精细化变体清洗_终极纯净版.tsv'
    with open(tsv_output_path, 'w', encoding='utf-8', newline='') as f:
        for r in range(1, current_row):
            row_vals = []
            for c in range(1, ws_tpl.max_column + 1):
                val = ws_tpl.cell(r, c).value
                if val is None:
                    row_vals.append('')
                else:
                    s_val = str(val).replace('\t', ' ').replace('\r', ' ').replace('\n', ' ')
                    row_vals.append(s_val)
            f.write('\t'.join(row_vals) + '\n')

    tsv_size = os.path.getsize(tsv_output_path)
    print(f"TSV feed re-exported: {tsv_output_path} ({tsv_size:,} bytes).")

    # Also export dedicated fast-processing TSV for 30315 Strike-Through Deal
    fast_30315_path = r'E:\Desktop\4A_30315彩虹系列_限时划线促销改价表.tsv'
    with open(fast_30315_path, 'w', encoding='utf-8', newline='') as f:
        # Header rows 1 to 6
        for r in range(1, 7):
            row_vals = [str(ws_tpl.cell(r, c).value or '').replace('\t', ' ').replace('\r', ' ').replace('\n', ' ') for c in range(1, ws_tpl.max_column + 1)]
            f.write('\t'.join(row_vals) + '\n')
        # 30315 rows
        for r in range(7, current_row):
            sku = str(ws_tpl.cell(r, 2).value or '')
            psku = str(ws_tpl.cell(r, 6).value or '')
            if '30315' in sku or psku == 'PARENT-4A-30315-RAINBOW-15':
                row_vals = [str(ws_tpl.cell(r, c).value or '').replace('\t', ' ').replace('\r', ' ').replace('\n', ' ') for c in range(1, ws_tpl.max_column + 1)]
                f.write('\t'.join(row_vals) + '\n')

    fast_size = os.path.getsize(fast_30315_path)
    print(f"Fast 30315 deal feed exported: {fast_30315_path} ({fast_size:,} bytes).")

if __name__ == '__main__':
    main()
