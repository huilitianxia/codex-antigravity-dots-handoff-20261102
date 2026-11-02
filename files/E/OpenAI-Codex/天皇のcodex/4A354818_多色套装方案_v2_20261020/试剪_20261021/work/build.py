from pathlib import Path
import json, html
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'film'; C=P/'compositions';C.mkdir(exist_ok=True)
shots=[
 ('hero',106,'Small-size','Sticky Notes','4A 354818',.45),
 ('colors',78,'18 colors.','Pick yours.','',1),
 ('write',86,'Write it down.','','',1),
 ('office',86,'Keep priorities','in sight.','AT YOUR DESK',1),
 ('move',94,'Re-stick.','Reorganize.','',6.35/(94/24)),
 ('wall',84,'Color-code','your day.','A COLOR FOR EACH PRIORITY',1),
 ('colors_flat',46,'','','',1),
 ('notebook',76,'Make room','for ideas.','ON THE PAGE',1),
 ('closing',116,'','','',1)]
start=0;hosts=[];manifest=[]
common='''
@font-face{font-family:Editorial;src:url('../assets/segoeui.ttf');font-weight:400}
@font-face{font-family:Editorial;src:url('../assets/seguisb.ttf');font-weight:600}
@font-face{font-family:Editorial;src:url('../assets/segoeuil.ttf');font-weight:300}
.scene-video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.copy{position:absolute;left:96px;bottom:100px;color:#fffaf3;font-family:Editorial,sans-serif;z-index:2}
.eyebrow{font-size:24px;letter-spacing:4px;font-weight:600;margin-bottom:16px;line-height:1.3}
.headline{font-size:68px;font-weight:600;letter-spacing:-1.7px;line-height:1.12;margin:0}
.brand{font-family:Editorial,sans-serif;font-size:36px;font-weight:600;letter-spacing:1px;color:#fffaf3;position:absolute;left:96px;top:68px;z-index:3}
.shade{position:absolute;inset:0;background:linear-gradient(0deg,rgba(25,24,22,.85),rgba(25,24,22,.55) 25%,transparent 55%);z-index:1}
'''
for idx,(name,n,title1,title2,kicker,rate) in enumerate(shots):
    sid=f's{idx+1:02}';dur=n/24
    styles=common+f'#{sid}{{position:absolute;inset:0;overflow:hidden;font-family:Editorial,sans-serif}}'
    tween=''
    if name!='closing':
        body=f'<video id="{sid}-video" class="clip scene-video" src="../assets/{name}.mp4" data-start="0" data-duration="{dur:.8f}" data-playback-rate="{rate:.8f}" data-track-index="0" muted playsinline></video>'
        if name=='office':body=body.replace('assets/office.mp4','assets/office_v2.mp4')
        if title1:
            body+=f'<div class="shade" data-layout-ignore></div><div id="{sid}-copy" class="copy"><div class="eyebrow">{kicker}</div><div class="headline">{title1}</div>'
            if title2:body+=f'<div class="headline">{title2}</div>'
            body+='</div>'
            tween+=f'tl.fromTo("#{sid}-copy",{{opacity:0,y:14}},{{opacity:1,y:0,duration:.38,ease:"power2.out"}},.14);'
            tween+=f'tl.to("#{sid}-copy",{{opacity:0,duration:.18}}, {dur-.2:.8f});'
        if name=='hero':
            styles+='''
 .copy{left:96px;top:180px;bottom:auto;width:400px}.headline{font-size:62px;line-height:1.12}
 .shade{background:linear-gradient(90deg,rgba(26,24,22,.72),rgba(26,24,22,.20) 31%,transparent 49%)}
 .eyebrow{font-size:25px;letter-spacing:3px;margin-bottom:20px}
'''
            body+='<div class="brand">4A</div>'
        elif name=='office':
            styles+='.copy{bottom:105px}.headline{font-size:62px}'
        elif name=='wall':
            # Negative space on wall left of the actual four notes; no covering the product.
            styles+='.copy{left:750px;top:90px;bottom:auto;color:#272823}.headline{font-size:62px}.eyebrow{font-size:21px;letter-spacing:2px}.shade{display:none}'
        elif name=='notebook':
            styles+='.copy{left:104px;bottom:92px}.headline{font-size:62px}'
    else:
        styles+='''
.end-bg{position:absolute;inset:0;background:#fff}
.pack{position:absolute;left:100px;top:115px;width:865px;height:825px;object-fit:contain}
.end-copy{position:absolute;left:1050px;top:145px;width:790px;color:#242826}
.end-brand{font-size:43px;font-weight:600;letter-spacing:2px;margin-bottom:35px}
.end-kicker{font-size:25px;letter-spacing:3px;margin-bottom:15px;color:#4e5650}
.end-title{font-size:64px;line-height:1.12;font-weight:600;letter-spacing:-1.5px}
.tagline{font-size:31px;margin-top:25px;color:#4e5650}
.specs{margin-top:57px;display:flex;gap:53px;padding-top:28px;border-top:1px solid #cbd0c8}
.spec-number{font-size:49px;font-weight:600;line-height:1.1}
.spec-label{font-size:25px;color:#4e5650;line-height:1.4;margin-top:9px}
.size{font-size:27px;color:#4e5650;margin-top:33px}
'''
        body='''<div class="end-bg"></div><img id="end-pack" class="pack" src="../assets/packshot.png" alt="Actual 18-pad product photograph"><div id="end-copy" class="end-copy"><div class="end-brand">4A</div><div class="end-kicker">354818 · SMALL-SIZE STICKY NOTES</div><div class="end-title">18 colors.</div><div class="end-title">Everyday possibilities.</div><div class="tagline">A small note. A clearer day.</div><div class="specs"><div><div class="spec-number">18</div><div class="spec-label">pads / colors</div></div><div><div class="spec-number">100</div><div class="spec-label">sheets per pad</div></div><div><div class="spec-number">1,800</div><div class="spec-label">sheets total</div></div></div><div class="size">1⅜ × 1⅞ in · approximately 35 × 48 mm</div></div>'''
        tween='tl.fromTo("#end-pack",{opacity:0,x:-18},{opacity:1,x:0,duration:.5,ease:"power2.out"},0);tl.fromTo("#end-copy",{opacity:0,y:14},{opacity:1,y:0,duration:.45,ease:"power2.out"},.15);'
    doc=f'<!doctype html><html><head><meta charset="utf-8"></head><body><template><style>{styles}</style><div id="{sid}" data-composition-id="{sid}" data-width="1920" data-height="1080" data-duration="{dur:.8f}">{body}</div><script>{{const tl=gsap.timeline({{paused:true}});{tween}window.__timelines["{sid}"]=tl;}}</script></template></body></html>'
    (C/(sid+'.html')).write_text(doc,encoding='utf8')
    hosts.append(f'<div id="host-{sid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{start/24:.8f}" data-duration="{dur:.8f}" data-track-index="0"></div>')
    manifest.append({'scene':sid,'name':name,'start':start/24,'duration':dur,'frames':n,'rate':rate,'headline':' '.join([title1,title2]).strip()});start+=n
duration=start/24
automation=html.escape(json.dumps({'version':1,'lanes':[{'target':'volume','points':[{'t':0,'v':0},{'t':.7,'v':1.0},{'t':duration-2,'v':1.0},{'t':duration,'v':0}]}]}),quote=True)
doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>4A 354818 — First complete edit</title><script src="assets/gsap.min.js"></script><style>html,body{{margin:0;width:100%;height:100%;background:#fff}}#root{{position:relative;width:100%;height:100%;overflow:hidden}}.clip{{position:absolute;inset:0}}</style></head><body><div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-duration="{duration}">{''.join(hosts)}<audio id="music" src="assets/A_Close_Up_32s.wav" data-start="0" data-duration="{duration}" data-media-start="0" data-track-index="3" data-automation="{automation}"></audio></div><script>window.__timelines['main']=gsap.timeline({{paused:true}});</script></body></html>'''
(P/'index.html').write_text(doc,encoding='utf8')
(P/'edit_manifest.json').write_text(json.dumps({'duration':duration,'fps':24,'frames':start,'shots':manifest,'screen':'Tracked replacement using earlier work-interface video; existing bezel and blue/pink notes preserved.'},ensure_ascii=False,indent=2),encoding='utf8')
(P/'BRIEF.md').write_text('''---
workflow: general-video
flow: automation
storyboard: no
---
# 4A 354818 first complete trial edit
User authorized a complete trial render from supplied footage. Premium Amazon presentation with clear product identity. 16:9, English copy, music, no voiceover. Preserve all source files and earlier edits. No publishing.
Use the four reviewed Flow scenes plus actual unstacking, paper handling, writing and repositioning. Screen in office scene must match earlier active work-interface look. No new paid generations.
Full-screen photographic footage and concise overlays; no repeated slide-like white split layouts. White product/specification closing only. Product: 18 pads, 18 colors, 100 sheets/pad, 1800 total, 1 3/8 by 1 7/8 inches. Adhesive direction omitted because source information conflicts.
Source footage is 960x544 for actual hands and 1280x720 for Flow scenes, upscaled to 1920x1080 for delivery. Do not describe as native 1080p detail.
''',encoding='utf8')
(P/'design.md').write_text('Full-frame warm daylight photography. Neutral ivory white and charcoal typography. Product colors lead; no invented colored panels. Segoe UI light/regular/semibold local fonts. Gentle 0.38s text entrance and clean action cuts. Display 4A and full series identification from opening. Protect notes from overlays. Keep real source actions intact. End with actual product photo and factual specs. Existing ambient music, moderate volume, fades. No motion decorations or synthetic hand footage.',encoding='utf8')
(P/'MUSIC_LICENSE.md').write_text('Hazy After Hours — Alejandro Magaña (A. M.). Existing downloaded project asset. Source https://assets.mixkit.co/music/132/132.mp3 . License rechecked 2026-10-21: https://mixkit.co/license/modal/musicFree/ permits commercial online marketing ads; does not permit TV/radio, games or CD/DVD. Do not claim ownership or register music in rights-management systems. This file is production documentation, not a license sublicense.',encoding='utf8')
print('Built',duration,'seconds',start,'frames')
