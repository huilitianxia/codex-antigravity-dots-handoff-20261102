from pathlib import Path
import subprocess, json, sys, shutil
sys.path.insert(0,r'C:\Users\24243\Documents\Codex\2026-09-08\15-pads-sticky-notes-3-x\work\python_libs')
from PIL import Image,ImageDraw
W=Path(__file__).resolve().parent;R=W.parent.parent;P=R/'film';A=P/'assets'
ff=str(R/'work/bin/ffmpeg.exe');fp=str(R/'work/bin/ffprobe.exe')
dur=832/24
def run(args):return subprocess.run(args,check=True,capture_output=True,encoding='utf-8')
va=R/'4A_354818_v3_品牌开场_A.mp4'; vb=R/'4A_354818_v3_品牌开场_B.mp4'
run([ff,'-y','-v','error','-i',str(va),'-i',str(A/'B_Curiosity_34s.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',f'afade=t=in:st=0:d=0.7,afade=t=out:st={dur-2}:d=2','-c:a','aac','-b:a','192k','-t',str(dur),'-movflags','+faststart',str(vb)])
intro=R/'4A皇冠_通用品牌片头_2.5秒.mp4'
run([ff,'-y','-v','error','-i',str(va),'-an','-frames:v','60','-c:v','libx264','-crf','16','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(intro)])
checks=[]
for video,frames in [(va,832),(vb,832),(intro,60)]:
    probe=json.loads(run([fp,'-v','error','-show_format','-show_streams','-of','json',str(video)]).stdout)
    vs=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert vs['width']==1920 and vs['height']==1080 and vs['r_frame_rate']=='24/1'
    assert int(vs['nb_frames'])==frames
    assert abs(float(probe['format']['duration'])-frames/24)<.05
    checks.append({'file':video.name,'bytes':video.stat().st_size,'duration':probe['format']['duration'],'frames':frames,'size':'1920x1080','fps':24})
hashes=[run([ff,'-v','error','-i',str(v),'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256','-']).stdout.strip() for v in [va,vb]]
assert hashes[0]==hashes[1]
times=[.1,.5,1.25,2.458,2.5,3,6.4,17.2,34.4]
contact=Image.new('RGB',(1440,900),'#eeeeee');d=ImageDraw.Draw(contact)
for i,t in enumerate(times):
    out=W/f'export_{i}.png'
    run([ff,'-y','-v','error','-ss',str(t),'-i',str(va),'-frames:v','1',str(out)])
    im=Image.open(out).convert('RGB');im.thumbnail((480,270));x=(i%3)*480;y=(i//3)*300
    contact.paste(im,(x,y+30));d.text((x+10,y+8),f'{t:.3f}s',fill='black')
contact.save(R/'品牌开场_v3_画面检查.jpg',quality=94)
shutil.copy2(W/'export_2.png',R/'4A品牌开场预览.png')
(W/'output_checks.json').write_text(json.dumps({'outputs':checks,'video_stream_hash':hashes[0],'A_B_visuals_identical':True,'screen_uses':'office_v2.mp4','decoded_frames':times},ensure_ascii=False,indent=2),encoding='utf-8')
(R/'品牌开场_v3_说明.txt').write_text('4A皇冠品牌开场 v3\n\nA、B两版均为34.6667秒，1080p、24帧。前2.5秒统一展示原版4A皇冠，接现有产品介绍。\n标识来自已有4A logo.ai矢量文件的高分辨率渲染，未重新绘制。\n文案：Color your everyday.（为每一天添点色彩。）\nA音乐为Close Up，B为Curiosity。授权记录沿用MUSIC_LICENSE_V2.md。\n修复后的电脑屏幕保留；旧版成片保留。\n通用片头另存为4A皇冠_通用品牌片头_2.5秒.mp4，无配乐，方便以后接入不同视频。\n可编辑项目：film/index.html。品牌片头：film/compositions/brand-intro.html。请直接编辑当前工程；work/build.py是旧的基础组装脚本。\n',encoding='utf-8')
print(json.dumps(checks,ensure_ascii=False))
