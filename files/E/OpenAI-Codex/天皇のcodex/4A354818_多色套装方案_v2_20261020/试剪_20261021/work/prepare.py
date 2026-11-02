from pathlib import Path
import sys, subprocess, json, shutil, concurrent.futures
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'work/libs'))
sys.path.append(r'C:/Users/24243/Documents/Codex/2026-09-08/15-pads-sticky-notes-3-x/work/python_libs')
import cv2, numpy as np, imageio_ffmpeg
from PIL import Image, ImageDraw
FF=imageio_ffmpeg.get_ffmpeg_exe()
A=ROOT/'film/assets'; A.mkdir(parents=True,exist_ok=True)
OLD=Path(r'C:/Users/24243/Documents/Codex/2026-09-08/15-pads-sticky-notes-3-x')
DOWNLOAD=Path('D:/下载文件')
def find(stamp):
    fs=list(DOWNLOAD.glob('*'+stamp+'.mp4')); assert len(fs)==1,fs
    return fs[0]
def run(args):
    p=subprocess.run([FF,'-v','error','-y']+list(map(str,args)),capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode(errors='replace'))
def frame(path,sec=0):
    cap=cv2.VideoCapture(str(path));cap.set(cv2.CAP_PROP_POS_MSEC,sec*1000);ok,im=cap.read();cap.release();assert ok
    return im
def save(path,im):
    cv2.imencode('.png',im)[1].tofile(str(path))

def screen_composite():
    # Recover the actual work-screen appearance from the earlier user-selected clip.
    original=frame(find('20261020134243'))
    p=np.float32([[516,107],[1007,53],[996,406],[494,395]])
    uv=np.float32([[0,0],[1599,0],[1599,899],[0,899]])
    ui=cv2.warpPerspective(original,cv2.getPerspectiveTransform(p,uv),(1600,900))
    save(ROOT/'work/screen_reference.png',ui)
    source=find('20261020232935'); cap=cv2.VideoCapture(str(source));ok,first=cap.read();assert ok
    h,w=first.shape[:2]
    # The upper-right corner lies beyond the photographed frame.
    base=np.float32([[534,59],[1256,-27],[1237,426],[503,408]])
    prev=cv2.cvtColor(first,cv2.COLOR_BGR2GRAY)
    region=np.zeros_like(prev);cv2.fillPoly(region,[np.int32([[492,0],[1279,0],[1279,510],[483,470]])],255)
    points=cv2.goodFeaturesToTrack(prev,maxCorners=350,qualityLevel=.008,minDistance=8,mask=region)
    origin=points.copy(); H=np.eye(3)
    process=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{w}x{h}','-r','24','-i','-','-an','-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p',str(A/'office_screen.mp4')],stdin=subprocess.PIPE)
    logs=[]; n=0; im=first
    while True:
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        if n:
            q,status,err=cv2.calcOpticalFlowPyrLK(prev,gray,points,None,winSize=(31,31),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,30,.01))
            back,st2,_=cv2.calcOpticalFlowPyrLK(gray,prev,q,None,winSize=(31,31),maxLevel=3)
            good=(status.ravel()==1)&(st2.ravel()==1)&(np.linalg.norm(back-points,axis=2).ravel()<1.2)
            origin=origin[good];points=q[good]
            assert len(points)>=12, f'Tracking lost at {n}'
            h0,inliers=cv2.findHomography(origin,points,cv2.RANSAC,2.5)
            if h0 is not None: H=h0
        corners=cv2.perspectiveTransform(base.reshape(-1,1,2),H).reshape(4,2)
        # Inset avoids covering the real black bezel.
        ctr=corners.mean(axis=0);corners=ctr+(corners-ctr)*.995
        M=cv2.getPerspectiveTransform(uv,corners.astype(np.float32))
        patch=cv2.warpPerspective(ui,M,(w,h))
        mask=cv2.warpPerspective(np.full((900,1600),255,np.uint8),M,(w,h)).astype(np.float32)/255
        mask=cv2.GaussianBlur(mask,(3,3),.65)[...,None]
        # Keep the moving shot's window reflections/light response over the display.
        mixed=patch.astype(np.float32)*.84+im.astype(np.float32)*.16
        result=np.clip(im*(1-mask)+mixed*mask,0,255).astype(np.uint8)
        process.stdin.write(result.tobytes())
        if n in [0,24,48,72,96,120,143]:
            save(ROOT/'work'/f'screen_{n:03}.png',result)
            logs.append({'frame':n,'tracked_points':len(points),'corners':corners.tolist()})
        prev=gray;n+=1;ok,im=cap.read()
        if not ok: break
    cap.release();process.stdin.close();assert process.wait()==0
    (ROOT/'work/screen_tracking.json').write_text(json.dumps(logs,indent=2),encoding='utf8')
    print('Screen replaced',n,'frames',flush=True)

def prepare_clips():
    src=OLD/'outputs/354818_business_v1/assets/source_B_original.mp4'
    # Native source ranges retain the real use actions; no generative repair of hands.
    specs=[('hero',find('20261020232249'),.08,4.4,None),
           ('colors',src,17.25,3.25,None),
           ('paper',src,27.5,1.35,'crop=800:450:160:82'),
           ('write',src,306.7,3.6,'crop=850:478:110:50'),
           ('office',A/'office_screen.mp4',.08,3.6,None),
           ('move',src,311.8,6.35,'crop=900:506:60:38'),
           ('wall',find('20261021001502'),.08,3.5,None),
           ('colors_flat',src,346.1,1.9,'crop=830:466:130:78'),
           ('notebook',find('20261021202713'),.08,3.2,None)]
    def prep(spec):
        name,path,start,dur,crop=spec
        filters=([crop] if crop else [])+['scale=1920:1080:flags=lanczos','setsar=1','fps=24']
        run(['-ss',start,'-t',dur,'-i',path,'-an','-vf',','.join(filters),'-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p',A/(name+'.mp4')])
        print('Prepared',name,flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(prep,specs))
    for name in ['segoeui.ttf','segoeuil.ttf','seguisb.ttf']:
        shutil.copy2(Path('C:/Windows/Fonts')/name,A/name)
    shutil.copy2(ROOT.parent/'图片/01_整套18本_实拍.png',A/'packshot.png')
    shutil.copy2(ROOT.parent/'图片/02_18色展开_实拍.png',A/'colors_real.png')
    shutil.copy2(OLD/'work/live_edit_303/mixkit_hazy_after_hours_132.mp3',A/'music.mp3')
    (ROOT/'work/source_ranges.json').write_text(json.dumps([{'name':s[0],'source':str(s[1]),'in':s[2],'duration':s[3],'crop':s[4]} for s in specs],indent=2,ensure_ascii=False),encoding='utf8')

if __name__=='__main__':
    screen_composite()
    prepare_clips()
