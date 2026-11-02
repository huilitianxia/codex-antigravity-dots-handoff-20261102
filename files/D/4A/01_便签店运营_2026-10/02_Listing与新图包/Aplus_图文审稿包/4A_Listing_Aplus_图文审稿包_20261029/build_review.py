from pathlib import Path
import json, html, shutil, zipfile
from PIL import Image

ROOT = Path(__file__).parent
data = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
manifest = json.loads((ROOT / 'image_manifest.json').read_text(encoding='utf-8'))
(ROOT / 'images').mkdir(exist_ok=True)
(ROOT / 'sources').mkdir(exist_ok=True)
qa = []
for item in manifest:
    src = Path(item['source'])
    assert src.is_file(), src
    dst = ROOT / 'images' / item['file']
    shutil.copy2(src, dst)
    with Image.open(dst) as im:
        qa.append({'file': item['file'], 'width': im.width, 'height': im.height, 'mode': im.mode})
assert len(qa) == 12
for entry in data['listings']:
    assert len(entry['bullets']) == 5
    assert len(entry['title']) <= 200, entry['title']
    assert len(entry['keywords'].encode('utf-8')) < 250
assert len(data['checklist']) == 22
for family in ('ap406', 'ap5082'):
    assert len(data[family]) == 4
    assert all(len(x['cards']) == 3 for x in data[family])

source_root = Path('E:/QQ文件/1-----4A Stiky notes')
for src, name in [
    (Path('E:/Desktop/4A_图片与A+优化方案_GPT直接执行包.md'), '原始执行包.md'),
    (source_root / 'Variation Family-406x6系列/A+/套1（细节已修改）/406x6系列A+修改想法.docx', '爸爸原始22条意见.docx'),
    (source_root / 'Variation Family-406x6系列/父体-406x6-大-New.png', '406x6_实物参考.png'),
    (source_root / 'Variation Family-406x6系列/父体-406x6-N-大.png', '406x6-N_实物参考.png'),
    (source_root / 'Variation Family-406x6系列/父体-406x6-Y-大.png', '406x6-Y_实物参考.png'),
    (source_root / '4A 5082-Y-L/主图/4A 5082-Y-L_1.jpg', '5082_尺寸参考.jpg'),
    (source_root / '4A 5082-Y-L/x2/IMG_1.jpg', '5082_包装标签参考_非成品主图.jpg')
]:
    shutil.copy2(src, ROOT / 'sources' / name)

e = lambda text: html.escape(str(text), quote=True)
css = '''
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f5f3ed;color:#26383c;font-family:Arial,"Microsoft YaHei",sans-serif;line-height:1.7}header{background:#203e42;color:#fff;padding:56px max(6vw,24px)}header small{letter-spacing:3px;color:#d9d8ab}h1{font-size:36px;line-height:1.25;margin:14px 0}header p{max-width:900px;color:#e0e7e2}nav{position:sticky;top:0;background:#fffef9ed;backdrop-filter:blur(10px);padding:13px 6vw;z-index:5;border-bottom:1px solid #ddd}nav a{margin-right:24px;color:#245a61;text-decoration:none;font-size:14px}main{max-width:1160px;margin:auto;padding:32px 24px}section{margin:0 0 58px;scroll-margin-top:75px}h2{font-size:27px;border-bottom:1px solid #c9d2cb;padding-bottom:12px}h3{margin:0 0 12px;font-size:20px}h4{margin:0 0 8px}.notice{background:#fff0c2;border-left:5px solid #d6a23a;padding:18px 22px;margin:20px 0}.muted{color:#687578;font-size:13px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}.tile,.module,details{background:white;border:1px solid #dee2dc;border-radius:12px;overflow:hidden}.tile img{display:block;width:100%;height:auto}.tile .body{padding:18px}.badge{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:#85662a}.module{margin-bottom:28px;padding:24px}.module img{display:block;width:100%;height:auto;border-radius:6px;margin:15px 0 22px}.cards{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px}.cards article{border-top:3px solid #ded89b;padding-top:14px}.copy{background:#f5f7f4;border-radius:6px;padding:16px;white-space:pre-wrap;overflow-wrap:anywhere}.titlecopy{font-size:18px;line-height:1.6}.keywords{font-size:13px;color:#526965}details{margin-bottom:20px;padding:22px}summary{font-size:20px;font-weight:bold;cursor:pointer}.bullet{margin:20px 0}.bullet p{margin:4px 0}table{border-collapse:collapse;width:100%;font-size:13px;background:white}td,th{padding:12px;text-align:left;border:1px solid #dde3dc;vertical-align:top}th{background:#e7eee9}a{color:#22636d}li{margin:9px 0}.stats{display:flex;gap:16px;flex-wrap:wrap}.stats div{padding:12px 22px;border:1px solid #dde3dc;border-radius:6px;background:white}.stats strong{font-size:27px;display:block}.source{overflow-wrap:anywhere}footer{padding:30px;text-align:center;color:#5d7270;font-size:13px}@media(max-width:700px){header{padding:30px 22px}h1{font-size:28px}.grid,.cards{grid-template-columns:1fr}nav{position:static;padding:12px 20px}nav a{display:inline-block;margin:5px 12px 5px 0}main{padding:20px 14px}.module,details{padding:18px}table{min-width:700px}.tablewrap{overflow:auto}}@media print{nav{display:none}body{background:white}header{background:white;color:#203e42;padding:20px}header p{color:#334}details{display:block}section{break-before:page}img{max-height:500px;object-fit:contain}.module,.tile{break-inside:avoid}}
'''
parts = [f'<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>4A Listing 与 A+ 图文审稿包</title><style>{css}</style></head><body>',
f'<header><small>4A · STATIONERY CONTENT SYSTEM</small><h1>让产品说清楚。让画面更干净。</h1><p>5082-Y-L × 406x6 Family<br>{e(data["version"])}</p></header>',
'<nav><a href="#read">先看说明</a><a href="#gallery">12张图片</a><a href="#listing">英文Listing</a><a href="#ap406">406x6 A+</a><a href="#ap5082">5082 A+</a><a href="#audit">22条核对</a></nav><main>',
f'<section id="read"><h2>交付范围与使用方式</h2><p>{e(data["intro"])}</p><div class="stats"><div><strong>4</strong>套完整 Listing</div><div><strong>12</strong>张独立 PNG 审稿</div><div><strong>8</strong>个 A+ 文案模块</div><div><strong>22</strong>条意见逐项对应</div></div>',
'<div class="notice"><strong>这是图文审稿包，不是已获Amazon审核的上传成品。</strong><br>先核准实际纸色、横线、包装和性能，再按后台选定图片槽位导出尺寸。部分图含AI重绘封面，不能替代真实包装原图或条码。英文文案为保守版；未经证实的强承诺已剔除。</div>',
'<p><a href="英文文案_可复制.txt">打开纯英文可复制文本</a> · <a href="生成提示词与修订记录.txt">查看完整生成提示词</a> · <a href="content.json">结构化文案源文件</a></p><ul>',
*[f'<li>{e(x)}</li>' for x in data['decisions']], '</ul></section>',
'<section id="gallery"><h2>图片审稿 · 点击查看独立原图</h2><p class="muted">5082 7张主副图；406x6 4张主模块图＋1张场景补充图。图片内英文需与下方文字保持一致。</p><div class="grid">']
for filename, title, note, alt in data['images']:
    parts.append(f'<article class="tile"><a href="images/{e(filename)}"><img src="images/{e(filename)}" alt="{e(alt)}" loading="lazy"></a><div class="body"><span class="badge">REVIEW DRAFT</span><h3>{e(title)}</h3><p>{e(note)}</p><p class="muted">{e(filename)}</p></div></article>')
parts.append('</div></section><section id="listing"><h2>英文 Listing · 4套</h2><p class="muted">复制英文正文即可；中文备注不要粘贴至买家可见页面。Search terms 为建议词组，提交前按已有字段去重。</p>')
txt=['4A LISTING & A+ COPY | 2026-10-29', 'Conservative copy draft. Verify product specifications before publishing.', '']
for entry in data['listings']:
    parts.append(f'<details open><summary>{e(entry["sku"])}</summary><h4>Title</h4><div class="copy titlecopy" lang="en">{e(entry["title"])}</div><p class="muted">{len(entry["title"])} characters</p>')
    txt += [entry['sku'], 'TITLE', entry['title'], '', 'BULLET POINTS']
    for i,(head,body) in enumerate(entry['bullets'],1):
        parts.append(f'<div class="bullet" lang="en"><strong>{i}. {e(head)}</strong><p>{e(body)}</p></div>')
        txt.append(f'{i}. {head}: {body}')
    parts.append(f'<h4>Description</h4><div class="copy" lang="en">{e(entry["description"])}</div><h4>Suggested search terms</h4><p class="keywords" lang="en">{e(entry["keywords"])}</p><p class="muted">内部说明：{e(entry["note"])}</p></details>')
    txt += ['', 'DESCRIPTION', entry['description'], '', 'SUGGESTED SEARCH TERMS', entry['keywords'], '', '='*70, '']
parts.append('</section>')
for key,label in [('ap406','406x6 · 4个 A+ 主模块'),('ap5082','5082-Y-L · 4个 A+ 文案模块')]:
    parts.append(f'<section id="{key}"><h2>{label}</h2><p class="muted">每个模块包含标题、副标题与三卡正文。图片和文本分开使用；当前画板不是后台模块尺寸承诺。</p>')
    txt += [label, '']
    for i,m in enumerate(data[key],1):
        parts.append(f'<article class="module"><span class="badge">MODULE {i:02}</span><h3 lang="en">{e(m["headline"])}</h3><p lang="en">{e(m["sub"])}</p><img src="images/{e(m["image"])}" alt="{e(m.get("alt",m["headline"]))}" loading="lazy"><div class="cards">')
        txt += [f'MODULE {i}', 'Headline: '+m['headline'], 'Subheadline: '+m['sub']]
        for h,b in m['cards']:
            parts.append(f'<article lang="en"><h4>{e(h)}</h4><p>{e(b)}</p></article>')
            txt += [h, b]
        parts.append(f'</div><p class="muted">{e(m.get("layout","图片复用5082主副图；不是额外生成的另一张图片。"))}</p></article>')
        if 'alt' in m: txt += ['Alt text: '+m['alt']]
        txt += ['']
    parts.append('<div class="copy" lang="en"><strong>Your Trusted Partner in Stationery</strong><br>Premium Stationery Designed for Daily Use</div></section>')
txt += ['BRAND COPY', 'Your Trusted Partner in Stationery', 'Premium Stationery Designed for Daily Use']
parts.append('<section id="audit"><h2>爸爸的22条意见 · 执行与待核状态</h2><div class="tablewrap"><table><thead><tr><th>序号</th><th>原意</th><th>本版处理</th><th>状态／边界</th></tr></thead><tbody>')
for row in data['checklist']: parts.append('<tr>'+''.join(f'<td>{e(x)}</td>' for x in row)+'</tr>')
parts.append('</tbody></table></div><h3 style="margin-top:30px">上传前最后核验</h3><ol><li>核对对应ASIN、实际销售包装和变体色名；不要把父体混色图当黄色子体主图。</li><li>用真实包装原图替换AI小字、条码；确认主图纯白、数量准确、无不包含的道具。</li><li>确认纸色、横线密度、纸厚、胶位、胶带宽度；当前图片不提供性能测试证据。</li><li>如需启用80GSM、无残胶或不渗墨，先提供批次规格及对应笔型/表面测试，保留适用条件。</li><li>按实际A+模块槽位与移动端裁切导出。不要简单拉伸宽图；实际像素优先于DPI标签。</li><li>预览手机端文字和三卡顺序，通过后再提交；本次未进行任何后台提交。</li></ol></section>')
parts.append('<section><h2>来源与制作记录</h2><p>图片使用内置图像生成工具，基于已查看的本地产品参考进行生成与定向返修；未使用API回退。原图均保留。</p><ul>')
for name,source in data['sources']:
    href = source if source.startswith('http') else Path(source).as_uri()
    parts.append(f'<li class="source"><a href="{e(href)}">{e(name)}</a><br><span class="muted">{e(source)}</span></li>')
parts.append('</ul><p>Amazon官方规则核对点：主图白底、真实商品与数量；A+不放保证/退款承诺。具体类目与模块审核仍以账户后台为准。</p></section></main><footer>4A · 图文审稿包 · 2026-10-29 · 原素材未覆盖</footer></body></html>')
(ROOT/'图文审稿.html').write_text(''.join(parts),encoding='utf-8')
(ROOT/'英文文案_可复制.txt').write_text('\n'.join(txt),encoding='utf-8-sig')
prompts=['Built-in image generation. Reference-guided draft images; not photographic proof.']
for item in manifest:
    prompts += ['', item['file'], 'Initial prompt:', item['prompt'], 'Repair prompt:', item.get('repair','None'), 'Selected source file:', item['source']]
(ROOT/'生成提示词与修订记录.txt').write_text('\n'.join(prompts),encoding='utf-8-sig')
report={'images':qa,'image_count':len(qa),'listings':4,'bullets_per_listing':5,'ap_modules':8,'cards_per_module':3,'father_items':22,'publication_status':'Not submitted; review drafts','title_lengths':{x['sku']:len(x['title']) for x in data['listings']},'keyword_bytes':{x['sku']:len(x['keywords'].encode()) for x in data['listings']}}
(ROOT/'验证记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
