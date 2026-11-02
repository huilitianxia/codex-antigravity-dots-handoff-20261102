import json
import sys
import re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\unified_entities_summary.json", 'r', encoding='utf-8') as f:
    entities = json.load(f)

def classify_entity_v2(ent):
    sku = ent.get('sku', '')
    asin = ent.get('asin', '')
    title = ent.get('title', '')
    blob = f"{sku} {asin} {title}".upper()
    
    # 1. 30315 Rainbow 15-Color Series (3x3 in 15 colors)
    if '30315' in blob or '15 PADS STICKY NOTES 3 X 3' in blob or '15 COLORS, COLORFUL STICK' in blob:
        return 'FAM_01_30315_RAINBOW'
        
    # 2. BS 1801 / 1802 / 1803 Executive Leather Series & Refill
    if any(k in blob for k in ['1801', '1802', '1803', 'BS1801', 'GMBS 1801', 'LEATHER', 'BUNDLE SET,NEON ASSORTED']):
        return 'FAM_02_BS_LEATHER_BOX'
        
    # 3. 4012 / 4013 PP Box Assorted Desk Cube Series (18-Pads Box)
    if any(k in blob for k in ['4012', '4013', '4A050', 'PP BOX', '18 PADS/BOX', '1800 SHEETS TOTAL, 4A 4012', '18 PADS STICKY NOTES 3X3', '18 PADS LINED STICKY NOTES 3X3']):
        return 'FAM_03_4012_4013_PPBOX'
        
    # 4. 5084 / 5088 Large Ruled Notes Series (5x8 in)
    if any(k in blob for k in ['5084', '5088', '5082', '5X8', '5 X 8', '508']):
        return 'FAM_04_508_LARGE_5X8'
        
    # 5. 608 Extra Large Ruled Notes Series (6x8 in)
    if any(k in blob for k in ['608', '6X8', '6 X 8']):
        return 'FAM_05_608_XLARGE_6X8'
        
    # 6. 406x4 / 406x6 / 305 / 404 Large & Medium Notes Series (3x5, 4x4, 4x6 in)
    if any(k in blob for k in ['406X6', '406X4', '40612', '4064', '4066', '4 X 6', '4X6', '305X6', '30512', '3 X 5', '3X5', '40412', '404S', '4 X 4', '4X4']) and not any(k in blob for k in ['40609', '40606', '40607', '40608', '40621', '40622', '40623', '40624', '40630', 'FULL ADHESIVE', 'FULL GLUE']):
        return 'FAM_06_406_305_LARGE_NOTES'
        
    # 7. 406xx Index Tabs & Booklets Series (40606-40630)
    if any(k in blob for k in ['40606', '40607', '40608', '40609', '40621', '40622', '40623', '40624', '40630', 'DIVIDER STICKY', 'NOTE TABS,2 2/3', 'NOTE TABS,3 3/8', 'INDEX FLAGS']):
        return 'FAM_07_406XX_INDEX_TABS'
        
    # 8. 301 / 202 / 3548 Mini Notes Series (1.5x2, 2x2, 1 3/8x1 7/8 in Small Notes)
    if any(k in blob for k in ['301X12', '301X24', '301M', '30132', '1.5X2', '1.5 X 2', '1 1/2 X 2', '4A 004', '20232', '2028', '2 X 2', '2X2', '354818', '354832', '1 3/8', '484810', '1 7/8']):
        return 'FAM_08_301_MINI_SMALL_NOTES'
        
    # 9. 302 / 303 / 304 / 305 Full Adhesive Series (满胶全粘便签)
    if any(k in blob for k in ['FULL ADHESIVE', 'FULL GLUE', '302-FULL', '303-FULL', '304-FULL', '305-FULL', '306-FULL', 'FBG138ND', 'QXJWDPL', 'QXJZKHC', 'QXJYTZ7']):
        return 'FAM_09_FULL_ADHESIVE_PADS'
        
    # 10. 303 Classic 3x3 Series (Square & Lined Standard Notes)
    if any(k in blob for k in ['303X6', '303X12', '303X24', '303M', '303S', '303-Z', '4A 010', '4A 008', '3X3 INCHES', '3 X 3 INCHES', '3X3 IN,', '3 X 3 IN,', '3X3', '3 X 3']):
        return 'FAM_10_303_CLASSIC_3X3'
        
    # 11. 601 / 602 / 603 / 604 Sign Here & Arrow Flags Series
    if any(k in blob for k in ['SIGN HERE', 'ARROW FLAGS', 'PAGE MAKER', '124418', '501516', '501521', '752516', '4A 601', '4A 602', '4A 603', '4A 604', 'POP-UP FLAGS', 'PAGE MARKER', 'HIGHLIGHTER STRIPS', 'WRITABLE LABELS', 'RULE,NEON COLOR']):
        return 'FAM_11_SIGN_HERE_FLAGS'
        
    # 12. PSS Full Adhesive Roll Tape & Refill Series
    if any(k in blob for k in ['PSS', 'ROLL STICKY', 'ROLL TAPE', 'DISPENSER', 'NANBX2', 'ROLL']):
        return 'FAM_12_PSS_ROLL_TAPE'
        
    # 13. 8065~8088 24-Color Rainbow Spectrum Series
    if any(f'80{i}' in blob for i in range(65, 89)):
        return 'FAM_13_8065_8088_SPECTRUM_24'
        
    # 14. SMC / Shapes / Cube Novelty & Printed Pads
    if any(k in blob for k in ['SHAPES', 'PUZZLE', 'HEART', 'BOMB', 'BUBBLE', 'LEAF', 'TREE', 'ARROW SHAPE', 'CUBE', 'SMC', 'PRINTED STICKY', 'VINTAGE CARRIAGE', 'MERRY CHRISTMAS', '5078', '5013', '5020', '5036', '5037', '5059', '5061', '50024', '3031', '3032', '8663', '8665', '8667']):
        return 'FAM_14_SHAPES_CUBE_NOVELTY'
        
    # 15. BP Meeting Large Notes, Planners & Acrylic Desk Sets
    if any(k in blob for k in ['BP 1111', 'BP 1515', 'BP 2222', 'BP1111', 'MEETING', '404-AC', '303-AC', 'AC-HOLDER', 'ACJT', 'PLANNER', 'WHITEBOARD', 'EASEL PAD', '6533', '6534']):
        return 'FAM_15_BP_MEETING_PLANNERS'
        
    return 'FAM_UNMAPPED'

fam_counts = defaultdict(int)
fam_reviews = defaultdict(int)
fam_stock = defaultdict(int)
unmapped = []

for key, ent in entities.items():
    fam = classify_entity_v2(ent)
    fam_counts[fam] += 1
    rev = ent.get('reviews', 0)
    if isinstance(rev, int): fam_reviews[fam] += rev
    qty = ent.get('fba_qty', 0)
    if isinstance(qty, int): fam_stock[fam] += qty
    if fam == 'FAM_UNMAPPED':
        unmapped.append(ent)

print(f"\nTotal entities: {len(entities)}")
for fam in sorted(fam_counts.keys()):
    print(f"{fam}: {fam_counts[fam]} items | {fam_reviews[fam]} reviews | {fam_stock[fam]} FBA stock")

print(f"\nRemaining unmapped: {len(unmapped)}")
for u in unmapped[:15]:
    print(f"SKU: '{u.get('sku')}' | ASIN: '{u.get('asin')}' | Title: '{u.get('title')[:60]}'")
