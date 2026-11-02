from pathlib import Path
import json,re,shutil,html,subprocess
R=Path(__file__).resolve().parent.parent;P=R/'film';W=R/'work/pace_v4';W.mkdir(exist_ok=True)
for name in ['index.html','music-b.html.template','edit_manifest.json','BRIEF.md','design.md']:
 if not (W/name).exists():shutil.copy2(P/name,W/name)
if not (W/'compositions').exists():shutil.copytree(P/'compositions',W/'compositions')
shots=[('brand-intro',42,0),('s01',106,0),('s02',78,0),('s03',86,0),('s04',62,.35),('s05',94,0),('s06',66,.2),('s08',70,.15),('s09',116,0)]
orig=json.loads((W/'edit_manifest.json').read_text(encoding='utf-8'));lookup={s['scene']:s for s in orig['shots']}
start=0;hosts=[];manifest=[]
for sid,n,offset in shots:
 dur=n/24;f=W/'compositions'/f'{sid}.html';s=f.read_text(encoding='utf-8')
 s=re.sub(r'data-duration="[\d.]+"',f'data-duration="{dur:.8f}"',s)
 if offset:
  s=re.sub(r'(<video\b[^>]*?) data-start="0"',lambda m:m[1]+f' data-media-start="{offset}" data-start="0"',s)
 if sid!='brand-intro':
  s=re.sub(r'(duration:\.18\},\s*)[\d.]+(\);)',lambda m:m[1]+f'{dur-.2:.8f}'+m[2],s)
 if sid in ['s02','s03','s05']:
  s=s.replace('rgba(25,24,22,.85),rgba(25,24,22,.55) 25%,transparent 55%','rgba(25,24,22,.78),rgba(25,24,22,.36) 25%,transparent 52%')
 if sid=='brand-intro':
  s=s.replace("duration:.6,ease:","duration:.48,ease:").replace("duration:.42,ease:","duration:.36,ease:").replace("},.32)","},.2)")
 if sid=='s09':
  s=s.replace('left:1050px;top:145px','left:1050px;top:100px')
  s=s.replace('.end-brand{font-size:43px;font-weight:600;letter-spacing:2px;margin-bottom:35px}', '.end-brand{height:128px;margin-bottom:26px}.end-crown{display:block;width:180px;height:128px;object-fit:contain}')
  s=s.replace('<div class="end-brand">4A</div>','<div class="end-brand"><img id="end-crown" class="end-crown" src="../assets/4A_crown_master.png" alt="4A crown brand"></div>')
  s=s.replace('A small note. A clearer day.','Color your everyday.')
 (P/'compositions'/f'{sid}.html').write_text(s,encoding='utf-8')
 hid='host-brand' if sid=='brand-intro' else 'host-'+sid
 hosts.append(f'<div id="{hid}" class="clip" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{start:.8f}" data-duration="{dur:.8f}" data-track-index="0"></div>')
 item=dict(lookup[sid]);item.update(start=start,duration=dur,frames=n,source_offset=offset);manifest.append(item);start+=dur
assert round(start*24)==720
s=(W/'index.html').read_text(encoding='utf-8')
s=re.sub(r'(<div id="root"[^>]*data-duration=")[\d.]+',r'\g<1>30',s)
s=re.sub(r'<div id="host-brand".*?(?=<audio id="music")',''.join(hosts),s,flags=re.S)
s=s.replace('A_Close_Up_34s.wav','A_Close_Up_30s.wav')
s=re.sub(r'(<audio id="music"[^>]*data-duration=")[\d.]+',r'\g<1>30',s)
auto={'version':1,'lanes':[{'target':'volume','points':[{'t':0,'v':0},{'t':.55,'v':1},{'t':28,'v':1},{'t':30,'v':0}]}]}
s=re.sub(r'data-automation="[^"]+"','data-automation="'+html.escape(json.dumps(auto),quote=True)+'"',s)
(P/'index.html').write_text(s,encoding='utf-8')
(P/'music-b.html.template').write_text(s.replace('A_Close_Up_30s.wav','B_Curiosity_30s.wav'),encoding='utf-8')
(P/'edit_manifest.json').write_text(json.dumps({'duration':30,'frames':720,'fps':24,'shots':manifest},ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['A_Close_Up','B_Curiosity']:
 subprocess.run([str(R/'work/bin/ffmpeg.exe'),'-y','-v','error','-i',str(P/'assets'/(name+'.mp3')),'-t','30','-af','loudnorm=I=-19:TP=-2:LRA=11','-ar','48000','-ac','2',str(P/'assets'/(name+'_30s.wav'))],check=True)
note='\n\n2026-10-22 v4: existing footage only, 30 seconds / 720 frames. Crown opener 1.75 s; crown and matching tagline on closing card. Remove duplicated s07 color spread; shorten lifestyle scenes; keep complete s05 re-stick action. Conservative live-footage white balance/shadow correction plus lighter lower shading. A music for review; previous outputs retained.\n'
for name in ['BRIEF.md','design.md']:
 with (P/name).open('a',encoding='utf-8') as f:f.write(note)
print(json.dumps(manifest,ensure_ascii=False))
