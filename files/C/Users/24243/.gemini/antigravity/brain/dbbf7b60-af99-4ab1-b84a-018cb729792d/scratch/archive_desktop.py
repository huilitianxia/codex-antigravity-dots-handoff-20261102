import os, sys, zipfile, json, time
sys.stdout.reconfigure(encoding='utf-8')
R = r'E:\Desktop'
OUT_DIR = r'D:\4A'
OUT = os.path.join(OUT_DIR, '4A_桌面归档_20261101.zip')
os.makedirs(OUT_DIR, exist_ok=True)

IMG_KEYS = ['新图文素材库', '亚马逊', '30315_', '图文审稿包', '4A_Listing_Aplus', '4A_视频生成素材', 'GPT最终审定图包']
DOC_EXT = ('.tsv', '.xlsx', '.xlsm', '.md', '.txt', '.csv')
DOC_PREFIX = ('4A_', 'WooCommerce_', 'extracted_order_data', 'subagent_orders', 'gpt_', 'tool_call_mapping',
              '通宵自动监听', 'A-Level', '全店幽灵')
VID_EXT = ('.mp4',)

def category(name, isdir):
    if any(k in name for k in IMG_KEYS):
        return '1_图包'
    if not isdir:
        low = name.lower()
        if low.endswith(VID_EXT) or name.endswith('_concat_list.txt') or name == '40609_cover.jpg':
            return '3_视频素材'
        if low.endswith(DOC_EXT) and name.startswith(DOC_PREFIX):
            return '2_表格与文档'
    return None

items = []
for n in sorted(os.listdir(R)):
    p = os.path.join(R, n)
    c = category(n, os.path.isdir(p))
    if c:
        items.append((c, n, p))

manifest = []
STORED = ('.jpg', '.jpeg', '.png', '.zip', '.mp4')
t0 = time.time()
with zipfile.ZipFile(OUT, 'w', allowZip64=True) as z:
    for c, n, p in items:
        if os.path.isdir(p):
            for a, _, fs in os.walk(p):
                for f in fs:
                    fp = os.path.join(a, f)
                    arc = os.path.join(c, os.path.relpath(fp, R))
                    comp = zipfile.ZIP_STORED if f.lower().endswith(STORED) else zipfile.ZIP_DEFLATED
                    z.write(fp, arc, compress_type=comp)
                    manifest.append((fp, arc, os.path.getsize(fp)))
        else:
            arc = os.path.join(c, n)
            comp = zipfile.ZIP_STORED if n.lower().endswith(STORED) else zipfile.ZIP_DEFLATED
            z.write(p, arc, compress_type=comp)
            manifest.append((p, arc, os.path.getsize(p)))

with open(os.path.join(OUT_DIR, '_桌面归档清单_20261101.json'), 'w', encoding='utf-8') as f:
    json.dump({'items': [i[1] for i in items], 'files': len(manifest)}, f, ensure_ascii=False, indent=1)
with open(r'C:\Users\24243\.gemini\antigravity\brain\dbbf7b60-af99-4ab1-b84a-018cb729792d\scratch\archive_manifest.json', 'w', encoding='utf-8') as f:
    json.dump([[a, b, c] for a, b, c in manifest], f, ensure_ascii=False)
print('top-level items archived:', len(items))
print('files:', len(manifest), 'bytes in:', sum(m[2] for m in manifest) // 1048576, 'MB')
print('zip MB:', os.path.getsize(OUT) // 1048576, 'secs:', int(time.time() - t0))
