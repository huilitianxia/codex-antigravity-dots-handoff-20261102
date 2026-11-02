from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import imageio.v2 as imageio
import imageio_ffmpeg
import math, os, wave, subprocess

W, H, FPS, DUR = 720, 1280, 30, 25
ROOT = r"C:\Users\24243\Documents\Codex\2026-08-11\7-30-slack-plugin-slack-openai"
SRC = r"E:\Desktop\L1310466.png"
OUT = os.path.join(ROOT, "outputs")
os.makedirs(OUT, exist_ok=True)
SILENT = os.path.join(ROOT, "work", "sticky_ad_silent.mp4")
WAV = os.path.join(ROOT, "work", "sticky_ad_audio.wav")
FINAL = os.path.join(OUT, "翰林纸院便利贴_25秒产品视频.mp4")
POSTER = os.path.join(OUT, "翰林纸院便利贴_视频封面.jpg")

FONT_B = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_R = r"C:\Windows\Fonts\msyh.ttc"

def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT_R, size)

def ease(x):
    x = max(0.0, min(1.0, x))
    return x*x*(3-2*x)

def clamp(x, a=0, b=1): return max(a, min(b, x))

def cover(im, size):
    sw, sh = im.size; tw, th = size
    s = max(tw/sw, th/sh)
    r = im.resize((int(sw*s), int(sh*s)), Image.Resampling.LANCZOS)
    x = (r.width-tw)//2; y=(r.height-th)//2
    return r.crop((x,y,x+tw,y+th))

def shadow_rect(base, box, color, radius=20, shadow=16, alpha=65):
    x0,y0,x1,y1=box
    sh = Image.new("RGBA", base.size, (0,0,0,0))
    sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((x0+5,y0+10,x1+5,y1+10), radius=radius, fill=(20,30,45,alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(shadow))
    base.alpha_composite(sh)
    d=ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=color)

def center_text(d, y, text, fnt, fill, maxw=None):
    box=d.textbbox((0,0), text, font=fnt)
    x=(W-(box[2]-box[0]))//2
    d.text((x,y), text, font=fnt, fill=fill)

def pill(d, xy, text, fill, fg=(255,255,255), fs=26):
    f=font(fs, True); x,y=xy
    b=d.textbbox((0,0),text,font=f); ww=b[2]-b[0]+34; hh=b[3]-b[1]+22
    d.rounded_rectangle((x,y,x+ww,y+hh),radius=hh//2,fill=fill)
    d.text((x+17,y+7),text,font=f,fill=fg)

def note_layer(color, size=(250,250), text=None, text_color=(25,31,43), angle=0):
    w,h=size
    lay=Image.new("RGBA",(w+60,h+60),(0,0,0,0))
    sh=Image.new("RGBA",lay.size,(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.rounded_rectangle((32,38,32+w,38+h),radius=11,fill=(10,20,30,70))
    sh=sh.filter(ImageFilter.GaussianBlur(14)); lay.alpha_composite(sh)
    d=ImageDraw.Draw(lay); d.rounded_rectangle((30,30,30+w,30+h),radius=10,fill=color)
    # a very subtle straight adhesive band; note remains fully flat
    d.rectangle((30,30,30+w,39),fill=tuple(max(0,c-12) for c in color[:3])+(120,))
    if text:
        f=font(30,True)
        bb=d.multiline_textbbox((0,0),text,font=f,spacing=7,align="center")
        tx=30+(w-(bb[2]-bb[0]))/2; ty=30+(h-(bb[3]-bb[1]))/2
        d.multiline_text((tx,ty),text,font=f,fill=text_color,spacing=7,align="center")
    if angle:
        lay=lay.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    return lay

def paste_center(base, layer, x, y, scale=1.0, alpha=1.0):
    if scale != 1:
        layer=layer.resize((max(1,int(layer.width*scale)),max(1,int(layer.height*scale))),Image.Resampling.LANCZOS)
    if alpha < 1:
        aa=layer.getchannel('A').point(lambda v:int(v*alpha)); layer.putalpha(aa)
    base.alpha_composite(layer,(int(x-layer.width/2),int(y-layer.height/2)))

COLORS=[(255,230,50,255),(255,118,143,255),(61,192,235,255),(169,224,69,255),
        (255,144,55,255),(218,92,215,255),(125,106,206,255),(237,240,232,255)]

src=Image.open(SRC).convert("RGB")

def base_bg():
    im=Image.new("RGBA",(W,H),(247,247,242,255))
    d=ImageDraw.Draw(im)
    # quiet studio sweep
    for y in range(H):
        v=int(250-8*y/H)
        d.line((0,y,W,y),fill=(v,v,min(255,v+2),255))
    d.ellipse((-170,-170,340,340),fill=(255,232,54,28))
    d.ellipse((480,930,900,1350),fill=(255,113,153,25))
    return im

def frame_at(t):
    im=base_bg(); d=ImageDraw.Draw(im)
    # Scene 1: product opening
    if t < 3.2:
        p=ease(t/1.0); fade=clamp((3.2-t)/.45)
        # crop the colorful lower product area, framed as a real source image
        crop=src.crop((0,330,src.width,src.height))
        crop=cover(crop,(620,610)).convert("RGBA")
        card=Image.new("RGBA",(650,650),(255,255,255,255)); card.alpha_composite(crop,(15,20))
        card=card.filter(ImageFilter.GaussianBlur(0.2))
        paste_center(im,card,W/2,710,0.86+0.06*p,fade)
        center_text(d,120,"翰林纸院",font(42,True),(25,28,35,255))
        center_text(d,184,"彩色便利贴",font(72,True),(25,28,35,255))
        center_text(d,275,"灵感随手贴  ·  重点不遗漏",font(28),(92,96,102,255))
        pill(d,(218,1080),"16色可选",(24,27,35,255),fs=28)

    # Scene 2: color shapes, all notes flat
    elif t < 7.0:
        u=(t-3.2)/3.8
        center_text(d,90,"一贴成型，平整不卷边",font(46,True),(25,28,35,255))
        center_text(d,154,"不同颜色 · 不同造型 · 一眼记住",font(25),(93,97,102,255))
        poses=[(210,380,-9),(360,330,6),(510,400,12),(170,610,7),(360,590,-5),(545,640,-11),(265,830,8),(470,850,-4)]
        labels=["IDEA","会议","重点","灵感","待办","提醒","计划","完成"]
        for i,(x,y,a) in enumerate(poses):
            q=ease(clamp((u*1.25-i*.075)/.30))
            lay=note_layer(COLORS[i],(170,170),labels[i],angle=a)
            paste_center(im,lay,x,y,0.25+0.75*q,q)
        # connection accents form a lively composition without curling notes
        d.arc((170,295,565,930),20,155,fill=(35,39,48,90),width=3)
        pill(d,(250,1070),"完全平整贴合",(35,39,48,255),fs=25)

    # Scene 3: peel and reposition using a rigid flat plane
    elif t < 12.2:
        u=(t-7.0)/5.2
        center_text(d,92,"轻松揭下，再贴依然牢",font(47,True),(25,28,35,255))
        center_text(d,158,"动作顺滑 · 无残胶 · 可重复粘贴",font(25),(91,96,102,255))
        # white board surface
        shadow_rect(im,(78,245,642,1050),(255,255,255,255),radius=30,shadow=25,alpha=45)
        d=ImageDraw.Draw(im)
        # target markers
        d.rounded_rectangle((130,370,360,600),radius=14,outline=(210,214,218,255),width=3)
        d.rounded_rectangle((360,680,590,910),radius=14,outline=(210,214,218,255),width=3)
        # two repeated moves: first center to left, then left to bottom-right
        if u < .50:
            v=ease(u/.50); x=470+(245-470)*v; y=455-120*math.sin(math.pi*v)+(485-455)*v
            scale=1+0.08*math.sin(math.pi*v)
        else:
            v=ease((u-.50)/.50); x=245+(475-245)*v; y=485-130*math.sin(math.pi*v)+(795-485)*v
            scale=1+0.08*math.sin(math.pi*v)
        lay=note_layer(COLORS[0],(210,210),"重要\nFOLLOW UP")
        paste_center(im,lay,x,y,scale)
        # motion line and captions
        d.arc((155,330,555,870),300,80,fill=(255,130,35,180),width=5)
        pill(d,(122,965),"① 揭下",(255,128,42,255),fs=23)
        pill(d,(300,965),"② 移位",(52,172,222,255),fs=23)
        pill(d,(478,965),"③ 贴牢",(99,179,68,255),fs=23)

    # Scene 4: smooth handwriting
    elif t < 17.3:
        u=(t-12.2)/5.1
        center_text(d,95,"落笔顺滑，字迹清晰",font(48,True),(25,28,35,255))
        center_text(d,160,"中性笔流畅书写 · 不易晕染",font(26),(89,94,101,255))
        shadow_rect(im,(105,280,615,985),(181,228,251,255),radius=22,shadow=24,alpha=55)
        d=ImageDraw.Draw(im)
        # subtle ruled lines
        for yy in [480,590,700,810]: d.line((160,yy,560,yy),fill=(75,156,198,60),width=2)
        texts=[("今日计划",350,.18),("回复客户",490,.38),("整理资料",600,.58),("15:00 会议",710,.80)]
        for txt,yy,start in texts:
            q=clamp((u-start)/.20)
            if q>0:
                # reveal by mask to simulate real writing
                layer=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(layer)
                ld.text((165,yy),txt,font=font(37,True),fill=(34,47,59,255))
                mask=Image.new("L",(W,H),0); md=ImageDraw.Draw(mask); md.rectangle((150,yy-10,150+430*q,yy+70),fill=255)
                layer.putalpha(Image.composite(layer.getchannel('A'),Image.new('L',(W,H),0),mask))
                im.alpha_composite(layer)
        # pen follows current reveal
        prog=clamp((u-.15)/.75); py=350+470*prog; px=190+300*((prog*4)%1)
        d=ImageDraw.Draw(im)
        d.line((px+100,py-100,px,py),fill=(20,24,30,255),width=18)
        d.line((px+100,py-100,px+112,py-112),fill=(74,78,86,255),width=7)
        d.ellipse((px-6,py-6,px+6,py+6),fill=(20,24,30,255))
        pill(d,(250,1085),"书写顺滑",(25,28,35,255),fs=27)

    # Scene 5: final product wall + brand
    else:
        u=(t-17.3)/7.7
        if u < .52:
            center_text(d,82,"电脑 · 玻璃 · 文件夹 · 笔记本",font(31,True),(35,39,46,255))
            center_text(d,135,"多场景稳稳贴住",font(48,True),(25,28,35,255))
            panels=[(45,245,345,575,"电脑"),(375,245,675,575,"玻璃"),(45,620,345,950,"文件夹"),(375,620,675,950,"笔记本")]
            for i,(x0,y0,x1,y1,lab) in enumerate(panels):
                shadow_rect(im,(x0,y0,x1,y1),(255,255,255,255),radius=20,shadow=15,alpha=35)
                d=ImageDraw.Draw(im)
                if i==0: d.rounded_rectangle((x0+35,y0+40,x1-35,y1-65),radius=10,fill=(45,50,59,255)); d.rectangle((x0+125,y1-65,x0+175,y1-35),fill=(120,125,132,255))
                elif i==1: d.rectangle((x0+50,y0+35,x1-50,y1-35),fill=(222,244,248,255)); d.line((x0+60,y0+60,x1-70,y1-50),fill=(255,255,255,230),width=9)
                elif i==2: d.rounded_rectangle((x0+40,y0+55,x1-40,y1-35),radius=12,fill=(225,229,235,255)); d.rectangle((x0+65,y0+35,x0+175,y0+70),fill=(225,229,235,255))
                else:
                    d.rounded_rectangle((x0+45,y0+40,x1-35,y1-35),radius=12,fill=(247,241,223,255));
                    for yy in range(y0+85,y1-45,38): d.line((x0+70,yy,x1-55,yy),fill=(194,186,168,130),width=2)
                n=note_layer(COLORS[i],(105,105),["TO DO","MEET","IDEA","NOW"][i],angle=[-6,5,4,-5][i])
                paste_center(im,n,(x0+x1)/2,(y0+y1)/2,0.9)
                center_text(ImageDraw.Draw(im),0,"",font(1),(0,0,0))
                d.text((x0+110,y1+10),lab,font=font(23,True),fill=(62,66,73,255))
            pill(d,(250,1070),"粘性稳定",(25,28,35,255),fs=27)
        else:
            v=ease((u-.52)/.48)
            center_text(d,90,"翰林纸院",font(54,True),(25,28,35,255))
            center_text(d,158,"让每一个灵感，都有位置",font(31),(76,80,88,255))
            # actual product image strip and colorful lineup
            prod=src.crop((110,360,src.width-60,860)); prod=cover(prod,(620,410)).convert("RGBA")
            card=Image.new("RGBA",(650,450),(255,255,255,255)); card.alpha_composite(prod,(15,20))
            paste_center(im,card,W/2,530,0.82+0.18*v)
            xs=[105,190,275,360,445,530,615]
            for i,x in enumerate(xs):
                q=ease(clamp((v-i*.06)/.38)); n=note_layer(COLORS[i%len(COLORS)],(92,92),None,angle=-8+i*2.5)
                paste_center(im,n,x,900,0.2+0.8*q,q)
            d=ImageDraw.Draw(im)
            center_text(d,1035,"可重复粘贴  ·  顺滑书写  ·  平整服帖",font(27,True),(33,37,44,255))
            pill(d,(222,1110),"翰林纸院便利贴",(25,28,35,255),fs=28)

    # clean top/bottom safe-area markers: subtle brand bug after intro
    if t>=3.2 and t<21.2:
        d=ImageDraw.Draw(im); d.text((28,1218),"翰林纸院  HANLIN PAPER",font=font(18,True),fill=(85,88,94,170))
    return im.convert("RGB")

def make_audio():
    sr=44100; n=sr*DUR; rng=np.random.default_rng(2026)
    x=np.zeros(n,dtype=np.float64)
    tt=np.arange(n)/sr
    # quiet modern bed: warm chords and soft pulse
    freqs=[220,277.18,329.63]
    for f in freqs:
        x += .015*np.sin(2*np.pi*f*tt)*(0.65+0.35*np.sin(2*np.pi*.12*tt))
    for beat in np.arange(0,DUR,.75):
        s=int(beat*sr); m=min(int(.16*sr),n-s); env=np.exp(-np.arange(m)/(sr*.045))
        x[s:s+m]+=0.055*np.sin(2*np.pi*95*np.arange(m)/sr)*env
    # peel swishes
    for st in [7.35,9.65,10.75]:
        s=int(st*sr); m=int(.5*sr); noise=rng.normal(0,1,m); env=np.sin(np.pi*np.arange(m)/m)**2
        x[s:s+m]+=0.035*noise*env
    # writing scratch texture
    s=int(12.9*sr); m=int(3.8*sr); noise=rng.normal(0,1,m)
    env=.5+.5*np.sin(2*np.pi*6*np.arange(m)/sr)
    x[s:s+m]+=0.010*noise*env
    # end chime
    for st,f in [(21.8,659.25),(22.05,783.99),(22.30,987.77)]:
        s=int(st*sr); m=min(int(1.2*sr),n-s); env=np.exp(-np.arange(m)/(sr*.45))
        x[s:s+m]+=.07*np.sin(2*np.pi*f*np.arange(m)/sr)*env
    x=np.tanh(x*1.15); pcm=(x*32767).astype('<i2')
    with wave.open(WAV,'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(pcm.tobytes())

def main():
    writer=imageio.get_writer(SILENT,fps=FPS,codec='libx264',quality=8,pixelformat='yuv420p',macro_block_size=None)
    poster=None
    for i in range(FPS*DUR):
        fr=frame_at(i/FPS)
        if i==690: poster=fr.copy()
        writer.append_data(np.asarray(fr))
    writer.close()
    if poster: poster.save(POSTER,quality=94)
    make_audio()
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run([ff,'-y','-i',SILENT,'-i',WAV,'-c:v','copy','-c:a','aac','-b:a','160k','-shortest',FINAL],check=True)
    print(FINAL)

if __name__=='__main__': main()
