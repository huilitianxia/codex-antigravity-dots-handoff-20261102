"""Prepare an auditable, non-overlapping repair batch from Amazon's error receipt."""
import collections
import json
import re
from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).parent
raw = json.loads((ROOT / 'category-report-raw.json').read_text(encoding='utf-8'))
audit = json.loads((ROOT / 'category-report-audit.json').read_text(encoding='utf-8'))
prior = json.loads((ROOT / 'analysis.json').read_text(encoding='utf-8'))
raw_by = {r['contribution_sku#1.value']: r for r in raw['rows']}
aud_by = {r['sku']: r for r in audit['rows']}
old_by = {r['sku']: r for r in prior['master']}
old_asin = collections.defaultdict(list)
for r in prior['master']:
    if not r['parent']:
        old_asin[r['asin']].append(r)
headers = raw['headers']
def col(prefix):
    found = [get_column_letter(i) for i, (_, k) in enumerate(headers, 1) if k.startswith(prefix)]
    assert found, prefix
    return found[0]
def raw_value(row, prefix):
    return next((v for k, v in row.items() if k.startswith(prefix)), None)

receipt_path = Path('D:/下载文件/01-price-title-fixes-processing-summary.xlsm')
w = openpyxl.load_workbook(receipt_path, data_only=False)
s = w['Template']
receipt_errors = []
title_asins = set()
catalog_fixes = collections.defaultdict(dict)
for row in s.iter_rows(min_row=7):
    sku, asin = row[3].value, row[13].value
    if not sku or not asin:
        continue
    for cell in row:
        if not cell.comment or 'ERROR' not in cell.comment.text:
            continue
        message = cell.comment.text.replace('_x000d_', '')
        if 'Your changes were applied' in message:
            continue
        receipt_errors.append({'sku': sku, 'asin': asin, 'cell': cell.coordinate, 'message': message})
        if '75 characters or less' in message:
            title_asins.add(asin)
        for field, value in re.findall(r"'(color|manufacturer)' \(Merchant .*? / Amazon \[en_US: \"([^\"]+)\"", message):
            if field in catalog_fixes[asin]:
                assert catalog_fixes[asin][field] == value
            catalog_fixes[asin][field] = value

# Reserved for live UI handling; never race the upload with these edits.
ui_asins = {'B07FKJNNHP', 'B07FK8ML41', 'B01N6J0VZO', 'B07F2FCHLK', 'B07F2CWVQ7', 'B07FKL115P'}

names = {
    '常规平叠便签': 'Sticky Notes', '强粘便签': 'Super Sticky Notes',
    '满胶便签': 'Full Adhesive Sticky Notes', '抽取便签': 'Pop-up Sticky Notes',
    '循环色平叠便签': 'Color-Cycling Sticky Notes', '循环色抽取便签': 'Color-Cycling Pop-up Notes',
    '毫米规格小便签': 'Sticky Notes', '窄条纸便签': 'Narrow Sticky Notes',
    '分隔便签': 'Divider Sticky Notes', '透明索引': 'Transparent Page Flags',
    '耐用分隔索引': 'Durable File Tabs', '带尺索引': 'Page Flags with Ruler',
    '带孔活页索引': 'Binder Index Tabs', '箭头透明索引': 'Arrow Page Flags',
    '印花透明索引': 'Printed Page Flags', '签字指示贴': 'Sign Here Flags',
    '纸质或材质待核索引': 'Page Markers',
    '卷带套装含替芯': 'Sticky Note Rolls with Dispenser and Refills',
    '卷带含切割器': 'Sticky Note Rolls with Dispensers',
    '卷带替芯': 'Sticky Note Roll Refills', '卷带配置待核': 'Sticky Note Rolls',
    '大幅方形便签': 'Big Sticky Notes', '大幅会议纸': 'Sticky Easel Pads',
    '桌立会议本': 'Tabletop Easel Pads', '桌立会议本含白板': 'Tabletop Easel Pad and Whiteboard',
    '白板贴': 'Dry Erase Whiteboard Sheets', '大幅便签尺寸待核': 'Big Sticky Notes',
    'PP盒多尺寸便签': 'Sticky Notes Value Pack in Storage Box',
    '笔筒便签标签组合': 'Pen Holder Set with Sticky Notes and Flags',
    '抽取便签座': 'Pop-up Note Dispenser', '便签收纳座': 'Sticky Note Holder',
    'BS商务便签套装': 'Desk Sticky Notes Organizer Set', 'BS便签替芯': 'Desk Notes Organizer Refills',
    '磁吸便签含笔': 'Magnetic Notepad with Pen', '周计划': 'Weekly Planner Notes',
    '月计划': 'Monthly Planner Notes', '日计划': 'Daily Planner Notes',
    '计划本周期待核': 'Planner Notes',
    '印花自粘便签砖': 'Printed Sticky Note Cube', '彩色自粘便签砖': 'Colored Sticky Note Cube',
    '无胶便签砖': 'Non-Adhesive Memo Cube', '圆点分类贴': 'Color Coding Dot Stickers',
    '黑板贴': 'Chalkboard Labels', '金边黑板贴': 'Chalkboard Labels with Gold Border',
    '3D动物印花便签': '3D Animal Sticky Notes', '折页印花套装': 'Folding Sticky Notes Set',
    '印花便签套装': 'Printed Sticky Notes Set', '其他异形': 'Shaped Sticky Notes',
    '心形': 'Heart Shaped Sticky Notes', '叶形': 'Leaf Shaped Sticky Notes',
    '树形': 'Tree Shaped Sticky Notes', '拼图形': 'Puzzle Shaped Sticky Notes',
    '对话框': 'Speech Bubble Sticky Notes', '门挂形': 'Door Hanger Sticky Notes',
    '箭头形': 'Arrow Shaped Sticky Notes', '混合异形': 'Assorted Shape Sticky Notes',
    '彩虹造型便签': 'Rainbow Shaped Sticky Notes',
}

def identity(asin, fallback):
    candidates = old_asin.get(asin, [])
    good = [r for r in candidates if r['type'] != '信息不足' and r.get('basis')]
    return max(good, key=lambda x: (not x['basis'].startswith('4A Self-Stick Notes,'), len(x['basis']))) if good else fallback

def short_copy(a):
    o = identity(a['asin'], old_by.get(a['sku'], {}))
    title = o.get('basis') or a['title'] or ''
    low = title.lower()
    typ = o.get('type', '')
    if a['asin'] == 'B07WK3JX6K':
        product = 'Pen Holder with Lined Sticky Notes'
    elif a['asin'] == 'B078BQV25Y':
        product = '3D White Tiger Sticky Notes'
    elif a['asin'] == 'B077QC33J2':
        product = '3D Panda Sticky Notes'
    elif a['asin'] == 'B00SMEEN8G':
        product = 'Hand Shaped Sticky Notes'
    elif re.search(r'coloring paper|colouring paper', low):
        product = 'Self-Adhesive Coloring Paper Rolls'
    else:
        product = names.get(typ)
    if not product:
        return None
    if typ in {'常规平叠便签', '强粘便签', '满胶便签', '大幅方形便签'} and re.search(r'\blined\b|\bruled\b|with lines', low):
        product = product.replace('Sticky Notes', 'Lined Sticky Notes')
    if 'grid' in low and typ.startswith('卷带'):
        product = 'Grid ' + product
    elif 'grid' in low and typ in {'常规平叠便签', '强粘便签', '满胶便签'}:
        product = 'Grid ' + product
    product = product.replace('Super Lined Sticky', 'Super Sticky Lined')
    # Preserve the product's source display brand, not a polluted SKU prefix.
    brand = '4A' if title.lower().startswith('4a ') else (a['brand'] or '4A')
    base = f'{brand} {product}'
    dim = o.get('dimensions', '')
    if re.fullmatch(r'[\d.]+ × [\d.]+ (?:in|mm|ft)', dim):
        candidate = base + ', ' + dim.replace('×', 'x')
        if len(candidate) <= 75:
            base = candidate
    lead_pads = re.match(r'4A\s+(\d+)\s+Pads?\b', title, re.I)
    pack_pads = re.search(r'(\d+)\s*Pads?\s*/\s*(?:Pack|Box)', title, re.I)
    outer_packs = re.search(r'\b(\d+)\s+(?:Packs|Boxes)\b', title, re.I)
    pad_count = int(lead_pads[1]) if lead_pads else int(pack_pads[1]) * (int(outer_packs[1]) if outer_packs else 1) if pack_pads else None
    standalone_pads = set(int(v) for v in re.findall(r'\b(\d+)\s+Pads?\b(?!\s*/)', title, re.I))
    if pad_count is None and len(standalone_pads) == 1:
        pad_count = next(iter(standalone_pads))
    total_sheets = re.search(r'(\d+)\s+Sheets\s+Total', title, re.I)
    per_pad = re.search(r'(\d+)\s*Sheets\s*/\s*Pad', title, re.I)
    if pad_count and pad_count <= 100 and typ not in {'透明索引', '耐用分隔索引', '带孔活页索引'}:
        pack_label = f'{pad_count} Pad' + ('s' if pad_count != 1 else '')
        if len(base + ', ' + pack_label) <= 75:
            base += ', ' + pack_label
    # Keep only product colors explicitly stated in the same-ASIN source title.
    color = None
    color_words = set(re.findall(r'\b(?:yellow|white|black|blue|green|pink|purple|orange|red|magenta)\b', low))
    if '3D ' in product:
        color = None
    elif 'pastel' in low and 'yellow' in low and color_words == {'yellow'}:
        color = 'Pastel Yellow'
    elif 'pastel' in low and not ('neon' in low or 'bright' in low):
        color = 'Pastel Colors'
    elif ('neon' in low or 'bright' in low) and 'pastel' not in low:
        color = 'Neon Colors' if 'neon' in low else 'Bright Colors'
    elif color_words == {'yellow'}:
        color = 'Yellow'
    elif color_words == {'white'} or ('white paper' in low and 'black grid' in low):
        color = 'White'
    elif color_words == {'black'}:
        color = 'Black'
    if color and len(base + ', ' + color) <= 75:
        base += ', ' + color
    # The highlight retains a clearly stated pack detail where available.
    if pad_count and per_pad and int(per_pad[1]) <= 1000 and (not total_sheets or pad_count * int(per_pad[1]) == int(total_sheets[1])):
        highlight = f'{int(per_pad[1])} sheets per pad'
        if total_sheets:
            highlight += f', {int(total_sheets[1])} sheets total'
    elif total_sheets and int(total_sheets[1]) <= 10000 and not typ.startswith('卷带'):
        highlight = f'{int(total_sheets[1])} sheets total for notes and reminders'
    elif typ in {'卷带套装含替芯', '卷带含切割器', '卷带替芯', '卷带配置待核'}:
        highlight = 'Cut notes to the length needed'
    elif typ == '签字指示贴':
        highlight = 'Mark places that need a signature'
    elif typ in {'磁吸便签含笔', '周计划', '月计划', '日计划', '计划本周期待核'}:
        highlight = 'Keep plans and reminders in view'
    elif typ in {'透明索引', '耐用分隔索引', '带尺索引', '带孔活页索引', '箭头透明索引', '印花透明索引', '纸质或材质待核索引', '分隔便签'}:
        highlight = 'Mark and organize pages for easy reference'
    elif typ in {'黑板贴', '金边黑板贴', '圆点分类贴'}:
        highlight = 'Label and organize everyday items'
    elif typ in {'笔筒便签标签组合', 'PP盒多尺寸便签', '抽取便签座', '便签收纳座', 'BS商务便签套装'}:
        highlight = 'Keep notes organized on your desk'
    elif typ in {'大幅会议纸', '桌立会议本', '桌立会议本含白板', '白板贴', '大幅方形便签'}:
        highlight = 'Space for meeting notes and shared ideas'
    else:
        highlight = 'For everyday notes and reminders'
    if re.search(r'coloring paper|colouring paper', low):
        highlight = 'Continuous patterned coloring paper'
    assert len(base) <= 75, (a['sku'], base)
    return base, highlight, o.get('source', '现有商品标题'), title

ops, holds = [], []
for a in audit['rows']:
    if a['parentage'] == 'Parent' or not a['asin'] or a['asin'] in ui_asins:
        continue
    asin, sku = a['asin'], a['sku']
    changes, reasons, sources = {}, [], []
    if asin in title_asins or (asin in catalog_fixes and len(a['title'] or '') > 75
                              and raw_value(raw_by[sku], 'title_differentiation[')):
        c = short_copy(a)
        if not c:
            holds.append({'sku': sku, 'asin': asin, 'reason': '标题错误已确认，但现有产品信息不足以准确重写'})
        else:
            new_title, highlight, source, evidence = c
            changes.update({col('item_name['): new_title, col('title_differentiation['): highlight})
            reasons.append('修复回执100476；同ASIN各SKU统一产品标题与真实亮点')
            sources.extend([source, '上传处理报告的商品名称/亮点错误'])
    for field, value in catalog_fixes.get(asin, {}).items():
        key = col(field + '[')
        changes[key] = value
        reasons.append('按8541回执明确的Amazon en_US目录值修复' + field)
        sources.append('01-price-title-fixes-processing-summary.xlsm 的目录冲突明细')
    if changes:
        before = {c: raw_by[sku].get(headers[openpyxl.utils.column_index_from_string(c)-1][1]) for c in changes}
        actual = {c: v for c, v in changes.items() if before.get(c) != v}
        if actual:
            cells = {'C': sku, 'D': a['product_type'], 'E': 'Edit (Partial Update)', 'L': 'ASIN', 'M': asin, **actual}
            ops.append({'sku': sku, 'asin': asin, 'product_type': a['product_type'],
                        'cells': cells, 'before': before, 'reasons': reasons,
                        'sources': sorted(set(sources)), 'evidence_title': (short_copy(a) or ('','','',a['title']))[3]})

stats = {'rows': len(ops), 'asins': len({x['asin'] for x in ops}),
         'title_rows': sum(col('item_name[') in x['cells'] for x in ops),
         'color_rows': sum(col('color[') in x['cells'] for x in ops),
         'manufacturer_rows': sum(col('manufacturer[') in x['cells'] for x in ops),
         'ui_reserved_asins': sorted(ui_asins), 'holds': len(holds)}
out = {'source_template': 'D:/下载文件/分类商品报告_10-31-2026.xlsm',
       'receipt': str(receipt_path), 'stats': stats, 'operations': ops, 'holds': holds,
       'unresolved_receipt_errors': [x for x in receipt_errors if '75 characters or less' not in x['message']
                                     and 'conflict with Amazon catalog' not in x['message']]}
(ROOT / 'consolidated-repairs-data.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
digest = []
for i, x in enumerate(ops, 7):
    digest.append(f"{i}. {x['sku']} | {x['asin']}\n   SOURCE: {x['evidence_title']}\n   NEW: {x['cells'].get('I', '')} | {x['cells'].get('J', '')}\n   OTHER: " + json.dumps({c:v for c,v in x['cells'].items() if c not in {'C','D','E','L','M','I','J'}}, ensure_ascii=False))
(ROOT / 'consolidated-repairs-review.txt').write_text('\n'.join(digest), encoding='utf-8')
print(json.dumps(stats, ensure_ascii=False, indent=2))
print('Holds:', json.dumps(holds, ensure_ascii=False))
