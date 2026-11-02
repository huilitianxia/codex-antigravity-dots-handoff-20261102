from pathlib import Path
import re, json, html, shutil, subprocess
R=Path(__file__).resolve().parent.parent
P=R/'film'; A=P/'assets'; W=R/'work'/'brand_intro'; W.mkdir(exist_ok=True)
duration=832/24
for name in ['index.html','edit_manifest.json','music-b.html.template','BRIEF.md','design.md']:
    src=P/name
    if src.exists() and not (W/name).exists(): shutil.copy2(src,W/name)
src=(W/'index.html').read_text(encoding='utf-8')
src=re.sub(r'(<div id="host-s\d+"[^>]*data-start=")([\d.]+)',lambda m:m[1]+f'{float(m[2])+2.5:.8f}',src)
src=src.replace('data-duration="32.166666666666664"',f'data-duration="{duration}"')
host='<div id="host-brand" class="clip" data-composition-id="brand-intro" data-composition-src="compositions/brand-intro.html" data-start="0" data-duration="2.5" data-track-index="0"></div>'
src=src.replace('<div id="host-s01"',host+'<div id="host-s01"',1)
src=src.replace('assets/A_Close_Up_32s.wav','assets/A_Close_Up_34s.wav')
automation={'version':1,'lanes':[{'target':'volume','points':[{'t':0,'v':0},{'t':.7,'v':1},{'t':duration-2,'v':1},{'t':duration,'v':0}]}]}
src=re.sub(r'data-automation="[^"]+"','data-automation="'+html.escape(json.dumps(automation),quote=True)+'"',src)
(P/'index.html').write_text(src,encoding='utf-8')
(P/'music-b.html.template').write_text(src.replace('A_Close_Up_34s.wav','B_Curiosity_34s.wav'),encoding='utf-8')
intro='''<template><div id="brand-intro" data-composition-id="brand-intro" data-width="1920" data-height="1080" data-duration="2.5">
<style>
@font-face{font-family:BrandEditorial;src:url('../assets/segoeui.ttf');font-weight:400}
#brand-intro{position:absolute;inset:0;background:#fff;overflow:hidden}
#brand-lockup{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:55px;padding-bottom:12px;box-sizing:border-box}
#brand-crown{display:block;width:560px;height:398px;object-fit:contain;margin-left:55px}
#brand-line{font-family:BrandEditorial,sans-serif;font-size:42px;letter-spacing:1.6px;color:#353c38;line-height:1.3;text-align:center;margin:0}
</style>
<div id="brand-lockup"><img id="brand-crown" src="../assets/4A_crown_master.png" alt="4A crown brand"><p id="brand-line">Color your everyday.</p></div>
<script>const tl=gsap.timeline({paused:true});tl.fromTo('#brand-crown',{opacity:.15,scale:.97},{opacity:1,scale:1,duration:.6,ease:'power2.out'},0);tl.fromTo('#brand-line',{opacity:0,y:8},{opacity:1,y:0,duration:.42,ease:'power2.out'},.32);window.__timelines['brand-intro']=tl;</script>
</div></template>'''
(P/'compositions'/'brand-intro.html').write_text(intro,encoding='utf-8')
m=json.loads((W/'edit_manifest.json').read_text(encoding='utf-8'));m['duration']=duration;m['frames']=832
for s in m['shots']:s['start']+=2.5
m['shots'].insert(0,{'scene':'brand-intro','name':'4A crown','start':0,'duration':2.5,'frames':60,'rate':1,'headline':'Color your everyday.'})
(P/'edit_manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding='utf-8')
for fn in ['BRIEF.md','design.md']:
    with (P/fn).open('a',encoding='utf-8') as f:f.write('\n\n2026-10-21 brand revision: prepend 2.5 seconds of the authentic color 4A crown logo, rendered from the supplied Illustrator master. White background, restrained scale/opacity entrance and “Color your everyday.” line. Both music variants remain. Product scenes, repaired office_v2 screen and color treatments are retained. Total 34.6667 s, 832 frames.\n')
(W/'asset_provenance.json').write_text(json.dumps({'source':r'D:\4A\印刷用图片\电商\亚马逊图片-2021\A+页面\4A logo.ai','derived':'film/assets/4A_crown_master.png','method':'Poppler native PDF-compatible Illustrator render at 1600 px; no redraw or shape change'},ensure_ascii=False,indent=2),encoding='utf-8')
ff=str(R/'work/bin/ffmpeg.exe')
for name in ['A_Close_Up','B_Curiosity']:
    subprocess.run([ff,'-y','-v','error','-i',str(A/(name+'.mp3')),'-t',str(duration),'-af','loudnorm=I=-19:TP=-2:LRA=11','-ar','48000','-ac','2',str(A/(name+'_34s.wav'))],check=True)
print('Brand intro and extended music ready',duration)
