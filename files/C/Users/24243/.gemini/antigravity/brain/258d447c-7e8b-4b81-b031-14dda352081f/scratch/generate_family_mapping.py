import json
import sys
import re
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# Load unified entities
with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\unified_entities_summary.json", 'r', encoding='utf-8') as f:
    entities = json.load(f)

print(f"Total entities loaded: {len(entities)}")

# Define the 14 Hero Mega Families Meta
FAMILIES_META = {
    'FAM_01_30315_RAINBOW': {
        'id': 1,
        'name': '30315 彩虹15色便签家族 (3x3 in 15-Color Pads)',
        'parent_sku': 'PARENT-4A-30315-RAINBOW-3X3',
        'theme': 'StyleName-NumberOfItems',
        'master_asin': 'B07F295DPC',
        'master_sku': '4A 30315',
        'benefit': '【0评秒变122评】将断货老链接122条好评无缝注入新上架的22件现货Listing，激活视频与A+极速出单。'
    },
    'FAM_02_BS_LEATHER_BOX': {
        'id': 2,
        'name': 'BS 1801 / 1803 商务皮质礼盒与替芯家族 (Executive Leather Set & Refill)',
        'parent_sku': 'PARENT-4A-BS-EXECUTIVE-LEATHER',
        'theme': 'StyleName-NumberOfItems',
        'master_asin': 'B07JVSYNYV',
        'master_sku': '4A BS 1801-FBA',
        'benefit': '【533评霸权+盘活37件替芯】将23评重复链接合入510评主页，并挂载37件12叠替芯子体，以礼盒高流量零广告动销替芯。'
    },
    'FAM_03_4012_4013_PPBOX': {
        'id': 3,
        'name': '4012 / 4013 PP盒18叠组合便签家族 (18-Pads Desk Storage Cube)',
        'parent_sku': 'PARENT-4A-4012-4013-PPBOX',
        'theme': 'ColorName-NumberOfItems',
        'master_asin': 'B01M3N310M',
        'master_sku': '4A 4012-B07T-FBA',
        'benefit': '【救急补库存+评价聚合】将分流在低曝光链接上的17件FBA库存合并至213评高权重链接，库存升至20件，规避断货。'
    },
    'FAM_04_508_LARGE_5X8': {
        'id': 4,
        'name': '5084 / 5088 大号横线便签家族 (5x8 in Large Ruled Sticky Notes)',
        'parent_sku': 'PARENT-4A-508-LARGE-5X8',
        'theme': 'ColorName-NumberOfItems',
        'master_asin': 'B07FKJM2LX',
        'master_sku': 'AAAA 4A 5084-N-L',
        'benefit': '【全店第一资产+评价破百】统合全店最大货值资产（101件现货/285件总库存），融合5088的60评与5084的39评，评价达99+。'
    },
    'FAM_05_608_XLARGE_6X8': {
        'id': 5,
        'name': '608 特大横线便签家族 (6x8 in Extra Large Ruled Sticky Notes)',
        'parent_sku': 'PARENT-4A-608-XLARGE-6X8',
        'theme': 'ColorName-NumberOfItems',
        'master_asin': 'B07HDVVZ1B',
        'master_sku': '4A 608-N-L-210',
        'benefit': '【消灭低分链接+吸收现货】将3.6★孤立链接合并至90评4.3★主链接，吸收现货并挂载2本/420张及彩色装。'
    },
    'FAM_06_406_305_LARGE_NOTES': {
        'id': 6,
        'name': '406x4 / 406x6 / 305 大号横线与纯色便签家族 (4x6 & 3x5 in Large Notes)',
        'parent_sku': 'PARENT-4A-406-LARGE-4X6',
        'theme': 'ColorName-NumberOfItems',
        'master_asin': 'B07FKL263W',
        'master_sku': 'AAAA 4A 406x6',
        'benefit': '【稀释1星差评+引入135条历史权重】将20件现货但带1星差评的B07FKHHTY4与淡彩135评老款及12叠装合体，全面激活现货。'
    },
    'FAM_07_406XX_INDEX_TABS': {
        'id': 7,
        'name': '406xx 手账索引便签本与书签家族 (40606~40630 Index Tabs & Flags)',
        'parent_sku': 'PARENT-4A-406XX-INDEX-TABS',
        'theme': 'StyleName-NumberOfItems',
        'master_asin': 'B07FKBHTDG',
        'master_sku': '4A 40609',
        'benefit': '【以614件现货巨无霸为核心合体】以全店单品库存第一的40609为基座，统合10个散乱索引贴链接，形成完整办公手账选购家族。'
    },
    'FAM_08_301_MINI_SMALL_NOTES': {
        'id': 8,
        'name': '301 / 202 迷你便签家族 (1.5x2 & 2x2 in Small Size Sticky Notes)',
        'parent_sku': 'PARENT-4A-301-MINI-SMALL',
        'theme': 'ColorName-NumberOfItems',
        'master_asin': 'B01LVTWP7Q',
        'master_sku': '4A 301x12-N',
        'benefit': '【千评VC老祖宗合流+盘活3.3万件资产】承接VC历史69,848套爆款权重，统合12/24/32叠小规格便签，释放全店最大库存池。'
    },
    'FAM_09_FULL_ADHESIVE_PADS': {
        'id': 9,
        'name': '302 / 303 / 304 / 305 满胶全粘便签家族 (Full Adhesive All-Stick Pads)',
        'parent_sku': 'PARENT-4A-FULL-ADHESIVE-PADS',
        'theme': 'StyleName-NumberOfItems',
        'master_asin': 'B07QXJYTZ7',
        'master_sku': '4A 303-Full Adhesive-400',
        'benefit': '【营收支柱大合体+激活534件积压款】全粘满胶贡献店铺70%营收，将3x3/3x4/3x5全粘规格打通，吸收144评并引爆大批量采购。'
    },
    'FAM_10_303_CLASSIC_3X3': {
        'id': 10,
        'name': '303 经典正方形便签家族 (3x3 in Square Standard & Lined Notes)',
        'parent_sku': 'PARENT-4A-303-CLASSIC-3X3',
        'theme': 'ColorName-NumberOfItems',
        'master_asin': 'B07B7JF9LB',
        'master_sku': '4A 303M-PNx12',
        'benefit': '【统领文具第一大词3x3】将6叠/12叠/24叠平装与横线、荧光色/黄色/粉彩彻底统合，霸占Amazon核心主流搜索入口。'
    },
    'FAM_11_SIGN_HERE_FLAGS': {
        'id': 11,
        'name': '601 / 602 / 603 / 604 办公文档签字贴与标签家族 (Sign Here & Arrow Flags)',
        'parent_sku': 'PARENT-4A-SIGN-HERE-FLAGS',
        'theme': 'StyleName-NumberOfItems',
        'master_asin': 'B07F2CWVQ7',
        'master_sku': '4A 124418',
        'benefit': '【B2B极速出单组合】文档审核Sign Here箭头贴与0.6x2/0.75x2.5多色便签条合流，针对律所、金融、高校B2B采购打爆客单价。'
    },
    'FAM_12_PSS_ROLL_TAPE': {
        'id': 12,
        'name': 'PSS 满胶卷带与切刀替芯收纳家族 (Full Adhesive Roll Tape & Dispensers)',
        'parent_sku': 'PARENT-4A-PSS-ROLL-TAPE',
        'theme': 'StyleName-NumberOfItems',
        'master_asin': 'B07T791NDQ',
        'master_sku': '4A PSS 9-5',
        'benefit': '【带底座+替芯捆绑销售】以带切刀底座为主力，挂载1卷/2卷/4卷不同色彩替芯，实现零边角料自由裁剪文具大升级。'
    },
    'FAM_13_8065_8088_SPECTRUM_24': {
        'id': 13,
        'name': '8065~8088 24色全光谱便签家族 (24-Color Rainbow Spectrum Sticky Notes)',
        'parent_sku': 'PARENT-4A-8065-8088-SPECTRUM-24',
        'theme': 'ColorName-NumberOfItems',
        'master_asin': 'B077QFD8G7',
        'master_sku': '4A 8065',
        'benefit': '【消灭24个碎片自竞孤岛】将老爸当年拆分的整整24个单色链接合二为一，打造24色全光谱彩虹选色大页，转化率直线上升。'
    },
    'FAM_14_SHAPES_CUBE_NOVELTY': {
        'id': 14,
        'name': 'SMC / Shapes / Cube 异形与印花便签砖神仙家族 (Die-Cut Shapes & Printed Cubes)',
        'parent_sku': 'PARENT-4A-SHAPES-CUBE-NOVELTY',
        'theme': 'StyleName-NumberOfItems',
        'master_asin': 'B00SMEEF2A',
        'master_sku': '4A 5078',
        'benefit': '【异形好评合体出击】统合拼图(43评4.1★)、心形、树叶、炸弹与四面印花便签砖，形成高溢价个性礼品便签矩阵。'
    },
    'FAM_15_BP_MEETING_PLANNERS': {
        'id': 15,
        'name': 'BP / Meeting 会议大看板、日程计划本与亚克力收纳系列 (Big Pads & Planners)',
        'parent_sku': 'PARENT-4A-BP-MEETING-PLANNERS',
        'theme': 'StyleName-NumberOfItems',
        'master_asin': 'B07Z2555TN',
        'master_sku': '4A 404-AC-Holder',
        'benefit': '【$50+高客单价B2B专攻】统合11x11/15x15/22x22会议大白板便签与日程计划本、亚克力笔筒收纳，主攻企业批量团购。'
    }
}

# Extraction functions
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
    m_pads = re.search(r'(\d+)\s*(PADS|PAD|PACKS|PACK|BOXES|BOX|DIVIDERS|DIVIDER|ROLLS|ROLL|SHEETS|PCS)', text)
    if m_pads:
        pads = m_pads.group(1)
        unit = m_pads.group(2)
        if unit in ['PADS', 'PAD']: return f"{pads} Pads"
        if unit in ['PACKS', 'PACK']: return f"{pads} Packs"
        if unit in ['BOXES', 'BOX']: return f"{pads} Box"
        if unit in ['ROLLS', 'ROLL']: return f"{pads} Rolls"
        if unit in ['DIVIDERS', 'DIVIDER']: return f"{pads} Dividers"
        if unit in ['PCS']: return f"{pads} Pcs"
        if unit in ['SHEETS']: return f"{pads} Sheets"
            
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

from test_classification_v2 import classify_entity_v2

# Map every entity
family_buckets = defaultdict(list)

for key, ent in entities.items():
    fam_key = classify_entity_v2(ent)
    if fam_key == 'FAM_UNMAPPED':
        # fallback by text
        text = ((ent.get('title') or '') + ' ' + (ent.get('sku') or '')).upper()
        if 'LABEL' in text or 'STICKER' in text or 'ROUND' in text:
            fam_key = 'FAM_11_SIGN_HERE_FLAGS'
        elif 'SHAPE' in text or 'DIE-CUT' in text or 'HAND' in text or 'MAGNET' in text:
            fam_key = 'FAM_14_SHAPES_CUBE_NOVELTY'
        elif 'PAD' in text or 'NOTE' in text:
            fam_key = 'FAM_10_303_CLASSIC_3X3'
        else:
            fam_key = 'FAM_14_SHAPES_CUBE_NOVELTY'
            
    ent['color_name'] = extract_color(ent.get('title', ''), ent.get('sku', ''))
    ent['number_of_items'] = extract_pack_items(ent.get('title', ''), ent.get('sku', ''))
    ent['style_name'] = extract_style(ent.get('title', ''), ent.get('sku', ''))
    
    # Determine role
    meta = FAMILIES_META.get(fam_key, {})
    master_asin = meta.get('master_asin', '')
    master_sku = meta.get('master_sku', '')
    
    sku = ent.get('sku', '')
    asin = ent.get('asin', '')
    
    if asin == master_asin or (master_sku and sku == master_sku):
        ent['role'] = 'MASTER_TARGET'
    else:
        # Check if identical specification duplicate to merge
        # E.g. AAAA prefix or same model with 0 stock vs active stock
        if ('AAAA' in sku) or ('GM' in sku) or (ent.get('reviews', 0) > 0 and ent.get('fba_qty', 0) == 0 and ent.get('is_historical_oos')):
            ent['role'] = 'MERGE_DUPLICATE'
        else:
            ent['role'] = 'VARIATION_CHILD'
            
    family_buckets[fam_key].append(ent)

print("All entities successfully classified and attributes extracted!")
for fk in sorted(family_buckets.keys()):
    print(f"  {fk}: {len(family_buckets[fk])} members")

# Save to JSON
with open(r"C:\Users\24243\.gemini\antigravity\brain\258d447c-7e8b-4b81-b031-14dda352081f\scratch\family_mapping_export.json", 'w', encoding='utf-8') as f:
    # convert sets
    serializable = {}
    for fk, items in family_buckets.items():
        s_items = []
        for it in items:
            c = dict(it)
            c['sources'] = list(c['sources'])
            s_items.append(c)
        serializable[fk] = s_items
    json.dump(serializable, f, ensure_ascii=False, indent=2)
print("Saved family_mapping_export.json")
