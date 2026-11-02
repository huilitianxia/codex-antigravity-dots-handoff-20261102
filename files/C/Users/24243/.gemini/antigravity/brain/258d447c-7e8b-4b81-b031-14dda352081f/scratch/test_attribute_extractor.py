import json
import sys
import re
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\unified_entities_summary.json", 'r', encoding='utf-8') as f:
    entities = json.load(f)

print(f"Total entities loaded: {len(entities)}")

# Helper functions to extract ColorName, NumberOfItems, StyleName
def extract_color(title, sku):
    text = (title + " " + sku).upper()
    if '15-COLOR' in text or '15 COLORS' in text or '30315' in text: return '15-Color Rainbow'
    if '16 COLORS' in text or '16 COLOR' in text: return '16 Colors Assorted'
    if '8 COLORS' in text or '8 COLOR' in text: return '8 Colors Assorted'
    if 'NEON' in text: return 'Neon Assorted'
    if 'PASTEL' in text or 'MACARON' in text: return 'Pastel Assorted'
    if 'CANARY' in text or 'YELLOW' in text or '-Y' in text: return 'Canary Yellow'
    if 'BRIGHT' in text or 'ULTRA' in text: return 'Bright Ultra Colors'
    if 'PINK' in text: return 'Pink'
    if 'BLUE' in text: return 'Blue'
    if 'GREEN' in text: return 'Green'
    if 'ORANGE' in text: return 'Orange'
    if 'PURPLE' in text or 'VIOLET' in text: return 'Purple / Violet'
    if 'WHITE' in text: return 'White'
    if 'TRANSPARENT' in text or 'CLEAR' in text: return 'Transparent Writable'
    if 'KRAFT' in text or 'BROWN' in text: return 'Kraft Brown'
    if 'RAINBOW' in text or 'ASSORTED' in text or 'COLOR-CYCLING' in text: return 'Multicolor Assorted'
    return 'Classic Assorted'

def extract_pack_items(title, sku):
    text = (title + " " + sku).upper()
    # match pads
    m_pads = re.search(r'(\d+)\s*(PADS|PAD|PACKS|PACK|BOXES|BOX|DIVIDERS|DIVIDER|ROLLS|ROLL|SHEETS|PCS)', text)
    pads = None
    if m_pads:
        pads = m_pads.group(1)
        unit = m_pads.group(2)
        if unit in ['PADS', 'PAD']:
            return f"{pads} Pads"
        elif unit in ['PACKS', 'PACK']:
            return f"{pads} Packs"
        elif unit in ['BOXES', 'BOX']:
            return f"{pads} Box"
        elif unit in ['ROLLS', 'ROLL']:
            return f"{pads} Rolls"
        elif unit in ['DIVIDERS', 'DIVIDER']:
            return f"{pads} Dividers"
        elif unit in ['PCS']:
            return f"{pads} Pcs"
        elif unit in ['SHEETS']:
            return f"{pads} Sheets"
            
    # SKU hints: e.g. x12, x24, x6, x4, -400
    if 'X24' in text or '32' in text: return '24 Pads / 2400 Sheets'
    if 'X18' in text or '18' in text: return '18 Pads / 1800 Sheets'
    if 'X16' in text: return '16 Pads / 800 Sheets'
    if 'X12' in text or '12' in text: return '12 Pads / 1200 Sheets'
    if 'X8' in text or '5088' in text: return '8 Pads / 400 Sheets'
    if 'X6' in text or '406' in text: return '6 Pads / 600 Sheets'
    if 'X4' in text or '5084' in text: return '4 Pads / 200 Sheets'
    if 'X2' in text or '5082' in text: return '2 Pads / 100 Sheets'
    if '400' in text: return '4 Pads / 400 Sheets'
    if '100' in text: return '1 Pad / 100 Sheets'
    return '1 Pack'

def extract_style(title, sku):
    text = (title + " " + sku).upper()
    if 'POP-UP' in text or 'POP UP' in text or '-Z' in text: return 'Pop-Up Accordion Pad'
    if 'LINED' in text or 'RULED' in text or '-L' in text: return 'Lined / Ruled Notes'
    if 'GRID' in text or 'GRAPH' in text: return 'Grid / Graph Notes'
    if 'BLANK' in text or 'UNLINED' in text: return 'Blank / Plain Notes'
    if 'REFILL' in text: return 'Replacement Refill Pack'
    if 'CALENDAR' in text: return 'With Calendar Desk Set'
    if 'LEATHER' in text or '1801' in text or '1803' in text: return 'Executive Leather Gift Box'
    if 'PP BOX' in text or '4012' in text or '4013' in text: return 'PP Desk Storage Box'
    if 'FULL ADHESIVE' in text or 'FULL GLUE' in text: return 'Full Adhesive All-Stick Pad'
    if 'DISPENSER' in text or 'HOLDER' in text: return 'Dispenser / Organizer Set'
    if 'INDEX' in text or 'TABS' in text or 'DIVIDER' in text or 'PAGE MARKER' in text or 'FLAGS' in text: return 'Index Tabs & Page Markers'
    if 'SIGN HERE' in text: return 'Sign Here Arrow Flags'
    if 'PUZZLE' in text: return 'Die-Cut Puzzle Shape'
    if 'HEART' in text: return 'Die-Cut Heart Shape'
    if 'BOMB' in text: return 'Die-Cut Bomb Shape'
    if 'TREE' in text or 'LEAF' in text: return 'Die-Cut Nature Shape'
    if 'CUBE' in text: return 'Memo Note Cube'
    if 'MAGNET' in text: return 'Fridge Magnetic Note Pad'
    if 'PLANNER' in text: return 'Weekly/Monthly Planner Pad'
    if 'BIG PAD' in text or 'MEETING' in text: return 'Large Meeting Presentation Pad'
    return 'Standard Flat Note Pad'

print("Extraction helpers ready.")
