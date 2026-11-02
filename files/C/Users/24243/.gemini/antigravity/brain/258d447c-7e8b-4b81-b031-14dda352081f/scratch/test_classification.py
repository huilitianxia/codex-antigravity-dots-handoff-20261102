import json
import sys
import re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\unified_entities_summary.json", 'r', encoding='utf-8') as f:
    entities = json.load(f)

print(f"Total entities to classify: {len(entities)}")

# Define Family Categories and matching patterns
def classify_entity(ent):
    sku = ent.get('sku', '')
    asin = ent.get('asin', '')
    title = ent.get('title', '')
    blob = f"{sku} {asin} {title}".upper()
    
    # 1. 30315 Rainbow 15-Color Series
    if '30315' in blob or '15 PADS STICKY NOTES 3 X 3' in blob or '15 COLORS' in blob:
        return 'FAM_01_30315_RAINBOW'
        
    # 2. BS 1801 / 1802 / 1803 Executive Leather Series & Refill
    if any(k in blob for k in ['1801', '1802', '1803', 'BS1801', 'GMBS 1801', 'LEATHER', 'BUNDLE SET,NEON ASSORTED']):
        return 'FAM_02_BS_LEATHER_BOX'
        
    # 3. 4012 / 4013 PP Box Assorted Desk Cube Series
    if any(k in blob for k in ['4012', '4013', '4A050', 'PP BOX', '18 PADS', '1800 SHEETS TOTAL, 4A 4012', '18 PADS/BOX']):
        return 'FAM_03_4012_4013_PPBOX'
        
    # 4. 5084 / 5088 Large Ruled Notes Series (5x8 in)
    if any(k in blob for k in ['5084', '5088', '5082', '5X8', '5 X 8']):
        return 'FAM_04_508_LARGE_5X8'
        
    # 5. 608 Extra Large Ruled Notes Series (6x8 in)
    if any(k in blob for k in ['608', '6X8', '6 X 8']):
        return 'FAM_05_608_XLARGE_6X8'
        
    # 6. 406x4 / 406x6 Large Notes Series (4x6 in)
    if any(k in blob for k in ['406X6', '406X4', '4064', '4066', '4 X 6', '4X6']) and not any(k in blob for k in ['40609', '40606', '40607', '40608', '40621', '40622', '40623', '40624', '40630']):
        return 'FAM_06_406_LARGE_4X6'
        
    # 7. 406xx Index Tabs & Booklets Series (40606-40630)
    if any(k in blob for k in ['40606', '40607', '40608', '40609', '40621', '40622', '40623', '40624', '40630', 'DIVIDER STICKY', 'NOTE TABS,2 2/3', 'INDEX FLAGS']):
        return 'FAM_07_406XX_INDEX_TABS'
        
    # 8. 301 Mini Series (1.5x2 in)
    if any(k in blob for k in ['301X12', '301X24', '301M', '1.5X2', '1.5 X 2', '1 1/2 X 2', '4A 004']):
        return 'FAM_08_301_MINI_1.5X2'
        
    # 9. 304 / 305 / 306 Full Adhesive Series (满胶全粘便签)
    if any(k in blob for k in ['FULL ADHESIVE', 'FULL GLUE', '304-FULL', '305-FULL', '306-FULL', '3X4 INCHES,FULL', '3X5 INCHES,FULL', 'FBG138ND', 'QXJWDPL', 'QXJZKHC']):
        return 'FAM_09_FULL_ADHESIVE_PADS'
        
    # 10. 303 Classic 3x3 Series (Square & Lined Standard Notes)
    if any(k in blob for k in ['303X6', '303X12', '303X24', '303M', '303-Z', '3X3 INCHES,NEON', '3 X 3 INCHES,NEON', '4A 010', '4A 008', '3X3', '3 X 3']):
        return 'FAM_10_303_CLASSIC_3X3'
        
    # 11. 601 / 603 / 604 Sign Here & Arrow Flags Series
    if any(k in blob for k in ['SIGN HERE', 'ARROW FLAGS', 'PAGE MAKER', '124418', '501516', '501521', '752516', '4A 601', '4A 603', '4A 604']):
        return 'FAM_11_SIGN_HERE_FLAGS'
        
    # 12. PSS Full Adhesive Roll Tape & Refill Series
    if any(k in blob for k in ['PSS', 'ROLL STICKY', 'ROLL TAPE', 'DISPENSER', 'NANBX2']):
        return 'FAM_12_PSS_ROLL_TAPE'
        
    # 13. 8065~8088 24-Color Rainbow Spectrum Series
    if any(f'80{i}' in blob for i in range(65, 89)):
        return 'FAM_13_8065_8088_SPECTRUM_24'
        
    # 14. SMC / Shapes / Cube Novelty & Printed Pads
    if any(k in blob for k in ['SHAPES', 'PUZZLE', 'HEART', 'BOMB', 'BUBBLE', 'LEAF', 'ARROW SHAPE', 'CUBE', 'SMC', 'PRINTED STICKY', '5078', '5013', '5020', '5036', '5059', '5061', '3031', '3032']):
        return 'FAM_14_SHAPES_CUBE_NOVELTY'
        
    # 15. BP Meeting Large Notes & Acrylic Desk Sets
    if any(k in blob for k in ['BP 1111', 'BP 1515', 'BP 2222', 'MEETING', '404-AC', '303-AC', 'AC-HOLDER', 'ACJT']):
        return 'FAM_15_BP_MEETING_ACRYLIC'
        
    return 'FAM_UNMAPPED'

fam_counts = defaultdict(int)
fam_samples = defaultdict(list)
fam_reviews = defaultdict(int)
fam_stock = defaultdict(int)

for key, ent in entities.items():
    fam = classify_entity(ent)
    fam_counts[fam] += 1
    rev = ent.get('reviews', 0)
    if isinstance(rev, int): fam_reviews[fam] += rev
    qty = ent.get('fba_qty', 0)
    if isinstance(qty, int): fam_stock[fam] += qty
    if len(fam_samples[fam]) < 3:
        fam_samples[fam].append((ent.get('sku'), ent.get('asin'), ent.get('title')[:40]))

print("\n=== CLASSIFICATION BREAKDOWN ===")
for fam in sorted(fam_counts.keys()):
    print(f"\n{fam}: {fam_counts[fam]} items | {fam_reviews[fam]} reviews | {fam_stock[fam]} FBA stock")
    for s in fam_samples[fam]:
        print(f"  sample: SKU='{s[0]}' ASIN='{s[1]}' Title='{s[2]}'")
