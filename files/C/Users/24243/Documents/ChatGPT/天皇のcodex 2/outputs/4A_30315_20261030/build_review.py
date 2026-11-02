from pathlib import Path
import json, html, shutil, zipfile
from PIL import Image

root = Path(__file__).parent
d = json.loads((root/'content.json').read_text(encoding='utf-8'))
m = json.loads((root/'image_manifest.json').read_text(encoding='utf-8'))
for folder in ('images','sources'):
    (root/folder).mkdir(exist_ok=True)
qa=[]
for item in m:
    src=Path(item['source']); assert src.is_file(), src
    dest=root/'images'/item['file']; shutil.copy2(src,dest)
    with Image.open(dest) as im:
        qa.append({'file':item['file'],'width':im.width,'height':im.height,'mode':im.mode})
assert len(qa)==8
assert len(d['listing']['bullets'])==5
assert len(d['listing']['title'])<=200
assert len(d['listing']['keywords'].encode())<250
assert len(d['aplus'])==4
assert all(len(module['cards'])==3 for module in d['aplus'])
source=Path('D:/4A/印刷用图片/电商/亚马逊图片-2021/1-----4A Stiky notes/4A 30315')
for f in ['702877124802.pt01.jpg','702877124802.pt04.JPG','30315-2.JPG']:
    shutil.copy2(source/f,root/'sources'/f)
quality=Path('D:/4A/印刷用图片/电商/国内电商图片/品质说明-配照片.txt')
(root/'sources/品质说明_原文转UTF8.txt').write_text(quality.read_text(encoding='gb18030'),encoding='utf-8-sig')
for f,n in [('codex-clipboard-95b44601-e7fd-492e-8d3a-d2ba79394181.png','谷歌方案_截图1.png'),('codex-clipboard-a8bd6e4f-df77-4dc3-8b95-84bdfaa3268d.png','谷歌方案_截图2.png')]:
    shutil.copy2(Path('C:/Users/24243/AppData/Local/Temp')/f,root/'sources'/n)

e=lambda x:html.escape(str(x),quote=True)
css='''*{box-sizing:border-box}body{margin:0;background:#f6f5ef;color:#253c40;font:16px/1.75 Arial,"Microsoft YaHei",sans-serif}header{background:#203e42;color:white;padding:50px max(24px,6vw)}header small{letter-spacing:3px;color:#ccd9c4}h1{font-weight:500;font-size:40px;line-height:1.25}header p{color:#dce5df;max-width:850px}nav{position:sticky;top:0;z-index:3;background:#fffef9ed;backdrop-filter:blur(8px);padding:14px 6vw;border-bottom:1px solid #ddd}nav a{margin-right:24px;text-decoration:none}a{color:#246371}main{max-width:1140px;padding:32px 24px;margin:auto}section{margin-bottom:60px;scroll-margin-top:85px}h2{font-size:27px;border-bottom:1px solid #d6ded7;padding-bottom:12px}h3{font-weight:600;margin:0 0 12px}h4{margin:0 0 6px}.hero{background:#fff;border-radius:12px;overflow:hidden}.hero img{display:block;width:100%}.notice{padding:18px 22px;background:#fff0ce;border-left:4px solid #c99f4e;margin:24px 0}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:22px}.tile,.module{border:1px solid #dce2dd;background:white;border-radius:10px;overflow:hidden}.tile img{display:block;width:100%;height:auto}.body{padding:20px}.body p{font-size:14px;margin:8px 0}.muted{font-size:13px;color:#647879}.badge{font-size:11px;letter-spacing:2px;color:#967343}.module{padding:24px;margin:25px 0}.module img{display:block;width:100%;margin:20px 0}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:25px}.cards article{border-top:2px solid #bdcdc0;padding-top:14px}.copy{background:#fff;padding:24px;border:1px solid #dce2dd;border-radius:8px;white-space:pre-wrap;overflow-wrap:anywhere}.bullets article{margin:20px 0}.bullets p{margin:4px 0}table{border-collapse:collapse;width:100%;background:#fff;font-size:14px}td,th{padding:13px;text-align:left;border:1px solid #dce2dd;vertical-align:top}th{background:#e7eee9}li{margin:9px 0}.stats{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}.stats div{background:white;border:1px solid #dde3de;border-radius:8px;padding:16px 26px}.stats strong{font-size:29px;display:block}.source{overflow-wrap:anywhere}footer{text-align:center;padding:30px;color:#647879;font-size:13px}@media(max-width:700px){header{padding:28px 22px}h1{font-size:29px}.grid,.cards{grid-template-columns:1fr}nav{position:static;padding:14px 20px}nav a{display:inline-block;margin:4px 14px 4px 0}main{padding:22px 14px}.module{padding:18px}.tablewrap{overflow:auto}table{min-width:640px}}@media print{nav{display:none}section{break-before:page}.tile,.module{break-inside:avoid}header{background:white;color:#203e42}header p{color:#253c40}img{max-height:520px;object-fit:contain}}'''
p=[f'<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>4A 30315 · 彩虹阶梯图文审稿</title><style>{css}</style></head><body>',
'<header><small>4A / COLOR, WITH PURPOSE.</small><h1>让十五种颜色，各有用处。</h1><p>30315 · Standard Flat<br>彩虹阶梯主副图 + 英文 Listing + A+ · 2026-10-30</p></header>',
'<nav><a href="#visual">先看设计</a><a href="#gallery">全套图片</a><a href="#copy">英文Listing</a><a href="#ap">A+模块</a><a href="#facts">规格与核验</a></nav><main>',
'<section id="visual"><div class="hero"><img src="images/303_A1.png" alt="4A30315 fifteen assorted square note pads with the headline More colors. A clearer plan."></div>',
f'<p>{e(d["intro"])}</p><div class="stats"><div><strong>15</strong>本／15色</div><div><strong>1500</strong>张总计</div><div><strong>8</strong>张独立设计图</div><div><strong>4</strong>个A+文案模块</div></div>',
'<div class="notice"><strong>实物参考生成 · 图文审稿版</strong><br>不是已审核的最终上架成品。新图中的颜色、纸厚和细小结构仍需当前批次实物确认。本次没有操作价格、合并变体或提交后台。</div>',
'<p><a href="英文文案_可复制.txt">英文文案纯文本</a> · <a href="生成提示词与修订记录.txt">生成与返修提示词</a> · <a href="验证记录.json">文件与结构校验</a></p></section>',
'<section id="gallery"><h2>主副图 7 张 + 横版 A+ 1 张</h2><p class="muted">点击图片查看原始文件。A+中的其他配图复用副图，不重复计入新图数量。</p><div class="grid">']
for f,title,note,alt in d['images']:
    p.append(f'<article class="tile"><a href="images/{e(f)}"><img loading="lazy" src="images/{e(f)}" alt="{e(alt)}"></a><div class="body"><span class="badge">REVIEW DRAFT</span><h3>{e(title)}</h3><p>{e(note)}</p><p class="muted">{e(f)}</p></div></article>')
p.append('</div></section><section id="copy"><h2>英文 Listing · Standard Flat</h2><p class="muted">仅复制英文内容。不要把本套用于30315-Z抽取款；不要把中文审稿说明复制到商品页。</p>')
l=d['listing']
p.append(f'<h3>Title</h3><div class="copy" lang="en">{e(l["title"])}</div><p class="muted">{len(l["title"])} characters</p><div class="bullets" lang="en">')
text=['4A 30315 | STANDARD FLAT | 2026-10-30','Review copy. Verify current product and listing details before publication.','','TITLE',l['title'],'','BULLET POINTS']
for i,(h,b) in enumerate(l['bullets'],1):
    p.append(f'<article><h3>{i}. {e(h)}</h3><p>{e(b)}</p></article>');text += [f'{i}. {h}: {b}']
p.append(f'</div><h3>Description</h3><div class="copy" lang="en">{e(l["description"])}</div><h3 style="margin-top:25px">Suggested search terms</h3><div class="copy" lang="en">{e(l["keywords"])}</div><p class="muted">{e(l["internal"])}</p></section>')
text += ['','DESCRIPTION',l['description'],'','SUGGESTED SEARCH TERMS',l['keywords'],'','A+ CONTENT']
p.append('<section id="ap"><h2>A+ 内容 · 标题、副标题、三卡正文</h2><p class="muted">下方为模块内容组合，不代表具体后台图片槽位尺寸。将文字保留在可访问的文本栏，避免全部压成小字图片。</p>')
for i,a in enumerate(d['aplus'],1):
    p.append(f'<article class="module"><span class="badge">MODULE {i:02}</span><h3 lang="en">{e(a["headline"])}</h3><p lang="en">{e(a["sub"])}</p><img loading="lazy" src="images/{e(a["image"])}" alt="{e(a["headline"])}"><div class="cards" lang="en">')
    text += ['',f'MODULE {i}',a['headline'],a['sub']]
    for h,b in a['cards']:
        p.append(f'<article><h4>{e(h)}</h4><p>{e(b)}</p></article>');text += [h,b]
    p.append('</div></article>')
p.append('<div class="copy" lang="en">'+'<br>'.join(e(x) for x in d['brand'])+'</div></section>')
text += ['','BRAND COPY']+d['brand']
p.append('<section id="facts"><h2>规格来源与方案取舍</h2><div class="tablewrap"><table><tr><th>项目</th><th>采用值</th><th>依据／边界</th></tr>')
for row in d['facts']:p.append('<tr>'+''.join(f'<td>{e(x)}</td>' for x in row)+'</tr>')
p.append('</table></div><h3 style="margin-top:28px">落实谷歌方案，但不照搬有误的假设</h3><ul>')
p += [f'<li>{e(x)}</li>' for x in d['decisions']]
p.append('</ul><h3>上架前核验清单</h3><ol>')
p += [f'<li>{e(x)}</li>' for x in d['preflight']]
p.append('</ol></section><section><h2>参考来源与制作记录</h2><p>使用内置图像生成工具进行实物参考生成与定向返修，未使用CLI/API回退。所有选中输出已复制进本包，原始素材未覆盖。</p><ul>')
for title,path in d['sources']:
    link=path if path.startswith('http') else Path(path).as_uri()
    p.append(f'<li class="source"><a href="{e(link)}">{e(title)}</a><br><span class="muted">{e(path)}</span></li>')
p.append('</ul><p class="muted">Amazon规则核对：主图纯白、商品本身，不叠加广告文字；当前图片仍需实际类目及账户预览确认。</p></section></main><footer>4A 30315 · Color, with purpose. · 2026-10-30</footer></body></html>')
(root/'30315_图文审稿.html').write_text(''.join(p),encoding='utf-8')
(root/'英文文案_可复制.txt').write_text('\n'.join(text),encoding='utf-8-sig')
prompts=['Built-in image generation | 4A30315 Standard Flat | 2026-10-30']
for item in m:
    prompts += ['',item['file'],'Initial prompt:',item.get('prompt',''),'Repair prompt:',item.get('repair','None'),'Selected original output:',item['source']]
(root/'生成提示词与修订记录.txt').write_text('\n'.join(prompts),encoding='utf-8-sig')
report={'images':qa,'image_count':8,'listing_count':1,'bullets':5,'ap_modules':4,'cards_per_module':3,'title_characters':len(l['title']),'search_term_bytes':len(l['keywords'].encode()),'source_sku':'4A30315 Standard Flat','published':False,'visual_review':'All selected outputs inspected; physical shade/thickness/adhesive properties still require batch verification.'}
(root/'验证记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
